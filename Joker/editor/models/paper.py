from neomodel import (StructuredNode, StringProperty, UniqueIdProperty, IntegerProperty, RelationshipFrom, RelationshipTo, Relationship)

class Paper(StructuredNode):
	title = StringProperty(required=True)
	short_title = StringProperty(required=True)
	year = IntegerProperty()
	numpages = IntegerProperty()
	author = Relationship('.author.Author', 'WRITTEN_BY')
	tag = RelationshipTo('.tag.Tag', 'IS_ABOUT')
	keyword = RelationshipTo('.keyword.Keyword', 'CONTAINS_KEYWORD')
	note = RelationshipFrom('.note.Note', 'NOTE_FOR')
