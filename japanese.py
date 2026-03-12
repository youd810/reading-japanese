from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from database import init_db, get_db
import fugashi
import spacy
import json

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"]
)
init_db()
tagger = fugashi.Tagger()

with open("kana.json", "r", encoding="utf-8") as f:
    kana_list = json.loads(f.read())

@app.get("/")
def home():
    return "testing"

@app.get("/api/lookup")
def lookup(word: str, dict: str = "en") -> list:    # "en" is the default arg
    conn = get_db()
    cursor = conn.cursor()
    if dict == "jp":
        cursor.execute("SELECT * FROM jpdict WHERE word = ?", (word,))
    else:
        cursor.execute("SELECT * FROM endict WHERE word = ?", (word,))
    result = cursor.fetchall()
    results = []
    for r in result:
        results.append({
            "word" : r["word"],
            "reading" : r["reading"],
            "definition" : r["definition"]
        })
    return results

nlp = spacy.load("ja_ginza")
@app.post("/api/text")
def text(text: dict) -> dict:
    naiyou = text.get("text")
    valid_attr = ["NOUN", "VERB", "ADJ", "ADV", "NUM", "PROPN", "DET"]
    word_list = [str(word) for word in nlp(naiyou) if word.pos_ in valid_attr]
    return {"words" : word_list}

@app.get("/api/kana")
def kana(ji: str = "h") -> dict: 
    return kana_list["katakana"] if ji == "k" else kana_list["hiragana"]

if __name__ == "__main__":
    uvicorn.run("japanese:app", host="0.0.0.0", port=8008, reload=True) # reload for debugging