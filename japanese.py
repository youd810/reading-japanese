from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from database import init_db, get_db
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

with open("kana.json", "r", encoding="utf-8") as f:
    kana_list = json.loads(f.read())

@app.get("/")
def home():
    return "hey buddy i think you got the wrong door. the leather club is two blocks down."

@app.get("/api/lookup")
def lookup(word: str, dict: str = "en") -> list:    # "en" is the default arg
    conn = get_db()
    cursor = conn.cursor()
    # so the way the query below works is that it will get all words from the db one by one 
    # and check if the pattern word+% match `?`
    # for example does the pattern 民主% match 民主主義？ (or vice versa) 
    if dict == "jp":
        cursor.execute("SELECT * FROM jpdict WHERE ? LIKE word || '%' ORDER BY LENGTH(word) DESC", (word,)) 
    else:                                                                        
        cursor.execute("SELECT * FROM endict WHERE ? LIKE word || '%' ORDER BY LENGTH(word) DESC", (word,)) 
    result = cursor.fetchall()
    results = []
    for r in result:
        results.append({
            "word" : r["word"],
            "reading" : r["reading"],
            "definition" : json.loads(r["definition"]) # since it's a json string by default i need to parse it back as a python object
        })                                             # well it's because i didn't set ensure_ascii to True when dumping them to the database   
    return results                                     # which turned the letters into unicode bytes

# imagine having to resort to using nlp lib just to make a word counter lmao
nlp = spacy.load("ja_ginza")

@app.post("/api/text")
def text(text: dict) -> dict:
    naiyou = text.get("text")
    valid_attr = ["NOUN", "VERB", "ADJ", "ADV", "NUM", "PROPN", "DET", "CCONJ", "ADP", "PRON", "INTJ"] # it's prob better if i just put exceptions instead
    word_list = []
    # still flawed but decent enough for now
    for word in nlp(naiyou):    
        if word.pos_ in valid_attr:
            compound = str(word)
            for child in word.children: # x.children gives you all tokens that point to the current token as their head.
                if child.pos_ in ["AUX", "SCONJ"]:
                    compound += str(child)
            word_list.append(compound)
    return {"words" : word_list}

@app.get("/api/kana")
def kana(ji: str = "h") -> dict: 
    return kana_list["katakana"] if ji == "k" else kana_list["hiragana"]

if __name__ == "__main__":
    uvicorn.run("japanese:app", host="0.0.0.0", port=8008, reload=True) # reload for debugging