from Term import *
from Quantifier import *
from Statement import *

class Predicate:
	
	def __init__(self,ID,args,negated=True,showTerms=False):
		self.checkPredicate(ID)
		self.terms = Terms(args)
		self.name = ID
		self.negated = not negated
		self.showTerms = showTerms

	def negate(self):
		self.negated = not self.negated
	
	def toString(self):
		return "{}{}{}".format("¬" if self.negated else "",self.name,"({})".format(self.terms.toString()) if self.showTerms else "")
		
	def checkPredicate(self,ID):
		if not isinstance(ID,(int,float,complex,str,bool)): raise Exception("Invalid Predicate")

class Concept(Predicate):
	
	def __init__(self,ID,args,negated=True,showTerms=False):
		super().__init__(ID,args,negated,showTerms)
		self.checkConcept()
	
	def checkConcept(self):
		if self.terms.len() != 1: raise Exception("Invalid Concept")
		
	def isComplete(self):
		return True

class Role(Predicate):

	def __init__(self,ID,args,negated=True,showTerms=False):
		super().__init__(ID,args,negated,showTerms)
		self.checkRole()
		
	def checkRole(self):
		if self.terms.len() != 2: raise Exception("Invalid Role")

class ConceptRole(Concept):
	
	def __init__(self,q,role,concept,negated=True,showTerms=False):
		self.checkConceptRoleMatch(role,concept)
		self.quantifier = Quantifier(q)
		super().__init__(role.name,[role.terms.getTerm(0)],negated)
		self.concept = concept
		self.role = role
	
	def checkConceptRoleMatch(self,role,concept):
		if not isinstance(role,Role) or not isinstance(concept,Concept) or not role.terms.getTerm(1) == concept.terms.getTerm(0) or not concept.isComplete(): raise Exception("Invalid ConceptRole")
	
	def toString(self):
		return "{}{}{}{}.{}".format("¬" if self.negated else "",self.quantifier.toString(),self.role.name,"({})".format(self.terms.toString()) if self.showTerms else "",self.concept.toString())
	
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
