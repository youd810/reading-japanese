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
            definition TEXT,
            rule TEXT,
            score INTEGER
    )""")
    # index for assingning each word to its own index and make it easier to look up
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_endict_word ON endict(word);")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jpdict(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT,
            reading TEXT,
            definition TEXT,
            rule TEXT,
            score INTEGER
    )""")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_jpdict_word ON jpdict(word);")
    conn.commit()
    conn.close()

