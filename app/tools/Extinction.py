import json
import os
from app import settings
import ast

def capitalise_text(text):
    str=""
    text = text.replace("_", " ")
    for word in  text.split(" "):
        w = word[0].upper() + word[1:]
        if str == "":
            str = w
        else:
            str += ' ' + w

    return str
def main(password=None, value=None):
    animallist = []
    with open(os.path.join(settings.APP_STATIC, 'img/WWF/list.csv'))as f:
        for line in f:
            row = ast.literal_eval(line)
            for elem in range(3, len(row)):
                row[elem] = row[elem].replace('../', '')
            row[4] = capitalise_text(row[4])
            animallist.append(row)
    animallist = sorted(animallist)
    return animallist