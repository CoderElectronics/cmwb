import json, os

curpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../config/bookmarks.json")

def addbookmark(title, page):
    bookmarksfile = {}
    with open(curpath, mode="r") as fn:
        bookmarksfile = json.load(fn)
    bookmarksfile["bookmarks"][title] = page
    with open(curpath, mode="w") as fn:
        json.dump(bookmarksfile, fn)

def readbookmark(title):
    bookmarksfile = {}
    with open(curpath, mode="r") as fn:
        bookmarksfile = json.load(fn)
    return bookmarksfile["bookmarks"][title]


def deletebookmark(title):
    bookmarksfile = {}
    with open(curpath, mode="r") as fn:
        bookmarksfile = json.load(fn)
    del bookmarksfile["bookmarks"][title]
    with open(curpath, mode="w") as fn:
        json.dump(bookmarksfile, fn)

def listbookmarks():
    bookmarksfile = {}
    bookmarksarray = []
    with open(curpath, mode="r") as fn:
        bookmarksfile = json.load(fn)
    for item in bookmarksfile["bookmarks"]:
        bookmarksarray.append(item)
    return bookmarksarray
