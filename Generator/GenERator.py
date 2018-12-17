from Statement import *
import random

class GenERator:
	
	def __init__(self,numConceptStatements=800,numRoleStatements=100,numRoleChainStatements=100,conceptNamespace=100,roleNamespace=100):
		self.numConceptStatements = numConceptStatements
		self.numRoleStatements = numRoleStatements
		self.numRoleChainStatements = numRoleChainStatements
		self.conceptNamespace = conceptNamespace
		self.roleNamespace = roleNamespace
		self.conceptStatementsTypeNull = []
		self.conceptStatementsType1 = []
		self.conceptStatementsType2 = []
		self.conceptStatementsType3 = []
		self.conceptStatementsType4 = []
		self.roleStatements = []
		self.roleChainStatements = []
	
	def genERate(self):
		self.genERateConceptStatements()
		self.genERateRoleStatements()
		self.genERateRoleChainStatements()

	def genERateConceptStatements(self):
		if len(self.conceptStatementsType1) + len(self.conceptStatementsType2) + len(self.conceptStatementsType3) + len(self.conceptStatementsType4) == self.numConceptStatements and len(self.conceptStatementsTypeNull) == self.conceptNamespace:
			print("Concept generator already completed")
			return False
		for i in range(0,self.conceptNamespace):
			cs = ConceptStatement(1,True,Concept(i,[0]),Concept(i,[0]))
			cs.complete('⊑')
			self.conceptStatementsTypeNull.append(cs)
		for i in range(0,int(self.numConceptStatements/4)):
			left = random.randint(0,self.conceptNamespace-1)
			right = random.randint(0,self.conceptNamespace-1)
			while left == right:
				right = random.randint(0,self.conceptNamespace-1)
			cs = ConceptStatement(1,True,Concept(left,[0]),Concept(right,[0]))
			cs.complete('⊑')
			self.conceptStatementsType1.append(cs)
		for i in range(0,int(self.numConceptStatements/4)):
			left1 = random.randint(0,self.conceptNamespace-1)
			left2 = random.randint(0,self.conceptNamespace-1)
			while left1 == left2:
				left2 = random.randint(0,self.conceptNamespace-1)
			cs1 = ConceptStatement(1,True,Concept(left1,[0]),Concept(left2,[0]))
			cs1.complete('⊓')
			right = random.randint(0,self.conceptNamespace-1)
			while left1 == right or right == left2:
				right = random.randint(0,self.conceptNamespace-1)
			cs = ConceptStatement(1,True,cs1,Concept(right,[0]))
			cs.complete('⊑')
			self.conceptStatementsType1.append(cs)


	def genERateRoleStatements(self):
		if len(self.roleStatements) == self.numRoleStatements:
			print("Role generator already completed")
			return False

	def genERateRoleChainStatements(self):
		if len(self.roleChainStatements) == self.numRoleChainStatements:
			print("RoleChain generator already completed")
			return False

	def toString(self):
		ret = ""
		#for statement in self.conceptStatementsTypeNull:
			#ret = ret + statement.toString() + "\n"
		for statement in self.conceptStatementsType1:
			ret = ret + statement.toString() + "\n"
		for statement in self.conceptStatementsType2:
			ret = ret + statement.toString() + "\n"
		for statement in self.conceptStatementsType3:
			ret = ret + statement.toString() + "\n"
		for statement in self.roleStatements:
			ret = ret + statement.toString() + "\n"
		for statement in self.roleChainStatements:
			ret = ret + statement.toString() + "\n"
		return ret
