import os
import json

from neomodel import config, db
from editor.models import Note
from editor.models import Paper
from editor.models import Tag
from editor.models import Keyword
from editor.models import Author

config.DATABASE_URL = 'neo4j+s://neo4j:9cRp7C_4p8ty1f_5XYlXorAtqM3OlksojlNGA9k7RlU@44305d6f.databases.neo4j.io:7687'

query = 'MATCH (n) DETACH DELETE n'
db.cypher_query(query)

note_dir_root = "./editor/static/editor/json/"
notes = {}
for _, _, files in os.walk(note_dir_root, topdown=False):
    for name in files:
        if name == "note-list.json" or name == "ntdb.json":
            continue
        title = ".".join(name.split(".")[:-1])
        path = os.path.join(note_dir_root, name)
        
        with open(path) as f:
            d = json.load(f)

            if "title" not in d:
                print("Paper missing required title")
                continue

            paper = Paper.nodes.get_or_none(title=d["title"])
            if paper is None:
                paper = Paper(title=d["title"], short_title=d["title"][:20])
            else:
                print("Paper already exists in database")
                continue
            
            if "year" in d:
                paper.year = d["year"]

            if "numpages" in d:
                paper.numpages = d["numpages"]

            paper.save()

            if "authors" in d:
                for author_data in d["authors"]:
                    author_name = author_data["first"] + " " + author_data["last"]
                    author = Author.nodes.get_or_none(name=author_name)
                    if author is None:
                        author = Author(name=author_name)
                        author.save()
                    paper.author.connect(author)

            if "tags" in d:
                for tag_name in d["tags"]:
                    tag = Tag.nodes.get_or_none(name=tag_name)
                    if tag is None:
                        tag = Tag(name=tag_name)
                        tag.save()
                    paper.tag.connect(tag)

            if "keywords" in d:
                for keyword_name in d["keywords"]:
                    keyword = Keyword.nodes.get_or_none(name=keyword_name)
                    if keyword is None:
                        keyword = Keyword(name=keyword_name)
                        keyword.save()
                    paper.keyword.connect(keyword)

