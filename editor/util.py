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

    if "url" in d:
        paper.url = d["url"]

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
    tags = ["'" + tag.name + "'" for tag in paper.tag]
    keywords = ["'" + keyword.name + "'" for keyword in paper.keyword]
    authors = ["'" + author.name + "'" for author in paper.author]
    query = "MATCH (n WHERE (n:Tag AND n.name IN [" + ",".join(tags) + "]) OR (n:Keyword AND n.name IN [" + ",".join(keywords) + "]) OR (n:Author AND n.name IN [" + ",".join(authors) + "]))<-[:IS_ABOUT|CONTAINS_KEYWORD|WRITTEN_BY]-(paper) return paper.title, paper.url"
    print(query)
    papers = db.cypher_query(query)[0]
    papers = list(filter(lambda paper: paper[0] != title, papers))

    for paper, url in papers:
        query = "MATCH (n:Paper {title: '" + paper + "'})-[:WRITTEN_BY]->(author) return author.name"
        authors = db.cypher_query(query)[0]
        recs[paper] = [authors, url]
    return recs


def getFilterOptions():
	papers = db.cypher_query("MATCH (n:Paper) RETURN n.title")[0]
	authors = db.cypher_query("MATCH (n:Author) RETURN n.name")[0]
	tags = db.cypher_query("MATCH (n:Tag) RETURN n.name")[0]
	keywords = db.cypher_query("MATCH (n:Keyword) RETURN n.name")[0]

	papers = [paperList[0] for paperList in papers]
	authors = [authorList[0] for authorList in authors]
	tags = [tagsList[0] for tagsList in tags]
	keywords = [keywordsList[0] for keywordsList in keywords]

	options = {
		"papers": papers,
		"authors": authors,
		"tags": tags,
		"keywords": keywords
	}

	return options

