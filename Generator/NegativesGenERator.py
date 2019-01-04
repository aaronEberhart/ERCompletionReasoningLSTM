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
        self.roleSubs = reasonER.syntheticData.roleTStatements
        self.roleChains = reasonER.syntheticData.roleChainStatements
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
        
    def genERateConceptStatements(self):
        for i in range(len(self.notCType1),self.numCType1):
            self.makeCType1()
    
        for i in range(len(self.notCType2),self.numCType2):
            self.makeCType2()
            
        for i in range(len(self.notCType3),self.numCType3):
            self.makeCType3()
            
        for i in range(len(self.notCType4),self.numCType4):
            self.makeCType4()
    
    def makeCType1(self):
        pass
    
    def makeCType2(self):
        pass
    
    def makeCType3(self):
        pass
        
    def makeCType4(self):
        pass
    
    def genERateRoleStatements(self):
        for i in range(len(self.notRoleSubs),self.numRoleSub):
            self.makeRS()
    
        for i in range(len(self.notRoleChains),self.numRoleChains):
            self.makeRC() 
            
    def makeRS(self):
        pass
    
    def makeRC(self):
        pass
    
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
            