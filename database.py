import sqlite3

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS endict(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT,
            reading TEXT,
            definition TEXT
    )""")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jpdict(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT,
            reading TEXT,
            definition TEXT
    )""")
    conn.commit()
    conn.close()

