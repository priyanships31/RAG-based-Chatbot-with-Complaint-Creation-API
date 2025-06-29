import sqlite3

def init_db():
    conn = sqlite3.connect("complaints.db")
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        complaint_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        phone_number TEXT NOT NULL,
        email TEXT NOT NULL,
        complaint_details TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect("complaints.db")
    conn.row_factory = sqlite3.Row  # Return rows as dicts
    return conn