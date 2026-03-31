import sqlite3
import csv

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("SELECT word, reading, definition, rule, score FROM jpdict") # jpdict / endict
rows = cursor.fetchall()

with open("jpdict.csv", "w", encoding="utf-8", newline="") as f: # jpdict / endict
    writer = csv.writer(f)
    writer.writerow(["word", "reading", "definition", "rule", "score"])
    writer.writerows(rows)