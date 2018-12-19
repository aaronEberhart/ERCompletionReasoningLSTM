from Statement import *
import random

class GenERator:
	
	def __init__(self,numConceptStatements=800,numRoleTStatements=150,numRoleChainStatements=50,conceptNamespace=100,roleNamespace=100):
		self.numConceptTStatements = int(numConceptStatements * 3 / 4)
		self.numConceptAStatements = numConceptStatements - self.numConceptTStatements
		self.numRoleTStatements = int(numRoleTStatements / 2)
		self.numRoleAStatements = self.numRoleTStatements - numRoleTStatements
		self.numRoleChainStatements = numRoleChainStatements
		self.conceptNamespace = conceptNamespace
		self.roleNamespace = roleNamespace
		self.conceptAStatements = []
		self.conceptTStatementsTypeNull = []
		self.conceptTStatementsType1 = []
		self.conceptTStatementsType2 = []
		self.conceptTStatementsType3 = []
		self.conceptTStatementsType4 = []
		self.roleAStatements = []
		self.roleTStatements = []
		self.roleChainStatements = []
	
	def genERate(self):
		self.genERateConceptStatements()
		self.genERateRoleStatements()
		self.genERateRoleChainStatements()

	def genERateConceptStatements(self):
		
		if len(self.conceptTStatementsType1) + len(self.conceptTStatementsType2) + len(self.conceptTStatementsType3) + len(self.conceptTStatementsType4) == self.numConceptTStatements and len(self.conceptAStatements) == self.numConceptAStatements and len(self.conceptTStatementsTypeNull) == self.conceptNamespace:
			print("Concept generator already completed")
			return False
		
		for i in range(len(self.conceptTStatementsTypeNull),self.conceptNamespace):
			self.makeCTTypeNull(i)
			
		for i in range(len(self.conceptTStatementsType1),int(self.numConceptTStatements/4)):
			self.makeCTType1()
				
		for i in range(len(self.conceptTStatementsType2),int(self.numConceptTStatements/4)):
			self.makeCTType2()
	
	def makeCTTypeNull(self,i):
		cs = ConceptStatement(1,True,Concept(i,[0]),Concept(i,[0]))
		cs.complete('⊑')
		self.conceptTStatementsTypeNull.append(cs)
		
	def makeCTType1(self):
		left = random.randint(0,self.conceptNamespace-1)
		right = random.randint(0,self.conceptNamespace-1)
		while left == right:
			right = random.randint(0,self.conceptNamespace-1)
		cs = ConceptStatement(1,True,Concept(left,[0]),Concept(right,[0]))
		cs.complete('⊑')
		if self.alreadyGenERated(self.conceptTStatementsType1,cs):
			self.makeCTType1()
		else:
			self.conceptTStatementsType1.append(cs)
			
	def makeCTType2(self):
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
		if self.alreadyGenERated(self.conceptTStatementsType2,cs):
			self.makeType2()
		else:
			self.conceptTStatementsType2.append(cs)

	def genERateRoleStatements(self):
		if len(self.roleTStatements) == self.numRoleTStatements:
			print("Role generator already completed")
			return False

	def genERateRoleChainStatements(self):
		if len(self.roleChainStatements) == self.numRoleChainStatements:
			print("RoleChain generator already completed")
			return False

	def alreadyGenERated(self,part,cs):
		for i in range(0,len(part)):
			if cs.equals(part[i]):
				return True
		return False

	def toString(self):
		ret = ""
		#for statement in self.conceptTStatementsTypeNull:
			#ret = ret + statement.toString() + "\n"
		for statement in self.conceptTStatementsType1:
			ret = ret + statement.toString() + "\n"
		for statement in self.conceptTStatementsType2:
			ret = ret + statement.toString() + "\n"
		for statement in self.conceptTStatementsType3:
			ret = ret + statement.toString() + "\n"
		for statement in self.roleTStatements:
			ret = ret + statement.toString() + "\n"
		for statement in self.roleChainStatements:
			ret = ret + statement.toString() + "\n"
		return ret
