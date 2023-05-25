"""
domapi - Support for the DOM in Python based off of MDN web docs - https://developer.mozilla.org/en-US/docs/Web/API

NOTE: This module does NOT support XML namespaces and will only fully support HTML features. Because of this, methods like `NamedNodeMap.getNamedItemNS()` are not defined.
"""

from .webapi_classes.elements import Document, Element, html

def make_document_from_str(htmlstr: str, cls: type=Document) -> Document:
	return cls(
		html.document_fromstring(
			htmlstr
		)
	)

def make_element_from_str(htmlstr: str) -> Element:
	return Element(
		html.fragment_fromstring(htmlstr)	
	)