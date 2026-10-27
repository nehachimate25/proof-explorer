"""
SQLite database connection and initialization.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "proofexplorer.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            statement TEXT NOT NULL,
            proof_method TEXT NOT NULL,
            result TEXT NOT NULL,
            num_steps INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()
