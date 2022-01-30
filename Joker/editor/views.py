from django.shortcuts import render
from django.http import HttpResponse
import os
import json
def index(request):
    return render(request, 'editor/index.html', {})


def generateNoteList():
    root = "editor/static/editor/notes/"
    res = {"notes":[]}
    for _, _, files in os.walk(root, topdown=False):
        for name in files:
            title = name[:-3]
            path = os.path.join(root, name)
            res["notes"].append({
                "title": title,
                "path" : path
            })
    with open("editor/static/editor/json/note-list.json", 'w') as f:
        json.dump(res, f)
    

def saveNote(request):
    md = request.POST.get('md')
    fname = request.POST.get('fname')
    root = "editor/static/editor/notes/"
    with open(root+fname, "w") as f:
        f.write(md)
    generateNoteList()
    return HttpResponse()