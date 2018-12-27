from GenERator import *

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
	
	def ERason(self):
		self.trySolveRules()
		while self.hasGrown():
			self.trySolveRules()
		self.knownCType1.sort(key=lambda x: x.antecedent[0].name)
		self.knownCType3.sort(key=lambda x: x.antecedent[0].name)
			
	def trySolveRules(self):
		self.solveRule1()
		self.solveRule2()
		self.solveRule3()
		self.solveRule4()
		self.solveRule5()
		self.solveRule6()
		self.pruneNewRules()
		
		
	def pruneNewRules(self):
		c1Known = self.knownCType1 + self.syntheticData.conceptTStatementsType1
		c3Known = self.knownCType3 + self.syntheticData.conceptTStatementsType3
		for rule in self.newCType1:
			if not self.alreadyKnown(c1Known,rule):
				if self.showSteps: print(rule.toString())
				self.knownCType1.append(rule)
				c1Known.append(rule)
		for rule in self.newCType3:
			if not self.alreadyKnown(c3Known,rule):
				if self.showSteps: print(rule.toString())
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
		candidates = self.syntheticData.conceptTStatementsType1 + self.knownCType1
		
		for candidate1 in candidates:
			for candidate2 in list(filter(lambda x: candidate1.antecedent[0].equals(x.consequent[0]),candidates)):
				
				if candidate2.antecedent[0].name == candidate1.consequent[0].name: continue
				
				cs = ConceptStatement(0,True,candidate2.antecedent[0],candidate1.consequent[0])
				cs.complete('⊑')
				self.newCType1.append(cs)
	
	def solveRule2(self):
		""" C1 ⊓ C2 ⊑ D, A ⊑ C1, A ⊑ C2 |= A ⊑ D """
		candidates = self.syntheticData.conceptTStatementsTypeNull + self.syntheticData.conceptTStatementsType1 + self.knownCType1
		
		for conjunction in self.syntheticData.conceptTStatementsType2:
			for candidate1 in list(filter(lambda x: conjunction.antecedent[0].antecedent[0].equals(x.consequent[0]),candidates)):
				for candidate2 in list(filter(lambda x: conjunction.antecedent[0].consequent[0].equals(x.consequent[0]) and x.antecedent[0].equals(candidate1.antecedent[0]),candidates)):
					
					if candidate1.antecedent[0].name == conjunction.consequent[0].name: continue
					
					cs = ConceptStatement(0,True,candidate1.antecedent[0],conjunction.consequent[0])
					cs.complete('⊑')	
					
					self.newCType1.append(cs)
	
	def solveRule3(self):
		""" C ⊑ ∃R.D, A ⊑ C |= A ⊑ ∃R.D """
		type1Candidates = self.syntheticData.conceptTStatementsTypeNull + self.syntheticData.conceptTStatementsType1 + self.knownCType1
		type3Candidates = self.syntheticData.conceptTStatementsType3 + self.knownCType3
		
		for candidate1 in type3Candidates:
			for candidate2 in list(filter(lambda x: candidate1.antecedent[0].equals(x.consequent[0]),type1Candidates)):
				
				cs = ConceptStatement(0,True,candidate2.antecedent[0],candidate1.consequent[0])
				cs.complete('⊑')	
				
				self.newCType3.append(cs)
	
	def solveRule4(self):
		""" ∃R.C ⊑ D, A ⊑ ∃R.B, B ⊑ C |= A ⊑ D """
		type1Candidates = self.syntheticData.conceptTStatementsTypeNull + self.syntheticData.conceptTStatementsType1 + self.knownCType1
		type3Candidates = self.syntheticData.conceptTStatementsType3 + self.knownCType3		
		
		for candidate1 in self.syntheticData.conceptTStatementsType4:
			for candidate2 in list(filter(lambda x: candidate1.antecedent[0].concept.name == x.consequent[0].name,type1Candidates)):
				for candidate3 in list(filter(lambda x: x.consequent[0].concept.name == candidate2.antecedent[0].name,type3Candidates)):
					
					if candidate3.antecedent[0].name == candidate1.consequent[0].name: continue
					
					cs = ConceptStatement(0,True,Concept(candidate3.antecedent[0].name,[0]),Concept(candidate1.consequent[0].name,[0]))
					cs.complete('⊑')	
					
					self.newCType1.append(cs)
	
	def solveRule5(self):
		""" R ⊑ S, A ⊑ ∃R.B |= A ⊑ ∃S.B """
		type3Candidates = self.syntheticData.conceptTStatementsType3 + self.knownCType3
		
		for roleStatement in self.syntheticData.roleTStatements:
			for matchingConceptStatement in list(filter(lambda x: roleStatement.antecedent[0].name == x.consequent[0].role.name,type3Candidates)):
				
				cs = ConceptStatement(0,True,matchingConceptStatement.antecedent[0],ConceptRole('e',roleStatement.consequent[0],matchingConceptStatement.consequent[0].concept))
				cs.complete('⊑')	
				
				self.newCType3.append(cs)
	
	def solveRule6(self):
		""" R1 ∘ R2 ⊑ R, A ⊑ ∃R1.B, B ⊑ ∃R2.C |= A ⊑ ∃R.C """
		type3Candidates = self.syntheticData.conceptTStatementsType3 + self.knownCType3
		
		for roleChain in self.syntheticData.roleChainStatements:
			for matchingConceptStatement1 in list(filter(lambda x: roleChain.antecedent[0].roles[0].name == x.consequent[0].role.name,type3Candidates)):
				for matchingConceptStatement2 in list(filter(lambda x: x.antecedent[0].name == matchingConceptStatement1.consequent[0].concept.name and roleChain.antecedent[0].roles[1].name == x.consequent[0].role.name,type3Candidates)):
					
					cs = ConceptStatement(0,True,matchingConceptStatement1.antecedent[0],ConceptRole('e',Role(roleChain.consequent[0].name,[0,1]),matchingConceptStatement2.consequent[0].concept))
					cs.complete('⊑')	
					
					self.newCType3.append(cs)
					
	def alreadyKnown(self,statements,s):
		return any(x.equals(s) for x in statements)
	
	def toString(self):
		ret = "Original KB:\n\n"+self.syntheticData.toString()+"\nExtended KB:\n\n"+("EMPTY" if len(self.knownCType1) == 0 and len(self.knownCType3) == 0 else "")
		for statement in self.knownCType1:
			ret = ret + statement.toString() + "\n"
		for statement in self.knownCType3:
			ret = ret + statement.toString() + "\n"	
		return ret