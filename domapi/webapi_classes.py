"""
Web API Classes based off of MDN web docs - https://developer.mozilla.org/en-US/docs/Web/API

NOTE: Not all classes, such as Node, are implemented.
"""

import json
from types import MethodType
from js2py import eval_js as _js_eval
from js2py.base import JsObjectWrapper as _JSObject
from htmlmin import minify as _minify
from html import unescape as _unescape
import xml.etree.ElementTree as xml # see docs, doesn't protect against malicious data

class WebAPIClassBase:
	def _dict(self): return {}

class Element(WebAPIClassBase):
	def __init__(self, root: xml.Element):
		self._root = root
		self.children: list[Element]
	
	@property
	def attributes(self):
		return NamedNodeMap(
			{
				name: Attr(name, self) for name in self._root.attrib
			}
		)

	@property
	def firstElementChild(self):
		return self.children[0] if self.children else None

	@property
	def lastElementChild(self):
		return self.children[-1] if self.children else None

	@property
	def className(self):
		return self._root.attrib.get("class", "")

	@className.setter
	def className(self, new_name: str):
		self._root.attrib["class"] = new_name

	@property
	def classList(self):
		return self.className.split()

	@property
	def children(self):
		return [Element(child) for child in self._root]

	@property
	def childElementCount(self):
		return len(self.children)

	@property
	def innerText(self):
		return self._root.text

	@innerText.setter
	def innerText(self, value: str):
		self._root.text = value

	def getAttribute(self, name: str) -> str:
		return self._root.get(name, None)

	def getAttributeNode(self, name: str) -> str:
		pass

	def getElementsByTagName(self, tagname: str):
		elems: list[Element] = [
			Element(elem) for elem in self._root.findall(tagname)
		]

		for child in self.children:
			elems+=child.getElementsByTagName(tagname)

		return elems

	def getElementsByClassName(self, classname: str):
		elems: list[Element] = []

		for child in self.children:
			if classname.split() in child.classList:
				elems.append(child)

		return elems

	def _getElementById_Helper(self, id: str):
		for child in self.children:
			if child._root.attrib.get("id", None) == id: return child

	def append(self, *items):
		for item in items:
			if isinstance(item, Element):
				self._root.append(item._root)
				continue

			self._root.append(
				xml.fromstring(item)
			)

	def _stringify(self, unescape=False) -> str:
		s = xml.tostring(self._root, "unicode")
		if unescape: s = _unescape(s)

		return s

	def _minify(self, unescape=False, **kwargs) -> str:
		"""This function is like Element._stringify() except that it uses htmlmin.minify() under the hood. Kwargs can be supplied to htmlmin.minifiy().
		
		NOTE: This function ONLY minifies HTML. JavaScript and CSS will NOT be minified"""
		return _minify(
			self._stringify(
				unescape
			),
			**kwargs
		)

	def __repr__(self) -> str:
		return f"Element {self._root.tag!r}"

	def _dict(self) -> dict:
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
				key: [json.loads(str(item)) for item in getattr(self, key)]
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
	"""Geez - this object takes a whole lot of time to fully implement!"""

	def __init__(self, root: xml.Element):
		self._root = root
		self.body = Element(root.find("body"))
		self.head = Element(root.find("head"))

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
		for child in self.children[0].children:
			if child._root.attrib.get("id", None) == id: return child

			res = child._getElementById_Helper(id)
			if res is not None: return res

	def createElement(self, tagname, options: dict={}) -> Element:
		html = f"<{tagname}></{tagname}>" if "is" not in options else f'<{tagname} is="{options["is"]}"></{tagname}>'

		return Element(
			xml.fromstring(
				html
			)
		)

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
	def __init__(self, name: str, owner: Element):
		self._name = name
		self._owner = owner

	@property
	def localName(self): return self._name

	@property
	def name(self): return self._name

	@property
	def ownerElement(self): return self._owner

	@property
	def prefix(self): pass

	@property
	def namespaceURI(self): pass

	@property
	def value(self) -> str:
		return self._owner._root.get(
			self._name,
			None
		)

	@value.setter
	def value(self, val: str):
		self._owner._root.set(
			self._name,
			val
		)

	def _dict(self): return { "name": self.name, "value": self.value }
	
	def __repr__(self):
		return json.dumps(
			self._dict()
		)

class NamedNodeMap(WebAPIClassBase):
	def __init__(self, map: dict[str, Attr]):
		self._map = map

	@property
	def length(self): return len(self._map)

	def getNamedItem(self, name: str):
		return self._map.get(
			name,
			None
		)

	def setNamedItem(self, attr: Attr):
		self._map[attr.name] = attr

	def removeNamedItem(self, name: str):
		return self._map.pop(name, None)

	def item(self, idx: int):
		return tuple(self._map.values())[idx]

	def _dict(self): return self._map

	def __repr__(self):
		return json.dumps(
			self._dict()
		)
		
