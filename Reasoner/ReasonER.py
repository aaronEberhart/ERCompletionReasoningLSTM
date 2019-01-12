from Statement import *

"""
Completion rules:

(1) C ⊑ D,A ⊑ C                         |= A ⊑ D

(2) C1 ⊓ C2 ⊑ D, A ⊑ C1, A ⊑ C2         |= A ⊑ D

(3) C ⊑ ∃R.D, A ⊑ C                     |= A ⊑ ∃R.D

(4) ∃R.C ⊑ D, A ⊑ ∃R.B, B ⊑ C           |= A ⊑ D

(5) R ⊑ S, A ⊑ ∃R.B                     |= A ⊑ ∃S.B

(6) R1 ∘ R2 ⊑ R, A ⊑ ∃R1.B, B ⊑ ∃R2.C   |= A ⊑ ∃R.C

"""

class ReasonER:
	
	def __init__(self,genERator,showSteps=False):
		self.hasRun = False
		self.syntheticData = genERator
		self.showSteps = showSteps
		if not self.syntheticData.hasRun:
			self.syntheticData.genERate()
		self.newCType1 = []
		self.knownCType1 = []
		self.numKnownCType1 = 0
		self.newCType3 = []
		self.knownCType3 = []
		self.numKnownCType3 = 0
		self.log = "" if not showSteps else "Reasoner Steps"
	
	def ERason(self):
		if self.hasRun: return
		
		self.trySolveRules(0)
		
		i = 1
		while self.hasGrown():
			self.trySolveRules(i)
			i = i + 1
		 
		self.knownCType1.sort(key=lambda x: (x.antecedent[0].name, x.consequent[0].name))
		self.knownCType3.sort(key=lambda x: (x.antecedent[0].name, x.consequent[0].role.name, x.consequent[0].concept.name))
		
		self.hasRun = True
			
	def trySolveRules(self,i):
		self.solveRule1()
		self.solveRule2()
		self.solveRule3()
		self.solveRule4()
		self.solveRule5()
		self.solveRule6()
		self.pruneNewRules(i)
		
	def pruneNewRules(self,i):
		c1Known = self.knownCType1 + self.syntheticData.CType1
		c3Known = self.knownCType3 + self.syntheticData.CType3
		for rule in self.newCType1:
			if not self.alreadyKnown(c1Known,rule):
				if self.showSteps: self.log = self.log + "\nLearned {} in loop {}".format(rule.toString(),i)
				self.knownCType1.append(rule)
				c1Known.append(rule)
		for rule in self.newCType3:
			if not self.alreadyKnown(c3Known,rule):
				if self.showSteps: self.log = self.log + "\nLearned {} in loop {}".format(rule.toString(),i)
				self.knownCType3.append(rule)
				c3Known.append(rule)
		self.newCType1 = []
		self.newCType3 = []
	
	def hasGrown(self):
		if len(self.knownCType1) == self.numKnownCType1 and len(self.knownCType3) == self.numKnownCType3: return False
		self.numKnownCType1 = len(self.knownCType1)
		self.numKnownCType3 = len(self.knownCType3)
		return True
	
	def solveRule1(self):
		""" C ⊑ D,A ⊑ C |= A ⊑ D """
		candidates = self.syntheticData.CType1 + self.knownCType1
		
		for candidate1 in candidates:
			for candidate2 in list(filter(lambda x: candidate1.antecedent[0].name == x.consequent[0].name,candidates)):
			
				if candidate2.antecedent[0].name == candidate1.consequent[0].name: continue
				
				cs = ConceptStatement(0,True,candidate2.antecedent[0],candidate1.consequent[0])
				cs.complete('⊑')
				self.newCType1.append(cs)
	
	def solveRule2(self):
		""" C1 ⊓ C2 ⊑ D, A ⊑ C1, A ⊑ C2 |= A ⊑ D """
		candidates = self.syntheticData.CTypeNull + self.syntheticData.CType1 + self.knownCType1
		
		for conjunction in self.syntheticData.CType2:
			for candidate1 in list(filter(lambda x: conjunction.antecedent[0].antecedent[0].name == x.consequent[0].name,candidates)):
				for candidate2 in list(filter(lambda x: conjunction.antecedent[0].consequent[0].name == x.consequent[0].name and x.antecedent[0].name == candidate1.antecedent[0].name,candidates)):
					
					if candidate1.antecedent[0].name == conjunction.consequent[0].name: continue
					
					cs = ConceptStatement(0,True,candidate1.antecedent[0],conjunction.consequent[0])
					cs.complete('⊑')					
					self.newCType1.append(cs)
	
	def solveRule3(self):
		""" C ⊑ ∃R.D, A ⊑ C |= A ⊑ ∃R.D """
		type1Candidates = self.syntheticData.CType1 + self.knownCType1
		type3Candidates = self.syntheticData.CType3 + self.knownCType3
		
		for candidate1 in type3Candidates:
			for candidate2 in list(filter(lambda x: candidate1.antecedent[0].name == x.consequent[0].name,type1Candidates)):
				
				cs = ConceptStatement(0,True,candidate2.antecedent[0],candidate1.consequent[0])
				cs.complete('⊑')				
				self.newCType3.append(cs)
	
	def solveRule4(self):
		""" ∃R.C ⊑ D, A ⊑ ∃R.B, B ⊑ C |= A ⊑ D """
		type1Candidates = self.syntheticData.CTypeNull + self.syntheticData.CType1 + self.knownCType1
		type3Candidates = self.syntheticData.CType3 + self.knownCType3		
		
		for candidate1 in self.syntheticData.CType4:
			for candidate2 in list(filter(lambda x: candidate1.antecedent[0].concept.name == x.consequent[0].name,type1Candidates)):
				for candidate3 in list(filter(lambda x: x.consequent[0].concept.name == candidate2.antecedent[0].name,type3Candidates)):
					
					if candidate3.antecedent[0].name == candidate1.consequent[0].name: continue
					
					cs = ConceptStatement(0,True,Concept(candidate3.antecedent[0].name,[0]),Concept(candidate1.consequent[0].name,[0]))
					cs.complete('⊑')					
					self.newCType1.append(cs)
	
	def solveRule5(self):
		""" R ⊑ S, A ⊑ ∃R.B |= A ⊑ ∃S.B """
		type3Candidates = self.syntheticData.CType3 + self.knownCType3
		
		for roleStatement in self.syntheticData.roleSubs:
			for matchingConceptStatement in list(filter(lambda x: roleStatement.antecedent[0].name == x.consequent[0].role.name,type3Candidates)):
				
				cs = ConceptStatement(0,True,matchingConceptStatement.antecedent[0],ConceptRole('e',roleStatement.consequent[0],matchingConceptStatement.consequent[0].concept))
				cs.complete('⊑')				
				self.newCType3.append(cs)
	
	def solveRule6(self):
		""" R1 ∘ R2 ⊑ R, A ⊑ ∃R1.B, B ⊑ ∃R2.C |= A ⊑ ∃R.C """
		type3Candidates = self.syntheticData.CType3 + self.knownCType3
		
		for roleChain in self.syntheticData.roleChains:
			for matchingConceptStatement1 in list(filter(lambda x: roleChain.antecedent[0].roles[0].name == x.consequent[0].role.name,type3Candidates)):
				for matchingConceptStatement2 in list(filter(lambda x: x.antecedent[0].name == matchingConceptStatement1.consequent[0].concept.name and roleChain.antecedent[0].roles[1].name == x.consequent[0].role.name,type3Candidates)):
					
					cs = ConceptStatement(0,True,matchingConceptStatement1.antecedent[0],ConceptRole('e',Role(roleChain.consequent[0].name,[0,1]),matchingConceptStatement2.consequent[0].concept))
					cs.complete('⊑')					
					self.newCType3.append(cs)
					
	def alreadyKnown(self,statements,s):
		return any(x.equals(s) for x in statements)
	
	def getLog(self):
		return self.log
	
	def toString(self):
		ret = "\nExtended KB"
		for statement in self.knownCType1:
			ret = ret + "\n" + statement.toString()
		for statement in self.knownCType3:
			ret = ret + "\n" + statement.toString()
		return ret
	
	def getStatistics(self):
		
		uniqueConceptNames = []
		allConceptNames = 0
		uniqueRoleNames = []
		allRoleNames = 0
		
		for statement in self.knownCType1:
			if statement.antecedent[0].name not in uniqueConceptNames: uniqueConceptNames.append(statement.antecedent[0].name)
			if statement.consequent[0].name not in uniqueConceptNames: uniqueConceptNames.append(statement.consequent[0].name)
			allConceptNames = allConceptNames + 2
		for statement in self.knownCType3:
			if statement.antecedent[0].name not in uniqueConceptNames: uniqueConceptNames.append(statement.antecedent[0].name)
			if statement.consequent[0].concept.name not in uniqueConceptNames: uniqueConceptNames.append(statement.consequent[0].concept.name)
			if statement.consequent[0].role.name not in uniqueRoleNames: uniqueRoleNames.append(statement.consequent[0].role.name)
			allConceptNames = allConceptNames + 2
			allRoleNames = allRoleNames + 1
			
		return [["both",["unique",len(uniqueConceptNames)+len(uniqueRoleNames)],["all",allConceptNames+allRoleNames]],["concept",["unique",len(uniqueConceptNames)],["all",allConceptNames]],["role",["unique",len(uniqueRoleNames)],["all",allRoleNames]]]
	