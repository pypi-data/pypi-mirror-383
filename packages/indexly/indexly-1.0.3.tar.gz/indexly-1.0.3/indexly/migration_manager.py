# src/indexly/migration_manager.py
import os
import re
import time
import shutil
import sqlite3
import logging
from typing import Optional
from .config import BASE_DIR, DB_FILE

logger = logging.getLogger(".migrate")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Expected FTS definition
EXPECTED_SCHEMA = {
    "file_index": {
        "fts5": True,
        "columns": ["path", "content", "clean_content", "modified", "hash", "tag"],
        "prefix": "2 3 4",   # desired normalized prefix
        "tokenize": "porter",
    },
    "file_tags": {"columns": ["path TEXT PRIMARY KEY", "tags TEXT"]},
    "file_metadata": {
        "columns": [
            "path TEXT PRIMARY KEY",
            "title TEXT",
            "author TEXT",
            "created TEXT"
        ]
    },
}


def resolve_db_path(db_path: str | None) -> str:
    if not db_path:
        return DB_FILE
    if os.path.isabs(db_path):
        return db_path
    # make it relative to BASE_DIR
    return os.path.join(BASE_DIR, db_path)

# ----------------- helpers -----------------
def backup_database(db_path: str) -> Optional[str]:
    if not os.path.exists(db_path):
        raise FileNotFoundError(db_path)
    ts = time.strftime("%Y%m%d_%H%M%S")
    backup_path = f"{db_path}.bak_{ts}"
    shutil.copy2(db_path, backup_path)
    logger.info(f"📦 Backup created: {backup_path}")
    return backup_path

def _normalize_prefix(pref) -> str:
    if pref is None:
        return ""
    if isinstance(pref, (list, tuple)):
        return " ".join(str(int(x)) for x in pref)
    return " ".join(p for p in str(pref).replace(",", " ").split() if p.strip())

def _has_prefix(create_sql: str, desired_pref: str) -> bool:
    if not create_sql:
        return False
    pattern = r"prefix\s*=\s*['\"]?" + re.escape(desired_pref) + r"['\"]?"
    return re.search(pattern, create_sql, flags=re.IGNORECASE) is not None

def _list_shadow_tables(conn: sqlite3.Connection, base_name: str):
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type IN ('table','index') AND name LIKE ?",
        (f"{base_name}%",),
    )
    return [row[0] for row in cur.fetchall()]

# ----------------- migration history -----------------
def ensure_migration_history(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            migration TEXT NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

def record_migration(conn: sqlite3.Connection, migration_name: str):
    cur = conn.cursor()
    cur.execute("INSERT INTO schema_migrations (migration) VALUES (?)", (migration_name,))
    conn.commit()

def backfill_migrations(conn: sqlite3.Connection):
    """Fill migration history with baseline entries if missing."""
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM schema_migrations")
    count = cur.fetchone()[0]
    if count > 0:
        logger.info("ℹ️ Migration history already populated (%s rows)", count)
        return

    baseline = [
        "baseline_file_index",
        "baseline_file_index_vocab",
        "baseline_file_tags",
        "baseline_file_metadata",
    ]
    for m in baseline:
        cur.execute("INSERT INTO schema_migrations (migration) VALUES (?)", (m,))
        logger.info("📜 Backfilled migration: %s", m)
    conn.commit()

def list_migrations(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("SELECT id, migration, applied_at FROM schema_migrations ORDER BY id")
    return cur.fetchall()

def last_migration(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("SELECT migration, applied_at FROM schema_migrations ORDER BY id DESC LIMIT 1")
    return cur.fetchone()

def migration_applied(conn: sqlite3.Connection, name: str) -> bool:
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM schema_migrations WHERE migration=?", (name,))
    return cur.fetchone() is not None

# ----------------- FTS rebuild -----------------
def rebuild_fts5(conn: sqlite3.Connection, spec: dict, dry_run: bool = False):
    cur = conn.cursor()
    pref_str = _normalize_prefix(spec.get("prefix"))
    tokenize = spec.get("tokenize", "porter")
    cols = spec["columns"]
    cols_sql = ", ".join(cols)

    logger.info(
        "🔁 Preparing to rebuild FTS5 table 'file_index' with prefix='%s' tokenize='%s'",
        pref_str, tokenize
    )
    old_name = "file_index_old"
    new_name = "file_index_new"

    if dry_run:
        logger.info("[DRY-RUN] Would rename file_index -> %s", old_name)
        logger.info(
            "[DRY-RUN] Would CREATE VIRTUAL TABLE %s USING fts5(%s, tokenize='%s'%s)",
            new_name, cols_sql, tokenize,
            f", prefix='{pref_str}'" if pref_str else ""
        )
        logger.info("[DRY-RUN] Would copy data from old -> new and drop old + shadow tables")
        return

    cur.execute("ALTER TABLE file_index RENAME TO file_index_old;")

    pref_clause = f", prefix='{pref_str}'" if pref_str else ""
    create_sql = f"CREATE VIRTUAL TABLE {new_name} USING fts5({cols_sql}, tokenize='{tokenize}'{pref_clause});"
    cur.execute(create_sql)

    cur.execute(f"INSERT INTO {new_name}({cols_sql}) SELECT {cols_sql} FROM file_index_old;")

    cur.execute("DROP TABLE IF EXISTS file_index;")
    cur.execute(f"ALTER TABLE {new_name} RENAME TO file_index;")

    shadow_tables = _list_shadow_tables(conn, "file_index_old")
    for t in shadow_tables:
        cur.execute(f"DROP TABLE IF EXISTS {t};")
        logger.info("Dropped shadow object: %s", t)

    conn.commit()
    logger.info("✅ Rebuilt FTS5 table file_index and removed old shadow tables")

    record_migration(conn, "rebuild_file_index_with_prefix")

# ----------------- ensure functions -----------------
def ensure_fts5(conn: sqlite3.Connection, dry_run: bool = False):
    spec = EXPECTED_SCHEMA["file_index"]
    desired_pref = _normalize_prefix(spec.get("prefix"))
    tokenize = spec.get("tokenize", "porter")
    cur = conn.cursor()

    cur.execute("SELECT sql FROM sqlite_master WHERE type IN ('table','view') AND name='file_index'")
    row = cur.fetchone()
    if not row:
        if dry_run:
            logger.info("[DRY-RUN] Would CREATE virtual table file_index with prefix '%s'", desired_pref)
        else:
            pref_clause = f", prefix='{desired_pref}'" if desired_pref else ""
            cur.execute(
                f"CREATE VIRTUAL TABLE file_index USING fts5({', '.join(spec['columns'])}, tokenize='{tokenize}'{pref_clause});"
            )
            conn.commit()
            logger.info("✅ Created missing FTS5 file_index")
            record_migration(conn, "create_file_index")
    else:
        create_sql = row[0] or ""
        if desired_pref and not _has_prefix(create_sql, desired_pref):
            logger.info("⚠️ Prefix mismatch detected in file_index (needs: %s)", desired_pref)
            rebuild_fts5(conn, spec, dry_run=dry_run)
        else:
            logger.info("✅ file_index OK (prefix present or not required)")

    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='file_index_vocab'")
    if not cur.fetchone():
        if dry_run:
            logger.info("[DRY-RUN] Would CREATE file_index_vocab USING fts5vocab(file_index,'row')")
        else:
            cur.execute("CREATE VIRTUAL TABLE file_index_vocab USING fts5vocab(file_index, 'row');")
            conn.commit()
            logger.info("✅ Created file_index_vocab")
            record_migration(conn, "create_file_index_vocab")

def ensure_normal_tables(conn: sqlite3.Connection, dry_run: bool = False):
    cur = conn.cursor()
    for name, spec in EXPECTED_SCHEMA.items():
        if spec.get("fts5"):
            continue
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,))
        if not cur.fetchone():
            cols_sql = ", ".join(spec["columns"])
            if dry_run:
                logger.info("[DRY-RUN] Would CREATE table %s (%s)", name, cols_sql)
            else:
                cur.execute(f"CREATE TABLE {name} ({cols_sql})")
                conn.commit()
                logger.info("✅ Created missing table %s", name)
                record_migration(conn, f"create_{name}")

# ----------------- run migrations -----------------
def run_migrations(db_path: str, dry_run: bool = False, no_backup: bool = False):
    
    db_path = resolve_db_path(db_path)
    if not os.path.exists(db_path):
        raise FileNotFoundError(db_path)
    
    logger.info("Starting migration: db=%s dry_run=%s no_backup=%s", db_path, dry_run, no_backup)
    if not os.path.exists(db_path):
        raise FileNotFoundError(db_path)

    if not dry_run and not no_backup:
        backup_database(db_path)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        ensure_migration_history(conn)
        backfill_migrations(conn)  # ✅ added
        ensure_normal_tables(conn, dry_run=dry_run)
        ensure_fts5(conn, dry_run=dry_run)
        logger.info("✅ Migration run complete (dry_run=%s)", dry_run)
    except Exception as e:
        logger.exception("Migration failed: %s", e)
        raise
    finally:
        conn.close()
