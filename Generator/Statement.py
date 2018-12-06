from Predicate import *
import random

class Statement(Concept):
    
    def __init__(self,ID,scope):
        super().__init__(ID,[scope])
        self.antecedent = []
        self.consequent = []
        self.majorOperator = 'X'
        random.seed()
    
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
        return "{} {} {}".format(" ".join([item.toString() for item in self.antecedent]),self.majorOperator," ".join([item.toString() for item in self.consequent]))
    
class ConceptStatement(Statement):
    
    def __init__(self,ID,scope):
        super().__init__(ID,scope)
    
    def checkConceptStatement(self,concept):
        if not isinstance(concept,Concept): raise Exception("Invalid Concept")
    
    def addToAntecedent(self,concept):
        self.checkConceptStatement(concept)
        super().addToAntecedent(concept)
        
    def addToConsequent(self,concept):
        self.checkConceptStatement(concept)
        super().addToConsequent(concept)    
        
class RoleStatement(Statement):
    
    def __init__(self,ID,scope):
        super().__init__(ID,scope)
    
    def checkRoleStatement(self,role):
        if not isinstance(role,Role): raise Exception("Invalid Role")
    
    def addToAntecedent(self,role):
        self.checkRoleStatement(role)
        super().addToAntecedent(role)
        
    def addToConsequent(self,role):
        self.checkRoleStatement(role)
        super().addToConsequent(role)