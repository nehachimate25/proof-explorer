"""
History model -- simple data access layer over the `history` table.
"""

from database.db import get_connection


def add_entry(statement, proof_method, result, num_steps):
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO history (statement, proof_method, result, num_steps) VALUES (?, ?, ?, ?)",
        (statement, proof_method, result, num_steps),
    )
    conn.commit()
    entry_id = cur.lastrowid
    conn.close()
    return entry_id


def list_entries():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM history ORDER BY created_at DESC, id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_entry(entry_id):
    conn = get_connection()
    conn.execute("DELETE FROM history WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()


def get_entry(entry_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM history WHERE id = ?", (entry_id,)).fetchone()
    conn.close()
    return dict(row) if row else None
