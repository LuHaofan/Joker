from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
import os
import json
from django.urls import reverse
from numpy import inner
from .models import Note, Paper, Tag, Author
from . import util

class NameTranslator():
    def __init__(self):
        self.ntdbPath = "editor/static/editor/json/ntdb.json"
        f = open(self.ntdbPath, "r")
        self.json = json.load(f)
        f.close()
    
    def i2d(self, innerName):
        '''
        Translate innerName to displayName
        '''
        db = self.json["i2d"]
        return db[innerName]

    def d2i(self, displayName):
        '''
        Translate displayName to innerName
        '''
        db = self.json["d2i"]
        return db[displayName]

    def addEntry(self, innerName, displayName):
        '''
        Add new entry to the name translation database
        '''
        self.json["i2d"][innerName] = displayName
        self.json["d2i"][displayName] = innerName
        with open(self.ntdbPath, 'w') as f:
            json.dump(self.json, f)

    def updateEntry(self, innerName, displayName):
        '''
        update entry in the name translation database
        '''
        if innerName in self.json["i2d"].keys():
            old_displayName = self.json["i2d"][innerName]
            self.json["i2d"][innerName] = displayName
            self.json["d2i"][old_displayName] = innerName
            with open(self.ntdbPath, 'w') as f:
                json.dump(self.json, f)
        else:
            print("Note file does not exist")

    def deleteEntry(self, displayName):
        if displayName in self.json["d2i"].keys():
            innerName = self.json["d2i"][displayName]
            del self.json["d2i"][displayName]
            del self.json["i2d"][innerName]
        with open(self.ntdbPath, 'w') as f:
            json.dump(self.json, f)

    def clear(self):
        self.json["i2d"] = {}
        self.json["d2i"] = {}
        with open(self.ntdbPath, 'w') as f:
            json.dump(self.json, f)


nt = NameTranslator()

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

    parseBibFile(fname)
    generateNote(fname)
    return HttpResponseRedirect(reverse('editor:index'))

def parseLine(line):
    return line[line.find("{")+1:line.rfind("}")]

def parseBibtex(tex):
    d = {}
    for i in range(len(tex)):
        line = tex[i].strip().lstrip("\t")
        if line.startswith("author"):
            author_list = line[line.find("{")+1:line.rfind("}")].split('and')
            author_list_item = []
            for author in author_list:
                if author.find(",") >= 0:
                    comma = author.find(",")
                    first = author[comma+2:].strip()
                    last = author[:comma].strip()
                    author_list_item.append({"first":first, "last": last})
            # print(author_list_item)
            d["authors"] = author_list_item
        elif line.startswith("title"):
            title = parseLine(line)
            d["title"] = title
        elif line.startswith("year"):
            d["year"] = parseLine(line)
        elif line.startswith("url"):
            d["url"] = parseLine(line)
        elif line.startswith("keywords"):
            keywords_list = parseLine(line).split(", ")
            d["keywords"] = keywords_list
        elif line.startswith("isbn"):
            isbn = parseLine(line)
            d["isbn"] = isbn
        elif line.startswith("publisher"):
            d["publisher"] = parseLine(line)
        elif line.startswith("series"):
            d["series"] = parseLine(line)
        elif line.startswith("address"):
            d["address"] = parseLine(line)
        elif line.startswith("doi"):
            d["doi"] = parseLine(line)
        elif line.startswith("booktitle"):
            d["booktitle"] = parseLine(line)
        elif line.startswith("numpages"):
            d["numpages"] = parseLine(line)
        elif line.startswith("location"):
            d["location"] = parseLine(line)
        elif line.startswith("abstract"):
            d["abstract"] = parseLine(line)

    return d, title

def parseBibFile(fname):
    bibDir = "./editor/static/editor/bib/"
    jsonDir = "./editor/static/editor/json/"
    inputPath = bibDir+fname+".bib"
    outputPath = jsonDir+fname+".json"
    with open(inputPath, 'r', encoding='utf-8') as f:
        raw = f.readlines()
        d, title = parseBibtex(raw)
        nt.addEntry(fname, title)   #by default the innerName and displayName should be the same
    with open(outputPath, 'w') as f:
        json.dump(d, f)

def formatAuthorList(al):
    res = ""
    for name in al:
        res += name["first"] + " " + name["last"] + ", "
    return res[:-2]

def generateNote(fname):
    noteDir = "./editor/static/editor/notes/"
    notePath = noteDir+fname+".md"
    jsonDir = "./editor/static/editor/json/"
    jsonPath = jsonDir+fname+".json"
    # Opening JSON file
    with open(jsonPath, "r") as f:
        data = json.load(f)
        util.updateGraph(data)

    displayList = ["title", "year", "url", "series"]
    with open(notePath, "w") as f:
        lines = []
        for k in data.keys():
            if k == "authors":
                lines.append("> "+k.capitalize()+": "+ formatAuthorList(data[k]) + "\n")
            elif k == "keywords":
                lines.append("> "+k.capitalize()+": "+ ", ".join(data[k])+ "\n")
            elif k in displayList:
                lines.append("> "+k.capitalize()+": "+ data[k]+ "\n")
            else:
                continue
        lines.append("> Tags: *Define your own tags here, separate by comma*")
        f.writelines(lines)

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

def parseBibGroupFile(group_name):
    groupDir = "./editor/static/editor/dataset/"
    groupPath = groupDir+group_name+".bib"
    jsonDir = "./editor/static/editor/json/"

    with open(groupPath, "r") as f:
        raw = f.read()
        bib_list = raw.split("\n\n")
        for bib in bib_list:
            bib_lines = bib.split("\n")
            firstline = bib_lines[0]
            fname = firstline[firstline.find("/")+1:firstline.find(",")]
            try:
                d, title = parseBibtex(bib_lines)
                print(fname)
                print(d)
                print(title)
                print("\n")
                nt.addEntry(fname, title)   #by default the innerName and displayName should be the same

                with open(jsonDir+fname+".json", 'w') as f:
                    json.dump(d, f)
                generateNote(fname)
            except:
                print("done")
                
def getRecs(request):
    title = request.GET.get('title')
    recs = util.recommend(title[:-1])
    return HttpResponse(json.dumps(recs))
    # return recs

if __name__ == "__main__":
    parseBibGroupFile("sigcomm")