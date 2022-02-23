import json
from . import util
from . import KeywordExtractor, NameTranslator

class BibParser():
    def __init__(self, fname = ""):
        self.nt = NameTranslator.NameTranslator()
        self.ke = KeywordExtractor.KeywordExtractor()
        self.fname = fname

    def parseBibFile(self):
        bibDir = "./editor/static/editor/bib/"
        jsonDir = "./editor/static/editor/json/"
        inputPath = bibDir+self.fname+".bib"
        outputPath = jsonDir+self.fname+".json"
        with open(inputPath, 'r', encoding='utf-8') as f:
            raw = f.readlines()
            d, title = self.parseBibtex(raw)
        with open(outputPath, 'w') as f:
            json.dump(d, f)
        return title

    def parseLine(self, line):
        return line[line.find("{")+1:line.rfind("}")]

    def parseBibtex(self, tex):
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
                title = self.parseLine(line)
                d["title"] = title
            elif line.startswith("year"):
                d["year"] = self.parseLine(line)
            elif line.startswith("url"):
                d["url"] = self.parseLine(line)
            elif line.startswith("keywords"):
                keywords_list = self.parseLine(line).split(", ")
                d["keywords"] = keywords_list
            elif line.startswith("isbn"):
                isbn = self.parseLine(line)
                d["isbn"] = isbn
            elif line.startswith("publisher"):
                d["publisher"] = self.parseLine(line)
            elif line.startswith("series"):
                d["series"] = self.parseLine(line)
            elif line.startswith("address"):
                d["address"] = self.parseLine(line)
            elif line.startswith("doi"):
                d["doi"] = self.parseLine(line)
            elif line.startswith("booktitle"):
                d["booktitle"] = self.parseLine(line)
            elif line.startswith("numpages"):
                d["numpages"] = self.parseLine(line)
            elif line.startswith("location"):
                d["location"] = self.parseLine(line)
            elif line.startswith("abstract"):
                d["abstract"] = self.parseLine(line)
                self.ke.setText(d["abstract"])
                d["tags"] = self.ke.getKeywords()

        return d, title

    def formatAuthorList(self, al):
        res = ""
        for name in al:
            res += name["first"] + " " + name["last"] + ", "
        return res[:-2]

    def parseBibGroupFile(self, group_name):
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
                    d, title = self.parseBibtex(bib_lines)
                    print(fname)
                    print(d)
                    print(title)
                    print("\n")
                    self.nt.addEntry(fname, title)   #by default the innerName and displayName should be the same

                    with open(jsonDir+fname+".json", 'w') as f:
                        json.dump(d, f)
                    self.generateNote(fname)
                except:
                    print("done")

    def generateNote(self):
        noteDir = "./editor/static/editor/notes/"
        notePath = noteDir+self.fname+".md"
        jsonDir = "./editor/static/editor/json/"
        jsonPath = jsonDir+self.fname+".json"
        # Opening JSON file
        with open(jsonPath, "r") as f:
            data = json.load(f)
            # util.updateGraph(data)
        displayList = ["title", "year", "url", "series"]
        with open(notePath, "w") as f:
            lines = []
            for k in data.keys():
                if k == "authors":
                    lines.append("> "+k.capitalize()+": "+ self.formatAuthorList(data[k]) + "\n")
                elif k == "keywords":
                    lines.append("> "+k.capitalize()+": "+ ", ".join(data[k])+ "\n")
                elif k in displayList:
                    lines.append("> "+k.capitalize()+": "+ data[k]+ "\n")
                else:
                    continue
            lines.append("> Tags: *Define your own tags here, separate by comma*")
            f.writelines(lines)
