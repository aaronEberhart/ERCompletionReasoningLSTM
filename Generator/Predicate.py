from Term import *
from Quantifier import *

class Predicate(ABC):
	
	def __init__(self,ID,args):
		if not self.validParams(ID,args): raise Exception("Invalid Predicate")
		self.name = ID
		self.terms = Terms(args)
	
	def toString(self):
		return "{}({})".format(self.name,self.terms.toString())
		
	def validParams(self,ID,args):
		return isinstance(ID,(int,float,complex,str,bool))

class Concept(Predicate):
	
	def __init__(self,ID,args):
		super().__init__(ID,args)
		self.checkConcept()
	
	def checkConcept(self):
		if self.terms.len() != 1: raise Exception("Invalid Concept")

class Role(Predicate):

	def __init__(self,ID,args):
		super().__init__(ID,args)
		if self.terms.len() != 2: raise Exception("Invalid Role")

class ConceptRole(Concept):
	
	def __init__(self,q,role,concept):
		self.checkConceptRoleMatch(role,concept)
		self.quantifier = Quantifier(q)
		super().__init__(role.name,[role.terms.getTerm(0)])
		self.concept = concept
		self.role = role
	
	def checkConceptRoleMatch(self,role,concept):
		if not isinstance(role,Role) or not isinstance(concept,Concept) or not role.terms.getTerm(1) == concept.terms.getTerm(0): raise Exception("Invalid ConceptRole")
	
	def toString(self):
		return "{}{}({}).{}({})".format(self.quantifier.toString(),self.role.name,self.role.terms.toString(),self.concept.name,self.concept.terms.toString())