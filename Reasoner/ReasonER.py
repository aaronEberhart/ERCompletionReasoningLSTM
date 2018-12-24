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
	
	def __init__(self,genERator):
		self.syntheticData = genERator
		if not self.syntheticData.hasRun:
			self.syntheticData.genERate()
		self.newCType1 = []
		self.lenNewCType1 = 0
		self.newCType3 = []
		self.lenNewCType3 = 0
	
	def ERason(self):
		self.trySolveRules()
		while self.hasGrown():
			self.trySolveRules()
			
	def trySolveRules(self):
		self.solveRule1()
		self.solveRule2()
		self.solveRule3()
		self.solveRule4()
		self.solveRule5()
		self.solveRule6()
	
	def hasGrown(self):
		if len(self.newCType1) == self.lenNewCType1 and len(self.newCType3) == self.lenNewCType3: return False
		self.lenNewCType1 = len(self.newCType1)
		self.lenNewCType3 = len(self.newCType3)
		return True
	
	def solveRule1(self):
		""" C ⊑ D,A ⊑ C |= A ⊑ D """
		candidates = self.syntheticData.conceptTStatementsTypeNull + self.syntheticData.conceptTStatementsType1 + self.newCType1
		
		for candidate in candidates:
			pass
		
		pass
	
	def solveRule2(self):
		""" C1 ⊓ C2 ⊑ D, A ⊑ C1, A ⊑ C2 |= A ⊑ D """
		pass
	
	def solveRule3(self):
		""" C ⊑ ∃R.D, A ⊑ C |= A ⊑ ∃R.D """
		pass
	
	def solveRule4(self):
		""" ∃R.C ⊑ D, A ⊑ ∃R.B, B ⊑ C |= A ⊑ D """
		pass
	
	def solveRule5(self):
		""" R ⊑ S, A ⊑ ∃R.B |= A ⊑ ∃S.B """
		pass
	
	def solveRule6(self):
		""" R1 ∘ R2 ⊑ R, A ⊑ ∃R1.B, B ⊑ ∃R2.C |= A ⊑ ∃R.C """
		pass
	
	def toString(self):
		ret = self.syntheticData.toString()
		for statement in self.newCType1:
			ret = ret + statement.toString() + "\n"
		for statement in self.newCType3:
			ret = ret + statement.toString() + "\n"	
		return ret