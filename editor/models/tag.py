from neomodel import (StructuredNode, StringProperty)

class Tag(StructuredNode):
	name = StringProperty(required=True)
