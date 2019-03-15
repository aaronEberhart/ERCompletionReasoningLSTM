from Statement import *

"""
Completion rules:

(1) C ⊑ D,A ⊑ C                         ⊨ A ⊑ D    2

(2) C1 ⊓ C2 ⊑ D, A ⊑ C1, A ⊑ C2         ⊨ A ⊑ D    3
    uses Null
(3) C ⊑ ∃R.D, A ⊑ C                     ⊨ A ⊑ ∃R.D 2

(4) ∃R.C ⊑ D, A ⊑ ∃R.B, B ⊑ C           ⊨ A ⊑ D    3
    uses Null
(5) R ⊑ S, A ⊑ ∃R.B                     ⊨ A ⊑ ∃S.B 2

(6) R1 ∘ R2 ⊑ R, A ⊑ ∃R1.B, B ⊑ ∃R2.C   ⊨ A ⊑ ∃R.C 3

"""

class DependencyReducer:
    
    def __init__(self,kbTerms,*logs):
        self.kb = kbTerms
        self.rawlogs = [x for x in logs]
        self.donelogs = []
        self.reduceLogs()
        
    def reduceLogs(self):
        for iterLog in self.rawlogs:
            thisIter = []
            for logType in iterLog:
                thisType = []
                for log in logType:
                    for i in range(0,len(log[2])):
                        if not self.inKB(self.determineType(log[2][i]),log[2][i]):
                            print(log[2][i].toString())                            
                            x = self.fixTerm(log[2][i],thisType,thisIter)
                            log[2].remove(log[2][i])
                            log[2] = log[2] + x
                            print(log[2][i].toString())
                    thisType.append(log)
                thisIter.append(thisType)
            self.donelogs.append(thisIter)
    
    def determineType(self,term):
        if isinstance(term.antecedent,RoleChain): return 5
        elif isinstance(term.consequent,Role): return 4
        elif isinstance(term.antecedent,ConceptRole): return 3
        elif isinstance(term.consequent,ConceptRole): return 2
        elif isinstance(term.antecedent,ConceptStatement): return 1
        else: return 0
           
    def inKB(self,termType,term):
        if termType == 0 and term.antecedent.name == term.consequent.name: return True
        return term in self.kb[termType]

    def fixTerm(self,term,thisType,thisIter):
        for log in thisType:
            if log[0].toString() == term.toString():
                return log[2]
        for logType in thisIter:
            for log in logType:
                if log[0].toString() == term.toString():
                    return log[2]           
        for iterLog in self.donelogs:
            for logType in iterLog:
                for log in logType:
                    if log[0].toString() == term.toString():
                        return log[2]
        raise Exception("BAH")
    
    def toString(self,rules):
        return "\n".join(["{}: ({}){}".format(rule[0].toString(),str(rule[1]),",".join([x.toString() for x in rule[2]])) for rule in rules])
        