from Statement import *
import random

class NegativesGenERator:
    
    def __init__(self,reasonER,numCType1=5,numCType2=5,numCType3=5,numCType4=1,numRoleSub=5,numRoleChains=1):
        self.reasonER = reasonER
        if not self.reasonER.hasRun:
            self.reasonER.ERason()
        self.hasRun = False
        self.CType1 = reasonER.syntheticData.conceptTStatementsType1 + reasonER.knownCType1
        self.CType2 = reasonER.syntheticData.conceptTStatementsType2
        self.CType3 = reasonER.syntheticData.conceptTStatementsType3 + reasonER.knownCType3
        self.CType4 = reasonER.syntheticData.conceptTStatementsType4
        self.allC = self.CType1 + self.CType2 + self.CType3 + self.CType4
        self.roleSubs = reasonER.syntheticData.roleTStatements
        self.roleChains = reasonER.syntheticData.roleChainStatements
        self.allR = []
        self.addNullRs()
        self.allR = self.allR + self.roleChains + self.roleSubs
        self.numCType1 = numCType1
        self.numCType2 = numCType2
        self.numCType3 = numCType3
        self.numCType4 = numCType4
        self.numRoleSub = numRoleSub
        self.numRoleChains = numRoleChains
        self.notCType1 = []
        self.notCType2 = []
        self.notCType3 = []
        self.notCType4 = []
        self.notRoleSubs = []
        self.notRoleChains = []
        
        self.makeNegatives()
        
        
    def makeNegatives(self):
        if self.hasRun: return   
        
        self.genERateConceptStatements()		
        self.genERateRoleStatements()        
        
        self.hasRun = True
    
    def addNullRs(self):
        for statement in self.CType3:
            rs = RoleStatement(len(self.roleSubs),True,Role(statement.consequent[0].role.name,[0,1]),Role(statement.consequent[0].role.name,[0,1]))
            rs.complete('⊑')
            if not self.alreadyGenERated(self.allR,rs):
                self.allR.append(rs)
        for statement in self.CType4:
            rs = RoleStatement(len(self.roleSubs),True,Role(statement.antecedent[0].role.name,[0,1]),Role(statement.antecedent[0].role.name,[0,1]))
            rs.complete('⊑')
            if not self.alreadyGenERated(self.allR,rs):
                self.allR.append(rs)
      
    def genERateConceptStatements(self):
        for i in range(len(self.notCType1),self.numCType1):
            self.makeCType1()
    
        for i in range(len(self.notCType2),self.numCType2):
            self.makeCType2()
            
        for i in range(len(self.notCType3),self.numCType3):
            self.makeCType3()
            
        for i in range(len(self.notCType4),self.numCType4):
            self.makeCType4()
    
    def pickFromKB(self,exType):
        ex = exType[random.randint(0,len(exType)-1)].antecedent[0] if bool(random.getrandbits(1)) else exType[random.randint(0,len(exType)-1)].consequent[0]
        if isinstance(ex,ConceptRole): return ex.concept.name
        elif isinstance(ex,RoleChain): return ex.roles[0].name if bool(random.getrandbits(1)) else ex.roles[1].name        
        elif isinstance(ex,ConceptStatement): return ex.antecedent[0].name if bool(random.getrandbits(1)) else ex.consequent[0].name
        elif isinstance(ex,(Concept,Role)): return ex.name
        else: raise Exception("OOPS")
    
    def makeCType1(self):
        """ C ⊑ D """
        left = self.pickFromKB(self.allC)
        right = self.pickFromKB(self.allC)
        while left == right:
            right = self.pickFromKB(self.allC)   
        cs = ConceptStatement(len(self.CType1),True,Concept(left,[0]),Concept(right,[0]))
        cs.complete('⊑')
        if self.alreadyGenERated(self.CType1+self.notCType1,cs):
            self.makeCType1()
        else:
            self.notCType1.append(cs)

    def makeCType2(self):
        """ C ⊓ D ⊑ E """
        left1 = self.pickFromKB(self.allC)
        left2 = self.pickFromKB(self.allC)
        while left1 == left2:
            left2 = self.pickFromKB(self.allC)
        cs1 = ConceptStatement(0,True,Concept(left1,[0]),Concept(left2,[0]))
        cs1.complete('⊓')
        right = self.pickFromKB(self.allC)
        while left1 == right or right == left2:
            right = self.pickFromKB(self.allC)
        cs = ConceptStatement(len(self.CType2),True,cs1,Concept(right,[0]))
        cs.complete('⊑')
        if self.alreadyGenERated(self.CType2+self.notCType2,cs):
            self.makeCType2()
        else:
            self.notCType2.append(cs)

    def makeCType3(self):
        """ C ⊑ ∃R.D """
        left = self.pickFromKB(self.allC)
        rightC = self.pickFromKB(self.allC)
        rightR = self.pickFromKB(self.allR)
        cs = ConceptStatement(len(self.CType3),True,Concept(left,[0]),ConceptRole('e',Role(rightR,[0,1]),Concept(rightC,[1])))
        cs.complete('⊑')
        if self.alreadyGenERated(self.CType3+self.notCType3,cs):
            self.makeCType3()
        else:
            self.notCType3.append(cs)

    def makeCType4(self):
        """ ∃R.C ⊑ D """
        right = self.pickFromKB(self.allC)
        leftC = self.pickFromKB(self.allC)
        leftR = self.pickFromKB(self.allR)
        cs = ConceptStatement(len(self.CType4),True,ConceptRole('e',Role(leftR,[0,1]),Concept(leftC,[1])),Concept(right,[0]))
        cs.complete('⊑')
        if self.alreadyGenERated(self.notCType4+self.CType4,cs):
            self.makeCType4()
        else:
            self.notCType4.append(cs)
    
    def genERateRoleStatements(self):
        for i in range(len(self.notRoleSubs),self.numRoleSub):
            self.makeRS()
    
        for i in range(len(self.notRoleChains),self.numRoleChains):
            self.makeRC() 
     
    def makeRS(self):
        """ R ⊑ S """
        left = self.pickFromKB(self.allR)
        right = self.pickFromKB(self.allR)
        while left == right:
            right = self.pickFromKB(self.allR)
        rs = RoleStatement(len(self.roleSubs),True,Role(left,[0,1]),Role(right,[0,1]))
        rs.complete('⊑')
        if self.alreadyGenERated(self.roleSubs+self.notRoleSubs,rs):
            self.makeRS()
        else:
            self.notRoleSubs.append(rs)	        
    
    def makeRC(self):
        """ R1 ∘ R2 ⊑ S """
        leftR1 = self.pickFromKB(self.allR)
        leftR2 = self.pickFromKB(self.allR)
        right = self.pickFromKB(self.allR)
        while leftR1 == leftR2:
            leftR2 = self.pickFromKB(self.allR)
        rs = RoleStatement(len(self.roleChains),True,RoleChain(0,Role(leftR1,[0,1]),Role(leftR2,[1,2])),Role(right,[0,2]))
        rs.complete('⊑')
        if self.alreadyGenERated(self.roleChains+self.notRoleChains,rs):
            self.makeRC()
        else:
            self.notRoleChains.append(rs)
    
    def alreadyGenERated(self,listy,y):
        return any(x.equals(y) for x in listy)    
    
    def toString(self):
        ret = self.reasonER.toString()+("\nNegative Examples:\n\n" if self.hasRun else "")
        
        for statement in self.notCType1:
            ret = ret + statement.toString() + "\n"
        for statement in self.notCType2:
            ret = ret + statement.toString() + "\n"
        for statement in self.notCType3:
            ret = ret + statement.toString() + "\n"
        for statement in self.notCType4:
            ret = ret + statement.toString() + "\n"
        for statement in self.notRoleSubs:
            ret = ret + statement.toString() + "\n"
        for statement in self.notRoleChains:
            ret = ret + statement.toString() + "\n"
        
        return ret
            