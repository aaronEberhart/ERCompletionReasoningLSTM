from Term import *

class Predicate(ABC):
	
	@abstractmethod
	def __init__(self,ID,args):
		if not self.validParams(ID,args):
			raise Exception("Invalid Predicate")
		self.name = ID
		self.terms = Terms(args)
	
	def display(self):
		print("{}({})".format(self.name,self.terms.toString()))
		
	def validParams(self,ID,args):
		if isinstance(ID,(list,)):
			return False
		return True

class Concept(Predicate):
	
	def __init__(self,ID,args):
		super().__init__(ID,args)
		if self.terms.len() != 1:
			raise Exception("Invalid Concept")

class Role(Predicate):

	def __init__(self,ID,args):
		super().__init__(ID,args)
		if self.terms.len() != 2:
			raise Exception("Invalid Role")
