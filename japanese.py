from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from database import init_db, get_db
import spacy
import json
import jaconv

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


with open("assets/chars.json", "r", encoding="utf-8") as f:
    chars = json.loads(f.read())

@app.get("/api/home")
def homepage():
    return chars


def convert_to_sets(reasons_data):
    converted = []
    for reason, rules in reasons_data.items():
        variants = []
        for rule in rules:
            # convert to set first thing so we can check rule overlaps with `&` operation later
            variants.append((
                rule["kanaIn"],
                rule["kanaOut"],
                set(rule["rulesIn"]), 
                set(rule["rulesOut"])
            ))
        converted.append((reason, variants))
        # format example
        # ("past", [
        #   ("った", "う", {'v5'}, set()),
        #   "た", "る", {'v1'}, set()),
        #   etc
        #  ])
    return converted

with open("assets/deinflection.json", "r", encoding="utf-8") as f:
    deinflect_raw = json.loads(f.read())
    deinflect_conv = convert_to_sets(deinflect_raw)

def deinflect_word(source):
    results = [{"word": source, "rules": set(), "reasons": []}]
    i = 0
    # `while` instead of `for` because the latter only captures len() at the start of the loop, while the former checks it every iteration
    # and since len of results is dynamic with the append at every iteration (except when it has no more to append)
    while i < len(results): 
        item = results[i]
        for reason, variants in deinflect_conv: # first and multi-step deinflections combined
            for kana_in, kana_out, rules_in, rules_out in variants:
                # checks if two overlapping rules exist to filter out rules_in that don't match (even if reason is the exact same)
                # 例: adj-i (item rules) can only match with adj-i (rules in) and so on
                # also combining these 3 cond into if true might be spaghetti so i'll leave them be for now  
                if item["rules"] and (not item["rules"] & rules_in): 
                    continue
                if not item["word"].endswith(kana_in):
                    continue
                if len(item["word"]) - len(kana_in) + len(kana_out) <= 0:
                    continue
                new_word = item["word"][:-len(kana_in)] + kana_out
                results.append({
                    "word": new_word,
                    "rules": rules_out,
                    "reasons": [reason] + item["reasons"]
                })
        i += 1
    return results


# TODO: restore rules, look for raw word first, if none then deiflect (label them with their rule also). query with said rule. 
@app.get("/api/lookup")
def lookup(word: str, dict: str = "en") -> list:
    #if dict not in ["endict", "jpdict"]: # this should prevent sql injections (hopefully)
    #    return ["ないです"] TODO: implement these later, or not
    conn = get_db()                                 
    cursor = conn.cursor()
    deinflects = []
    conv = word
    if '\u30a1' <= word[0] <= '\u30f6': # converts katakana to hiragana
        conv = jaconv.kata2hira(word)
    for w in [word, conv]:
        for i in range(1, len(w)): # first deinflection, skips i = 0 to reduce noises
            substring = w[:i+1]
            print(f"sub: {substring}")
            # sends substring of incremental len to deinflect
            # putting this in here for now, might move later
            for d in deinflect_word(substring): 
                if d["word"] != substring: # this just ensures word doesn't duplicate with word param in the query later
                    deinflects.append({
                        "original" : substring,
                        "word" : d["word"],
                        "rules" : d["rules"] 
                    })
    candidates = [d["word"] for d in deinflects]
    placeholders = ','.join("?" * len(candidates))
    if dict == "jp":
    # so the way the query below works is that it will get all words from the db one by one 
    # and check if the pattern word+% match `?`
    # for example does the pattern 民主% match 民主主義？ (or vice versa) 
    # the parentheses at the start are important to wrap the results of the two selects into one, otherwise it will return an error 
    # TODO: FIX DEINFLECTION AND SORTING AND HIGHLIGHING (done?　YES THEY'RE ALL DONE DON'T TOUCH THEM ANYMORE *coping*) 
        cursor.execute(f"""
            SELECT * FROM (
                SELECT *, ? as input FROM jpdict WHERE word IN ({placeholders}) OR reading IN ({placeholders})
                UNION ALL
                SELECT *, ? as input FROM jpdict 
                WHERE (? LIKE word || '%') OR (? LIKE reading || '%' AND LENGTH(reading) >= 1) 
                OR (? LIKE word || '%') OR (? LIKE reading || '%' AND LENGTH(reading) >= 1))
            ORDER BY 
                CASE
                    WHEN input LIKE word || '%' THEN LENGTH(word)
                    ELSE LENGTH(reading)
                END DESC,
                CASE WHEN input LIKE word || '%' OR input LIKE reading || '%' THEN 1 ELSE 0 END DESC,
                LENGTH(word) DESC,
                word ASC""", [word] + candidates + candidates + [word, word, word, conv, conv])  
    # in the case of CASE, it would only get words/readings that are already filtered by WHERE
    # the logic itself is similar to WHERE with the matching stuff
    # theoretically i can merge them into 1 query with dict argument being dict name but i'm not risking it 
    else:                                                             
        cursor.execute(f"""
            SELECT * FROM (
                SELECT *, ? as input FROM endict WHERE word IN ({placeholders}) OR reading IN ({placeholders})
                UNION ALL
                SELECT *, ? as input FROM endict 
                WHERE (? LIKE word || '%') OR (? LIKE reading || '%' AND LENGTH(reading) >= 1) 
                OR (? LIKE word || '%') OR (? LIKE reading || '%' AND LENGTH(reading) >= 1))
            ORDER BY CASE
                WHEN input LIKE word || '%' THEN LENGTH(word)
                ELSE LENGTH(reading)
            END DESC,
            word ASC""", [word] + candidates + candidates + [word, word, word, conv, conv])  
    result = cursor.fetchall()
    results = []
    for r in result:
        # this prevents noises to get appended 例: filtering out 乞い from word param こさ
        is_direct = (word.startswith(r["word"]) or word.startswith(r["reading"]) or conv.startswith(r["reading"]))
        # these are for the highlighting
        # basically finds the longest possible string of valid chars 
        matching_deinflect = None
        matching_deinflects = [
            d for d in deinflects
            if (r["word"] == d["word"] or r["reading"] == d["word"]) # checks if d exists in result
            and (not d["rules"] or r["rule"] in d["rules"])  # checks if d has rule or one of its rules matches with r's
        ]
        if matching_deinflects:
            matching_deinflect = max(matching_deinflects, key=lambda x: len(x["original"])) # original refers to the pre-inflected word
        if not is_direct and not matching_deinflects:
            continue
        if matching_deinflect:
            length = len(matching_deinflect["original"])
        elif word.startswith(r["reading"]) and len(r["reading"]) >= 1:
            length = len(r["reading"])
        elif conv.startswith(r["reading"]) and len(r["reading"]) >= 1:
            length = len(r["reading"])
        else:
            length = len(r["word"])
        # since it's a json string by default i need to parse the def back as a python object
        # well it's because i didn't set ensure_ascii to True when dumping them into the database  
        # which turned the letters into unicode bytes 
        results.append({
            "word": r["word"],
            "reading": r["reading"],
            "definition": json.loads(r["definition"]),
            "len": length
        })          
    conn.close()
    return results                                    


# imagine having to resort to using nlp lib just to make a word counter lmao
nlp = spacy.load("ja_ginza")

@app.post("/api/text")
def text(text: dict) -> dict:
    naiyou = text.get("text")
    # for more details refer to "assets/POS_tags.md"
    valid_attr = ["NOUN", "VERB", "ADJ", "ADV", "NUM", "PROPN", "DET", "CCONJ", "ADP", "PRON", "INTJ", "SCONJ"] # it's prob better if i just put exceptions instead
    word_list = []
    # still flawed but decent enough for now
    tokens = list(nlp(naiyou))
    i = 0
    while i < len(tokens): # while instead of for loop since we want to set i = j and not get reassigned to i += 1 every iteration
        word = tokens[i]
        if word.pos_ in valid_attr and word.dep_ != "fixed": # words with a `fixed` dependency is processed in a different way so we filter them out (cont)
            compound = word.text
            j = i + 1
            while j < len(tokens): # starts an inner loop to process i's relation to words after it
                # (cont) an exception would be if a words's POS are these two. 
                if tokens[j].pos_ in ["AUX", "PART"] or tokens[j].dep_ == "fixed": 
                    compound += tokens[j].text
                    j += 1
                elif tokens[j].pos_ == "SCONJ":
                    prev_morph = str(tokens[j-1].morph)
                    if "終止形" in prev_morph: # 終止形 acts as an end signal to the current j, so the current j/sconj should start as a new word (i+1)
                        break
                    compound += tokens[j].text # otherwise we glue it to current word (i) 例: 泣い + て
                    j += 1
                else:
                    break
            if compound.strip(): # filters whitespaces of any kind (hopefully)
                word_list.append(compound)
            # i = j so for the next i iteration, j indexes (which has fulfilled their task in the inner loop) are skipped 
            # so no more 泣いていた  ていた  い  duplicates
            i = j 
        elif word.dep_ == "fixed":
            # glues multiple consecutive `fixed` dependendcies into one word
            # 例: すぎ + ない = すぎない
            compound = word.text
            j = i + 1
            while j < len(tokens) and tokens[j].dep_ == "fixed": # same as the first inner loop
                compound += tokens[j].text
                j += 1
            word_list.append(compound)
            i = j
        else:
            i += 1
    return {"words" : word_list}


with open("assets/kana.json", "r", encoding="utf-8") as f:
    kana_list = json.loads(f.read())

with open("assets/yojijukugo.json", "r", encoding="utf-8") as f:
    yoji = json.loads(f.read())

@app.get("/api/quiz")
def kana(ji: str):
    if ji == "k":
        return kana_list["katakana"]  
    elif ji == "h":
        return kana_list["hiragana"]
    else:
        return yoji


with open("assets/texts.json", "r", encoding="utf-8") as f:
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