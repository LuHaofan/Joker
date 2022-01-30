from neomodel import (StructuredNode, StringProperty, UniqueIdProperty, DateTimeProperty, Relationship)

class Note(StructuredNode):
	uid = UniqueIdProperty()
	file_name = StringProperty(required=True)
	last_updated = DateTimeProperty()
