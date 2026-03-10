import os
import json
from dotenv import load_dotenv
from database import get_db, init_db

init_db()
conn = get_db()
cursor = conn.cursor()

load_dotenv()
folder = os.getenv("EN_FOLDER")

files = [f for f in os.listdir(folder) if f.startswith("term")] # filter first then sort
for file in sorted(files, key=lambda x: int(x.split("_")[2].split(".")[0])): # sorted() for sorting the filename first     
    word_list = []                                                           # step: term_bank_10.json > 10.json > 10 > int(10)
    reading_list = []
    definition_list = []
    with open(os.path.join(folder, file), "r", encoding="utf-8") as f: #path.join() if the script is in different loc from the file it wants to open
        entries = json.loads(f.read()) #json.load() (or loads, whatever the difference is) to load json files, otherwise everything will turn into a string
        for entry in entries:
            if entry[1] == "":
                continue
            word_list.append(entry[0])
            reading_list.append(entry[1])
            definition_list.append(entry[5])
        for i in range(len(word_list)):
            cursor.execute("""
                INSERT INTO endict(word, reading, definition)
                VALUES (?, ?, ?)""", (word_list[i], reading_list[i], json.dumps(definition_list[i]))) #dumps to turn them into json cuz tuple doesn't work with columns
            print(f"file: {file}, entry: {word_list[i]}")
    print(f"{file} comlpleted")
conn.commit()
conn.close()
print("done")
