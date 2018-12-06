from Predicate import *

class Statement:
    
    @abstractmethod
    def __init__(self):
        self.antecedent = []
        self.consequent = []
        self.majorOperator = 'X'
        self.complete = self.isComplete()
    
    def isComplete(self):
        return not self.majorOperator == 'X'
    
    def canComplete(self):
        if self.isComplete(): raise Exception("Already complete")
        return len(self.antecedent) > 0 and len(self.consequent) > 0
    
class ConceptStatement(Statement):
    
    def __init__(self):
        super.__init__(self)
        
class RoleStatement(Statement):
    
    def __init__(self):
        super.__init__(self)