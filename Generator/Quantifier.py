class Quantifier:
    
    def __init__(self,kind):
        self.quantifier = 0 if (kind == 'a' or kind == 'A') else (1 if (kind == 'e' or kind == 'E') else -1)
        self.checkQuantifier()
    
    def checkQuantifier(self):
        if self.quantifier == -1: raise Exception("Invalid Quantifier")
    
    def toString(self):
        return str('∀' if self.quantifier == 0 else '∃')
    
    def toFunctionalSyntax(self):
        return "{}".format("ObjectSomeValuesFrom" if self.quantifier == 1 else "ObjectAllValuesFrom")