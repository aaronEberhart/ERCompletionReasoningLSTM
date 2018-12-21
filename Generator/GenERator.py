from Statement import *
import random

class GenERator:
	
	def __init__(self,numConceptStatements=750,numRoleStatements=200,numRoleChainStatements=50,conceptNamespace=100,termNamespace=50):
		self.numConceptTStatements = int(numConceptStatements * 4 / 5)
		self.numConceptAStatements = numConceptStatements - self.numConceptTStatements
		self.numRoleTStatements = int(numRoleStatements *  3 / 4)
		self.numRoleAStatements = numRoleStatements - self.numRoleTStatements
		self.numRoleChainStatements = numRoleChainStatements
		self.conceptNamespace = conceptNamespace
		self.roleNamespace = conceptNamespace * 2
		self.termNamespace = termNamespace
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

	def genERateConceptStatements(self):
		
		if len(self.conceptTStatementsType1) + len(self.conceptTStatementsType2) + len(self.conceptTStatementsType3) + len(self.conceptTStatementsType4) == self.numConceptTStatements and len(self.conceptAStatements) == self.numConceptAStatements and len(self.conceptTStatementsTypeNull) == self.conceptNamespace:
			print("Concept generator already completed")
			return False
		
		for i in range(len(self.conceptTStatementsTypeNull),self.conceptNamespace):
			self.makeCTypeNull(i)
			
		for i in range(len(self.conceptTStatementsType1),int(self.numConceptTStatements/4)):
			self.makeCType1()
				
		for i in range(len(self.conceptTStatementsType2),int(self.numConceptTStatements/4)):
			self.makeCType2()
		
		for i in range(len(self.conceptTStatementsType3),int(self.numConceptTStatements/4)):
			self.makeCType3()
			
		for i in range(len(self.conceptTStatementsType4),self.numConceptTStatements - len(self.conceptTStatementsType1) - len(self.conceptTStatementsType2) - len(self.conceptTStatementsType3)):
			self.makeCType4()
			
		for i in range(len(self.conceptAStatements),self.numConceptAStatements):	
			self.makeCTypeA()
			
		return True
	
	def makeCTypeNull(self,i):
		""" C ⊑ C """
		cs = ConceptStatement(len(self.conceptTStatementsTypeNull),True,Concept(i,[0]),Concept(i,[0]))
		cs.complete('⊑')
		self.conceptTStatementsTypeNull.append(cs)
		
	def makeCType1(self):
		""" C ⊑ D """
		left = random.randint(0,self.conceptNamespace-1)
		right = random.randint(0,self.conceptNamespace-1)
		while left == right:
			right = random.randint(0,self.conceptNamespace-1)
		cs = ConceptStatement(len(self.conceptTStatementsType1),True,Concept(left,[0]),Concept(right,[0]))
		cs.complete('⊑')
		if self.alreadyGenERated(self.conceptTStatementsType1,cs):
			self.makeCType1()
		else:
			self.conceptTStatementsType1.append(cs)
			
	def makeCType2(self):
		""" C ⊓ D ⊑ E """
		left1 = random.randint(0,self.conceptNamespace-1)
		left2 = random.randint(0,self.conceptNamespace-1)
		while left1 == left2:
			left2 = random.randint(0,self.conceptNamespace-1)
		cs1 = ConceptStatement(0,True,Concept(left1,[0]),Concept(left2,[0]))
		cs1.complete('⊓')
		right = random.randint(0,self.conceptNamespace-1)
		while left1 == right or right == left2:
			right = random.randint(0,self.conceptNamespace-1)
		cs = ConceptStatement(len(self.conceptTStatementsType2),True,cs1,Concept(right,[0]))
		cs.complete('⊑')
		if self.alreadyGenERated(self.conceptTStatementsType2,cs):
			self.makeCType2()
		else:
			self.conceptTStatementsType2.append(cs)
	
	def makeCType3(self):
		""" C ⊑ ∃R.D """
		left = random.randint(0,self.conceptNamespace-1)
		rightC = random.randint(0,self.conceptNamespace-1)
		rightR = random.randint(self.conceptNamespace,self.roleNamespace - 1)
		cs = ConceptStatement(len(self.conceptTStatementsType3),True,Concept(left,[0]),ConceptRole('e',Role(rightR,[0,1]),Concept(rightC,[1])))
		cs.complete('⊑')
		if self.alreadyGenERated(self.conceptTStatementsType3,cs):
			self.makeCType3()
		else:
			self.conceptTStatementsType3.append(cs)
		
	def makeCType4(self):
		""" ∃R.C ⊑ D """
		right = random.randint(0,self.conceptNamespace-1)
		leftC = random.randint(0,self.conceptNamespace-1)
		leftR = random.randint(self.conceptNamespace,self.roleNamespace - 1)
		cs = ConceptStatement(len(self.conceptTStatementsType4),True,ConceptRole('e',Role(leftR,[0,1]),Concept(leftC,[1])),Concept(right,[0]))
		cs.complete('⊑')
		if self.alreadyGenERated(self.conceptTStatementsType4,cs):
			self.makeCType4()
		else:
			self.conceptTStatementsType4.append(cs)

	def makeCTypeA(self):
		"""C(rand)"""
		c = Concept(random.randint(0,self.conceptNamespace-1),[random.randint(0,self.termNamespace-1)],showTerms=True)
		if self.alreadyGenERated(self.conceptAStatements,c):
			self.makeCTypeA()
		else:
			self.conceptAStatements.append(c)
		
	def genERateRoleStatements(self):
		if len(self.roleTStatements) == self.numRoleTStatements and len(self.roleChainStatements) == self.numRoleChainStatements and len(self.roleAStatements) == self.numRoleAStatements:
			print("Role generator already completed")
			return False
		
		for i in range(len(self.roleTStatements),self.numRoleTStatements):
			self.makeRTypeT()
		
		for i in range(len(self.roleChainStatements),self.numRoleChainStatements):
			self.makeRTypeC()
		
		for i in range(len(self.roleAStatements),self.numRoleAStatements):
			self.makeRTypeA()		
		
	def makeRTypeT(self):
		""" R ⊑ S """
		left = random.randint(self.conceptNamespace,self.roleNamespace-1)
		right = random.randint(self.conceptNamespace,self.roleNamespace-1)
		while left == right:
			right = random.randint(self.conceptNamespace,self.roleNamespace-1)
		rs = RoleStatement(len(self.roleTStatements),True,Role(left,[0,1]),Role(right,[0,1]))
		rs.complete('⊑')
		if self.alreadyGenERated(self.roleTStatements,rs):
			self.makeRTypeT()
		else:
			self.roleTStatements.append(rs)		
		
	def makeRTypeA(self):
		""" R(rand,rand) """
		r = Role(random.randint(self.conceptNamespace,self.roleNamespace-1),[random.randint(0,self.termNamespace-1),random.randint(0,self.termNamespace-1)],showTerms=True)
		if self.alreadyGenERated(self.roleAStatements,r):
			self.makeRTypeA()
		else:
			self.roleAStatements.append(r)		

	def makeRTypeC(self):
		""" R1 ∘ R2 ⊑ S """
		leftR1 = random.randint(self.conceptNamespace,self.roleNamespace-1)
		leftR2 = random.randint(self.conceptNamespace,self.roleNamespace-1)
		right = random.randint(self.conceptNamespace,self.roleNamespace-1)
		while leftR1 == leftR2:
			leftR2 = random.randint(self.conceptNamespace,self.roleNamespace-1)
		rs = RoleStatement(len(self.roleChainStatements),True,RoleChain(0,Role(leftR1,[0,1]),Role(leftR2,[1,2])),Role(right,[0,2]))
		rs.complete('⊑')
		if self.alreadyGenERated(self.roleChainStatements,rs):
			self.makeRTypeC()
		else:
			self.roleChainStatements.append(rs)			

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
		for statement in self.conceptTStatementsType4:
			ret = ret + statement.toString() + "\n"		
		for statement in self.conceptAStatements:
			ret = ret + statement.toString() + "\n"		
		for statement in self.roleTStatements:
			ret = ret + statement.toString() + "\n"
		for statement in self.roleChainStatements:
			ret = ret + statement.toString() + "\n"
		for statement in self.roleAStatements:
			ret = ret + statement.toString() + "\n"			
		return ret
