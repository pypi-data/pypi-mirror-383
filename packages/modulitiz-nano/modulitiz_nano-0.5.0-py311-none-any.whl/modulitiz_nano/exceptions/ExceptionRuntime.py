class ExceptionRuntime(RuntimeError):
	
	def __init__(self,*args):
		super().__init__(*args)
	
	def getMessage(self)->str:
		return " ".join(self.args)
