from Predicate import *
   
class ConceptStatement(Concept):
    
    def __init__(self,ID,outer=False,*seed):
        self.checkPredicate(ID)
        self.name = ID
        self.antecedent = []
        self.consequent = []
        self.terms = None
        if len(seed) > 0: 
            self.addToAntecedent(seed[0])
        if len(seed) > 1:
            self.addToConsequent(seed[1])
        self.operator = 'X'
        self.outer = outer
        self.setScope()
    
    def setScope(self):
        self.terms = None if len(self.antecedent) == 0 and len(self.consequent) == 0 else (Terms([self.antecedent[0].terms.getTerm(0)]) if len(self.antecedent) > 0 else Terms([self.consequent[0].terms.getTerm(0)]))
    
    def checkConceptStatement(self,concept):
        if not isinstance(concept,Concept) or not (self.terms == None or concept.terms.getTerm(0) == self.terms.getTerm(0)): raise Exception("Invalid ConceptStatement")
    
    def addToAntecedent(self,concept):
        self.checkConceptStatement(concept)
        self.antecedent.append(concept)
        if self.terms == None: self.setScope()
        
    def addToConsequent(self,concept):
        self.checkConceptStatement(concept)
        self.consequent.append(concept)
        if self.terms == None: self.setScope()
        
    def complete(self,operator):
        self.checkCanBeComplete()
        self.operator = operator
    
    def isComplete(self):
        return not self.operator == 'X'
    
    def checkCanBeComplete(self):
        if self.antecedent == None or not len(self.antecedent) > 0 or self.consequent == None or not len(self.consequent) > 0 or (isinstance(self.antecedent[0],ConceptStatement) and not self.antecedent[0].isComplete()) or (isinstance(self.consequent[0],ConceptStatement) and not self.consequent[0].isComplete()): raise Exception("Not complete yet") 
    
    def toString(self):
        return "{}{} {} {}{}".format("( " if not self.outer else ""," ".join([item.toString() for item in self.antecedent]),self.operator," ".join([item.toString() for item in self.consequent])," )" if not self.outer else "")
    
        
class RoleStatement(Role):
    
    def __init__(self,ID,outer=False,*seed):
        self.checkPredicate(ID)
        self.name = ID
        self.antecedent = []
        self.consequent = []
        self.terms = None
        if len(seed) > 0: 
            self.addToAntecedent(seed[0])
        if len(seed) > 1:
            self.addToConsequent(seed[1])
        self.operator = 'X'
        self.outer = outer
        self.setScope()
    
    def checkRoleStatement(self,role):
        if not isinstance(role,Role) or (self.terms != None and (role.terms.getTerm(0) != self.terms.getTerm(0) or role.terms.getTerm(1) != self.terms.getTerm(1))): raise Exception("Invalid RoleStatement")
    
    def addToAntecedent(self,role):
        if len(self.antecedent) > 0 and not isinstance(self.antecedent[0],RoleChain): 
            self.antecedent[0] = RoleChain(role.name,self.antecedent[0])
            if len(self.consequent) > 0 and isinstance(self.consequent[0],RoleChain):
                self.antecedent[0].terms.setTerm(1,self.consequent[0].roles[len(self.consequent[0].roles) - 1].terms.getTerm(0))
        if len(self.antecedent) == 1:
            if self.consequent != None and not isinstance(self.consequent[0],RoleChain):
                self.consequent[0].terms.setTerm(1,role.terms.getTerm(1))            
            if role.terms.getTerm(1) != self.terms.getTerm(1): 
                self.terms.setTerm(1,role.terms.getTerm(1))
            self.antecedent[0].appendRoles([role])
        else:
            self.checkRoleStatement(role)
            self.antecedent.append(role)
        if self.terms == None: self.setScope()
        
    def addToConsequent(self,role):
        if len(self.consequent) > 0 and not isinstance(self.consequent[0],RoleChain): 
            self.consequent[0] = RoleChain(role.name,self.consequent[0])
            if len(self.antecedent) > 0 and isinstance(self.antecedent[0],RoleChain):
                self.consequent[0].terms.setTerm(1,self.antecedent[0].roles[len(self.antecedent[0].roles) - 1].terms.getTerm(0))            
        if len(self.consequent) == 1:
            if self.antecedent != None and not isinstance(self.antecedent[0],RoleChain):
                self.antecedent[0].terms.setTerm(1,role.terms.getTerm(1))
            if role.terms.getTerm(1) != self.terms.getTerm(1): 
                self.terms.setTerm(1,role.terms.getTerm(1))
            self.consequent[0].appendRoles([role])
        else:
            self.checkRoleStatement(role)
            self.consequent.append(role)
        if self.terms == None: self.setScope()            
        
    def complete(self,operator):
        self.checkCanBeComplete()
        self.checkTermsSame()
        self.operator = operator
    
    def checkTermsSame(self):
        for i in range(0,len(self.terms.getTerms())):
            if self.terms.getTerm(i) != self.antecedent[0].terms.getTerm(i) or self.terms.getTerm(i) != self.consequent[0].terms.getTerm(i): raise Exception("Roles do not match")
        
    def isComplete(self):
        return not self.operator == 'X'
    
    def checkCanBeComplete(self):
        if not len(self.antecedent) > 0 or not len(self.consequent) > 0: raise Exception("Not complete yet") 
    
    def toString(self):
        return "{}{} {} {}{}".format("( " if not self.outer else ""," ".join([item.toString() for item in self.antecedent]),self.operator," ".join([item.toString() for item in self.consequent])," )" if not self.outer else "")
    
    def setScope(self):
        self.terms = None if len(self.antecedent) == 0 and len(self.consequent) == 0 else (Terms([self.antecedent[0].terms.getTerm(0),self.antecedent[0].terms.getTerm(1)]) if len(self.antecedent) > 0 else Terms([self.consequent[0].terms.getTerm(0),self.consequent[0].terms.getTerm(1)]))
    