class Quantifier:
    
    def __init__(self,kind):
        self.quantifier = '∀' if (kind == 'a' or kind == 'A') else ('∃' if (kind == 'e' or kind == 'E') else 'n')
        if self.quantifier == 'n': raise Exception("not a quantifier")
        
    