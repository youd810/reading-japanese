import os
import json
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cursor = conn.cursor()

folder = os.getenv("JP_FOLDER")

with open(os.path.join(folder, "term_bank_1.json"), "r", encoding="utf-8") as f:
    entries = json.loads(f.read())
    rows = []
    for entry in entries:
        word = entry[0]
        reading = entry[1]
        definition = entry[5]
        rule = entry[3]
        score = entry[4]
        def_temp = []
        for d in definition:
            n = d.find("\n")
            def_temp.append(d[n+1:].strip())
        rows.append((word, reading, json.dumps(def_temp), rule, score))
    execute_values(cursor, """
        INSERT INTO jpdict(word, reading, definition, rule, score)
        VALUES %s""", rows)
    print(f"entry: {word}, {len(rows)} entries added")
conn.commit()
conn.close()
print("done")


