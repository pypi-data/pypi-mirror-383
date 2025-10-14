from abc import ABC

from modulitiz_nano.ModuloFunzioni import ModuloFunzioni
from modulitiz_nano.exceptions.ExceptionRuntime import ExceptionRuntime


class AbstractOverrideTestUtil(ABC):
	"""
	Solo le funzioni statiche devono essere revertate
	"""
	
	def __init__(self):
		super().__init__()
		self._cache={}
	
	def __enter__(self):
		self._cache.clear()
		return self
	
	def __exit__(self,*_args,**_kwargs):
		self._cache.clear()
	
	@staticmethod
	def getMockedFunction(throwExc:Exception|None,expectedValue):
		"""
		Must use only 1 param.
		"""
		if throwExc is not None:
			return ModuloFunzioni.getFunctionThatRaises(throwExc)
		elif expectedValue is not None:
			return lambda *_args,**_kwargs:expectedValue
		raise ExceptionRuntime("Use only 1 param")
