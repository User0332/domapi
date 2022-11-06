class WebAPIClassBase:
	"""Interface for all WebAPI Objects."""
	def __init__(self, prototype: dict):
		self.__dict__ = prototype

	def _dict(self):
		return self.__dict__