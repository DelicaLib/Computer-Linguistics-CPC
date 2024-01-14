import os
import json


def find_people(text: str) -> list:
    edited_text = text.replace("\n", "")

    with open("people-parser/test.txt", "w") as f:
        f.write(edited_text)
    os.system("cd people-parser; tomita-parser config.proto; cd ..")

    with open('people-parser/peoples.json') as f:
        try:
            people = json.load(f)
        except:
            return []

    res = set()

    for i in people:
        for j in i["Lead"]:
            for k in j["Span"]:
                res.add(k["Lemma"])

    return list(res)


def find_places(text: str) -> list:
    edited_text = text.replace("\n", "")

    with open("place-parser/test.txt", "w") as f:
        f.write(edited_text)
    os.system("cd place-parser; tomita-parser config.proto; cd ..")

    with open('place-parser/places.json') as f:
        try:
            place = json.load(f)
        except:
            return []

    res = set()

    for i in place:
        for j in i["Lead"]:
            for k in j["Span"]:
                res.add(k["Lemma"])

    return list(res)
