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


@app.get("/")
def home():
    return "hey buddy i think you got the wrong door. the leather club is two blocks down."

@app.get("/api/lookup")
def lookup(word: str, dict: str = "en") -> list:    # "en" is the default arg
    conn = get_db()                                 # also apparently lists, string, or anything as simple only requires queries instead of req body?
    cursor = conn.cursor()
    # so the way the query below works is that it will get all words from the db one by one 
    # and check if the pattern word+% match `?`
    # for example does the pattern 民主% match 民主主義？ (or vice versa) 
    # TODO: IMPROVE QUERY TO DEINFLECT WORDS TO THEIR BASIC FORM (例: 行けば to 行く)
    if dict == "jp":
        cursor.execute("""
            SELECT * FROM jpdict 
            WHERE (? LIKE word || '%') OR (? LIKE reading || '%' AND LENGTH(reading) >= 1) 
            ORDER BY CASE
                WHEN ? LIKE word || '%' THEN LENGTH(word)
                ELSE LENGTH(reading)
            END DESC""", (word, word, word)) 
    # in the case of CASE, it would only get words/readings that are already filtered by WHERE
    # the logic itself is similar to WHERE with the matching stuff
    else:                                                                        
        cursor.execute("""
            SELECT * FROM endict 
            WHERE (? LIKE word || '%') OR (? LIKE reading || '%' AND LENGTH(reading) >= 1) 
            ORDER BY CASE
                WHEN ? LIKE word || '%' THEN LENGTH(word)
                ELSE LENGTH(reading)
            END DESC""", (word, word, word)) 
    result = cursor.fetchall()
    results = []
    for r in result:
        if word.startswith(r["reading"]) and len(r["reading"]) >= 1:
            length = len(r["reading"])
        else:
            length = len(r["word"])
        # since it's a json string by default i need to parse the def back as a python object
        # well it's because i didn't set ensure_ascii to True when dumping them into the database  
        # which turned the letters into unicode bytes 
        results.append({
            "word" : r["word"],
            "reading" : r["reading"],
            "definition" : json.loads(r["definition"]),
            "len" : length                 
        })                                            
    return results                                    


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


with open("kana.json", "r", encoding="utf-8") as f:
    kana_list = json.loads(f.read())

@app.get("/api/kana")
def kana(ji: str = "h") -> dict: 
    return kana_list["katakana"] if ji == "k" else kana_list["hiragana"]


with open("texts.json", "r", encoding="utf-8") as f:
    texts = json.loads(f.read())

@app.get("/api/reading")
def reading(field: str = "literature", diff: str = "easy") -> dict:
    # making the arg names and key names the same saves the effort of if nesting
    # if i assign the result in a var it works, but not with returning the result directly??
    result = texts[field.lower()][diff.lower()]
    return result
    # below is an example of what will happen otherwise
#   if field == "lit":
#       text = texts["literature"]
#       if diff == "e":
#           return {"text" : text["easy"]["text"], "count" : text["easy"]["count"]}
#       elif diff == "m":
#           return texts["literature"]["medium"]["text"]
#       elif diff == "h":
#           return texts["literature"]["hard"]["text"]
#   elif field == "pol":
#       ...

if __name__ == "__main__":
    uvicorn.run("japanese:app", host="0.0.0.0", port=8008, reload=True) # reload for debugging