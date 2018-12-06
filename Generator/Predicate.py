from Term import *
from Quantifier import *

class Predicate(ABC):
	
	@abstractmethod
	def __init__(self,ID,args):
		if not self.validParams(ID,args): raise Exception("Invalid Predicate")
		self.name = ID
		self.terms = Terms(args)
	
	def display(self):
		print("{}({})".format(self.name,self.terms.toString()))
		
	def validParams(self,ID,args):
		return isinstance(ID,(int,float,complex,str,bool))

class Concept(Predicate):
	
	def __init__(self,ID,args):
		super().__init__(ID,args)
		if self.terms.len() != 1: raise Exception("Invalid Concept")

class Role(Predicate):

	def __init__(self,ID,args):
		super().__init__(ID,args)
		if self.terms.len() != 2: raise Exception("Invalid Role")

class ConceptRole(Concept):
	
	def __init__(self,q,concept,role):
		if not self.conceptRoleMatch(concept,role): raise Exception("Invalid Concept/Role")
		super.__init__(role.name,[role.terms.getTerm(0)])
		self.quantifier = Quantifier(q)
		self.concept = concept
		self.role = role
	
	@staticmethod
	def conceptRoleMatch(concept,role):
		return role.terms.getTerm(1) == concept.terms.getTerm(0)