from Statement import *
import random,time

class GenERator:
	
	def __init__(self,numCType1=25,numCType2=25,numCType3=25,numCType4=25,numRoleSub=10,numRoleChains=10,conceptNamespace=50,roleNamespace=10,seed=False):
		self.hasRun = False
		self.numCType1 = numCType1
		self.numCType2 = numCType2
		self.numCType3 = numCType3
		self.numCType4 = numCType4
		self.numRoleSub = numRoleSub
		self.numRoleChains = numRoleChains
		self.conceptNamespace = conceptNamespace
		self.roleNamespace = roleNamespace
		self.CTypeNull = []
		self.CType1 = []
		self.CType2 = []
		self.CType3 = []
		self.CType4 = []
		self.roleSubs = []
		self.roleChains = []
		self.seed = time.time() if not seed else seed
		random.seed(self.seed)
	
	def genERate(self):
		if self.hasRun: return
		
		self.genERateConceptStatements()		
		self.genERateRoleStatements()
		
		self.hasRun = True

	def genERateConceptStatements(self):		
		for i in range(len(self.CTypeNull),self.conceptNamespace):
			self.makeCTypeNull(i)
			
		for i in range(len(self.CType1),self.numCType1):
			self.makeCType1()
				
		for i in range(len(self.CType2),self.numCType2):
			self.makeCType2()
		
		for i in range(len(self.CType3),self.numCType3):
			self.makeCType3()
			
		for i in range(len(self.CType4),self.numCType4):
			self.makeCType4()
			
		self.CType1.sort(key=lambda x: (x.antecedent.name, x.consequent.name))
		self.CType2.sort(key=lambda x: (x.antecedent.antecedent.name, x.antecedent.consequent.name, x.consequent.name))
		self.CType3.sort(key=lambda x: (x.antecedent.name, x.consequent.role.name, x.consequent.concept.name))
		self.CType4.sort(key=lambda x: (x.antecedent.role.name, x.antecedent.concept.name, x.consequent.name))
	
	def makeCTypeNull(self,i):
		""" C ⊑ C """
		cs = ConceptStatement(len(self.CTypeNull),True,Concept(i,[0]),Concept(i,[0]))
		cs.complete('⊑')
		self.CTypeNull.append(cs)
		
	def makeCType1(self):
		""" C ⊑ D """
		left = random.randint(0,self.conceptNamespace-1) if self.conceptNamespace > 0 else random.randint(self.conceptNamespace,-1)
		right = random.randint(0,self.conceptNamespace-1) if self.conceptNamespace > 0 else random.randint(self.conceptNamespace,-1)
		while left == right:
			right = random.randint(0,self.conceptNamespace-1) if self.conceptNamespace > 0 else random.randint(self.conceptNamespace,-1)
		cs = ConceptStatement(len(self.CType1),True,Concept(left,[0]),Concept(right,[0]))
		cs.complete('⊑')
		if self.alreadyGenERated(self.CType1,cs):
			self.makeCType1()
		else:
			self.CType1.append(cs)
			
	def makeCType2(self):
		""" C ⊓ D ⊑ E """
		left1 = random.randint(0,self.conceptNamespace-1) if self.conceptNamespace > 0 else random.randint(self.conceptNamespace,-1)
		left2 = random.randint(0,self.conceptNamespace-1) if self.conceptNamespace > 0 else random.randint(self.conceptNamespace,-1)
		while left1 == left2:
			left2 = random.randint(0,self.conceptNamespace-1) if self.conceptNamespace > 0 else random.randint(self.conceptNamespace,-1)
		cs1 = ConceptStatement(0,True,Concept(left1,[0]),Concept(left2,[0]))
		cs1.complete('⊓')
		right = random.randint(0,self.conceptNamespace-1) if self.conceptNamespace > 0 else random.randint(self.conceptNamespace,-1)
		while left1 == right or right == left2:
			right = random.randint(0,self.conceptNamespace-1) if self.conceptNamespace > 0 else random.randint(self.conceptNamespace,-1)
		cs = ConceptStatement(len(self.CType2),True,cs1,Concept(right,[0]))
		cs.complete('⊑')
		if self.alreadyGenERated(self.CType2,cs):
			self.makeCType2()
		else:
			self.CType2.append(cs)
	
	def makeCType3(self):
		""" C ⊑ ∃R.D """
		left = random.randint(0,self.conceptNamespace-1) if self.conceptNamespace > 0 else random.randint(self.conceptNamespace,-1)
		rightC = random.randint(0,self.conceptNamespace-1) if self.conceptNamespace > 0 else random.randint(self.conceptNamespace,-1)
		rightR = random.randint(0,self.roleNamespace-1) if self.roleNamespace > 0 else random.randint(self.roleNamespace,-1) 
		cs = ConceptStatement(len(self.CType3),True,Concept(left,[0]),ConceptRole('e',Role(rightR,[0,1]),Concept(rightC,[1])))
		cs.complete('⊑')
		if self.alreadyGenERated(self.CType3,cs):
			self.makeCType3()
		else:
			self.CType3.append(cs)
		
	def makeCType4(self):
		""" ∃R.C ⊑ D """
		right = random.randint(0,self.conceptNamespace-1) if self.conceptNamespace > 0 else random.randint(self.conceptNamespace,-1)
		leftC = random.randint(0,self.conceptNamespace-1) if self.conceptNamespace > 0 else random.randint(self.conceptNamespace,-1)
		leftR = random.randint(0,self.roleNamespace-1) if self.roleNamespace > 0 else random.randint(self.roleNamespace,-1) 
		cs = ConceptStatement(len(self.CType4),True,ConceptRole('e',Role(leftR,[0,1]),Concept(leftC,[1])),Concept(right,[0]))
		cs.complete('⊑')
		if self.alreadyGenERated(self.CType4,cs):
			self.makeCType4()
		else:
			self.CType4.append(cs)
		
	def genERateRoleStatements(self):			
		for i in range(len(self.roleSubs),self.numRoleSub):
			self.makeRTypeT()
		
		for i in range(len(self.roleChains),self.numRoleChains):
			self.makeRTypeC()	
			
		self.roleSubs.sort(key=lambda x: (x.antecedent.name, x.consequent.name))
		self.roleChains.sort(key=lambda x: (x.antecedent.roles[0].name, x.antecedent.roles[1].name, x.consequent.name))
		
	def makeRTypeT(self):
		""" R ⊑ S """
		left = random.randint(0,self.roleNamespace-1) if self.roleNamespace > 0 else random.randint(self.roleNamespace,-1) 
		right = random.randint(0,self.roleNamespace-1) if self.roleNamespace > 0 else random.randint(self.roleNamespace,-1) 
		while left == right:
			right = random.randint(0,self.roleNamespace-1) if self.roleNamespace > 0 else random.randint(self.roleNamespace,-1) 
		rs = RoleStatement(len(self.roleSubs),True,Role(left,[0,1]),Role(right,[0,1]))
		rs.complete('⊑')
		if self.alreadyGenERated(self.roleSubs,rs):
			self.makeRTypeT()
		else:
			self.roleSubs.append(rs)			

	def makeRTypeC(self):
		""" R1 ∘ R2 ⊑ S """
		leftR1 = random.randint(0,self.roleNamespace-1) if self.roleNamespace > 0 else random.randint(self.roleNamespace,-1) 
		leftR2 = random.randint(0,self.roleNamespace-1) if self.roleNamespace > 0 else random.randint(self.roleNamespace,-1) 
		right = random.randint(0,self.roleNamespace-1) if self.roleNamespace > 0 else random.randint(self.roleNamespace,-1) 
		while leftR1 == leftR2:
			leftR2 = random.randint(0,self.roleNamespace-1) if self.roleNamespace > 0 else random.randint(self.roleNamespace,-1) 
		rs = RoleStatement(len(self.roleChains),True,RoleChain(0,Role(leftR1,[0,1]),Role(leftR2,[1,2])),Role(right,[0,2]))
		rs.complete('⊑')
		if self.alreadyGenERated(self.roleChains,rs):
			self.makeRTypeC()
		else:
			self.roleChains.append(rs)			

	def alreadyGenERated(self,listy,y):
		return any(x.equals(y) for x in listy)

	def toString(self):
		ret = "Original KB"
		#for statement in self.CTypeNull:
			#ret = ret + statement.toString() + "\n"
		for statement in self.CType1:
			ret = ret + "\n" + statement.toString()
		for statement in self.CType2:
			ret = ret + "\n" + statement.toString()
		for statement in self.CType3:
			ret = ret + "\n" + statement.toString()
		for statement in self.CType4:
			ret = ret + "\n" + statement.toString()	
		for statement in self.roleSubs:
			ret = ret + "\n" + statement.toString()
		for statement in self.roleChains:
			ret = ret + "\n" + statement.toString()
		return ret
	
	def toFunctionalSyntax(self):
		ret = ""
		for statement in self.CType1:
			ret = ret + "\n" + statement.toFunctionalSyntax()
		for statement in self.CType2:
			ret = ret + "\n" + statement.toFunctionalSyntax()
		for statement in self.CType3:
			ret = ret + "\n" + statement.toFunctionalSyntax()
		for statement in self.CType4:
			ret = ret + "\n" + statement.toFunctionalSyntax()	
		for statement in self.roleSubs:
			ret = ret + "\n" + statement.toFunctionalSyntax()
		for statement in self.roleChains:
			ret = ret + "\n" + statement.toFunctionalSyntax()
		return ret		

	def getStatistics(self):
		
		uniqueConceptNames = []
		allConceptNames = 0
		uniqueRoleNames = []
		allRoleNames = 0
		
		for statement in self.CType1:
			if statement.antecedent.name not in uniqueConceptNames: uniqueConceptNames.append(statement.antecedent.name)
			if statement.consequent.name not in uniqueConceptNames: uniqueConceptNames.append(statement.consequent.name)
			allConceptNames = allConceptNames + 2
		for statement in self.CType2:
			if statement.antecedent.antecedent.name not in uniqueConceptNames: uniqueConceptNames.append(statement.antecedent.antecedent.name)
			if statement.antecedent.consequent.name not in uniqueConceptNames: uniqueConceptNames.append(statement.antecedent.consequent.name)
			if statement.consequent.name not in uniqueConceptNames: uniqueConceptNames.append(statement.consequent.name)
			allConceptNames = allConceptNames + 3
		for statement in self.CType3:
			if statement.antecedent.name not in uniqueConceptNames: uniqueConceptNames.append(statement.antecedent.name)
			if statement.consequent.concept.name not in uniqueConceptNames: uniqueConceptNames.append(statement.consequent.concept.name)
			if statement.consequent.role.name not in uniqueRoleNames: uniqueRoleNames.append(statement.consequent.role.name)
			allConceptNames = allConceptNames + 2
			allRoleNames = allRoleNames + 1
		for statement in self.CType4:
			if statement.consequent.name not in uniqueConceptNames: uniqueConceptNames.append(statement.consequent.name)
			if statement.antecedent.concept.name not in uniqueConceptNames: uniqueConceptNames.append(statement.antecedent.concept.name)
			if statement.antecedent.role.name not in uniqueRoleNames: uniqueRoleNames.append(statement.antecedent.role.name)
			allConceptNames = allConceptNames + 2
			allRoleNames = allRoleNames + 1
		for statement in self.roleSubs:
			if statement.antecedent.name not in uniqueRoleNames: uniqueRoleNames.append(statement.antecedent.name)
			if statement.consequent.name not in uniqueRoleNames: uniqueRoleNames.append(statement.consequent.name)
			allRoleNames = allRoleNames + 2
		for statement in self.roleChains:
			if statement.antecedent.roles[0].name not in uniqueRoleNames: uniqueRoleNames.append(statement.antecedent.roles[0].name)
			if statement.antecedent.roles[1].name not in uniqueRoleNames: uniqueRoleNames.append(statement.antecedent.roles[1].name)
			if statement.consequent.name not in uniqueRoleNames: uniqueRoleNames.append(statement.consequent.name)
			allRoleNames = allRoleNames + 3
			
		return [["both",["unique",len(uniqueConceptNames)+len(uniqueRoleNames)],["all",allConceptNames+allRoleNames]],["concept",["unique",len(uniqueConceptNames)],["all",allConceptNames]],["role",["unique",len(uniqueRoleNames)],["all",allRoleNames]]]
