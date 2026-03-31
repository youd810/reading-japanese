import os
import json
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cursor = conn.cursor()

folder = os.getenv("EN_FOLDER")

files = [f for f in os.listdir(folder) if f.startswith("term")]
for file in sorted(files, key=lambda x: int(x.split("_")[2].split(".")[0])):
    with open(os.path.join(folder, file), "r", encoding="utf-8") as f:
        entries = json.loads(f.read())
        for entry in entries:
            if entry[1] == "":
                continue
            # it's painfully slow without batch execute. don't do this
            cursor.execute(""" 
                INSERT INTO endict(word, reading, definition, rule, score)
                VALUES (%s, %s, %s, %s, %s)""",
                (entry[0], entry[1], json.dumps(entry[5]), entry[3], entry[4]))
            print(f"file: {file}, entry: {entry[0]}")
    print(f"{file} completed")
conn.commit()
conn.close()
print("done")
