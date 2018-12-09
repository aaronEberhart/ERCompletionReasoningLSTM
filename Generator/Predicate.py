from Term import *
from Quantifier import *
from Statement import *

class Predicate:
	
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
		return "{}{}({}).{}".format(self.quantifier.toString(),self.role.name,self.role.terms.toString(),self.concept.toString())
	
class RoleChain(Role):
	
	def __init__(self,ID,*chain):
		self.checkRoleChain(chain)
		self.checkPredicate(ID)
		self.name = ID
		self.roles = []
		self.appendRoles(chain)
	
	def checkRoleChain(self,chain):
		if chain == None or len(chain) == 0: raise Exception("Invalid RoleChain")
		
	def checkRoleChainAppend(self,role):
		role.checkRole()
		if self.terms.getTerm(1) != role.terms.getTerm(0): raise Exception("Invalid RoleChain")
	
	def appendRoles(self,chain):
		for i in range(0,len(chain)):
			
			if i == 0 and self.roles == []:
				chain[i].checkRole()
				self.terms = Terms([term.getTerm() for term in chain[i].terms.getTerms()])
				self.roles.append(chain[i])
			else:
				self.checkRoleChainAppend(chain[i])
				self.roles.append(chain[i])
				self.terms.setTerm(1,chain[i].terms.getTerm(1))
	
	def toString(self):
		return "".join(["{}{}".format("∘" if role != self.roles[0] else "",role.toString()) for role in self.roles])
