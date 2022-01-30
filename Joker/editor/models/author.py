from neomodel import (StructuredNode, StringProperty)

class Author(StructuredNode):
	name = StringProperty(required=True)
