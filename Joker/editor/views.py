from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
import os
import json
from django.urls import reverse
from numpy import inner

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
            self.json["i2d"][innerName] = displayName
            self.json["d2i"][displayName] = innerName
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
        if l.startswith("> Tags"):
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
    nt.addEntry(fname, fname)   #by default the innerName and displayName should be the same
    fpath = bibDir+fname+'.bib'
    with open(fpath, 'w', encoding = 'utf-8') as f:
        f.write(bibtex)

    parseBibFile(fname)
    generateNote(fname)
    return HttpResponseRedirect(reverse('editor:index'))

def parseLine(line):
    return line[line.find("{")+1:line.rfind("}")]

def parseBibFile(fname):
    bibDir = "editor/static/editor/bib/"
    jsonDir = "editor/static/editor/json/"
    inputPath = bibDir+fname+".bib"
    outputPath = jsonDir+fname+".json"
    d = {}
    with open(inputPath, 'r', encoding='utf-8') as f:
        raw = f.readlines()
        for i in range(len(raw)):
            line = raw[i].strip().lstrip("\t")
            if line.startswith("author"):
                author_list = line[line.find("{")+1:line.rfind("}")].split('and')
                author_list_item = []
                for author in author_list:
                    if author.find(",") >= 0:
                        comma = author.find(",")
                        first = author[comma+2:].strip()
                        last = author[:comma].strip()
                        author_list_item.append({"first":first, "last": last})
                    # else:
                    #     author_list_item.append(author.strip())
                print(author_list_item)
                d["authors"] = author_list_item
            elif line.startswith("title"):
                d["title"] = parseLine(line)
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
    jsonDir = "editor/static/editor/json/"
    jsonPath = jsonDir+fname+".json"
    # Opening JSON file
    f = open(jsonPath)
    data = json.load(f)
    f.close()
    displayList = ["title", "authors", "year", "url", "keywords", "series"]
    with open(notePath, "w") as f:
        lines = []
        for k in displayList:
            if k == "authors":
                lines.append("> "+k.capitalize()+": "+ formatAuthorList(data[k]) + "\n")
            elif k == "keywords":
                lines.append("> "+k.capitalize()+": "+ ", ".join(data[k])+ "\n")
            else:
                lines.append("> "+k.capitalize()+": "+ data[k]+ "\n")
        lines.append("> Tags: *Define your own tags here, separate by comma*")
        f.writelines(lines)

