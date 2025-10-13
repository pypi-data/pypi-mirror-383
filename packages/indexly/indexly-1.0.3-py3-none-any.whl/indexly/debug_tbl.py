"""
Debug tool for indexly database configuration and content.

Usage:
    python -m indexly.debug_tbl                          # ✅ default: debug metadata and file_index tables
    python -m indexly.debug_tbl --show-index              # ✅ show file_index with alias and other details
    python -m indexly.debug_tbl --show-migrations         # ✅ show all migration history
    python -m indexly.debug_tbl --show-migrations --last 5  # ✅ show last 5 migrations
"""

import os
import sqlite3
import argparse
from .config import DB_FILE
from .db_utils import connect_db


def debug_file_index_table():
    print("\n📁 Debugging file_index table...\n")

    if not os.path.exists(DB_FILE):
        print(f"❌ DB file not found at: {DB_FILE}")
        return

    conn = connect_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='file_index';")
    if not cursor.fetchone():
        print("❌ file_index table not found.")
        conn.close()
        return

    # Show column info
    print("📋 Columns in file_index:")
    cursor.execute("PRAGMA table_info(file_index);")
    for col in cursor.fetchall():
        print(f"  - {col['name']}")

    # Count total rows
    cursor.execute("SELECT COUNT(*) AS total FROM file_index;")
    total = cursor.fetchone()["total"]
    print(f"\n📊 Total rows: {total}")

    # Show sample entries (focus on alias)
    print("\n🔍 Sample entries (showing alias and metadata fields):")
    try:
        cursor.execute("""
            SELECT 
                path, 
                alias,
                tag,
                modified,
                substr(content, 1, 80) AS snippet
            FROM file_index
            ORDER BY modified DESC
            LIMIT 5;
        """)
        rows = cursor.fetchall()
        if not rows:
            print("⚠️ No entries found in file_index.")
        for row in rows:
            print(f"- path: {row['path']}")
            print(f"  alias: {row['alias']}")
            print(f"  tag: {row['tag']}")
            print(f"  modified: {row['modified']}")
            print(f"  content snippet: {row['snippet']}\n")
    except Exception as e:
        print(f"⚠️ Error fetching file_index rows: {e}")

    # Show alias summary (count of distinct values)
    print("📦 Alias summary:")
    try:
        cursor.execute("""
            SELECT 
                COUNT(*) AS total_aliases,
                COUNT(DISTINCT alias) AS unique_aliases
            FROM file_index
            WHERE alias IS NOT NULL AND alias != '';
        """)
        stats = cursor.fetchone()
        print(f"  Total aliases: {stats['total_aliases']}")
        print(f"  Unique aliases: {stats['unique_aliases']}")
    except Exception as e:
        print(f"⚠️ Error counting alias stats: {e}")

    conn.close()


def debug_metadata_table():
    print("📂 Database file check:")
    if os.path.exists(DB_FILE):
        size = os.path.getsize(DB_FILE)
        print(f"✅ DB exists at: {DB_FILE}")
        print(f"   Size: {size / 1024:.2f} KB")
    else:
        print(f"❌ DB file not found at: {DB_FILE}")
        return

    conn = connect_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # List tables
    print("\n📋 Checking available tables...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row["name"] for row in cursor.fetchall()]
    print("✅ Found tables:", tables if tables else "⚠️ None found")

    # Debug file_metadata
    if "file_metadata" in tables:
        print("\n📋 Columns in file_metadata:")
        cursor.execute("PRAGMA table_info(file_metadata);")
        for col in cursor.fetchall():
            print(f"  - {col['name']}")

        print("\n🔍 Sample entries (with FTS content):")
        try:
            cursor.execute("""
                SELECT 
                    fm.path,
                    fm.title,
                    fm.author,
                    fm.camera,
                    fm.created,
                    fm.dimensions,
                    fm.format,
                    fm.gps,
                    fi.alias
                FROM file_metadata fm
                LEFT JOIN file_index fi ON fm.path = fi.path
                LIMIT 3;
            """)
            rows = cursor.fetchall()
            if not rows:
                print("⚠️ No rows found in file_metadata or file_index.")
            for row in rows:
                print(dict(row))
        except Exception as e:
            print(f"⚠️ Error fetching metadata rows: {e}")
    else:
        print("❌ file_metadata table not found")

    # Debug file_tags
    if "file_tags" in tables:
        print("\n🏷️ Sample entries in file_tags:")
        try:
            cursor.execute("SELECT path, tags FROM file_tags LIMIT 3;")
            for row in cursor.fetchall():
                print(dict(row))
        except Exception as e:
            print(f"⚠️ Error fetching tags rows: {e}")
    else:
        print("❌ file_tags table not found")

    conn.close()


def show_migrations(last: int | None = None):
    if not os.path.exists(DB_FILE):
        print(f"❌ DB file not found at: {DB_FILE}")
        return

    conn = connect_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='schema_migrations';
    """)
    if not cursor.fetchone():
        print("⚠️ No migration history table found.")
        conn.close()
        return

    print("\n📜 Migration History:")
    if last:
        cursor.execute(
            "SELECT id, migration, applied_at FROM schema_migrations ORDER BY id DESC LIMIT ?;",
            (last,)
        )
        rows = cursor.fetchall()
        rows.reverse()
    else:
        cursor.execute("SELECT id, migration, applied_at FROM schema_migrations ORDER BY id;")
        rows = cursor.fetchall()

    if rows:
        for row in rows:
            print(f"#{row['id']:03d} | {row['migration']} | {row['applied_at']}")
    else:
        print("⚠️ No migrations recorded yet.")
    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Debug indexly database tables and migrations")
    parser.add_argument("--show-index", action="store_true", help="Show file_index table with alias and stats")
    parser.add_argument("--show-migrations", action="store_true", help="Show migration history")
    parser.add_argument("--last", type=int, help="Show only the last N migrations (requires --show-migrations)")

    args = parser.parse_args()

    if args.show_migrations:
        show_migrations(last=args.last)
    elif args.show_index:
        debug_file_index_table()
    else:
        debug_metadata_table()
        debug_file_index_table()
