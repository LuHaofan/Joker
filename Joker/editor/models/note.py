from neomodel import (StructuredNode, StringProperty, UniqueIdProperty, DateTimeProperty, Relationship)

class Note(StructuredNode):
	file_name = StringProperty(required=True)
	last_updated = DateTimeProperty()
