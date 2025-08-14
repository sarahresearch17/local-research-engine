import sqlite3
from pathlib import Path

DB_PATH = Path("outputs/policy.db")

def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS docs (
            id INTEGER PRIMARY KEY,
            title TEXT,
            source_path TEXT,
            organization TEXT,
            pub_date TEXT
        );
    """)
    conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS docs_fts
        USING fts5(content, content_rowid='id', tokenize='porter');
    """)
    conn.commit()
    conn.close()