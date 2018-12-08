"""
⊑ ⊓ ⊔ ≡
"""

from Predicate import *

class Statement(Predicate):
    
    def __init__(self,ID,outer=False,*seed):
        self.checkPredicate(ID)
        self.name = ID
        self.antecedent = [] if len(seed) < 1 else seed[0]
        self.consequent = [] if len(seed) < 2 else seed[1]
        self.operator = 'X'
        self.outer = outer
    
    def complete(self,operator):
        self.majorOperator = operator
    
    def isComplete(self):
        return not self.majorOperator == 'X'
    
    def canBeComplete(self):
        return len(self.antecedent) > 0 and len(self.consequent) > 0
    
    def checkStatementPredicate(self,predicate):
        if not isinstance(predicate,Predicate): raise Exception("Invalid Predicate")
    
    def addToAntecedent(self,predicate):
        self.checkStatementPredicate(predicate)
        self.antecedent.append(predicate)
        
    def addToConsequent(self,predicate):
        self.checkStatementPredicate(predicate)
        self.consequent.append(predicate)
        
    def toString(self):
        return "{}{} {} {}{}".format("( " if not self.outer else ""," ".join([item.toString() for item in self.antecedent]),self.operator," ".join([item.toString() for item in self.consequent])," )" if not self.outer else "")
    
class ConceptStatement(Concept):
    
    def __init__(self,ID,outer=False,*seed):
        self.checkPredicate(ID)
        self.name = ID
        self.antecedent = [] if len(seed) < 1 else seed[0]
        self.consequent = [] if len(seed) < 2 else seed[1]
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
        self.operator = operator
    
    def isComplete(self):
        return not self.operator == 'X'
    
    def canBeComplete(self):
        return len(self.antecedent) > 0 and len(self.consequent) > 0   
    
    def toString(self):
        return "{}{} {} {}{}".format("( " if not self.outer else ""," ".join([item.toString() for item in self.antecedent]),self.operator," ".join([item.toString() for item in self.consequent])," )" if not self.outer else "")
    
        
class RoleStatement(Role):
    
    def __init__(self,ID,outer=False,*seed):
        self.checkPredicate(ID)
        self.name = ID
        self.antecedent = [] if len(seed) < 1 else seed[0]
        self.consequent = [] if len(seed) < 2 else seed[1]
        self.operator = 'X'
        self.outer = outer
    
    def checkRoleStatement(self,role):
        if not isinstance(role,Role): raise Exception("Invalid RoleStatement")
    
    def addToAntecedent(self,role):
        self.checkRoleStatement(role)
        self.antecedent.append(concept)
        if self.terms == None: self.setScope()
        
    def addToConsequent(self,role):
        if len(self.consequent) == 1 or isinstance(role, RoleStatement): raise Exception("Invalid RoleStatement")
        self.checkRoleStatement(role)
        self.consequent.append(role)
        if self.terms == None: self.setScope()
        
    def complete(self,operator):
        self.operator = operator
    
    def isComplete(self):
        return not self.operator == 'X'
    
    def canBeComplete(self):
        return len(self.antecedent) > 0 and len(self.consequent) > 0   
    
    def toString(self):
        return "{}{} {} {}{}".format("( " if not self.outer else ""," ".join([item.toString() for item in self.antecedent]),self.operator," ".join([item.toString() for item in self.consequent])," )" if not self.outer else "")
    
    def setScope(self):
        self.terms = None if len(self.antecedent) == 0 and len(self.consequent) == 0 else (Terms([self.antecedent[0].terms.getTerm(0),self.antecedent[0].terms.getTerm(1)]) if len(self.antecedent) > 0 else Terms([self.consequent[0].terms.getTerm(0),self.consequent[0].terms.getTerm(1)]))
    