import os,sys,shutil,argparse,re,fileinput,numpy
me = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,me+"/Generator")
sys.path.insert(0,me+"/Reasoner")

from HardGenERator2 import *
from HardGenERator import *
from GenERator import *
from ReasonER import *
from NegativesGenERator import *
from JustificationFindER import *
from DependencyReducer import *

def writeFile(filename,data):
    file = open(filename,"w")
    file.write(data)
    file.close()  
    
def EQtoSC(line,new):
    if "ObjectIntersectionOf" in line[1]: x = intersectionSplit(line,new)
    else: x = "SubClassOf({} {})\nSubClassOf({} {})".format(line[0],line[1],line[1],line[0])
    #print(x)
    return x

def intersectionSplit(line,new):
    newLine = [line[0]]
    newLine.extend(line[1][21:-1].split(" ",1))
    x = ""
    if canEasySplit(line[1]):
                
        while separable(newLine[-1]):
            if not "ObjectIntersectionOf" in newLine[-1]:
                rem = newLine[-1]
                newLine.extend(newLine[-1].split(" ",1))
                newLine.remove(rem)
            else:
                pass
        for C in newLine:
            if C in new.keys(): pass
            else: new[C] = "sep:X{:05d}".format(len(new)+1)
        if len(newLine) == 3:
            '''
            B ⊑ A
            B ⊑ X
            A ⊓ X ⊑ B
            X ⊑ ∃S.D
            ∃S.D ⊑ X
            '''
            if isExistential(newLine[-1]):
                x = "SubClassOf({} {})\nSubClassOf({} {})\nSubClassOf(ObjectIntersectionOf({} {}) {})\nSubClassOf({} {})\nSubClassOf({} {})\n".format(newLine[0],newLine[1],newLine[0],new[newLine[-1]],newLine[1],new[newLine[-1]],newLine[0],new[newLine[-1]],newLine[-1],newLine[-1],new[newLine[-1]])
            else:
                raise
        else:
            '''
            A ≡ B ⊓ C ⊓ ∃S.D
            
            A ⊑ B
            A ⊑ X1
            B ⊓ X1 ⊑ A
            X1 ⊑ C
            X1 ⊑ X2
            C ⊓ X2 ⊑ X1
            X2 ⊑ ∃S.D
            ∃S.D ⊑ X2
            '''
            X1 = "ObjectIntersectionOf({} {})".format(newLine[2],newLine[3])
            X1r = "ObjectIntersectionOf({} {})".format(newLine[3],newLine[2])
            
            if X1 in new.keys() or X1r in new.keys(): pass
            else: new[X1] = "sep:X{:05d}".format(len(new)+1)
            
            X2 = newLine[3]
            concept = True
            if isExistential(X2): 
                concept = False
                if X2 in new.keys(): pass
                else: new[X2] = "sep:X{:05d}".format(len(new)+1)
                '''
                X2 ⊑ ∃S.D
                ∃S.D ⊑ X2
                '''
                x = x + "SubClassOf({} {})\n".format(new[X2],newLine[3])
                x = x + "SubClassOf({} {})\n".format(newLine[3],new[X2])                
                
            #
            '''
            A ⊑ B
            A ⊑ X1
            '''
            x = x + "SubClassOf({} {})\n".format(newLine[0],newLine[1])
            x = x + "SubClassOf({} {})\n".format(newLine[0],new[X1])
            '''
            B ⊓ X1 ⊑ A
            C ⊓ X2 ⊑ X1
            '''
            x = x + "SubClassOf(ObjectIntersectionOf({} {}) {})\n".format(newLine[1],new[X1],newLine[0])
            x = x + "SubClassOf(ObjectIntersectionOf({} {}) {})\n".format(newLine[2],X2 if concept else new[X2],new[X1])            
            '''
            X1 ⊑ C
            X1 ⊑ X2
            '''
            x = x + "SubClassOf({} {})\n".format(new[X1],newLine[2])
            x = x + "SubClassOf({} {})\n".format(new[X1],X2 if concept else new[X2])
            #print(newLine)#print(x,"\n")
    else:
        if newLine[2][0] != 'O':
            '''
            A ≡ B ⊓ C ⊓ ∃R.D ⊓ ∃S.E
            
            A ⊑ B
            A ⊑ X1
            B ⊓ X1 ⊑ A
            X1 ⊑ C
            X1 ⊑ X2
            C ⊓ X2 ⊑ X1
            X2 ⊑ X3
            X2 ⊑ X4
            X3 ⊓ X4 ⊑ X2
            X3 ⊑ ∃R.D
            ∃R.D ⊑ X3
            X4 ⊑ ∃S.E
            ∃S.E ⊑ X4
            '''
            y = newLine[2].split(" ",1)
            z = y[1].split(" ",2)[-1]
            y[1] = " ".join(y[1].split(" ",2)[:2])
            y.append(z)
            del newLine[2]
            newLine.extend(y)
     
            #print(newLine)       
            X3 = newLine[3]
            if X3 in new.keys(): pass
            else: new[X3] = "sep:X{:05d}".format(len(new)+1)
            
            X4 = newLine[4]
            if X4 in new.keys(): pass
            else: new[X4] = "sep:X{:05d}".format(len(new)+1)
            
            X2 = "ObjectIntersectionOf({} {})".format(newLine[3],newLine[4])
            X2r = "ObjectIntersectionOf({} {})".format(newLine[4],newLine[3])
            
            if X2 in new.keys() or X2r in new.keys(): pass
            else: new[X2] = "sep:X{:05d}".format(len(new)+1)

            X1 = "ObjectIntersectionOf({} {})".format(newLine[2],X2)
            X12 = "ObjectIntersectionOf({} {})".format(newLine[2],X2r)
            X1r = "ObjectIntersectionOf({} {})".format(X2,newLine[2])
            X12r = "ObjectIntersectionOf({} {})".format(X2r,newLine[2])
            
            if X1 in new.keys() or X1r in new.keys() or X12 in new.keys() or X12r in new.keys(): pass
            else: new[X1] = "sep:X{:05d}".format(len(new)+1)            
            
            '''
            A ⊑ B
            A ⊑ X1
            X1 ⊑ C
            X1 ⊑ X2
            X2 ⊑ X3
            X2 ⊑ X4
            '''
            x = x + "SubClassOf({} {})\n".format(newLine[0],newLine[1])
            x = x + "SubClassOf({} {})\n".format(newLine[0],new[X1])
            x = x + "SubClassOf({} {})\n".format(new[X1],newLine[2])
            x = x + "SubClassOf({} {})\n".format(new[X1],new[X2])
            x = x + "SubClassOf({} {})\n".format(new[X2],new[X3])
            x = x + "SubClassOf({} {})\n".format(new[X2],new[X4])            
            '''
            B ⊓ X1 ⊑ A
            C ⊓ X2 ⊑ X1
            X3 ⊓ X4 ⊑ X2
            '''
            x = x + "SubClassOf(ObjectIntersectionOf({} {}) {})\n".format(newLine[1],new[X1],newLine[0])
            x = x + "SubClassOf(ObjectIntersectionOf({} {}) {})\n".format(newLine[2],new[X2],new[X1])
            x = x + "SubClassOf(ObjectIntersectionOf({} {}) {})\n".format(new[X3],new[X4],new[X2])
            '''
            X3 ⊑ ∃R.D
            ∃R.D ⊑ X3
            '''
            x = x + "SubClassOf({} {})\n".format(new[X3],newLine[3])
            x = x + "SubClassOf({} {})\n".format(newLine[3],new[X3])  
            '''
            X4 ⊑ ∃S.E
            ∃S.E ⊑ X4
            '''
            x = x + "SubClassOf({} {})\n".format(new[X4],newLine[4])
            x = x + "SubClassOf({} {})\n".format(newLine[4],new[X4])
            
            #print(newLine)
        else:
            
            while stillSplittable(newLine[-1]):
                #print(newLine)
                y = newLine[-1][21:-1].split(" ",1)
                #print(y)
                newLine.pop(-1)
                newLine.append(y[0])
                newLine.append(y[1])
                #            
            
            if newLine[-1].count(' ') > 1:
                y = newLine[-1][21:-1].split(" ",1)
                newLine.pop(-1)
                newLine.append(y[0])
                newLine.append(y[1])
                
            #print(newLine)
            
            last = newLine[-1]
            if last in new.keys(): pass
            else: new[last] = "sep:X{:05d}".format(len(new)+1)
            
            '''
            last ⊑ ∃R.C
            ∃R.C ⊑ last
            '''
            x = x + "SubClassOf({} {})\n".format(new[last],newLine[-1])
            x = x + "SubClassOf({} {})\n".format(newLine[-1],new[last])
            
            newLine[-1] = new[last]
            
            #print(newLine)
            
            while len(newLine) > 2:
                if len(newLine[-2]) > 7:
                    Y = "ObjectIntersectionOf({} {})".format(newLine[-2],newLine[-1])
                    Yr = "ObjectIntersectionOf({} {})".format(newLine[-1],newLine[-2])
                    
                    if Y in new.keys() or Yr in new.keys(): pass
                    else: 
                        new[Y] = "sep:X{:05d}".format(len(new)+1) 
                        '''
                        Y ⊑ B
                        Y ⊑ X
                        B ⊓ X ⊑ Y
                        '''
                        x = x + "SubClassOf({} {})\n".format(new[Y],newLine[-1])
                        x = x + "SubClassOf({} {})\n".format(new[Y],newLine[-2])
                        x = x + "SubClassOf(ObjectIntersectionOf({} {}) {})\n".format(newLine[-2],newLine[-1],new[Y])
                    
                    newLine.pop(-1)
                    newLine[-1] = new[Y]
                    
                    #print(newLine)
                else:
                    last = "ObjectSomeValuesFrom({} {})".format(newLine[-2],newLine[-1])
                    if last in new.keys(): pass
                    else: 
                        new[last] = "sep:X{:05d}".format(len(new)+1)
                        '''
                        last ⊑ ∃R.C
                        ∃R.C ⊑ last
                        '''
                        x = x + "SubClassOf({} {})\n".format(new[last],last)
                        x = x + "SubClassOf({} {})\n".format(last,new[last])
                    #print(x)
                    newLine.pop(-1)
                    newLine[-1] = new[last]
                    
                    #print(newLine)
            
            x = x + "SubClassOf({} {})\nSubClassOf({} {})\n".format(newLine[0],newLine[1],newLine[1],newLine[0])#"EquivalentClasses({} {})".format(line[0],line[1])
    
    return x


def stillSplittable(string):
    #print(string)
    pattern1 = re.compile("^.*(ObjectIntersectionOf)+.*$")
    pattern2 = re.compile("^.*(ObjectSomeValuesFrom){2,}.*$")
    val = pattern1.match(string) != None or pattern2.match(string) != None   
    return val

def isExistential(string):
    return "ObjectSomeValuesFrom" in string

def separable(string):
    pattern = re.compile("^[a-z]{3}:[A-Z]{1}[0-9]{5}\s")
    return pattern.match(string) != None

def canEasySplit(line):
    if not "ObjectSomeValuesFrom" in line: return True
    if line.count("ObjectSomeValuesFrom") == 1:
        return line.rfind("ObjectSomeValuesFrom") > line.rfind("ObjectIntersectionOf")
    #print(line)
    return False

def normalizeFS(inf,outf):
    pattern = re.compile("EquivalentClasses+")
    
    file = open(inf,"r")
    file2 = open(outf,"w")
    
    print("Normalizing "+inf)
    
    new = {}
    
    for line in file:
        if pattern.match(line) != None: file2.write(EQtoSC(line[18:-2].split(" ",1),new))
        else: file2.write(line)
    
    file.close()
    file2.close()
    
    newData = ["Declaration(Class(sep:X{:05d}))\n".format(x) for x in range(1,len(new)+1)]
    
    file3 = open(outf,"r")    
    data = file3.readlines()
    file3.close()
    
    for line in fileinput.FileInput(outf,inplace=1):
        if "Declaration(Class(sep:fauxP19550))" in line:
            line = line.replace(line,line+"".join(newData))
        print(line,end='')
    
    print("Saving as "+outf)
    
    return outf

def fsOWLReader(filename):
    file = open(filename,'r')
    
    print("Reading "+filename)
    
    line = file.readline()
    while "Declaration" not in line:
        line = file.readline()
    
    classes = 0
    classDict = {}
    classRetDict = {}
    labelDict = {}
    roles = 0
    roleDict = {}
    roleRetDict = {}
    CType1=[]
    CType2=[]
    CType3=[]
    CType4=[]
    roleSubs=[]
    roleChains=[]
    
    
    while "Declaration" in line:
        if "Class" in line: 
            classes = classes + 1
            st = line[18:-3]
            classDict[st] = classes
            classRetDict[classes] = st
            if "sep:X" in line:
                labelDict[st] = "Artificial node {}".format(st)
        elif 'Object' in line: 
            roles = roles - 1
            st = line[27:-3]
            roleDict[st] = roles
            roleRetDict[roles] = st
        line = file.readline()
        
    
    while line:
        if line[0] == '#': pass
        elif 'AnnotationAssertion(rdfs:label' in line:
            line = line[31:-2].split(' ',1)
            labelDict[line[0]] = line[1][1:-1]
        elif 'SubObjectPropertyOf(' in line:
            #print(line)
            line = line[20:-2]            
            if 'ObjectPropertyChain(' in line:
                first = (" ".join(line.split(" ",2)[:2]))[20:-1].split()
                last = line.split(" ",2)[2]
                rs = RoleStatement(len(roleSubs),True,RoleChain(0,Role(roleDict[first[0]],[0,1]),Role(roleDict[first[1]],[1,2])),Role(roleDict[last],[0,2]))
                rs.complete('⊑')
                roleChains.append(rs)
            else: 
                line = line.split()
                #print(line)
                rs = RoleStatement(len(roleChains),True,Role(roleDict[line[0]],[0,1]),Role(roleDict[line[1]],[0,1]))
                rs.complete('⊑')
                roleSubs.append(rs)
        elif 'TransitiveObjectProperty(' in line:
            '''SubObjectPropertyOf( ObjectPropertyChain( OPE OPE ) OPE )'''
            role = line[25:-2]
            rs = RoleStatement(len(roleChains),True,RoleChain(0,Role(roleDict[role],[0,1]),Role(roleDict[role],[1,2])),Role(roleDict[role],[0,2]))
            rs.complete('⊑')
            roleChains.append(rs) 
        elif 'SubClassOf(' in line:
            line = line[11:-2]
            inter = False     
            test = 'ObjectSomeValuesFrom(' in line or 'ObjectIntersectionOf(' in line
            first = line.split(" ")[0] if not test or line[0] != 'O' else " ".join(line.split(" ",2)[:2])
            last = line.split(" ",1)[1] if not test  or line[0] != 'O' else line.split(" ",2)[2]
            
            if test and 'ObjectIntersectionOf(' in first:
                thiss = first[21:-1].split()
                inter = True
            elif test and 'ObjectSomeValuesFrom(' in first:
                thiss = first[21:-1].split()
            elif test and 'ObjectSomeValuesFrom(' in last:
                thiss = last[21:-1].split()
            else:
                thiss = None
            
            if len(first) <= 14 and len(last) <= 14:
                cs = ConceptStatement(len(CType1),True,Concept(classDict[first],[0]),Concept(classDict[last],[0]))
                cs.complete('⊑')
                CType1.append(cs)
            elif len(first) >= 20 and inter:
                cs1 = ConceptStatement(1,False,Concept(classDict[thiss[0]],[0]),Concept(classDict[thiss[1]],[0]))
                cs1.complete('⊓')
                cs = ConceptStatement(len(CType2),True,cs1,Concept(classDict[last],[0]))
                cs.complete('⊑')
                CType2.append(cs)
            elif len(first) >= 20:
                cs = ConceptStatement(len(CType3),True,ConceptRole('e',Role(roleDict[thiss[0]],[0,1]),Concept(classDict[thiss[1]],[1])),Concept(classDict[last],[0]))
                cs.complete('⊑')
                CType4.append(cs)
            elif len(last) >= 20:
                cs = ConceptStatement(len(CType4),True,Concept(classDict[first],[0]),ConceptRole('e',Role(roleDict[thiss[0]],[0,1]),Concept(classDict[thiss[1]],[1]))) 
                cs.complete('⊑')
                CType3.append(cs)
            else:
                print("nooooooooo")
            
        else:pass
        line = file.readline()
    
    print("Shuffling axioms")
    random.shuffle(CType1)
    random.shuffle(CType2)
    random.shuffle(CType3)
    random.shuffle(CType4)
    random.shuffle(roleSubs)
    random.shuffle(roleChains)
    
    info = [['c',classes,classRetDict],['r',roles,roleRetDict],['cs',len(CType1),len(CType2),len(CType3),len(CType4)],['rs',len(roleSubs),len(roleChains)],['l',labelDict]]
    
    return [CType1,CType2,CType3,CType4],[roleSubs,roleChains],info

def makeKBFromSamples(concepts,roles,info):
       
    start = 0
    allowedCNames = []
    allowedRNames = []
    
    while isinstance(start,int):
        start = random.randint(1,info[0][1])
        #print(start)
        for intersection in concepts[1]:
            if intersection.antecedent.antecedent.name == start or intersection.antecedent.consequent.name == start or intersection.consequent.name == start:
                start = intersection
                allowedCNames.append(intersection.antecedent.antecedent.name) 
                allowedCNames.append(intersection.antecedent.consequent.name)
                allowedCNames.append(intersection.consequent.name)
                break
    
    numCType1 = 4
    numCType2 = 2
    numCType3 = 8
    numCType4 = 2
    numRoleSubs = 2
    numRoleChains = 2
    
    CTypeNull = []
    CType1 = []
    CType2 = [start]
    CType3 = []
    CType4 = []
    roleSubs = []
    roleChains = []   
    allType3Names = []
    allType4Names = []
    allRSubNames = []
    allRChainNames = []
    
    for restriction in concepts[2]:
        allType3Names.append(restriction.consequent.concept.name)
        allType3Names.append(restriction.antecedent.name)
    allType3Names = list(dict.fromkeys(allType3Names))
    for restriction in concepts[3]:
        allType4Names.append(restriction.antecedent.concept.name)
        allType4Names.append(restriction.consequent.name) 
    allType4Names = list(dict.fromkeys(allType4Names))
    for restriction in roles[0]:
        allRSubNames.append(restriction.antecedent.name)
        allRSubNames.append(restriction.consequent.name)     
    allRSubNames = list(dict.fromkeys(allRSubNames))
    for restriction in roles[1]:
        allRChainNames.append(restriction.antecedent.roles[0].name)
        allRChainNames.append(restriction.antecedent.roles[1].name)
        allRChainNames.append(restriction.consequent.name)     
    allRChainNames = list(dict.fromkeys(allRChainNames))    
    
    while len(CType1) < numCType1:
        usedBefore = False
        inclusion = random.choice(concepts[0])
        for other in CType1: 
            if other.antecedent.name == inclusion.antecedent.name and other.consequent.name==inclusion.consequent.name:
                usedBefore = True
                break
        if not usedBefore and (inclusion.antecedent.name in allowedCNames or inclusion.consequent.name in allowedCNames):
            CType1.append(inclusion)
            allowedCNames.append(inclusion.antecedent.name)
            allowedCNames.append(inclusion.consequent.name)
            no1InC = False
            
    allowedCNames = list(dict.fromkeys(allowedCNames))
    
    while len(CType2) < numCType2:
        usedBefore = False
        intersection = random.choice(concepts[1])
        for other in CType2: 
            if intersection.antecedent.antecedent.name == other.antecedent.antecedent.name and intersection.antecedent.consequent.name==other.antecedent.consequent.name and other.consequent.name==inclusion.consequent.name:
                usedBefore = True
                break
        if not usedBefore and (intersection.antecedent.antecedent.name in allowedCNames or intersection.antecedent.consequent.name in allowedCNames or intersection.consequent.name in allowedCNames):
            CType2.append(intersection)
            allowedCNames.append(intersection.antecedent.antecedent.name) 
            allowedCNames.append(intersection.antecedent.consequent.name)
            allowedCNames.append(intersection.consequent.name)
            
    allowedCNames = list(dict.fromkeys(allowedCNames))
    no3InC = bool(set(allowedCNames) & set(allType3Names))
    
    while len(CType3) < numCType3:
            usedBefore = False
            restriction = random.choice(concepts[2])
            for other in CType3: 
                if restriction.consequent.concept.name == other.consequent.concept.name and restriction.consequent.role.name==other.consequent.role.name and other.antecedent.name==restriction.antecedent.name:
                    usedBefore = True
                    break
            if not usedBefore and (no3InC or restriction.consequent.concept.name in allowedCNames or restriction.antecedent.name in allowedCNames):
                CType3.append(restriction)
                allowedCNames.append(restriction.consequent.concept.name)
                allowedRNames.append(restriction.consequent.role.name)
                allowedCNames.append(restriction.antecedent.name)
                no3InC = False
            
    allowedCNames = list(dict.fromkeys(allowedCNames))
    allowedRNames = list(dict.fromkeys(allowedRNames))          
    no4InC = bool(set(allowedCNames) & set(allType4Names))
    
    while len(CType4) < numCType4:
            usedBefore = False
            restriction = random.choice(concepts[3])
            for other in CType4: 
                if restriction.antecedent.concept.name == other.antecedent.concept.name and restriction.antecedent.role.name==other.antecedent.role.name and other.consequent.name==restriction.consequent.name:
                    usedBefore = True
                    break
            if not usedBefore and (no4InC or restriction.antecedent.concept.name in allowedCNames or restriction.consequent.name in allowedCNames):
                    CType4.append(restriction)
                    allowedCNames.append(restriction.antecedent.concept.name)
                    allowedRNames.append(restriction.antecedent.role.name)
                    allowedCNames.append(restriction.consequent.name)
                    no4InC = False
    
    allowedCNames = list(dict.fromkeys(allowedCNames))
    allowedCNames.sort(key=lambda x: (x))
    allowedRNames = list(dict.fromkeys(allowedRNames))
    random.shuffle(allowedRNames)
    noChain = bool(set(allowedRNames) & set(allRChainNames))
   
    iterations = 0
    while len(roleChains) < numRoleChains:
        iterations = iterations + 1 
        noChain = True if iterations > 1000 else noChain      
        restriction = random.choice(roles[1])
        if restriction in roleChains: iterations = iterations + 1 ; noChain = iterations > 1000 ; continue
        elif noChain or restriction.antecedent.roles[0].name in allowedRNames or restriction.antecedent.roles[1].name in allowedRNames or restriction.consequent.name in allowedRNames:
            roleChains.append(restriction)
            allowedRNames.append(restriction.antecedent.roles[0].name)
            allowedRNames.append(restriction.antecedent.roles[1].name)
            allowedRNames.append(restriction.consequent.name)
            noChain = False
            iterations = 0
    noSub = bool(set(allowedRNames) & set(allRSubNames))
    iterations = 0
    while len(roleSubs) < numRoleSubs:
        iterations = iterations + 1 
        noSub = True if iterations > 1000 else noSub
        restriction = random.choice(roles[0])
        if restriction in roleSubs: continue
        elif noSub or restriction.antecedent.name in allowedRNames or restriction.consequent.name in allowedRNames:
            roleSubs.append(restriction)
            allowedRNames.append(restriction.antecedent.name)
            allowedRNames.append(restriction.consequent.name)
            noSub = False
            iterations = 0
            
    allowedRNames = list(dict.fromkeys(allowedRNames))
    allowedRNames.sort(key=lambda x: (x))
    
    if len(allowedCNames) > conceptSpace:
        raise
    
    if len(allowedRNames) > roleSpace:
        raise 
        
    for item in range(1,22):
        cs = ConceptStatement(item,True,Concept(item,[0]),Concept(item,[0]))
        cs.complete('⊑')
        CTypeNull.append(cs) 
    
    CTypeNull,CType1,CType2,CType3,CType4,roleSubs,roleChains = copyAllStatements(CTypeNull,CType1,CType2,CType3,CType4,roleSubs,roleChains)
    mapping,CTypeNull,CType1,CType2,CType3,CType4,roleSubs,roleChains,allowedCNames,allowedRNames = shiftNames(CTypeNull,CType1,CType2,CType3,CType4,roleSubs,roleChains,allowedCNames,allowedRNames)
    
    generator = HardGenERator2(rGenerator=GenERator(conceptNamespace=conceptSpace,roleNamespace=roleSpace,CTypeNull=CTypeNull,CType1=CType1,CType2=CType2,CType3=CType3,CType4=CType4,roleSubs=roleSubs,roleChains=roleChains),difficulty=0)
    
    generator.hasRun = True
    
    generator.genERate()
    
    return mapping,generator

def copyAllStatements(oldCTypeNull,oldCType1,oldCType2,oldCType3,oldCType4,oldroleSubs,oldroleChains):
    CTypeNull=[]
    CType1=[]
    CType2=[]
    CType3=[]
    CType4=[]
    roleSubs=[]
    roleChains=[]		
    for i in range(0,len(oldCTypeNull)):
        cs = ConceptStatement(len(CTypeNull),True,Concept(oldCTypeNull[i].antecedent.name,[0]),Concept(oldCTypeNull[i].consequent.name,[0]))
        cs.complete('⊑')
        CTypeNull.append(cs)

    for i in range(0,len(oldCType1)):
        cs = ConceptStatement(len(CType1),True,Concept(oldCType1[i].antecedent.name,[0]),Concept(oldCType1[i].consequent.name,[0]))
        cs.complete('⊑')
        CType1.append(cs)

    for i in range(0,len(oldCType2)):
        cs1 = ConceptStatement(1,True,Concept(oldCType2[i].antecedent.antecedent.name,[0]),Concept(oldCType2[i].antecedent.consequent.name,[0]))
        cs1.complete('⊓')
        cs = ConceptStatement(len(CType2),True,cs1,Concept(oldCType2[i].consequent.name,[0]))
        cs.complete('⊑')
        CType2.append(cs)

    for i in range(0,len(oldCType3)):
        cs = ConceptStatement(len(CType3),True,Concept(oldCType3[i].antecedent.name,[0]),ConceptRole('e',Role(oldCType3[i].consequent.role.name,[0,1]),Concept(oldCType3[i].consequent.concept.name,[1])))
        cs.complete('⊑')
        CType3.append(cs)

    for i in range(0,len(oldCType4)):
        cs = ConceptStatement(len(CType4),True,ConceptRole('e',Role(oldCType4[i].antecedent.role.name,[0,1]),Concept(oldCType4[i].antecedent.concept.name,[1])),Concept(oldCType4[i].consequent.name,[0]))
        cs.complete('⊑')
        CType4.append(cs)	

    for i in range(0,len(oldroleSubs)):
        rs = RoleStatement(len(roleSubs),True,Role(oldroleSubs[i].antecedent.name,[0,1]),Role(oldroleSubs[i].consequent.name,[0,1]))
        rs.complete('⊑')
        roleSubs.append(rs)

    for i in range(0,len(oldroleChains)):
        rs = RoleStatement(len(roleChains),True,RoleChain(0,Role(oldroleChains[i].antecedent.roles[0].name,[0,1]),Role(oldroleChains[i].antecedent.roles[1].name,[1,2])),Role(oldroleChains[i].consequent.name,[0,2]))
        rs.complete('⊑')
        roleChains.append(rs)
    
    return CTypeNull,CType1,CType2,CType3,CType4,roleSubs,roleChains
    
    
def shiftNames(CTypeNull,CType1,CType2,CType3,CType4,roleSubs,roleChains,allowedCNames,allowedRNames):
    newVal = 1
    mapping = {}
    for name in allowedCNames:
        mapping[newVal] = name
        for statement in CTypeNull:
            if statement.antecedent.name == name:
                statement.antecedent.name = newVal
                statement.consequent.name = newVal
        for statement in CType1:
            if statement.antecedent.name == name:
                statement.antecedent.name = newVal
            if statement.consequent.name == name:
                statement.consequent.name = newVal
        for statement in CType2:
            if statement.antecedent.antecedent.name == name:
                statement.antecedent.antecedent.name = newVal
            if statement.antecedent.consequent.name == name:
                statement.antecedent.consequent.name = newVal
            if statement.consequent.name == name:
                statement.consequent.name = newVal
        for statement in CType3:
            if statement.antecedent.name == name:
                statement.antecedent.name = newVal
            if statement.consequent.concept.name == name:
                statement.consequent.concept.name = newVal
        for statement in CType4:
            if statement.antecedent.concept.name == name:
                statement.antecedent.concept.name = newVal
            if statement.consequent.name == name:
                statement.consequent.name = newVal
        newVal = newVal + 1
    
    newVal = -1    
    for name in allowedRNames:
        mapping[newVal] = name
        for statement in CType3:
            if statement.consequent.role.name == name:
                statement.consequent.role.name = -newVal
        for statement in CType4:
            if statement.antecedent.role.name == name:
                statement.antecedent.role.name = -newVal
        for statement in roleSubs:
            if statement.antecedent.name == name:
                statement.antecedent.name = -newVal
            if statement.consequent.name == name:
                statement.consequent.name = -newVal 
        for statement in roleChains:
            if statement.antecedent.roles[0].name == name:
                statement.antecedent.roles[0].name = -newVal
            if statement.antecedent.roles[1].name == name:
                statement.antecedent.roles[1].name = -newVal
            if statement.consequent.name == name:
                statement.consequent.name = -newVal
        newVal = newVal - 1
    
    return mapping,CTypeNull,CType1,CType2,CType3,CType4,roleSubs,roleChains,allowedCNames,allowedRNames
    
def sampleDataHardGenerator2Format(SNOMEDdata,trials):
    
    if os.path.isdir("snoutput/Dataset"): shutil.rmtree("snoutput/Dataset")
    if not os.path.isdir("snoutput"): os.mkdir("snoutput")
    if not os.path.isdir("snoutput/Dataset"): os.mkdir("snoutput/Dataset")     
    
    concepts,roles,info = SNOMEDdata  
    localmaps = []
    seq_in = numpy.empty(trials,dtype=numpy.ndarray)
    seq_out = numpy.empty(trials,dtype=numpy.ndarray)
    kbs = numpy.empty([trials,shapes[0]],dtype=numpy.float32)
    if not os.path.isdir("snoutput"): os.mkdir("snoutput")
    i = 0

    while i < trials:

        print("Sampling SNOMED to make KB"+str(i))

        if not os.path.isdir("snoutput/Dataset/{}".format(i)): os.mkdir("snoutput/Dataset/{}".format(i))
        
        localmap,generator = makeKBFromSamples(concepts,roles,info)
        
        generator.toFunctionalSyntaxFile("<http://www.randomOntology.com/SNOMED/Sample/random/{}/>".format(i),"snoutput/Dataset/{}/KB{}.owl".format(i,i))
        
        reasoner = ReasonER(generator,showSteps=True)

        reasoner.ERason()
        
        if len(reasoner.KBaLog) < shapes[1]:
            print("Sample has too few reasoner steps, trying again")
            continue
        
        if len(reasoner.KBaLog) > shapes[1]:
            print("Sample has too many reasoner steps, trying again")
            continue        

        supports = DependencyReducer(generator.getAllExpressions(),reasoner.sequenceLog,reasoner.KBsLog,reasoner.KBaLog)
        
        a,b = supports.toVector(generator.conceptNamespace,generator.roleNamespace)
        
        if len(a[0]) > shapes[2]:
            print("Sample has too many supports, trying again")
            continue
        
        if len(b[0]) > shapes[3]:
            print("Sample has too many entailments, trying again")
            continue        
        
        localmaps.append(localmap)
        
        kbs[i] = array(generator.toVector())
        
        seq_in[i] = a
        seq_out[i] = b
        
        if len(reasoner.KBaLog) > 0 and not os.path.isdir("snoutput/Dataset/{}/Reasoner Steps".format(i)): os.mkdir("snoutput/Dataset/{}/Reasoner Steps".format(i))
        generator.toStringFile("snoutput/Dataset/{}/completedKB.txt".format(i))
        reasoner.toFunctionalSyntaxFile("<http://www.randomOntology.com/SNOMED/Sample/random/{}/>".format(i),"snoutput/Dataset/{}/completion{}.owl".format(i,i))
        reasoner.toStringFile("snoutput/Dataset/{}/completedKB.txt".format(i))
        for j in range(0,len(supports.donelogs[2])):
            if len(reasoner.KBaLog[j]) > 0: writeFile("snoutput/Dataset/{}/Reasoner Steps/reasonerStep{}.txt".format(i,j+len(reasoner.sequenceLog)),supports.toString(supports.donelogs[2][j]))
            
        i = i + 1


    numpy.savez('ssaves/data', kbs,seq_in,seq_out,localmaps,info)

    return kbs,seq_in,seq_out,localmaps,info   

def makeSynData(trials):
    
    if os.path.isdir("output/Dataset"): shutil.rmtree("output/Dataset")
    if not os.path.isdir("output"): os.mkdir("output") 
    if not os.path.isdir("output/Dataset"): os.mkdir("output/Dataset")
    
    seq_in = numpy.empty(trials,dtype=numpy.ndarray)
    seq_out = numpy.empty(trials,dtype=numpy.ndarray)
    kbs = numpy.empty([trials,shapes[0]],dtype=numpy.float32)
    if not os.path.isdir("output"): os.mkdir("output")
    i = 0

    while i < trials:
        
        print("Making Random-Sequetial KB"+str(i))
        
        if not os.path.isdir("output/Dataset/{}".format(i)): os.mkdir("output/Dataset/{}".format(i))
        
        gen = GenERator(numCType1=2,numCType2=1,numCType3=2,numCType4=1,numRoleSub=1,numRoleChains=1,conceptNamespace=conceptSpace-3,roleNamespace=roleSpace-3,CTypeNull=[],CType1=[],CType2=[],CType3=[],CType4=[],roleSubs=[],roleChains=[])
        
        generator = HardGenERator2(rGenerator=gen,difficulty=int(shapes[1]/2))
        
        generator.genERate()
        
        if generator.conceptNamespace != conceptSpace or generator.roleNamespace != roleSpace:
            raise
        
        generator.toFunctionalSyntaxFile("<http://www.randomOntology.com/Synthetic/Sequential/random/{}/>".format(i),"output/Dataset/{}/KB{}.owl".format(i,i))
        
        reasoner = ReasonER(generator,showSteps=True)
        
        reasoner.ERason()
	
        if len(reasoner.KBaLog) > 1:
            print("KB has too many reasoner steps, trying again")
            continue
        
        supports = DependencyReducer(generator.getAllExpressions(),reasoner.sequenceLog,reasoner.KBsLog,reasoner.KBaLog)
        
        a,b = supports.toVector(generator.conceptNamespace,generator.roleNamespace)
        
        if len(a[0]) > shapes[2]:
            print("KB has too many supports, trying again")
            continue
        
        if len(b[0]) > shapes[3]:
            print("KB has too many entailments, trying again")
            continue
        
        kbs[i] = array(generator.toVector())
        
        seq_in[i] = a
        seq_out[i] = b

        if not os.path.isdir("output/Dataset/{}/sequence".format(i)): os.mkdir("output/Dataset/{}/sequence".format(i))
        if not os.path.isdir("output/Dataset/{}/KB during sequence".format(i)): os.mkdir("output/Dataset/{}/KB during sequence".format(i))        
        if len(reasoner.KBaLog) > 0 and not os.path.isdir("output/Dataset/{}/KB after sequence".format(i)): os.mkdir("output/Dataset/{}/KB after sequence".format(i))
        reasoner.toFunctionalSyntaxFile("<http://www.randomOntology.com/Synthetic/Sequential/random/{}/>".format(i),"output/Dataset/{}/completion{}.owl".format(i,i))
        generator.toStringFile("output/Dataset/{}/completedKB.txt".format(i))
        reasoner.toStringFile("output/Dataset/{}/completedKB.txt".format(i))        
        for j in range(0,len(supports.donelogs[0])):
            writeFile("output/Dataset/{}/sequence/reasonerStep{}.txt".format(i,j),supports.toString(supports.donelogs[0][j]))
        for j in range(0,len(supports.donelogs[1])):
            if len(reasoner.KBsLog[j]) > 0: writeFile("output/Dataset/{}/KB during sequence/reasonerStep{}.txt".format(i,j),supports.toString(supports.donelogs[1][j]))
        for j in range(0,len(supports.donelogs[2])):
            if len(reasoner.KBaLog[j]) > 0: writeFile("output/Dataset/{}/KB after sequence/reasonerStep{}.txt".format(i,j+len(reasoner.sequenceLog)),supports.toString(supports.donelogs[2][j]))
        
        i = i + 1
            
    numpy.savez('saves/data', kbs,seq_in,seq_out)
    
    return kbs,seq_in,seq_out

def messUpKB(gen,err):
    for statement in gen.CType1:
        if random.random() < err:
            statement.antecedent.name = random.randint(1,conceptSpace)
        if random.random() < err:
            statement.consequent.name = random.randint(1,conceptSpace)
    for statement in gen.CType2:
        if random.random() < err:
            statement.antecedent.antecedent.name = random.randint(1,conceptSpace)
        if random.random() < err:
            statement.antecedent.consequent.name = random.randint(1,conceptSpace)
        if random.random() < err:
            statement.consequent.name = random.randint(1,conceptSpace)
    for statement in gen.CType3:
        if random.random() < err:
            statement.antecedent.name = random.randint(1,conceptSpace)
        if random.random() < err:
            statement.consequent.role.name = random.randint(1,roleSpace)
        if random.random() < err:
            statement.consequent.concept.name = random.randint(1,conceptSpace)
    for statement in gen.CType4:
        if random.random() < err:
            statement.antecedent.role.name = random.randint(1,roleSpace)
        if random.random() < err:
            statement.antecedent.concept.name = random.randint(1,conceptSpace)
        if random.random() < err:
            statement.consequent.name = random.randint(1,conceptSpace)
    for statement in gen.roleSubs:
        if random.random() < err:
            statement.antecedent.name = random.randint(1,roleSpace)
        if random.random() < err:
            statement.consequent.name = random.randint(1,roleSpace)
    for statement in gen.roleChains:
        if random.random() < err:
            statement.antecedent.roles[0].name = random.randint(1,roleSpace)
        if random.random() < err:
            statement.antecedent.roles[1].name = random.randint(1,roleSpace)
        if random.random() < err:
            statement.consequent.name = random.randint(1,roleSpace)
    
    gen.CType1.sort(key=lambda x: (x.antecedent.name, x.consequent.name))
    gen.CType2.sort(key=lambda x: (x.antecedent.antecedent.name, x.antecedent.consequent.name, x.consequent.name))
    gen.CType3.sort(key=lambda x: (x.antecedent.name, x.consequent.role.name, x.consequent.concept.name))
    gen.CType4.sort(key=lambda x: (x.antecedent.role.name, x.antecedent.concept.name, x.consequent.name))
    gen.roleSubs.sort(key=lambda x: (x.antecedent.name, x.consequent.name))
    gen.roleChains.sort(key=lambda x: (x.antecedent.roles[0].name, x.antecedent.roles[1].name, x.consequent.name))    

def makeSynDataPerturbed(trials,err):
    
    if os.path.isdir("output/Dataset"): shutil.rmtree("output/Dataset")
    if not os.path.isdir("output"): os.mkdir("output") 
    if not os.path.isdir("output/Dataset"): os.mkdir("output/Dataset")
    
    seq_in = numpy.empty(trials,dtype=numpy.ndarray)
    seq_out = numpy.empty(trials,dtype=numpy.ndarray)
    bad_KBs = numpy.empty(trials,dtype=numpy.ndarray)
    bad_out = numpy.empty(trials,dtype=numpy.ndarray)
    kbs = numpy.empty([trials,shapes[0]],dtype=numpy.float32)
    if not os.path.isdir("output"): os.mkdir("output")
    i = 0

    while i < trials:
        
        print("Making Random-Sequetial KB"+str(i))
        
        if not os.path.isdir("output/Dataset/{}".format(i)): os.mkdir("output/Dataset/{}".format(i))
        
        gen = GenERator(numCType1=2,numCType2=1,numCType3=2,numCType4=1,numRoleSub=1,numRoleChains=1,conceptNamespace=conceptSpace-3,roleNamespace=roleSpace-3,CTypeNull=[],CType1=[],CType2=[],CType3=[],CType4=[],roleSubs=[],roleChains=[])
        
        generator = HardGenERator2(rGenerator=gen,difficulty=int(shapes[1]/2))
        
        generator.genERate()
        
        if generator.conceptNamespace != conceptSpace or generator.roleNamespace != roleSpace:
            raise
        
        reasoner = ReasonER(generator,showSteps=True)
        
        reasoner.ERason()
	
        if len(reasoner.KBaLog) > 1:
            print("KB has too many reasoner steps, trying again")
            continue
        
        supports = DependencyReducer(generator.getAllExpressions(),reasoner.sequenceLog,reasoner.KBsLog,reasoner.KBaLog)
        
        a,b = supports.toVector(generator.conceptNamespace,generator.roleNamespace)
        
        if len(a[0]) > shapes[2]:
            print("KB has too many supports, trying again")
            continue
        
        if len(b[0]) > shapes[3]:
            print("KB has too many entailments, trying again")
            continue
        
        badGenerator = generator.copy(conceptSpace,roleSpace)
        
        messUpKB(badGenerator,err)       
        
        badReasoner = ReasonER(badGenerator,showSteps=True)
        
        badReasoner.ERason()
        
        kbs[i] = array(generator.toVector())        
        seq_in[i] = a
        seq_out[i] = b
        bad_KBs[i] = array(badGenerator.toVector())
        bad_out[i] = badReasoner.toCompletion()    
        
        if not os.path.isdir("output/Dataset/{}/sequence".format(i)): os.mkdir("output/Dataset/{}/sequence".format(i))
        if not os.path.isdir("output/Dataset/{}/KB during sequence".format(i)): os.mkdir("output/Dataset/{}/KB during sequence".format(i))        
        if len(reasoner.KBaLog) > 0 and not os.path.isdir("output/Dataset/{}/KB after sequence".format(i)): os.mkdir("output/Dataset/{}/KB after sequence".format(i))
        generator.toFunctionalSyntaxFile("<http://www.randomOntology.com/Synthetic/Sequential/random/{}/>".format(i),"output/Dataset/{}/KB{}.owl".format(i,i))
        badGenerator.toFunctionalSyntaxFile("<http://www.randomOntology.com/Synthetic/Sequential/random/bad{}/>".format(i),"output/Dataset/{}/badKB{}.owl".format(i,i))        
        reasoner.toFunctionalSyntaxFile("<http://www.randomOntology.com/Synthetic/Sequential/random/{}/>".format(i),"output/Dataset/{}/completion{}.owl".format(i,i))
        badReasoner.toFunctionalSyntaxFile("<http://www.randomOntology.com/Synthetic/Sequential/random/bad{}/>".format(i),"output/Dataset/{}/completionBad{}.owl".format(i,i))
        generator.toStringFile("output/Dataset/{}/completedKB.txt".format(i))
        badReasoner.toStringFile("output/Dataset/{}/completedBadKB.txt".format(i))  
        badGenerator.toStringFile("output/Dataset/{}/completedBadKB.txt".format(i))
        reasoner.toStringFile("output/Dataset/{}/completedKB.txt".format(i))          
        for j in range(0,len(supports.donelogs[0])):
            writeFile("output/Dataset/{}/sequence/reasonerStep{}.txt".format(i,j),supports.toString(supports.donelogs[0][j]))
        for j in range(0,len(supports.donelogs[1])):
            if len(reasoner.KBsLog[j]) > 0: writeFile("output/Dataset/{}/KB during sequence/reasonerStep{}.txt".format(i,j),supports.toString(supports.donelogs[1][j]))
        for j in range(0,len(supports.donelogs[2])):
            if len(reasoner.KBaLog[j]) > 0: writeFile("output/Dataset/{}/KB after sequence/reasonerStep{}.txt".format(i,j+len(reasoner.sequenceLog)),supports.toString(supports.donelogs[2][j]))
        
        i = i + 1
            
    numpy.savez('saves/messData', kbs,seq_in,seq_out,bad_KBs)
    
    return kbs,seq_in,seq_out,bad_KBs,bad_out

def sampleDataHardGenerator2FormatPerturbed(SNOMEDdata,trials,err):
    
    if os.path.isdir("snoutput/Dataset"): shutil.rmtree("snoutput/Dataset")
    if not os.path.isdir("snoutput"): os.mkdir("snoutput")
    if not os.path.isdir("snoutput/Dataset"): os.mkdir("snoutput/Dataset")     
    
    concepts,roles,info = SNOMEDdata  
    localmaps = []
    seq_in = numpy.empty(trials,dtype=numpy.ndarray)
    seq_out = numpy.empty(trials,dtype=numpy.ndarray)
    bad_KBs = numpy.empty(trials,dtype=numpy.ndarray)
    bad_out = numpy.empty(trials,dtype=numpy.ndarray)    
    kbs = numpy.empty([trials,shapes[0]],dtype=numpy.float32)
    if not os.path.isdir("snoutput"): os.mkdir("snoutput")
    i = 0

    while i < trials:

        print("Sampling SNOMED to make KB"+str(i))

        if not os.path.isdir("snoutput/Dataset/{}".format(i)): os.mkdir("snoutput/Dataset/{}".format(i))
        
        localmap,generator = makeKBFromSamples(concepts,roles,info)
        
        generator.toFunctionalSyntaxFile("<http://www.randomOntology.com/SNOMED/Sample/random/{}/>".format(i),"snoutput/Dataset/{}/KB{}.owl".format(i,i))
        
        reasoner = ReasonER(generator,showSteps=True)

        reasoner.ERason()      
        
        if len(reasoner.KBaLog) < shapes[1]:
            print("Sample has too few reasoner steps, trying again")
            continue
        
        if len(reasoner.KBaLog) > shapes[1]:
            print("Sample has too many reasoner steps, trying again")
            continue        

        supports = DependencyReducer(generator.getAllExpressions(),reasoner.sequenceLog,reasoner.KBsLog,reasoner.KBaLog)
        
        a,b = supports.toVector(generator.conceptNamespace,generator.roleNamespace)
        
        if len(a[0]) > shapes[2]:
            print("Sample has too many supports, trying again")
            continue
        
        if len(b[0]) > shapes[3]:
            print("Sample has too many entailments, trying again")
            continue        
        
        badGenerator = generator.copy(conceptSpace,roleSpace)
        
        messUpKB(badGenerator,err)       
        
        badReasoner = ReasonER(badGenerator,showSteps=True)
        
        badReasoner.ERason()     
        
        localmaps.append(localmap)
        
        kbs[i] = array(generator.toVector())        
        seq_in[i] = a
        seq_out[i] = b
        bad_KBs[i] = array(badGenerator.toVector())
        bad_out[i] = badReasoner.toCompletion()        
        
        if len(reasoner.KBaLog) > 0 and not os.path.isdir("snoutput/Dataset/{}/Reasoner Steps".format(i)): os.mkdir("snoutput/Dataset/{}/Reasoner Steps".format(i))
        generator.toStringFile("snoutput/Dataset/{}/completedKB.txt".format(i))
        reasoner.toFunctionalSyntaxFile("<http://www.randomOntology.com/SNOMED/Sample/random/{}/>".format(i),"snoutput/Dataset/{}/completion{}.owl".format(i,i))
        reasoner.toStringFile("snoutput/Dataset/{}/completedKB.txt".format(i))
        for j in range(0,len(supports.donelogs[2])):
            if len(reasoner.KBaLog[j]) > 0: writeFile("snoutput/Dataset/{}/Reasoner Steps/reasonerStep{}.txt".format(i,j+len(reasoner.sequenceLog)),supports.toString(supports.donelogs[2][j]))
            
        i = i + 1


    numpy.savez('ssaves/messData', kbs,seq_in,seq_out,localmaps,info,bad_KBs,bad_out)

    return kbs,seq_in,seq_out,localmaps,info,bad_KBs,bad_out

def readInputs():
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-s","--snomed", help="sample SNOMED dataset", action="store_true", default=False)
    parser.add_argument("-c","--concepts", help="number of concepts in namespace", type=int, default=21)
    parser.add_argument("-r","--roles", help="number of roles in namespace", type=int, default=8)
    parser.add_argument("-k","--kbs", help="number of KBs to generate and reason over", type=int, default=1000)
    parser.add_argument("-p","--perturb", help="amount  to disturb each kb for comparison", type=float, default=0.3)
    
    args = parser.parse_args()
    
    return args

if __name__ == "__main__":
    
            #[input KB len * 4, max reasoning steps (odd number) , max supports * 4 , max completion * 4 ]
    shapes = [80,3,124,48]
    
    args = readInputs()
    
    conceptSpace = args.concepts
    roleSpace = args.roles
    
    if args.perturb == 0.0:
        if args.snomed:
            sampleDataHardGenerator2Format(fsOWLReader(normalizeFS("SNOMED/SNOMED2012fs.owl","SNOMED/SNOrMED2012fs.owl")),args.kbs)
        else:
            makeSynData(args.kbs)
    else:
        if args.snomed:
            sampleDataHardGenerator2FormatPerturbed(fsOWLReader(normalizeFS("SNOMED/SNOMED2012fs.owl","SNOMED/SNOrMED2012fs.owl")),args.kbs,args.perturb)
        else:
            makeSynDataPerturbed(args.kbs,args.perturb)        
        
    print("Done")