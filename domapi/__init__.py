"""
domapi - Support for the DOM in Python based off of MDN web docs - https://developer.mozilla.org/en-US/docs/Web/API

NOTE: This module does NOT support XML namespaces and will only fully support HTML features. Because of this, methods like `NamedNodeMap.getNamedItemNS()` are not defined.
"""

from .webapi_classes import Document, xml

def make_document_from_str(xmlstr: str) -> Document:
	return Document(
		xml.fromstring(
			xmlstr
		)
	)