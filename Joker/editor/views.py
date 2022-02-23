from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
import os
import json
from django.urls import reverse
from numpy import inner
from .models import Note, Paper, Tag, Author
from . import util
from . import KeywordExtractor, NameTranslator, BibParser
import requests

ke = KeywordExtractor.KeywordExtractor()
nt = NameTranslator.NameTranslator()

def index(request):
    generateNoteList()
    return render(request, 'editor/index.html', {})

def graph(request):
    return render(request, 'editor/graph.html', {})

def home(request):
    return render(request, 'editor/home.html', {})

def generateNoteList():
    note_dir_root = "./editor/static/editor/notes/"
    res = {"notes":[]}
    note_root = "../static/editor/notes/"
    for _, _, files in os.walk(note_dir_root, topdown=False):
        for name in files:
            if name == "empty.md":
                continue
            title = name[:-3]
            path = os.path.join(note_root,name)
            jsonPath = "editor/static/editor/json/"+title+".json"
            f = open(jsonPath)
            res["notes"].append({
                "title": nt.i2d(title),
                "path" : path,
                "papers": [json.load(f)]
            })
            f.close()
    with open("editor/static/editor/json/note-list.json", 'w') as f:
        json.dump(res, f)
    
def getNoteHeader(md):
    '''
    from the md text, extract the header, which contains the tags and innerName (the last segment of URL)
    return header as a list of features
    '''
    lines = md.split("\n")
    hdr = []
    for l in lines:
        if not l.startswith(">"):
            break
        else:
            hdr.append(l)
    return hdr

def getTags(hdr):
    tagList = []
    for l in hdr:
        if l.startswith("> Tags") and l.find("*") < 0:
            tagList += l[7:].strip().split(", ")
    return tagList

def setTags():
    pass

def saveNote(request):
    md = request.POST.get('md')
    fname = request.POST.get('fname')
    hdr = getNoteHeader(md)
    for l in hdr:
        if l.startswith("> Url"):
            innerName = l.split("/")[-1]

    # Update JSON file
    tags = getTags(hdr)
    print(tags)
    jsonPath = "editor/static/editor/json/"+innerName+".json"
    with open(jsonPath, 'r') as f:
        obj = json.load(f)
        obj["tags"] = tags
        util.updateGraph(obj)
    with open(jsonPath, "w") as f:
        json.dump(obj, f)

    # Update NameTranslator Database
    nt.updateEntry(innerName, fname)

    # Update note file
    root = "editor/static/editor/notes/"
    with open(root+nt.d2i(fname)+".md", "w") as f:
        f.write(md)

    # Update Note list
    generateNoteList()
    return HttpResponse()

def deleteNote(request):
    fname = request.POST.get('fname')
    innerName = nt.d2i(fname)
    nt.deleteEntry(fname)
    mdDir = "editor/static/editor/notes/"
    jsonDir = "editor/static/editor/json/"
    bibDir = "editor/static/editor/bib/"
    mdPath = mdDir+innerName+".md"
    jsonPath = jsonDir+innerName+".json"
    bibPath = bibDir+innerName+".bib"
    print("deleting note at path:", mdPath, jsonPath)
    if os.path.exists(mdPath):
        os.remove(mdPath)
    if os.path.exists(jsonPath):
        os.remove(jsonPath)
    if os.path.exists(bibPath):
        os.remove(bibPath)
    generateNoteList()
    return HttpResponse()

def bibtex_handler(request):
    bibDir = "editor/static/editor/bib/"
    bibtex = request.POST['bibtex']
    lines = bibtex.split('\n')
    firstline = lines[0]
    fname = firstline[firstline.find("/")+1:firstline.find(",")]
    fpath = bibDir+fname+'.bib'
    with open(fpath, 'w', encoding = 'utf-8') as f:
        f.write(bibtex)

    bibparser = BibParser.BibParser(fname=fname)
    bibparser.parseBibFile()
    bibparser.generateNote()
    # parseBibFile(fname)
    # generateNote(fname)
    return HttpResponseRedirect(reverse('editor:index'))

def querySemanticScholar(request):
    url = request.GET['url']
    print(url)
    response = requests.get(url+"&offset=1&limit=5&fields=title,authors")
    with open("editor/static/editor/json/query.json", 'w') as f:
        json.dump(response.json(), f)
    return HttpResponse()
    
def saveTag(request):
    paper_data = json.loads(request.POST.get('paper_data'))
    tag_name = request.POST.get('tag_name')
    paper = Paper.nodes.get_or_none(title=paper_data["title"])
    if paper is None:
        paper = Paper(title=paper_data["title"], short_title=paper_data["short_title"])
        paper.save()

    tag = Tag.nodes.get_or_none(name=tag_name)
    if tag is None:
        tag = Tag(name=tag_name)
        tag.save()
    paper.tag.connect(tag)
    return HttpResponse()
                
def getRecs(request):
    title = request.GET.get('title')
    recs = util.recommend(title[:-1])
    return HttpResponse(json.dumps(recs))
    # return recs

