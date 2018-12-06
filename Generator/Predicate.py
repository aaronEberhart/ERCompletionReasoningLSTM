from Term import *
from Quantifier import *

class Predicate(ABC):
	
	def __init__(self,ID,args):
		self.checkPredicate(ID)
		self.terms = Terms(args)
		self.name = ID		
	
	def toString(self):
		return "{}({})".format(self.name,self.terms.toString())
		
	def checkPredicate(self,ID):
		if not isinstance(ID,(int,float,complex,str,bool)): raise Exception("Invalid Predicate")

class Concept(Predicate):
	
	def __init__(self,ID,args):
		super().__init__(ID,args)
		self.checkConcept()
	
	def checkConcept(self):
		if self.terms.len() != 1: raise Exception("Invalid Concept")

class Role(Predicate):

	def __init__(self,ID,args):
		super().__init__(ID,args)
		self.checkRole()
		
	def checkRole(self):
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