import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    conn.cursor_factory = psycopg2.extras.RealDictCursor  #  postgres version of row_factory
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS endict(
            word TEXT,
            reading TEXT,
            definition TEXT,
            rule TEXT,
            score INTEGER
        )""")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_endict_word ON endict(word);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_endict_reading ON endict(reading);")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jpdict(
            word TEXT,
            reading TEXT,
            definition TEXT,
            rule TEXT,
            score INTEGER
        )""")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_jpdict_word ON jpdict(word);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_jpdict_reading ON jpdict(reading);")
    conn.commit()
    conn.close()
    