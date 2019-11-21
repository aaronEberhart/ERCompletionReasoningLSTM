from Predicate import *
   
class ConceptStatement(Concept):
    
    def __init__(self,ID,outer=False,*seed):
        self.checkPredicate(ID)
        self.name = ID
        self.antecedent = None
        self.consequent = None
        self.terms = None
        if len(seed) > 0: 
            self.addToAntecedent(seed[0])
        if len(seed) > 1:
            self.addToConsequent(seed[1])
        self.operator = 'X'
        self.outer = outer
        self.setScope()
    
    def setScope(self):
        self.terms = None if self.antecedent == None and self.consequent == None else (Terms([self.antecedent.terms.getTerm(0)]) if self.antecedent != None else Terms([self.consequent.terms.getTerm(0)]))
    
    def checkConceptStatement(self,concept):
        if not isinstance(concept,Concept) or not (self.terms == None or concept.terms.getTerm(0) == self.terms.getTerm(0)): raise Exception("Invalid ConceptStatement")
    
    def addToAntecedent(self,concept):
        self.checkConceptStatement(concept)
        self.antecedent = concept
        if self.terms == None: self.setScope()
        
    def addToConsequent(self,concept):
        self.checkConceptStatement(concept)
        self.consequent = concept
        if self.terms == None: self.setScope()
        
    def complete(self,operator):
        self.checkCanBeComplete()
        self.operator = operator
    
    def isComplete(self):
        return not self.operator == 'X'
    
    def checkCanBeComplete(self):
        if self.antecedent == None or self.consequent == None or (isinstance(self.antecedent,ConceptStatement) and not self.antecedent.isComplete()) or (isinstance(self.consequent,ConceptStatement) and not self.consequent.isComplete()): raise Exception("Not complete yet") 
    
    def equals(self,other):
        return self.operator == other.operator and self.antecedent.equals(other.antecedent) and self.consequent.equals(other.consequent)
    
    def toString(self):
        return "{}{} {} {}{}".format("( " if not self.outer else "",self.antecedent.toString(),self.operator,self.consequent.toString()," )" if not self.outer else "")
    
    def toFunctionalSyntax(self):
        return "{}( {} {} )".format("SubClassOf" if self.operator == "⊑" else ("ObjectIntersectionOf" if self.operator == "⊓" else "ObjectUnionOf"), self.antecedent.toFunctionalSyntax(),self.consequent.toFunctionalSyntax())
    
    def toVector(self,concepts,roles):
        if isinstance(self.antecedent,ConceptRole):
            return [self.antecedent.role.toVector()/roles, self.antecedent.concept.toVector()/concepts, self.consequent.toVector()/concepts, 0.0]
        elif isinstance(self.consequent,ConceptRole):
            return [0.0, self.antecedent.toVector()/concepts, self.consequent.role.toVector()/roles, self.consequent.concept.toVector()/concepts]
        elif isinstance(self.antecedent,ConceptStatement):
            return [self.antecedent.antecedent.toVector()/concepts, self.antecedent.consequent.toVector()/concepts, self.consequent.toVector()/concepts, 0.0]
        else:
            return [0.0, self.antecedent.toVector()/concepts, self.consequent.toVector()/concepts, 0.0]
    
    def copy(self):
        if isinstance(self.antecedent,ConceptRole):
            cs = ConceptStatement(self.name,True,ConceptRole('e',Role(self.antecedent.role.name,[0,1]),Concept(self.antecedent.concept.name,[1])),Concept(self.consequent.name,[0]))
        elif isinstance(self.consequent,ConceptRole):
            cs = ConceptStatement(self.name,True,Concept(self.antecedent.name,[0]),ConceptRole('e',Role(self.consequent.role.name,[0,1]),Concept(self.consequent.concept.name,[1])))
        elif isinstance(self.antecedent,ConceptStatement):
            cs1 = ConceptStatement(1,True,Concept(self.antecedent.antecedent.name,[0]),Concept(self.antecedent.consequent.name,[0]))
            cs1.complete('⊓')    
            cs = ConceptStatement(self.name,True,cs1,Concept(self.consequent.name,[0]))
        else:
            cs = ConceptStatement(self.name,True,Concept(self.antecedent.name,[0]),Concept(self.consequent.name,[0]))
            
        cs.complete('⊑')
        return cs       
        
class RoleStatement(Role):
    
    def __init__(self,ID,outer=False,*seed):
        self.checkPredicate(ID)
        self.name = ID
        self.antecedent = None
        self.consequent = None
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
        if self.antecedent != None and not isinstance(self.antecedent,RoleChain): 
            self.antecedent = RoleChain(role.name,self.antecedent)
            if self.consequent != None and isinstance(self.consequent,RoleChain):
                self.antecedent.terms.setTerm(1,self.consequent.roles[len(self.consequent.roles) - 1].terms.getTerm(0))
        if isinstance(self.antecedent,Role):
            if self.consequent != None and not isinstance(self.consequent,RoleChain):
                self.consequent.terms.setTerm(1,role.terms.getTerm(1))            
            if role.terms.getTerm(1) != self.terms.getTerm(1): 
                self.terms.setTerm(1,role.terms.getTerm(1))
            self.antecedent.appendRoles([role])
        else:
            self.checkRoleStatement(role)
            self.antecedent = role
        if self.terms == None: self.setScope()
        
    def addToConsequent(self,role):
        if self.consequent != None and not isinstance(self.consequent,RoleChain): 
            self.consequent = RoleChain(role.name,self.consequent)
            if self.antecedent != None and isinstance(self.antecedent,RoleChain):
                self.consequent.terms.setTerm(1,self.antecedent.roles[len(self.antecedent[0].roles) - 1].terms.getTerm(0))            
        if isinstance(self.consequent,Role):
            if self.antecedent != None and not isinstance(self.antecedent,RoleChain):
                self.antecedent.terms.setTerm(1,role.terms.getTerm(1))
            if role.terms.getTerm(1) != self.terms.getTerm(1): 
                self.terms.setTerm(1,role.terms.getTerm(1))
            self.consequent.appendRoles([role])
        else:
            self.checkRoleStatement(role)
            self.consequent = role
        if self.terms == None: self.setScope()            
        
    def complete(self,operator):
        self.checkCanBeComplete()
        self.checkTermsSame()
        self.operator = operator
    
    def checkTermsSame(self):
        for i in range(0,len(self.terms.getTerms())):
            if self.terms.getTerm(i) != self.antecedent.terms.getTerm(i) or self.terms.getTerm(i) != self.consequent.terms.getTerm(i): raise Exception("Roles do not match")
        
    def isComplete(self):
        return not self.operator == 'X'
    
    def checkCanBeComplete(self):
        if self.antecedent == None or self.consequent== None: raise Exception("Not complete yet") 
        
    def equals(self,other):
        return self.operator == other.operator and self.antecedent.equals(other.antecedent) and self.consequent.equals(other.consequent)
    
    def toString(self):
        return "{}{} {} {}{}".format("( " if not self.outer else "",self.antecedent.toString(),self.operator,self.consequent.toString()," )" if not self.outer else "")
    
    def setScope(self):
        self.terms = None if self.antecedent == None and self.consequent == None else (Terms([self.antecedent.terms.getTerm(0),self.antecedent.terms.getTerm(1)]) if self.antecedent != None else Terms([self.consequent.terms.getTerm(0),self.consequent.terms.getTerm(1)]))
    
    def toFunctionalSyntax(self):
        return "SubObjectPropertyOf( {} {} )".format(self.antecedent.toFunctionalSyntax(),self.consequent.toFunctionalSyntax())   
    
    def toVector(self,concepts,roles):
        if isinstance(self.antecedent,RoleChain):
            return [self.antecedent.roles[0].toVector()/roles, self.antecedent.roles[1].toVector()/roles, self.consequent.toVector()/roles, 0.0]
        else:
            return [0.0, self.antecedent.toVector()/roles, self.consequent.toVector()/roles, 0.0]
        
    def copy(self):
        if isinstance(self.antecedent,RoleChain):
            rs = RoleStatement(self.name,True,RoleChain(0,Role(self.antecedent.roles[0].name,[0,1]),Role(self.antecedent.roles[1].name,[1,2])),Role(self.consequent.name,[0,2]))
        else:
            rs = RoleStatement(self.name,True,Role(self.antecedent.name,[0,1]),Role(self.consequent.name,[0,1]))
        
        rs.complete('⊑')
        return rs