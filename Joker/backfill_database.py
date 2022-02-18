import os
import json

from neomodel import config, db
from editor import util

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
            try:
                util.updateGraph(d)
            except RuntimeError:
                continue
