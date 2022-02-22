from neomodel import db

from editor.models import Note
from editor.models import Paper
from editor.models import Tag
from editor.models import Keyword
from editor.models import Author

def updateGraph(d):
    if "title" not in d:
        raise RuntimeError("Paper missing required title")

    paper = Paper.nodes.get_or_none(title=d["title"])
    if paper is None:
        paper = Paper(title=d["title"], short_title=d["title"][:20])
    
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


def recommend(title):
    paper = Paper.nodes.get_or_none(title=title)
    if paper is None:
	    raise RuntimeError("Paper doesn't exist in DB")

    recs = {}
    for keyword in paper.keyword:
        query = "MATCH (n:Keyword {name: '" + keyword.name + "'})<-[:CONTAINS_KEYWORD]-(paper) return paper.title"
        papers = db.cypher_query(query)[0]
        papers = [p for sublist in papers for p in sublist]
        papers = list(filter(lambda paper_title: paper_title != title, papers))
        if len(papers) > 0:
            recs[keyword.name] = papers
    return recs