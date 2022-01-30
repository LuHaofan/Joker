from neomodel import (StructuredNode, StringProperty, UniqueIdProperty, RelationshipFrom, RelationshipTo, Relationship)

class Paper(StructuredNode):
	uid = UniqueIdProperty()
	title = StringProperty(required=True)
	author = Relationship('.author.Author', 'WRITTEN_BY')
	tag = RelationshipTo('.tag.Tag', 'IS_ABOUT')
	note = RelationshipFrom('.note.Note', 'NOTE_FOR')
