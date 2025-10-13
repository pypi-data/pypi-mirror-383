"""
📄 db_utils.py

Purpose:
    Provides SQLite database connection and initialization helpers.

Key Features:
    - connect_db(): Connects to the SQLite database with row factory.
    - initialize_db(): Ensures required tables (file_index, file_tags) exist.

Usage:
    Used during indexing, searching, and tagging operations.
"""

import sqlite3
import os
import re
import signal
import logging
from .config import DB_FILE
from .path_utils import normalize_path


logger = logging.getLogger(__name__)


user_interrupted = False


def handle_interrupt(sig, frame):
    global user_interrupted
    if not user_interrupted:
        user_interrupted = True
        print("\n⛔ Ctrl+C detected. Cleaning up...")


signal.signal(signal.SIGINT, handle_interrupt)


### 🔧 FILE: db_utils.py — Update `connect_db()`


def connect_db(db_path: str | None = None):
    """
    Connect to the SQLite database.

    - In production, always uses config.DB_FILE.
    - In tests, pytest fixtures may override config.DB_FILE or pass a temporary db_path.
    - Prevents accidental fallback to wrong database file.
    """
    import importlib
    import os
    from . import config

    # Only reload config in pytest to pick up monkeypatched DB_FILE
    if "PYTEST_CURRENT_TEST" in os.environ:
        importlib.reload(config)

    # ✅ Production always uses config.DB_FILE
    # Only respect db_path if we’re in a test or explicitly told to
    if "PYTEST_CURRENT_TEST" in os.environ and db_path:
        path = db_path
    else:
        path = config.DB_FILE

    # print(f"[debug] Using DB: {path}")

    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.create_function("REGEXP", 2, regexp)

    # Ensure required tables exist (idempotent)
    conn.execute(
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS file_index
        USING fts5(
            path, 
            content, 
            clean_content, 
            modified,
            alias, 
            hash, 
            tag, 
            tokenize = 'porter', 
            prefix='2 3 4'
        );
        """
    )

    cursor = conn.cursor()
    cursor.execute(
        "CREATE VIRTUAL TABLE IF NOT EXISTS file_index_vocab USING fts5vocab(file_index, 'row');"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS file_tags (path TEXT PRIMARY KEY, tags TEXT);"
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS file_metadata (
            path TEXT PRIMARY KEY,
            title TEXT,
            author TEXT,
            subject TEXT,
            created TEXT,
            last_modified TEXT,
            last_modified_by TEXT,
            camera TEXT,
            image_created TEXT,
            dimensions TEXT,
            format TEXT,
            gps TEXT
        );
        """
    )

    conn.commit()
    return conn

def _sync_path_in_db(old_path: str, new_path: str):
    """
    Fully synchronize a renamed file across all DB tables:
    - Updates path in all tables
    - Preserves hash, metadata, and tags
    - Writes old filename into alias column
    """
    from pathlib import Path

    old_path_str = normalize_path(old_path)
    new_path_str = normalize_path(new_path)
    old_name = Path(old_path_str).name

    try:
        conn = connect_db()
        cur = conn.cursor()

        # --- file_index ---
        cur.execute(
            """
            UPDATE file_index
            SET path = ?, alias = ?
            WHERE path = ?
            """,
            (new_path_str, old_name, old_path_str),
        )

        # --- file_metadata ---
        cur.execute(
            """
            UPDATE file_metadata
            SET path = ?
            WHERE path = ?
            """,
            (new_path_str, old_path_str),
        )

        # --- file_tags ---
        cur.execute(
            """
            UPDATE file_tags
            SET path = ?
            WHERE path = ?
            """,
            (new_path_str, old_path_str),
        )

        conn.commit()
        conn.close()

        logger.info(f"🗄️ DB fully synced for rename: {old_path_str} → {new_path_str}")
        return True

    except Exception as e:
        logger.error(f"⚠️ DB sync failed for rename {old_path_str} → {new_path_str}: {e}")
        return False




def regexp(pattern, string):
    if user_interrupted:
        raise KeyboardInterrupt  # force early exit

    if string is None:
        return False
    try:
        return re.search(pattern, string, re.IGNORECASE) is not None
    except re.error:
        return False


def get_tags_for_file(file_path, db_path=None):
    file_path = normalize_path(file_path)
    conn = connect_db(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT tags FROM file_tags WHERE path = ?", (file_path,))
    row = cursor.fetchone()
    conn.close()
    return row["tags"].split(",") if row else []
