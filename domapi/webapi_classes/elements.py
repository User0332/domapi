"""
Web API Classes based off of MDN web docs - https://developer.mozilla.org/en-US/docs/Web/API

NOTE: Not all classes, such as `Node`, are implemented.
"""

import json
import lxml.html as html
import warnings
from cssselect import GenericTranslator as _SelectorTranslator, SelectorError as MalformedSelector
from types import MethodType
from htmlmin import minify as _minify
from . import WebAPIClassBase
from .attrs import NamedNodeMap, Attr
from .xpath import XPathExpression, XPathResult

class DOMException(Exception): pass
class HierarchyRequestError(DOMException): pass

class Element(WebAPIClassBase):
	"""A singular HTML element."""
	def __init__(self, root: html.HtmlElement):
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
		"""Get the text inside this element."""
		warnings.warn(
			"This property currently yields more or less the same output as Element.textContent - "
			"may lead to code breaks!",
			UserWarning
		)
		return ''.join(self._root.itertext())

	@property
	def textContent(self) -> str:
		"""All the text in this element."""
		return self._root.text_content()

	@textContent.setter
	def textContent(self, text: str):
		self._clear()
		self._root.text = text

	@property
	def innerHTML(self) -> str:
		"""Get the HTML inside of this element"""

		descendants = list(self._root.iterchildren())

		for i, descendant in enumerate(descendants):
			if isinstance(descendant, html.HtmlElement):
				descendants[i] = Element(descendant)._stringify()

		return (self._root.text if self._root.text else "")+''.join(descendants)+(self._root.tail if self._root.tail else "")
				
	@innerHTML.setter
	def innerHTML(self, new_html: str):
		self._clear()

		for element in html.fromstring(new_html).iterchildren():
			self._root.append(element)

	def _clear(self):
		for child in self._root.iterchildren(): self._root.remove(child)

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
	
	def querySelector(self, query: str):
		"""Return the first element in the document that matches all the criteria in `query`."""

		selected = self.querySelectorAll(query)

		return selected[0] if selected else None

	def querySelectorAll(self, query: str):
		"""Return all elements in the document that match all the criteria in `query`."""
		
		try: expr = _SelectorTranslator().css_to_xpath(query)
		except MalformedSelector: return []


		return [Element(elem) for elem in self._root.xpath(expr)]

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
				html.fromstring(item)
			)

	def prepend(self, *items):
		"""Add elements before this element's current children"""
		for item in items:
			if isinstance(item, Element):
				self._root.insert(0, item._root)
				continue

			self._root.insert(
				0,
				html.fromstring(item)
			)

	def _stringify(self) -> str:
		return html.tostring(self._root).decode()

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
				if (not key.startswith('_'))
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
		}

	def __str__(self) -> str:
		return json.dumps(
			self._dict(),
			indent="\t"
		)

class Document(Element):
	"""Document object that supports most DOM manipulation functions and properties. Deprecated, less documented, and minimally used features such as `document.implementation` are not implemented. Features that a browser would support, like event listeners, are also not implemented."""
	def __init__(self, root: html.HtmlElement):
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
		return Element(self._root.get("meta", html.Element("meta"))).attributes._map

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
		return len(self.children)
	
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

	def createExpression(self, query: str) -> XPathExpression:
		"""Return an XPathExpression based of of `query`."""

		return XPathExpression(query)

	def evaluate(self, xpath_expr: XPathExpression, context_node: Element, namespace_resolver: None, result_type: int, result: XPathResult):
		"""Evaluate the XPath expression `xpath_expr`. Note that `namespace_resolver` is actually never called."""
		
		return xpath_expr.evaluate(context_node, result_type, result)


	def createElement(self, tagname, options: dict={ "is": str }) -> Element:
		"""Return a new `Element` with `tagname` and `options`."""
		htmlstr = f"<{tagname}></{tagname}>" if options.get("is", str) is str else f'<{tagname} is="{options["is"]}"></{tagname}>'

		return Element(
			html.fromstring(
				htmlstr
			)
		)

	def createAttribute(self, name: str):
		"""Return a `Attr` with the name `name`."""

		return Attr(name)

	def open(self):
		"""Not really sure what this is for so this just clears the document."""
		self._root = None

	def write(self, string: str):
		"""Pretty dumb method if you ask me - it just overwrites the entire document."""
		self.open()
		self._root = html.fromstring(string)

	def append(self, *items):
		"""LOL - this function always throws an error!"""
		
		if self._root:
			raise HierarchyRequestError("Cannot append another child to the document.")

		raise DOMException("Cannot append nodes to the document. Use document.write instead.")

	def prepend(self, *items):
		"""LOL - this function always throws an error!"""

		if self._root:
			raise HierarchyRequestError("Cannot prepend another child to the document.")

		
		raise DOMException("Cannot prepend nodes to the document. Use document.write instead.")

	def __repr__(self):
		return "Document"


