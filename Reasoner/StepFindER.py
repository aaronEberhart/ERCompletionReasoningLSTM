class StepFindER:
    
    def __init__(self,reasonER):
        if not reasonER.hasRun:
            reasonER.ERason()
        self.newType1 = [[x,[]] for x in reasonER.knownCType1]
        self.newType3 = [[x,[]] for x in reasonER.knownCType3]
        self.nullType = reasonER.syntheticData.CTypeNull
        self.allType1 = reasonER.knownCType1 + reasonER.syntheticData.CType1
        self.allType2 = reasonER.syntheticData.CType2
        self.allType3 = reasonER.knownCType3 + reasonER.syntheticData.CType3
        self.allType4 = reasonER.syntheticData.CType4
        self.allRoles = reasonER.syntheticData.roleSubs
        self.allChain = reasonER.syntheticData.roleChains
        
        self.findSteps()
        
    def findSteps(self):
        self.findStepsType1()
        self.findStepsType3()
    
    def findStepsType1(self):
        for statement in self.newType1:
            statement[1] = self.findMatchesRule1(statement[0]) + self.findMatchesRule2(statement[0]) + self.findMatchesRule4(statement[0])
            if len(statement[1])==0:raise Exception("OOPS")
    
    def findMatchesRule1(self,statement):
        """ C ⊑ D,A ⊑ C |= A ⊑ D """
        matches = []
        for candidate1 in list(filter(lambda x: statement.consequent.name == x.consequent.name,self.allType1)):
            for candidate2 in list(filter(lambda x: statement.antecedent.name == x.antecedent.name and x.consequent.name == candidate1.antecedent.name,self.allType1)):
                matches.append("(1){},{}".format(candidate2.toString(),candidate1.toString()))
        return matches
    
    def findMatchesRule2(self,statement):
        """ C1 ⊓ C2 ⊑ D, A ⊑ C1, A ⊑ C2 |= A ⊑ D """
        matches = []
        for candidate1 in list(filter(lambda x: statement.consequent.name == x.consequent.name,self.allType2)):
            for candidate2 in list(filter(lambda x: statement.antecedent.name == x.antecedent.name and x.consequent.name == candidate1.antecedent.antecedent.name,self.allType1+self.nullType)):
                for candidate3 in list(filter(lambda x: statement.antecedent.name == x.antecedent.name and x.consequent.name == candidate1.antecedent.consequent.name,self.allType1+self.nullType)):
                    matches.append("(2){},{},{}".format(candidate2.toString(),candidate3.toString(),candidate1.toString()))
        return matches
    
    def findMatchesRule4(self,statement):
        """ ∃R.C ⊑ D, A ⊑ ∃R.B, B ⊑ C |= A ⊑ D """
        matches = []
        for candidate1 in list(filter(lambda x: statement.consequent.name == x.consequent.name,self.allType4)):
            for candidate2 in list(filter(lambda x: statement.antecedent.name == x.antecedent.name, self.allType3)):
                for candidate3 in list(filter(lambda x: x.antecedent.name == candidate2.consequent.concept.name and x.consequent.name == candidate1.antecedent.concept.name,self.allType1+self.nullType)):
                    matches.append("(4){},{},{}".format(candidate2.toString(),candidate3.toString(),candidate1.toString()))
        return matches
    
    def findStepsType3(self):
        for statement in self.newType3:
            statement[1] = self.findMatchesRule3(statement[0]) + self.findMatchesRule5(statement[0]) + self.findMatchesRule6(statement[0])
            if len(statement[1])==0:raise Exception("OOPS")
    
    def findMatchesRule3(self,statement):
        """ C ⊑ ∃R.D, A ⊑ C |= A ⊑ ∃R.D """
        matches = []
        for candidate1 in list(filter(lambda x: statement.antecedent.name != x.antecedent.name and statement.consequent.role.name == x.consequent.role.name and statement.consequent.concept.name == x.consequent.concept.name,self.allType3)):
            for candidate2 in list(filter(lambda x: x.antecedent.name == statement.antecedent.name and x.consequent.name == candidate1.antecedent.name,self.allType1)):
                matches.append("(3){},{}".format(candidate2.toString(),candidate1.toString()))
        return matches
    
    def findMatchesRule5(self,statement):
        """ R ⊑ S, A ⊑ ∃R.B |= A ⊑ ∃S.B """
        matches = []
        for candidate1 in list(filter(lambda x: statement.consequent.role.name == x.consequent.name,self.allRoles)):
            for candidate2 in list(filter(lambda x: statement.antecedent.name == x.antecedent.name and statement.consequent.concept.name == x.consequent.concept.name and x.consequent.role.name == candidate1.antecedent.name,self.allType3)):
                matches.append("(5){},{}".format(candidate2.toString(),candidate1.toString()))
        return matches
    
    def findMatchesRule6(self,statement):
        """ R1 ∘ R2 ⊑ R, A ⊑ ∃R1.B, B ⊑ ∃R2.C |= A ⊑ ∃R.C """
        matches = []
        for candidate1 in list(filter(lambda x: x.consequent.name == statement.consequent.role.name,self.allChain)):
            for candidate2 in list(filter(lambda x: x.consequent.role.name == candidate1.antecedent.roles[0].name and x.antecedent.name == statement.antecedent.name,self.allType3)):
                for candidate3 in list(filter(lambda x: x.antecedent.name == candidate2.consequent.concept.name and x.consequent.role.name == candidate1.antecedent.roles[1].name and x.consequent.concept.name == statement.consequent.concept.name,self.allType3)):
                    matches.append("(6){},{},{}".format(candidate2.toString(),candidate3.toString(),candidate1.toString()))
        return matches
    
    def toString(self):
        ret = "\nExtended KB w/ Justifications"
        for statement in self.newType1:
            ret = ret + "\n{}: {}".format(statement[0].toString(),"" if len(statement[1]) == 0 else (statement[1][0] if len(statement[1]) == 1 else " ; ".join([x for x in statement[1]])))
        for statement in self.newType3:
            ret = ret + "\n{}: {}".format(statement[0].toString(),"" if len(statement[1]) == 0 else (statement[1][0] if len(statement[1]) == 1 else " ; ".join([x for x in statement[1]])))
        return ret    