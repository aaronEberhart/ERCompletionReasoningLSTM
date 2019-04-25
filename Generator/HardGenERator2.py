from Statement import *
from GenERator import *

"""
Completion rules:

(1) C ⊑ D,A ⊑ C                         ⊨ A ⊑ D

(2) C1 ⊓ C2 ⊑ D, A ⊑ C1, A ⊑ C2         ⊨ A ⊑ D
    uses Null
(3) C ⊑ ∃R.D, A ⊑ C                     ⊨ A ⊑ ∃R.D

(4) ∃R.C ⊑ D, A ⊑ ∃R.B, B ⊑ C           ⊨ A ⊑ D
    uses Null
(5) R ⊑ S, A ⊑ ∃R.B                     ⊨ A ⊑ ∃S.B

(6) R1 ∘ R2 ⊑ R, A ⊑ ∃R1.B, B ⊑ ∃R2.C   ⊨ A ⊑ ∃R.C

"""

class HardGenERator2:

    def __init__(self,rGenerator=GenERator(),difficulty=50):        
        self.conceptNamespace = (difficulty * 3) + 2
        self.roleNamespace = self.conceptNamespace - 1
        self.hConceptNamespace = (difficulty * 3) + 2
        self.hRoleNamespace = self.conceptNamespace - 1		
        self.rGenerator = rGenerator
        if rGenerator != None and not self.rGenerator.hasRun: 
                self.rGenerator.genERate()
                if self.keepTrying(self.rGenerator.CType1,self.rGenerator.conceptNamespace-1): 
                    self.rGenerator.CType1[0].consequent.name = self.rGenerator.conceptNamespace-1
                    if self.rGenerator.CType1[0].antecedent.name == self.rGenerator.CType1[0].consequent.name: self.rGenerator.CType1[0].antecedent.name = random.randint(0,self.conceptNamespace-2)
        self.seed = "N/A" if rGenerator == None else self.rGenerator.seed
        self.CTypeNull = []
        self.CType1 = []
        self.CType2 = []
        self.CType3 = []
        self.CType4 = []
        self.roleSubs = []
        self.roleChains = []
        self.difficulty = difficulty
        self.hasRun = False

    def keepTrying(self,listy,y):
        return not any(x.consequent.name == y for x in listy)

    def shiftSGenerator(self):
        for x in self.CTypeNull:
            x.antecedent.name = x.antecedent.name + self.rGenerator.conceptNamespace - 2
            x.consequent.name = x.consequent.name + self.rGenerator.conceptNamespace - 2
        for x in self.CType1:
            x.antecedent.name = x.antecedent.name + self.rGenerator.conceptNamespace - 2
            x.consequent.name = x.consequent.name + self.rGenerator.conceptNamespace - 2
        for x in self.CType2:
            x.antecedent.antecedent.name = x.antecedent.antecedent.name + self.rGenerator.conceptNamespace - 2
            x.antecedent.consequent.name = x.antecedent.consequent.name + self.rGenerator.conceptNamespace - 2
            x.consequent.name = x.consequent.name + self.rGenerator.conceptNamespace - 2
        for x in self.CType3:
            x.antecedent.name = x.antecedent.name + self.rGenerator.conceptNamespace - 2
            x.consequent.role.name = x.consequent.role.name + self.rGenerator.roleNamespace-1
            x.consequent.concept.name = x.consequent.concept.name + self.rGenerator.conceptNamespace - 2
        for x in self.CType4:
            x.antecedent.role.name = x.antecedent.role.name + self.rGenerator.roleNamespace-1
            x.antecedent.concept.name = x.antecedent.concept.name + self.rGenerator.conceptNamespace - 2
            x.consequent.name = x.consequent.name + self.rGenerator.conceptNamespace - 2
        for x in self.roleSubs:
            x.antecedent.name = x.antecedent.name + self.rGenerator.roleNamespace-1
            x.consequent.name = x.consequent.name + self.rGenerator.roleNamespace-1
        for x in self.roleChains:
            x.antecedent.roles[0].name = x.antecedent.roles[0].name + self.rGenerator.roleNamespace-1
            x.antecedent.roles[1].name = x.antecedent.roles[1].name + self.rGenerator.roleNamespace-1
            x.consequent.name = x.consequent.name + self.rGenerator.roleNamespace-1

    def spliceGenERators(self):
        self.conceptNamespace = self.conceptNamespace + self.rGenerator.conceptNamespace - 2
        self.roleNamespace = self.roleNamespace + self.rGenerator.roleNamespace -  1
        self.CTypeNull = self.CTypeNull + self.rGenerator.CTypeNull    
        self.CType1 = self.CType1 + self.rGenerator.CType1
        self.CType2 = self.CType2 + self.rGenerator.CType2
        self.CType3 = self.CType3 + self.rGenerator.CType3
        self.CType4 = self.CType4 + self.rGenerator.CType4
        self.roleSubs = self.roleSubs + self.rGenerator.roleSubs
        self.roleChains = self.roleChains + self.rGenerator.roleChains	

    def genERate(self):
        
        if self.hasRun: return
        
        self.setup()

        for i in range(2,self.conceptNamespace+1):
            self.makeCTypeNull(i)

        for i in range(0,self.difficulty):
            self.unwantedDeductions(i*3)
            self.genERateSequence(i)    
        
        if self.rGenerator != None: 
            self.shiftSGenerator() 
            self.spliceGenERators()              

        self.CTypeNull.sort(key=lambda x: (x.antecedent.name, x.consequent.name))            
        self.CType1.sort(key=lambda x: (x.antecedent.name, x.consequent.name))
        self.CType2.sort(key=lambda x: (x.antecedent.antecedent.name, x.antecedent.consequent.name, x.consequent.name))
        self.CType3.sort(key=lambda x: (x.antecedent.name, x.consequent.role.name, x.consequent.concept.name))
        self.CType4.sort(key=lambda x: (x.antecedent.role.name, x.antecedent.concept.name, x.consequent.name))

        self.hasRun = True

    def unwantedDeductions(self,i):
        cs = ConceptStatement(len(self.CType4),True,Concept(i+2,[0]),ConceptRole('e',Role(i+2,[0,1]),Concept(i+3,[1])))
        cs.complete('⊑')
        self.CType3.append(cs)

        cs = ConceptStatement(len(self.CType4),True,Concept(1,[0]),ConceptRole('e',Role(i+2,[0,1]),Concept(i+3,[1])))
        cs.complete('⊑')
        self.CType3.append(cs)

        cs = ConceptStatement(len(self.CType4),True,Concept(1,[0]),ConceptRole('e',Role(i+3,[0,1]),Concept(i+4,[1])))
        cs.complete('⊑')
        self.CType3.append(cs)

    def setup(self):	
        """seed"""
        cs1 = ConceptStatement(len(self.CType1),True,Concept(1,[0]),Concept(2,[0]))
        cs1.complete('⊑')
        self.CType1.append(cs1)

        """only need 1 for whole KB"""
        cs = ConceptStatement(len(self.CType3),True,Concept(1,[0]),ConceptRole('e',Role(1,[0,1]),Concept(1,[1])))
        cs.complete('⊑')
        self.CType3.append(cs)

    def makeCTypeNull(self,i):
        """ C ⊑ C """
        cs = ConceptStatement(len(self.CTypeNull),True,Concept(i,[0]),Concept(i,[0]))
        cs.complete('⊑')
        self.CTypeNull.append(cs)

    def genERateSequence(self,i):
        j = (i * 3)
        self.genERateFirstPart(j)
        self.genERateSecondPart(j)

    def genERateFirstPart(self,j):
        cs = ConceptStatement(len(self.CType4),True,ConceptRole('e',Role(1,[0,1]),Concept(j+2,[1])),Concept(j+4,[0]))
        cs.complete('⊑')
        self.CType4.append(cs)

        cs1 = ConceptStatement(len(self.CType1),True,Concept(j+2,[0]),Concept(j+3,[0]))
        cs1.complete('⊑')
        self.CType1.append(cs1)

        cs1 = ConceptStatement(0,True,Concept(j+3,[0]),Concept(j+4,[0]))
        cs1.complete('⊓')
        cs = ConceptStatement(len(self.CType2),True,cs1,Concept(j+5,[0]))
        cs.complete('⊑')
        self.CType2.append(cs)

    def genERateSecondPart(self,j):
        cs = ConceptStatement(len(self.CType4),True,Concept(j+2,[0]),ConceptRole('e',Role(j+1,[0,1]),Concept(j+3,[1])))
        cs.complete('⊑')
        self.CType3.append(cs)

        cs = ConceptStatement(len(self.CType4),True,Concept(j+1,[0]),ConceptRole('e',Role(j+3,[0,1]),Concept(j+4,[1])))
        cs.complete('⊑')
        self.CType3.append(cs)

        rs = RoleStatement(len(self.roleChains),True,RoleChain(0,Role(j+1,[0,1]),Role(j+3,[1,2])),Role(j+4,[0,2]))
        rs.complete('⊑')
        self.roleChains.append(rs)

        rs = RoleStatement(len(self.roleSubs),True,Role(j+1,[0,1]),Role(j+2,[0,1]))
        rs.complete('⊑')
        self.roleSubs.append(rs)

    def toString(self):
        ret = "Original KB"
        for statement in self.CTypeNull:
            ret = ret + "\n" + statement.toString()
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
    
    def toStringFile(self,filename):
        file = open(filename,"w")
        file.write("KB")
        for statement in self.CTypeNull:
            file.write("\n{}".format(statement.toString()))
        for statement in self.CType1:
            file.write("\n{}".format(statement.toString()))
        for statement in self.CType2:
            file.write("\n{}".format(statement.toString()))
        for statement in self.CType3:
            file.write("\n{}".format(statement.toString()))
        for statement in self.CType4:
            file.write("\n{}".format(statement.toString()))
        for statement in self.roleSubs:
            file.write("\n{}".format(statement.toString()))
        for statement in self.roleChains:
            file.write("\n{}".format(statement.toString()))
        file.close()  

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
    
    def toFunctionalSyntaxFile(self,IRI,filename): 
        file = open(filename,"w")
        file.write("Prefix(:="+IRI+")\nPrefix(owl:=<http://www.w3.org/2002/07/owl#>)\nOntology( "+IRI+"\n\n")
        for i in range(0,self.conceptNamespace):
            file.write("Declaration( Class( :C{} ) )\n".format(i))
        for i in range(0,self.roleNamespace):
            file.write("Declaration( ObjectProperty( :R{} ) )\n".format(i))        
        for statement in self.CType1:
            file.write(statement.toFunctionalSyntax())
        for statement in self.CType2:
            file.write(statement.toFunctionalSyntax())
        for statement in self.CType3:
            file.write(statement.toFunctionalSyntax())
        for statement in self.CType4:
            file.write(statement.toFunctionalSyntax())	
        for statement in self.roleSubs:
            file.write(statement.toFunctionalSyntax())
        for statement in self.roleChains:
            file.write(statement.toFunctionalSyntax())  
        file.write("\n\n)")
        file.close()         

    def toVector(self):
        vec = []
        for statement in self.CType1:
            vec.append(statement.toVector(self.conceptNamespace,self.roleNamespace))
        for statement in self.CType2:
            vec.append(statement.toVector(self.conceptNamespace,self.roleNamespace))
        for statement in self.CType3:
            vec.append(statement.toVector(self.conceptNamespace,self.roleNamespace))
        for statement in self.CType4:
            vec.append(statement.toVector(self.conceptNamespace,self.roleNamespace))	
        for statement in self.roleSubs:
            vec.append(statement.toVector(self.conceptNamespace,self.roleNamespace))
        for statement in self.roleChains:
            vec.append(statement.toVector(self.conceptNamespace,self.roleNamespace))	
        return vec        

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

    def alreadyKnown(self,statements,s):
        return any(x.equals(s) for x in statements) 
    
    def getAllExpressions(self):
        return [self.CType1,self.CType2,self.CType3,self.CType4,self.roleSubs,self.roleChains]
