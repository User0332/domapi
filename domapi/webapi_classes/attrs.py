import json
from . import WebAPIClassBase

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
	def __init__(self, map: dict[str, Attr], owner):
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
