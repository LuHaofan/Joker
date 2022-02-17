import json
from neomodel import config, db
from editor.models import Note
from editor.models import Paper
from editor.models import Tag
from editor.models import Author


# config.DATABASE_URL = 'bolt://neo4j:12345@localhost:7687'
config.DATABASE_URL = 'neo4j+s://neo4j:9cRp7C_4p8ty1f_5XYlXorAtqM3OlksojlNGA9k7RlU@44305d6f.databases.neo4j.io:7687'


# clear existing nodes
query = 'MATCH (n) DETACH DELETE n'
db.cypher_query(query)


f = open('test_data.json')
data = json.load(f)

for d in data:
	paper = Paper(title=d["title"], short_title=d["short_title"]).save()
	
	for author_name in d["authors"]:
		author = Author.nodes.get_or_none(name=author_name)
		if author is None:
			author = Author(name=author_name)
			author.save()
		paper.author.connect(author)

	for tag_name in d["tags"]:
		tag = Tag.nodes.get_or_none(name=tag_name)
		if tag is None:
			tag = Tag(name=tag_name)
			tag.save()
		paper.tag.connect(tag)

	note = Note(file_name=d["note"]["file_name"]).save()
	paper.note.connect(note)

f.close()