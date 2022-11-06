from . import WebAPIClassBase

ANY_TYPE = 0
NUMBER_TYPE = 1
STRING_TYPE = 2
BOOLEAN_TYPE = 3
UNORDERED_NODE_ITERATOR_TYPE = 4
ORDERED_NODE_ITERATOR_TYPE = 5
UNORDERED_SNAPSHOT_ITERATOR_TYPE = 6
ORDERED_SNAPSHOT_ITERATOR_TYPE = 7
ANY_ORDERED_NODE_TYPE = 8
FIRST_ORDERED_NODE_TYPE = 9

class XPathException(Exception, WebAPIClassBase):
	pass

class XPathResult(WebAPIClassBase):
	def __init__(self, result, document,result_type: int):
		self._result = result
		self._elem = document
		self._elem_html: str = document._stringify()
		self._type = result_type

	def _value_get(self, matchtype: int):
		if self.resultType != matchtype:
			XPathException("TYPE_ERR: result is not of the specified type")

		return self._result

	@property
	def booleanValue(self) -> bool:
		"""Return the boolean value of this XPathResult or raise an XPathException if it doesn't exist."""

		return self._value_get(BOOLEAN_TYPE)

	@property
	def numberValue(self) -> int:
		"""Return the number value of this XPathResult or raise an XPathException if it doesn't exist."""

		return self._value_get(NUMBER_TYPE)

	@property
	def singleNodeValue(self):
		return self._value_get(FIRST_ORDERED_NODE_TYPE)

	@property
	def snapshotLength(self) -> int:
		return len(self._value_get(ORDERED_NODE_ITERATOR_TYPE))

	@property
	def stringValue(self) -> str:
		return self._value_get(STRING_TYPE)

	@property
	def invalidIteratorState(self) -> bool:
		"""If the document has been modified since the XPathExpression evaluation, this will be true."""

		return self._elem._stringify() != self._elem_html

	@property
	def resultType(self):
		"""Return the numerical value corresponding to the correct result type."""

		return self._type

	def iterateNext(self):
		"""Use this method to iterate over a collection of nodes."""

		self.snapshotLength # to raise if not an iterator
		try: return next(self._result)
		except StopIteration: return None

	def snapshotItem(self, idx: int):
		"""Return the node at index `idx`."""

		try: return self._result[idx]
		except IndexError: return None

class XPathExpression(WebAPIClassBase):
	def __init__(self, text: str):
		self._str = text

	def evaluate(self, document, result_type: int=ANY_TYPE, result: XPathResult=None) -> XPathResult:
		if not (0<=result_type>=9): raise XPathException(
			"Invalid Result Type!"
		)

		if result: 
			result.__init__(document._root.xpath(self._str), document, result_type)
			return result

		else: return XPathResult(document._root.xpath(self._str), document, result_type)