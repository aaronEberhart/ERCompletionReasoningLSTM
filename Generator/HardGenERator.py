from Statement import *

"""
Completion rules:

(1) C ⊑ D,A ⊑ C                         ⊨ A ⊑ D

(2) C1 ⊓ C2 ⊑ D, A ⊑ C1, A ⊑ C2         ⊨ A ⊑ D

(3) C ⊑ ∃R.D, A ⊑ C                     ⊨ A ⊑ ∃R.D

(4) ∃R.C ⊑ D, A ⊑ ∃R.B, B ⊑ C           ⊨ A ⊑ D

(5) R ⊑ S, A ⊑ ∃R.B                     ⊨ A ⊑ ∃S.B

(6) R1 ∘ R2 ⊑ R, A ⊑ ∃R1.B, B ⊑ ∃R2.C   ⊨ A ⊑ ∃R.C

"""

class HardGenERator:
	
	def __init__(self,difficulty=50):
		self.seed = "N/A"
		self.conceptNamespace = 0
		self.roleNamespace = 0	
		self.CTypeNull = []
		self.CType1 = []
		self.CType2 = []
		self.CType3 = []
		self.CType4 = []
		self.roleSubs = []
		self.roleChains = []
		self.difficulty = difficulty
		self.hasRun = False
		
	def genERate(self):
		for i in range(0,self.difficulty):
			self.genERateSequence(i)
			
		self.CType1.sort(key=lambda x: (x.antecedent.name, x.consequent.name))
		self.CType2.sort(key=lambda x: (x.antecedent.antecedent.name, x.antecedent.consequent.name, x.consequent.name))
		self.CType3.sort(key=lambda x: (x.antecedent.name, x.consequent.role.name, x.consequent.concept.name))
		self.CType4.sort(key=lambda x: (x.antecedent.role.name, x.antecedent.concept.name, x.consequent.name))

		self.hasRun = True
		
	def makeCTypeNull(self,i):
		""" C ⊑ C """
		cs = ConceptStatement(len(self.CTypeNull),True,Concept(i,[0]),Concept(i,[0]))
		cs.complete('⊑')
		self.CTypeNull.append(cs)
			
	def genERateSequence(self,i):
		j = 20 * i
		k = 20 * i
		self.genERateFirstPart(j,k)
		j = j + 1
		k = k + 2
		self.genERateSecondPart(j,k)
		k = k + 1
		j = j + 6
		self.genERateThirdPart(j,k)
		
	def genERateFirstPart(self,j,k):
		"""(1) 0 ⊑ 1,1 ⊑ 2                         ⊨ 0 ⊑ 2
		   (6) 0 ∘ 1 ⊑ 2, 3 ⊑ 0.4, 4 ⊑ 1.5         ⊨ 3 ⊑ 2.5
		"""
		
		if j == 0:
			cs3 = ConceptStatement(len(self.CType1),True,Concept(j,[0]),Concept(j+1,[0]))
			cs3.complete('⊑')
			self.CType1.append(cs3)
			j = j + 1
			
		cs2 = ConceptStatement(len(self.CType1),True,Concept(j,[0]),Concept(j+1,[0]))
		cs2.complete('⊑')
		self.CType1.append(cs2)
		j = j + 2
		
		rs1 = RoleStatement(len(self.roleChains),True,RoleChain(0,Role(k,[0,1]),Role(k+1,[1,2])),Role(k+2,[0,2]))
		rs1.complete('⊑')
		self.roleChains.append(rs1)
		k = k + 3
					
		cs1 = ConceptStatement(len(self.CType3),True,Concept(j,[0]),ConceptRole('e',Role(k-3,[0,1]),Concept(j+1,[1])))
		cs1.complete('⊑')
		self.CType3.append(cs1)
		j = j + 1
		
		if j == 4:
			cs4 = ConceptStatement(len(self.CType3),True,Concept(j,[0]),ConceptRole('e',Role(k-2,[0,1]),Concept(j+1,[1])))
			cs4.complete('⊑')
			self.CType3.append(cs4)	
		
				
	
	def genERateSecondPart(self,j,k):
		"""
		   (2) 1 ⊓ 2 ⊑ 6, 0 ⊑ 1, 0 ⊑ 2         ⊨ 0 ⊑ 6
		   (5) 2 ⊑ 3, 3 ⊑ 2.5                  ⊨ 3 ⊑ 3.5
		"""
		rs = RoleStatement(len(self.roleSubs),True,Role(k,[0,1]),Role(k+1,[0,1]))
		rs.complete('⊑')
		self.roleSubs.append(rs)
		
		cs1 = ConceptStatement(0,True,Concept(j,[0]),Concept(j+1,[0]))
		cs1.complete('⊓')
		cs2 = ConceptStatement(len(self.CType2),True,cs1,Concept(j+5,[0]))
		cs2.complete('⊑')
		self.CType2.append(cs2)
	
	def genERateThirdPart(self,j,k):
		"""
		   (3) C ⊑ ∃R.D, A ⊑ C                     ⊨ A ⊑ ∃R.D
		   (4) ∃R.C ⊑ D, A ⊑ ∃R.B, B ⊑ C           ⊨ A ⊑ D
		"""
		
		cs1 = ConceptStatement(len(self.CType3),True,ConceptRole('e',Role(k,[0,1]),Concept(j-6,[1])),Concept(j,[0]))
		cs1.complete('⊑')
		self.CType4.append(cs1)	
	
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
		return ""
	
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
	