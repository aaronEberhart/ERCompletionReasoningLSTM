from Predicate import *
import random

class Statement(Concept):
    
    def __init__(self,ID,scope,outer):
        super().__init__(ID,[scope])
        self.antecedent = []
        self.consequent = []
        self.majorOperator = 'X'
        self.outer = outer
        self.size = 0
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
        self.size = self.size + 1
        
    def addToConsequent(self,predicate):
        self.checkStatementPredicate(predicate)
        self.consequent.append(predicate)
        self.size = self.size + 1
        
    def toString(self):
        return "{}{} {} {}{}".format("( " if not self.outer else ""," ".join([item.toString() for item in self.antecedent]),self.majorOperator," ".join([item.toString() for item in self.consequent])," )" if not self.outer else "")
    
class ConceptStatement(Statement):
    
    def __init__(self,ID,scope,outer):
        super().__init__(ID,scope,outer)
    
    def checkConceptStatement(self,concept):
        if not isinstance(concept,Concept) or not concept.terms.getTerm(0) == self.terms.getTerm(0): raise Exception("Invalid ConceptStatement")
    
    def addToAntecedent(self,concept):
        self.checkConceptStatement(concept)
        super().addToAntecedent(concept)
        
    def addToConsequent(self,concept):
        self.checkConceptStatement(concept)
        super().addToConsequent(concept)    
        
class RoleStatement(Statement):
    
    def __init__(self,ID,scope,outer):
        super().__init__(ID,scope,outer)
    
    def checkRoleStatement(self,role):
        if not isinstance(role,Role): raise Exception("Invalid RoleStatement")
    
    def addToAntecedent(self,role):
        self.checkRoleStatement(role)
        super().addToAntecedent(role)
        
    def addToConsequent(self,role):
        if len(self.consequent) == 1: raise Exception("Invalid RoleStatement")
        self.checkRoleStatement(role)
        super().addToConsequent(role)