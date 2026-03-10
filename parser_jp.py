import os
import json
from dotenv import load_dotenv
from database import get_db, init_db

init_db()
conn = get_db()
cursor = conn.cursor()

load_dotenv()
folder = os.getenv("JP_FOLDER")

with open(os.path.join(folder, "term_bank_1.json"), "r", encoding="utf-8") as f:
    entries = json.loads(f.read())
    for entry in entries:
        word = entry[0]
        reading = entry[1]
        definition = entry[5]
        def_temp = [] # no need to empty with .clear() since it gets reassigned every loop
        for d in definition:
            n = d.find("\n")
            def_temp.append(d[n+1:].strip()) # `\n` only has 1 len
        cursor.execute("""
            INSERT INTO jpdict(word, reading, definition)
            VALUES (?, ?, ?)""", (word, reading, json.dumps(def_temp)))
        print(f"entry: {word}")
conn.commit()
conn.close()
print("done")


