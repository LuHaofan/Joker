from neomodel import (StructuredNode, StringProperty)

class Keyword(StructuredNode):
    name = StringProperty(required=True)
    