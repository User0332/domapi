"""
Web API Classes based off of MDN web docs - https://developer.mozilla.org/en-US/docs/Web/API

NOTE: Not all classes, such as `Node`, are implemented.
"""

import json
from types import MethodType
from js2py import eval_js as _js_eval
from js2py.base import JsObjectWrapper as _JSObject
from htmlmin import minify as _minify
import lxml.etree as xml # see docs, doesn't protect against malicious data (last reg xml lib)

class WebAPIClassBase:
	"""Interface for all WebAPI Objects."""
	def __init__(self, prototype: dict):
		self.__dict__ = prototype

	def _dict(self):
		return self.__dict__

class Element(WebAPIClassBase):
	"""A singular HTML element."""
	def __init__(self, root: xml._Element):
		self._root = root
		self._attrib = NamedNodeMap({}, self)
		
		for attr in ( Attr(name) for name in self._root.attrib ):
			attr.value = self._root.attrib[attr.name]

			self._attrib.setNamedItem(attr)	
	
	@property
	def attributes(self):
		"""Return a `NamedNodeMap` of this element's attributes."""
		return self._attrib

	@property
	def firstElementChild(self):
		"""Synonym for `element.children[0]`."""
		return self.children[0] if self.children else None

	@property
	def lastElementChild(self):
		"""Synonym for `element.children[-1]`."""
		return self.children[-1] if self.children else None

	@property
	def className(self) -> str:
		"""Return the `class` attribute of this element as a string."""
		return self._root.attrib.get("class", "")

	@className.setter
	def className(self, new_name: str):
		self._root.attrib["class"] = new_name

	@property
	def classList(self):
		"""Return a list of this element's classes."""
		return self.className.split()

	@property
	def children(self):
		"""Return a list of all the child elements of the current element."""
		return [Element(child) for child in self._root]

	@property
	def childElementCount(self):
		"""Synonym for `len(element.children)`."""
		return len(self.children)

	@property
	def innerText(self):
		"""Get the text from an element."""
		return self._root.text

	@innerText.setter
	def innerText(self, value: str):
		self._root.text = value

	def getAttribute(self, name: str) -> str:
		"""Get the value of an attribute."""
		return self._root.get(name, None)

	def getAttributeNode(self, name: str):
		"""Get the `Attr` instance of an attribute."""
		return self.attributes.getNamedItem(name)

	def getElementsByTagName(self, tagname: str):
		"""Return a list of subelements that have the tag name `tagname`."""
		elems: list[Element] = [
			Element(elem) for elem in self._root.findall(tagname)
		]

		for child in self.children:
			elems+=child.getElementsByTagName(tagname)

		return elems

	def getElementsByClassName(self, classname: str):
		"""Return a list of subelements that have `classname` in their `class` attribute."""
		elems: list[Element] = []

		for child in self.children:
			if classname.split() in child.classList:
				elems.append(child)

		return elems

	def _getElementById_Helper(self, id: str):
		for child in self.children:
			if child._root.attrib.get("id", None) == id: return child

	def append(self, *items):
		"""Add elements to this element's children."""
		for item in items:
			if isinstance(item, Element):
				self._root.append(item._root)
				continue

			self._root.append(
				xml.fromstring(item)
			)

	def _stringify(self) -> str:
		return xml.tostring(self._root, method="html").decode()

	def _minify(self, **kwargs) -> str:
		"""This function is like Element._stringify() except that it uses htmlmin.minify() under the hood. Kwargs can be supplied to htmlmin.minifiy().
		
		NOTE: This function ONLY minifies HTML. JavaScript and CSS will NOT be minified"""
		return _minify(
			self._stringify(),
			**kwargs
		)

	def __repr__(self) -> str:
		return f"Element {self._root.tag!r}"

	def _dict(self) -> dict:
		"""Return a dictionary with all element properties and sub properties."""
		return {
			**{
				key: json.loads(str(value)) 
				for key, value in self.__dict__.items() 
				if (not key.startswith('_')) and (type(value) is not _JSObject)
			},
			**{
				key : json.loads(
					str(getattr(self, key))
				)
				for key in self.__class__.__dict__ 
				if (not key.startswith('_')) and (isinstance(getattr(self, key), (dict, WebAPIClassBase)))
			},
			**{
				key: getattr(self, key)
				for key in self.__class__.__dict__
				if (not key.startswith('_') and (isinstance(getattr(self, key), (str, int, float))))
			},
			**{
				key: [
					item for item in getattr(self, key) 
					if not isinstance(item, WebAPIClassBase)
				] + [
					item._dict() for item in getattr(self, key)
					if isinstance(item, WebAPIClassBase)
				]
				for key in self.__class__.__dict__
				if (not key.startswith('_') and (isinstance(getattr(self, key), list)))
			},
			**{
				key: f"Built-in Python Function {key}"
				for key in self.__class__.__dict__
				if (not key.startswith('_') and type(getattr(self, key)) is MethodType)
			},
			**{
				key: eval(str(value))
				for key, value in self.__dict__.items()
				if type(value) is _JSObject
			}
		}

	def __str__(self) -> str:
		return json.dumps(
			self._dict(),
			indent="\t"
		)

class Document(Element):
	"""Document object that supports most DOM manipulation functions and properties. Deprecated, less documented, and minimally used features such as `document.implementation` are not implemented. Features that a browser would support, like event listeners, are also not implemented."""
	def __init__(self, root: xml._Element):
		self._root = root

	@property
	def body(self):
		"""Return the `<body>` element of the document."""
		return Element(self._root.find("body"))

	@property
	def head(self):
		"""Return the `<head>` element of the document."""
		return Element(self._root.find("head"))

	@property
	def forms(self):
		"""Return a list of all the `<form>` elements in the document."""
		return self.getElementsByTagName("form")

	@property
	def embeds(self):
		"""Return a list of all the `<embed>` elements in the document."""
		return self.getElementsByTagName("embeds")

	@property
	def links(self):
		"""Return a list of all the `<a>` and `<area>` elements in the document."""
		return self.getElementsByTagName("a")+self.getElementsByTagName("area")

	@property
	def scripts(self):
		"""Return a list of all the `<script>` elements in the document."""
		return self.getElementsByTagName("script")

	@property
	def images(self):
		"""Return a list of all the `<img>` elements in the document."""
		return self.getElementsByTagName("img")

	@property
	def plugins(self):
		"""Synonym for `document.embeds`."""
		return self.embeds

	@property
	def doctype(self) -> str:
		"""This method does not implement DocumentType as the documentation for it is unclear. It returns the doctype declaration as a string."""
		return self._root.getroottree().docinfo.doctype

	@property
	def metadata(self) -> dict:
		"""Non-standard property that returns a dict of the attributes in the `<meta>` element."""
		return Element(self._root.get("meta", xml.Element("meta"))).attributes._map

	@property
	def characterSet(self) -> str: # make setter for this charset
		"""Get the charset of the document."""
		return self.metadata.get("charset", self._root.getroottree().docinfo.encoding)

	@property
	def children(self):
		"""Why do I need a list when there is only one child???"""
		return [
			Element(self._root)
		]

	@property
	def childElementCount(self):
		"""Like I don't know that there is only one child..."""
		return 1
	
	@property
	def documentElement(self):
		"""This stuff is getting kinda useless..."""
		return self.firstElementChild

	@property
	def firstElementChild(self):
		"""Ok - I actually don't need 50 properties that all give me the same thing."""
		return self.children[0]

	@property
	def lastElementChild(self):
		"""Now this is actually stupid - who thought of this?"""
		return self.children[0]
		
	def getElementById(self, id: str) -> Element:
		"""Pass in an ID to retrieve an element."""
		for child in self.children[0].children:
			if child._root.attrib.get("id", None) == id: return child

			res = child._getElementById_Helper(id)
			if res is not None: return res

	def createElement(self, tagname, options: dict={ "is": str }) -> Element:
		"""Return a new `Element` with `tagname` and `options`."""
		html = f"<{tagname}></{tagname}>" if options.get("is", str) is str else f'<{tagname} is="{options["is"]}"></{tagname}>'

		return Element(
			xml.fromstring(
				html
			)
		)

	def createAttribute(self, name: str):
		"""Return a `Attr` with the name `name`."""

		return Attr(name)

	def open(self):
		"""Not really sure what this is for so this just clears the document."""
		self._root = xml.fromstring("")

	def write(self, string: str):
		"""Pretty dumb method if you ask me - it just overwrites the entire document."""
		self.open()
		self._root = xml.fromstring(string)

	def _exec_js_dom_func(self, func: str, *args):
		"""Pass in a string containing an ES5 anonymous function that accepts a document object and *args"""
	
		func = _js_eval(func)

		return func(
			self,
			*args
		)

	def __repr__(self):
		return "Document"

class Attr(WebAPIClassBase):
	def __init__(self, name: str):
		self._name = name
		self._owner = None
		self._value = ""

	@property
	def localName(self): return self._name

	@property
	def name(self): return self._name

	@property
	def ownerElement(self): return self._owner

	@property
	def value(self) -> str:
		return self._value

	@value.setter
	def value(self, val: str):
		self._value = val

	def _dict(self): return { "name": self.name, "value": self.value }
	
	def __repr__(self):
		return json.dumps(
			self._dict()
		)

class NamedNodeMap(WebAPIClassBase):
	def __init__(self, map: dict[str, Attr], owner: Element):
		self._owner = owner
		self._map = map

	@property
	def length(self):
		"""Return the length of the map (the number of attributes)."""
		return len(self._map)

	def getNamedItem(self, name: str):
		"""Return the `Attr` object with the name `name`."""
		return self._map.get(
			name,
			None
		)

	def setNamedItem(self, attr: Attr):
		"""Set the attribute `attr` on this map."""
		self._map[attr.name] = attr
		attr._owner = self._owner
		self._owner._root.attrib[attr.name] = attr.value

	def removeNamedItem(self, name: str):
		"""Pop the attribute with the name `name`."""
		if name in self._map:
			self._map[name].ownerElement._root.attrib.pop(name)

		return self._map.pop(name, None)

	def item(self, idx: int):
		"""Get the attribute at index `idx`."""
		return tuple(self._map.values())[idx] if idx <= self.length else None

	def _dict(self): return { key: value._dict() for key, value in self._map.items() }

	def __repr__(self):
		return json.dumps(
			self._dict()
		)