from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from database import init_db, get_db
import spacy
import json
import ginza
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


with open("assets/deinflection.json", "r", encoding="utf-8") as f:
    deinflect = json.loads(f.read())

# TODO: restore rules, look for raw word first, if none then deiflect (label them with their rule also). query with said rule. 
@app.get("/api/lookup")
def lookup(word: str, dict: str = "en") -> list:    # "en" is the default arg
    conn = get_db()                                 # also apparently lists, string, or anything as simple only requires queries instead of req body?
    cursor = conn.cursor()
    #if dict not in ["endict", "jpdict"]:
    #    return ["no"]
    pairs = [] # a list of tuples of (original, deinflect) to validate later
    candidates = []
    deinflects = []
    all_rules = [rule for rules in deinflect.values() for rule in rules] # deinflect = {category : rules}
    # if not all('\u4e00' <= c <= '\u9fff' for c in word[0:4]): # checks if yojijukugo, if no use nlp
    #     word_pre = nlp(word)
    #     words = [span for span in ginza.bunsetu_spans(word_pre)]
    #     print(words)
    #     word = words[0].text
    #if len(words) > 10: TODO idk jsut whatever dude this is tiring i want to go home (TRY RECURSIVE FUNC DUMBASS (IT DOESN'T WORK SMARTASS YOU NEED A RULE LIST FIRST))
    # WHICH MEANS REFACTORINGG THHE WHOLE THING AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    #    word = words[0].text + words[1].text
    # TODO : TEXT PADDING FOR /text
    conv = word
    if '\u30a1' <= word[0] <= '\u30f6': # converts katakana to hiragana
        conv = jaconv.kata2hira(word)
    print(f"WOOOOOOOOOOOORD: {word}")
    for w in [word, conv]:
        for i in range(len(w)): # first deinflection
            if i == 0:
                continue
            substring = w[:i+1]
            for rule in all_rules:
                #candidates.append((candidate, rule["rulesOut"]))
                # each loop checks whether the current substring ends with the current deinflection rule 
                if substring.endswith(rule["kanaIn"]):
                    candidate = substring[:-len(rule["kanaIn"])] + rule["kanaOut"]
                    pairs.append((substring, candidate, rule["rulesOut"]))
                    candidates.append(candidate)
                    deinflects.append(rule)
    if candidates: # multi-step deinflection
        for candidate in candidates:
            for rule in all_rules:
                if candidate.endswith(rule["kanaIn"]):
                    candidate_new = candidate[0][:-len(rule["kanaIn"])] + rule["kanaOut"]
                    if candidate_new not in [candidate[0] for candidate in candidates]:
                        pairs.append((candidate, candidate_new, rule["rulesOut"]))
                        candidates.append(candidate_new)
                        deinflects.append(rule)
    placeholders = ','.join("?" * len(candidates))
    if dict == "jp":
    # so the way the query below works is that it will get all words from the db one by one 
    # and check if the pattern word+% match `?`
    # for example does the pattern 民主% match 民主主義？ (or vice versa) 
    # the parentheses at the start are important to wrap the results of the two selects into one, otherwise it will return an error 
    # TODO: FIX DEINFLECTION AND SORTING AND HIGHLIGHING (done?　YES THEY'RE ALL DONE DON'T TOUCH THEM ANYMORE *coping*) 
    # ) AND (rule IN ({placeholders}))
    # + [str(candidate[1]) for candidate in candidates]
        print(f"asd: {word}")
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
                word ASC""", [word]  + candidates + candidates + [word, word, word, conv, conv])  
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
    print(f"{word}, {conv}") 
    result = cursor.fetchall()
    # validates so only deinflected words (pair[1]) that are actually exsist in result get in for sorting
    # (well basically to make the highlighting non-greedy)
    valid_pairs = [pair for pair in pairs if pair[1] in [r["word"] for r in result]]
    #for pair in pairs: 
    #    for r in result:

    results = []
    for r in result:
        #print(word.startswith(r["reading"]))
        #if word.startswith(r["reading"]):
        #    print(r["reading"])
        #print(f"valid: {valid_pairs}")
        print(f"candidates: {candidates}, pairs: {pairs}")
        #print(f"reading: '{r['reading']}', len: {len(r['reading'])}")
        #print(f"startswith: {word.startswith(r['reading'])}, len check: {len(r['reading']) >= 1}")
        #print(deinflects)
        if valid_pairs:
            # 0 = original, 1 = deinflect
            # also max returns whatever type you put in (in this case tuple), hence the [0] at the very end
            # why does this work even without filtering??? nope, it only does when valid is truthy
            length = len(max(valid_pairs, key=lambda x: len(x[0]))[0]) 
        elif word.startswith(r["reading"]) and len(r["reading"]) >= 1:
            length = len(r["reading"])
        elif conv.startswith(r["reading"]) and len(r["reading"]) >= 1:
            length = len(r["reading"])
        else:
            length = len(r["word"])
        # since it's a json string by default i need to parse the def back as a python object
        # well it's because i didn't set ensure_ascii to True when dumping them into the database  
        # which turned the letters into unicode bytes 
        for pair in pairs:
            for rule in pair[2]:
                cursor.execute("""
                    SELECT * FROM jpdict
                    WHERE (word = ? OR reading = ?) AND rule = ?
                """, [pair[1], pair[1], rule])
                for r in cursor.fetchall():
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