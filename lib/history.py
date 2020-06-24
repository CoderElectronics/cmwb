import json, os

curpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../config/history.json")

def addhistory(page):
    historyfile = {}
    with open(curpath, mode="r") as fn:
        historyfile = json.load(fn)
    historyfile["history"].append(page)
    with open(curpath, mode="w") as fn:
        json.dump(historyfile, fn)

def clearhistory():
    with open(curpath, mode="w") as fn:
        json.dump({"history":[]}, fn)

def listhistory():
    historyfile = {}
    with open(curpath, mode="r") as fn:
        historyfile = json.load(fn)
    return historyfile["history"]
