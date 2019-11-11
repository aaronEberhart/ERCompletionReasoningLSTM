import os,sys,time,shutil
me = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,me+"/Generator")
sys.path.insert(0,me+"/Reasoner")

import re
import fileinput
import random
import numpy
import time
import multiprocessing
from functools import partial
from contextlib import contextmanager

from HardGenERator2 import *
from HardGenERator import *
from GenERator import *
from ReasonER import *
from NegativesGenERator import *
from JustificationFindER import *
from DependencyReducer import *

import tensorflow as tf

tf.logging.set_verbosity(tf.logging.ERROR)

from tensorflow.contrib import rnn
 
def makeRandomPredCompletions(shape,conceptSpace,roleSpace,syn):
    rando = []
    
    for i in range(shape[0]):
        kb = []
        for j in range(shape[1]):
            step = []
            inner = int(shape[2]/4)
            split = random.randint(0,inner)
            gen = GenERator(numCType1=split,numCType2=0,numCType3=(inner - split),numCType4=0,numRoleSub=0,numRoleChains=0,conceptNamespace=conceptSpace,roleNamespace=roleSpace,CTypeNull=[],CType1=[],CType2=[],CType3=[],CType4=[],roleSubs=[],roleChains=[])
            gen.genERate()
            for k in range(0,len(gen.CType1)):
                step.append([gen.CType1[k].antecedent.toString(),gen.CType1[k].consequent.toString()])
            for k in range(0,len(gen.CType3)):
                step.append([gen.CType3[k].antecedent.toString(),gen.CType3[k].consequent.role.toString(),gen.CType3[k].consequent.concept.toString()])
            kb.append(step)
        rando.append(kb)
        
    numpy.savez("saves/randoPred" if syn else "ssaves/randoPred",rando)   
    
    return rando

def makeRandomStrCompletions(shape,conceptSpace,roleSpace,syn):
    rando = []
    
    for i in range(shape[0]):
        kb = []
        for j in range(shape[1]):
            step = []
            inner = int(shape[2]/4)
            split = random.randint(0,inner)
            gen = GenERator(numCType1=split,numCType2=0,numCType3=(inner - split),numCType4=0,numRoleSub=0,numRoleChains=0,conceptNamespace=conceptSpace+1,roleNamespace=roleSpace+1,CTypeNull=[],CType1=[],CType2=[],CType3=[],CType4=[],roleSubs=[],roleChains=[])
            gen.genERate()
            for k in range(0,len(gen.CType1)):
                #print(gen.CType1[k].toString())
                if gen.CType1[k].antecedent.name == 0:
                    gen.CType1[k].antecedent.name = conceptSpace
                if gen.CType1[k].consequent.name == 0:
                    gen.CType1[k].consequent.name = conceptSpace
                step.append(gen.CType1[k].toString())
            for k in range(0,len(gen.CType3)):
                #print(gen.CType3[k].toString())
                if gen.CType3[k].antecedent.name == 0:
                    gen.CType3[k].antecedent.name = conceptSpace
                if gen.CType3[k].consequent.concept.name == 0:
                    gen.CType3[k].consequent.concept.name = conceptSpace
                if gen.CType3[k].consequent.role.name == 0:
                    gen.CType3[k].consequent.role.name = roleSpace
                step.append(gen.CType3[k].toString())
            kb.append(step)
        rando.append(kb) 
    
    numpy.savez("saves/randoStr" if syn else "ssaves/randoStr",rando)   
    
    return rando
    
def collapseLabelMap(localMap,classes,roles,labels):
    for mapping in localMap:
        for entry in mapping:
            mapping[entry] = labels[classes[mapping[entry]]] if mapping[entry] > 0 else labels[roles[mapping[entry]]]
    return localMap

def EQtoSC(line,new):
    if "ObjectIntersectionOf" in line[1]: x = intersectionSplit(line,new)
    else: x = "SubClassOf({} {})\nSubClassOf({} {})".format(line[0],line[1],line[1],line[0])
    #print(x)
    return x

'''
B ≡ A ⊓ ∃S.D

B ≡ A ⊓ X2
X2 ≡ ∃S.D

B ⊑ A
B ⊑ X2
A ⊓ X2 ⊑ B
X2 ⊑ ∃S.D
∃S.D ⊑ X2


A ≡ B ⊓ C ⊓ ∃S.D

A ≡ B ⊓ X1
X1 ≡ C ⊓ X2
X2 ≡ ∃S.D

A ⊑ B
A ⊑ X1
B ⊓ X1 ⊑ A
X1 ⊑ C
X1 ⊑ X2
C ⊓ X2 ⊑ X1
X2 ⊑ ∃S.D
∃S.D ⊑ X2
'''
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
    
def sampleDataHardGenerator2Format(trials,x):
    
    if os.path.isdir("snoutput/Dataset"): shutil.rmtree("snoutput/Dataset")
    if not os.path.isdir("snoutput"): os.mkdir("snoutput")
    if not os.path.isdir("snoutput/Dataset"): os.mkdir("snoutput/Dataset")     
    
    concepts,roles,info = x  
    localmaps = []
    seq_in = numpy.empty(trials,dtype=numpy.ndarray)
    seq_out = numpy.empty(trials,dtype=numpy.ndarray)
    kbs = numpy.empty([trials,80],dtype=numpy.float32)
    if not os.path.isdir("snoutput"): os.mkdir("snoutput")
    i = 0

    while i < trials:

        print("Sampling SNOMED to make KB"+str(i))

        if not os.path.isdir("snoutput/Dataset/{}".format(i)): os.mkdir("snoutput/Dataset/{}".format(i))
        
        localmap,generator = makeKBFromSamples(concepts,roles,info)
        
        generator.toFunctionalSyntaxFile("<http://www.randomOntology.com/SNOMED/Sample/random/{}/>".format(i),"snoutput/Dataset/{}/KB{}.owl".format(i,i))
        
        reasoner = ReasonER(generator,showSteps=True)

        reasoner.ERason()
        
        if len(reasoner.KBaLog) < 3:
            print("Sample has too few reasoner steps, trying again")
            continue
        
        if len(reasoner.KBaLog) > 3:
            print("Sample has too many reasoner steps, trying again")
            continue        

        supports = DependencyReducer(generator.getAllExpressions(),reasoner.sequenceLog,reasoner.KBsLog,reasoner.KBaLog)
        
        a,b = supports.toVector(generator.conceptNamespace,generator.roleNamespace)
        
        if len(a[0]) > 124:
            print("Sample has too many supports, trying again")
            continue
        
        if len(b[0]) > 48:
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
    kbs = numpy.empty([trials,80],dtype=numpy.float32)
    if not os.path.isdir("output"): os.mkdir("output")
    i = 0

    while i < trials:
        
        print("Making Random-Sequetial KB"+str(i))
        
        if not os.path.isdir("output/Dataset/{}".format(i)): os.mkdir("output/Dataset/{}".format(i))
        
        gen = GenERator(numCType1=2,numCType2=1,numCType3=2,numCType4=1,numRoleSub=1,numRoleChains=1,conceptNamespace=conceptSpace-3,roleNamespace=roleSpace-3,CTypeNull=[],CType1=[],CType2=[],CType3=[],CType4=[],roleSubs=[],roleChains=[])
        
        generator = HardGenERator2(rGenerator=gen,difficulty=1)
        
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
        
        if len(a[0]) > 124:
            print("KB has too many supports, trying again")
            continue
        
        if len(b[0]) > 48:
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

def getSynDataFromFile(filename):
    print("Loading data from "+filename)
    data = numpy.load(filename,allow_pickle=True)
    return data['arr_0'],data['arr_1'],data['arr_2']

def getSnoDataFromFile(filename):
    print("Loading data from "+filename)
    data = numpy.load(filename,allow_pickle=True)
    return data['arr_0'],data['arr_1'],data['arr_2'],data['arr_3'],data['arr_4']

def writeFile(filename,data):
    file = open(filename,"w")
    file.write(data)
    file.close()    

def writeVectorFileWithMap(filename,vector,mapping):
    file = open(filename,"w")
    for i in range(len(vector)):
        print(mapping[i])
        file.write("Trial: {}\n".format(i))
        for j in range(len(vector[i])):
            file.write("\tStep: {}\n".format(j))
            for k in range(len(vector[i][j])):
                file.write("\t\t{}\n".format(vector[i][j][k]))
        file.write("\n")
    file.close()
    
def writeVectorFile(filename,vector):
    file = open(filename,"w")
    for i in range(len(vector)):
        file.write("Trial: {}\n".format(i))
        for j in range(len(vector[i])):
            file.write("\tStep: {}\n".format(j))
            for k in range(len(vector[i][j])):
                file.write("\t\t{}\n".format(vector[i][j][k]))
        file.write("\n")
    file.close()
    
def pad(arr,maxlen1=0,maxlen2=0):

    for i in range(0,len(arr)):
        if len(arr[i]) > maxlen1: maxlen1 = len(arr[i])
        for j in range(0,len(arr[i])):
            if len(arr[i][j]) > maxlen2: maxlen2 = len(arr[i][j])
    
    newarr = numpy.zeros(shape=(len(arr),maxlen1,maxlen2),dtype=float)
    for i in range(0,len(arr)):
        for j in range(0,len(arr[i])):
            for k in range(0,len(arr[i][j])):
                newarr[i][j][k] = arr[i][j][k]

    return newarr

def vecToStatements(vec,conceptSpace,roleSpace):    
    four = []
    statementStr = []
    statementPred = []
    
    for i in range(len(vec)):
        trialStr = []
        trialPred = []
        for j in range(len(vec[i])):
            stepStr = []
            stepPred = []
            for k in range(len(vec[i][j])):
                if len(four) == 3:
                    four.append(vec[i][j][k])
                    pred,stri = convertToStatement(four,conceptSpace,roleSpace)
                    if stri != None: stepStr.append(stri)
                    if pred != None: stepPred.append(pred)
                    four = []                    
                else:
                    four.append(vec[i][j][k])
            if len(stepStr) > 0:
                trialStr.append(stepStr) 
            if len(stepPred) > 0: 
                trialPred.append(stepPred)          
        statementStr.append(trialStr)
        statementPred.append(trialPred)
        
    return statementPred,statementStr

def vecToStatementsWithLabels(vec,conceptSpace,roleSpace,labels):    
    four = []
    statementStr = []
    statementPred = []
    
    for i in range(len(vec)):
        trialStr = []
        trialPred = []
        for j in range(len(vec[i])):
            stepStr = []
            stepPred = []
            for k in range(len(vec[i][j])):
                if len(four) == 3:
                    four.append(vec[i][j][k])
                    pred,stri = convertToStatementWithLabels(four,conceptSpace,roleSpace,labels[i])
                    if stri != None: stepStr.append(stri)
                    if pred != None: stepPred.append(pred)
                    four = []                    
                else:
                    four.append(vec[i][j][k])
            if len(stepStr) > 0:
                trialStr.append(stepStr) 
            if len(stepPred) > 0: 
                trialPred.append(stepPred)          
        statementStr.append(trialStr)
        statementPred.append(trialPred)
        
    return statementPred,statementStr

def convertToStatementWithLabels(four,conceptSpace,roleSpace,labels):
    
    new = []
    text = []
    for number in four:
        if isinstance(number,numpy.float32): 
            number = number.item()
        if number < 0 and number >= -1:
            if int(number * roleSpace * -1) == 0: pass
            else: 
                number = int(number * roleSpace * -1)
                text.append(labels[-number]) if (-number) in labels.keys() else text.append("undefinedRelationTo{}".format(number))
                new.append("R{}".format(number))
        elif number > 0 and number <= 1:
            if int(number * conceptSpace) == 0: pass
            else: 
                number = int(number * conceptSpace)
                text.append(labels[number]) if number in labels.keys() else text.append("UndefinedConcept{}".format(number))
                new.append("C{}".format(number))   

    if  len(new) == 0:
        return None,None
    elif len(new) == 1:
        return new,None 
    elif len(new) == 2 and ((four[1] > 0 and four[2] > 0) or (four[1] < 0 and four[2] < 0)):
        return new,"{}\n\t\t\t{}".format(" ⊑ ".join(new)," is a ".join(text))
    elif len(new) == 2:
        return new,None
    elif len(new) == 3:
        if four[1] > 0 and four[2] < 0 and four[3] > 0:
            return new,"{} ⊑ ∃{}.{}\n\t\t\tif something is a {} then there is a {} that it is {}".format(new[0],new[1],new[2],text[0],text[2],text[1])
        elif four[1] > 0 and four[0] < 0 and four[2] > 0:
            return new,"∃{}.{} ⊑ {}\n\t\t\tif there is a {} that is {} another thing then the other thing is a {}".format(new[0],new[1],new[2],text[1],text[0],text[2])
        elif four[1] > 0 and four[0] > 0 and four[2] > 0:
            return new,"{} ⊓ {} ⊑ {}\n\t\t\tif something is both a {} and a {}, then it is also a {}".format(new[0],new[1],new[2],text[0],text[1],text[2])
        elif four[1] < 0 and four[0] < 0 and four[2] < 0:
            return new,"{} ∘ {} ⊑ {}\n\t\t\tif a first thing is {} anything that is {} a third thing, then the first is {} the third".format(new[0],new[1],new[2],text[0],text[1],text[2])
    
    return new,None

def convertToStatement(four,conceptSpace,roleSpace):
    
    new = []
    for number in four:
        if isinstance(number,numpy.float32): 
            number = number.item()
            #if number < 0: pass
        if number < 0 and number >= -1:
            if int(number * roleSpace * -1) == 0: pass
            else: new.append("R{}".format(int(number * roleSpace * -1)))
        elif number > 0 and number <= 1:
            if int(number * conceptSpace) == 0: pass
            else: new.append("C{}".format(int(number * conceptSpace)))   

    if  len(new) == 0:
        return None,None
    elif len(new) == 1:
        return new,None 
    elif len(new) == 2 and ((four[1] > 0 and four[2] > 0) or (four[1] < 0 and four[2] < 0)):
        return new," ⊑ ".join(new)
    elif len(new) == 2:
        return new,None
    elif len(new) == 3:
        if four[1] > 0 and four[2] < 0 and four[3] > 0:
            return new,"{} ⊑ ∃{}.{}".format(new[0],new[1],new[2])
        elif four[1] > 0 and four[0] < 0 and four[2] > 0:
            return new,"∃{}.{} ⊑ {}".format(new[0],new[1],new[2])
        elif four[1] > 0 and four[0] > 0 and four[2] > 0:
            return new,"{} ⊓ {} ⊑ {}".format(new[0],new[1],new[2])
        elif four[1] < 0 and four[0] < 0 and four[2] < 0:
            return new,"{} ∘ {} ⊑ {}".format(new[0],new[1],new[2])
    
    return new,None#" x ".join(new)
    
def splitTensors(inputs,outputs, size):
    inTest, inTrain = numpy.split(inputs,[int(len(inputs)*size)])
    outTest, outTrain = numpy.split(outputs,[int(len(outputs)*size)])
    return inTrain, inTest, outTrain, outTest

#https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python
def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1       # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

def levenshteinIgnoreNum(s1, s2):
    if len(s1) < len(s2):
        return levenshteinIgnoreNum(s2, s1)
    
    s1,s2 = convertAllNumsToAtoms(s1,s2)
    
    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1       # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

def convertAllNumsToAtoms(s1,s2):
    dic = {}
    a = 'a'
    st = ""
    longer = False
    for i in range(len(s1)):
        if s1[i].isdigit() and not longer:
            st = s1[i]
            for j in range(i+1,len(s1)):
                if s1[j].isdigit(): 
                    longer = True
                    st = st + s1[j]
                else: break
            if not int(st) in dic.keys():
                dic[int(st)] = a
                a = chr(ord(a) + 1)
        elif not s1[i].isdigit(): longer = False
    longer = False
    for i in range(len(s2)):
        if s2[i].isdigit() and not longer:
            st = s2[i]
            for j in range(i+1,len(s2)):
                if s2[j].isdigit(): 
                    longer = True
                    st = st + s2[j]
                else: break
            if not int(st) in dic.keys():
                dic[int(st)] = a
                a = chr(ord(a) + 1)
        elif not s1[i].isdigit(): longer = False
    
    for key in sorted(dic, reverse=True):
        s1 = s1.replace(str(key),dic[key])
        s2 = s2.replace(str(key),dic[key])
    s1 = s1.replace(" ","")
    s2 = s2.replace(" ","")
    return s1,s2

def findBestMatchNoNums(statement,reasonerSteps):
    return min(map(partial(levenshteinIgnoreNum,statement),reasonerSteps))

def levDistanceNoNums(shape,newStatements,trueStatements,conceptSpace,roleSpace,syn):
    
    if (syn and os.path.isfile("saves/randoStr.npz")) or os.path.isfile("ssaves/randoStr.npz"):
        rando = numpy.load("saves/randoStr.npz" if syn else "ssaves/randoStr.npz",allow_pickle=True)
        rando = rando['arr_0'].tolist()
    else:
        rando = makeRandomStrCompletions(shape,conceptSpace,roleSpace,syn)
    
    flatTrue = [[item for sublist in x for item in sublist] for x in trueStatements]
    flatRand = [[item for sublist in x for item in sublist] for x in rando]
    flatNew = [[item for sublist in x for item in sublist] for x in newStatements]
    
    levTR = 0
    levRT = 0
    levTN = 0
    levNT = 0
    
    sizeRan = 0
    sizeTrue = 0
    sizeNew = 0
    
    for i in range(len(rando)):
        for j in range(len(rando[i])):
            for k in range(len(rando[i][j])):    
                if len(trueStatements) > i and len(trueStatements[i]) > j and len(trueStatements[i][j]) > k: #FOR VERY TRUE STATEMENT
                    sizeTrue = sizeTrue + 1
                    levTR = levTR + findBestMatchNoNums(trueStatements[i][j][k],flatRand[i])                    #compare to best match in random                  
                    if (len(newStatements) > i and len(newStatements[i]) > 0):
                        levTN = levTN + findBestMatchNoNums(trueStatements[i][j][k],flatNew[i])        #if there are predictions for this KB, compare to best match in there
                    else:
                        levTN = levTN + levenshteinIgnoreNum(trueStatements[i][j][k],'')                     #otherwise compare with no prediction
                        
                if len(newStatements) > i and len(newStatements[i]) > j and len(newStatements[i][j]) > k:    #FOR EVERY PREDICTION
                    sizeNew = sizeNew + 1
                    if (len(trueStatements) > i and len(trueStatements[i]) > 0):
                        levNT = levNT + findBestMatchNoNums(newStatements[i][j][k],flatTrue[i])        #if there are true values for this KB, compare to best match in there
                    else:
                        levNT = levNT + levenshteinIgnoreNum(newStatements[i][j][k],'')                      #otherwise compare with no true value
                
                if (len(trueStatements) > i and len(trueStatements[i]) > 0):
                    levRT = levRT + findBestMatchNoNums(rando[i][j][k],flatTrue[i])                    #if there is a true KB corresponding to this random data, compare the random statement to its best match in the true statements
                    sizeRan = sizeRan + 1
                    
    return levTR,levRT,levTN,levNT,sizeTrue,sizeNew,sizeRan

def levDistance(shape,newStatements,trueStatements,conceptSpace,roleSpace,syn):
    
    if (syn and os.path.isfile("saves/randoStr.npz")) or os.path.isfile("ssaves/randoStr.npz"):
        rando = numpy.load("saves/randoStr.npz" if syn else "ssaves/randoStr.npz",allow_pickle=True)
        rando = rando['arr_0'].tolist()
    else:
        rando = makeRandomStrCompletions(shape,conceptSpace,roleSpace,syn)
    
    flatTrue = [[item for sublist in x for item in sublist] for x in trueStatements]
    flatRand = [[item for sublist in x for item in sublist] for x in rando]
    flatNew = [[item for sublist in x for item in sublist] for x in newStatements]
    
    levTR = 0
    levRT = 0
    levTN = 0
    levNT = 0
    
    countRan = 0
    countTrue = 0
    countNew = 0    
    
    for i in range(len(rando)):
        for j in range(len(rando[i])):
            for k in range(len(rando[i][j])):    
                if len(trueStatements) > i and len(trueStatements[i]) > j and len(trueStatements[i][j]) > k: #FOR VERY TRUE STATEMENT
                    countTrue = countTrue + 1
                    countRan = countRan + 1
                    levTR = levTR + findBestMatch(trueStatements[i][j][k],flatRand[i])                       #compare to best match in random and vice versa                  
                    levRT = levRT + findBestMatch(rando[i][j][k],flatTrue[i])
                    
                    if (len(newStatements) > i and len(newStatements[i]) > 0):
                        levTN = levTN + findBestMatch(trueStatements[i][j][k],flatNew[i])                   #if there are predictions for this KB, compare to best match in there
                    else: levTN = levTN + levenshtein(trueStatements[i][j][k],'')                           #otherwise compare with no prediction
                        
                if len(newStatements) > i and len(newStatements[i]) > j and len(newStatements[i][j]) > k:   #FOR EVERY PREDICTION
                    countNew = countNew + 1
                    if (len(trueStatements) > i and len(trueStatements[i]) > 0):
                        levNT = levNT + findBestMatch(newStatements[i][j][k],flatTrue[i])                   #if there are true values for this KB, compare to best match in there
                    else: levNT = levNT + levenshtein(newStatements[i][j][k],'')                            #otherwise compare with no true value
               
    return levTR,levRT,levTN,levNT,countTrue,countNew,countRan

def findBestMatch(statement,reasonerSteps):
    return min(map(partial(levenshtein,statement),reasonerSteps))

def custom(s1,s2,conceptSpace,roleSpace):
   
    if len(s1) < len(s2): return custom(s2,s1,conceptSpace,roleSpace)
    
    dist = 0
    
    for k in range(len(s1)):
        string1 = s1[k]
        string2 = s2[k] if len(s2) > k else ""
        if string2 == "":
            dist = dist + (conceptSpace if string1[0] == 'C' else roleSpace) + int(''.join(x for x in string1 if x.isdigit()))
        else:
            if (string1[0] == 'C' and string2[0] == 'R') or (string1[0] == 'R' and string2[0] == 'C'): 
                dist = dist + abs(int(''.join(x for x in string1 if x.isdigit())) + int(''.join(x for x in string2 if x.isdigit())))
            else: 
                dist = dist + abs(int(''.join(x for x in string1 if x.isdigit())) -  int(''.join(x for x in string2 if x.isdigit())))
                
    
    return dist

def customDistance(shape,newPred,truePred,conceptSpace,roleSpace,syn):
    
    if (syn and os.path.isfile("saves/randoPred.npz")) or os.path.isfile("ssaves/randoPred.npz"):
        rando = numpy.load("saves/randoPred.npz" if syn else "ssaves/randoPred.npz",allow_pickle=True)
        rando = rando['arr_0'].tolist()
    else:
        rando = makeRandomPredCompletions(shape,conceptSpace,roleSpace,syn)    
    
    flatTrue = [[item for sublist in x for item in sublist] for x in truePred]
    flatRand = [[item for sublist in x for item in sublist] for x in rando]
    flatNew = [[item for sublist in x for item in sublist] for x in newPred]
    
    custTR = 0
    custRT = 0
    custTN = 0
    custNT = 0
    
    countRan = 0
    countTrue = 0
    countNew = 0      
    
    for i in range(len(rando)):
        for j in range(len(rando[i])):
            for k in range(len(rando[i][j])):
                if (len(truePred) > i and len(truePred[i]) > j and len(truePred[i][j]) > k):
                    countTrue = countTrue + 1
                    countRan = countRan + 1
                    custTR = custTR + findBestPredMatch(truePred[i][j][k],flatRand[i],conceptSpace,roleSpace)
                    custRT = custRT + findBestPredMatch(rando[i][j][k],flatTrue[i],conceptSpace,roleSpace)                    
                    if (len(newPred) > i and len(newPred[i]) > 0):
                        custTN = custTN + findBestPredMatch(truePred[i][j][k],flatNew[i],conceptSpace,roleSpace)
                    else: 
                        custTN = custTN + custom(truePred[i][j][k],[""]*len(truePred[i][j][k]),conceptSpace,roleSpace)
                if (len(newPred) > i and len(newPred[i]) > j and len(newPred[i][j]) > k):
                    countNew = countNew + 1
                    if (len(truePred) > i and len(truePred[i]) > 0):
                        custNT = custNT + findBestPredMatch(newPred[i][j][k],flatTrue[i],conceptSpace,roleSpace)
                    else:
                        custNT = custNT + custom(newPred[i][j][k],[""]*len(newPred[i][j][k]),conceptSpace,roleSpace)                    
                    
    return custTR,custRT,custTN,custNT,countTrue,countNew,countRan

def findBestPredMatch(statement,otherKB,conceptSpace,roleSpace):
    return min(map(partial(levenshtein,statement),otherKB))

def repeatAndSplitKBs(kbs,steps,splitSize):
    newKBs = numpy.empty([kbs.shape[0],steps,kbs.shape[1]],dtype=numpy.float32)
    for i in range(len(newKBs)):
        for j in range(steps):
            newKBs[i][j] = kbs[i]
    return numpy.split(newKBs,[int(len(newKBs)*splitSize)])

def formatDataSynth(log,conceptSpace,roleSpace,KBs,supports,output):
    
    fileShapes1 = [3,124,48]#[0,0,0]#

    KBs_test,KBs_train = repeatAndSplitKBs(KBs,fileShapes1[0],0.33)

    X_train, X_test, y_train,y_test = splitTensors(supports, output, 0.33)

    X_train = pad(X_train,maxlen1=fileShapes1[0],maxlen2=fileShapes1[1])
    X_test = pad(X_test,maxlen1=fileShapes1[0],maxlen2=fileShapes1[1])

    y_train = pad(y_train,maxlen1=fileShapes1[0],maxlen2=fileShapes1[2])
    y_test = pad(y_test,maxlen1=fileShapes1[0],maxlen2=fileShapes1[2])

    print("KBs shape:\t\t{}\nExtended KBs shape:\t{}{}\nDependencies shape:\t{}{}\nOutput shape:\t\t{}{}\n\n".format(KBs.shape,KBs_train.shape,KBs_test.shape,X_train.shape,X_test.shape,y_train.shape,y_test.shape))
    log.write("KBs shape:\t\t{}\nExtended KBs shape:\t{}{}\nDependencies shape:\t{}{}\nOutput shape:\t\t{}{}\n\n".format(KBs.shape,KBs_train.shape,KBs_test.shape,X_train.shape,X_test.shape,y_train.shape,y_test.shape))

    KBvec,KBstr = vecToStatements(KBs_test,conceptSpace,roleSpace)
    truePreds,trueStatements = vecToStatements(y_test,conceptSpace,roleSpace)
    placeholder,inputs = vecToStatements(X_test,conceptSpace,roleSpace)

    writeVectorFile("output/KBsIn.txt",KBstr)
    writeVectorFile("output/supports.txt",inputs)
    writeVectorFile("output/reasonerCompletion.txt",trueStatements)
    
    return KBs_test,KBs_train,X_train,X_test,y_train,y_test,truePreds,trueStatements

def formatDataSno(log,conceptSpace,roleSpace,KBs,supports,output,localMaps,stats):
    
    labels = collapseLabelMap(localMaps,stats[0][2],stats[1][2],stats[4][1])
    
    fileShapes1 = [3,124,48]#

    KBs_test,KBs_train = repeatAndSplitKBs(KBs,fileShapes1[0],0.33)
    
    testLabels = labels[:len(KBs_test)]
    trainLabels = labels[len(KBs_test):]
    
    X_train, X_test, y_train, y_test = splitTensors(supports, output, 0.33)
    
    X_train = pad(X_train,maxlen1=fileShapes1[0],maxlen2=fileShapes1[1])
    X_test = pad(X_test,maxlen1=fileShapes1[0],maxlen2=fileShapes1[1])
    
    y_train = pad(y_train,maxlen1=fileShapes1[0],maxlen2=fileShapes1[2])
    y_test = pad(y_test,maxlen1=fileShapes1[0],maxlen2=fileShapes1[2])
    
    print("KBs shape:\t\t{}\nExtended KBs shape:\t{}{}\nDependencies shape:\t{}{}\nOutput shape:\t\t{}{}\n\n".format(KBs.shape,KBs_train.shape,KBs_test.shape,X_train.shape,X_test.shape,y_train.shape,y_test.shape))
    log.write("KBs shape:\t\t{}\nExtended KBs shape:\t{}{}\nDependencies shape:\t{}{}\nOutput shape:\t\t{}{}\n\n".format(KBs.shape,KBs_train.shape,KBs_test.shape,X_train.shape,X_test.shape,y_train.shape,y_test.shape))

    KBvec,KBstr = vecToStatementsWithLabels(KBs_test,conceptSpace,roleSpace,testLabels)
    preds,trueStatements = vecToStatementsWithLabels(y_test,conceptSpace,roleSpace,testLabels)
    placeholder,inputs = vecToStatementsWithLabels(X_test,conceptSpace,roleSpace,testLabels)
    
    writeVectorFile("snoutput/KBsIn.txt",KBstr)
    writeVectorFile("snoutput/supports.txt",inputs)
    writeVectorFile("snoutput/reasonerCompletion.txt",trueStatements)
    
    truePreds,trueStatements = vecToStatements(y_test,conceptSpace,roleSpace)
    
    return KBs_test,KBs_train,X_train,X_test,y_train,y_test,truePreds,trueStatements
  
def formatDataSyn2Sno(log,conceptSpace,roleSpace,KBs,supports,output,sKBs,ssupports,soutput,localMaps,stats):

    labels = collapseLabelMap(localMaps,stats[0][2],stats[1][2],stats[4][1])    
    
    fileShapes1 = [3,124,48]
    
    KBs_test,KBs_train = repeatAndSplitKBs(KBs,fileShapes1[0],0.33)    
    KBs_test,a = repeatAndSplitKBs(sKBs,fileShapes1[0],0.33)
    
    testLabels = labels[:len(KBs_test)]
    trainLabels = labels[len(KBs_test):]    
                            
    X_train,X_test, y_train,y_test = splitTensors(supports, output, 0.33)
    a,X_test,a,y_test = splitTensors(ssupports,soutput,0.33)
    
    X_train = pad(X_train,maxlen1=fileShapes1[0],maxlen2=fileShapes1[1])
    X_test = pad(X_test,maxlen1=fileShapes1[0],maxlen2=fileShapes1[1])
    
    y_train = pad(y_train,maxlen1=fileShapes1[0],maxlen2=fileShapes1[2])
    y_test = pad(y_test,maxlen1=fileShapes1[0],maxlen2=fileShapes1[2])
    
    print("KBs shape:\t\t{}\nExtended KBs shape:\t{}{}\nDependencies shape:\t{}{}\nOutput shape:\t\t{}{}\n\n".format(KBs.shape,KBs_train.shape,KBs_test.shape,X_train.shape,X_test.shape,y_train.shape,y_test.shape))
    log.write("KBs shape:\t\t{}\nExtended KBs shape:\t{}{}\nDependencies shape:\t{}{}\nOutput shape:\t\t{}{}\n\n".format(KBs.shape,KBs_train.shape,KBs_test.shape,X_train.shape,X_test.shape,y_train.shape,y_test.shape))
    
    truePreds,trueStatements = vecToStatements(y_test,conceptSpace,roleSpace)  
    
    return KBs_test,KBs_train,X_train,X_test,y_train,y_test,truePreds,trueStatements

def formatDataSno2Syn(log,conceptSpace,roleSpace,KBs,supports,output,sKBs,ssupports,soutput,localMaps,stats):
    labels = collapseLabelMap(localMaps,stats[0][2],stats[1][2],stats[4][1])
    
    fileShapes1 = [3,124,48]

    a,KBs_train = repeatAndSplitKBs(KBs,fileShapes1[0],0.33)
    KBs_test,a = repeatAndSplitKBs(sKBs,fileShapes1[0],0.33)
    
    testLabels = labels[:len(KBs_test)]
    trainLabels = labels[len(KBs_test):]
    
    X_train, X_test, y_train,y_test = splitTensors(supports, output, 0.33)
    a,X_test,a,y_test = splitTensors(ssupports,soutput,0.33)
    
    X_train = pad(X_train,maxlen1=fileShapes1[0],maxlen2=fileShapes1[1])
    X_test = pad(X_test,maxlen1=fileShapes1[0],maxlen2=fileShapes1[1])
    
    y_train = pad(y_train,maxlen1=fileShapes1[0],maxlen2=fileShapes1[2])
    y_test = pad(y_test,maxlen1=fileShapes1[0],maxlen2=fileShapes1[2])
    
    print("KBs shape:\t\t{}\nExtended KBs shape:\t{}{}\nDependencies shape:\t{}{}\nOutput shape:\t\t{}{}\n\n".format(KBs.shape,KBs_train.shape,KBs_test.shape,X_train.shape,X_test.shape,y_train.shape,y_test.shape))
    log.write("KBs shape:\t\t{}\nExtended KBs shape:\t{}{}\nDependencies shape:\t{}{}\nOutput shape:\t\t{}{}\n\n".format(KBs.shape,KBs_train.shape,KBs_test.shape,X_train.shape,X_test.shape,y_train.shape,y_test.shape))  
    
    truePreds,trueStatements = vecToStatements(y_test,conceptSpace,roleSpace)
    
    return KBs_test,KBs_train,X_train,X_test,y_train,y_test,truePreds,trueStatements

def distanceEvaluations(log,shape,newPreds,truePreds,newStatements,trueStatements,conceptSpace,roleSpace,syn):
    
    levTR,levRT,levTN,levNT,sizeTrue,sizeNew,sizeRan = levDistanceNoNums(shape,newStatements,trueStatements,conceptSpace,roleSpace,syn)          
    
    log.write("\n\tNo Nums\n\n\tLevenshtein Distance From Reasoner to Random Data:     {}\n\tLevenshtein Distance From Random to Reasoner Data:     {}\n\tLevenshtein Distance From Reasoner to Predicted Data:  {}\n\tLevenshtein Distance From Prediction to Reasoner Data: {}\n".format(levTR,levRT,levTN,levNT)) 
    log.write("\n\tAverage Levenshtein Distance From Reasoner to Random Statement:    {}\n\tAverage Levenshtein Distance From Random to Reasoner Statement:    {}\n\tAverage Levenshtein Distance From Reasoner to Predicted Statement: {}\n\tAverage Levenshtein Distance From Prediction to Reasoner Statement:{}\n".format(levTR/sizeTrue,levRT/sizeRan,levTN/sizeTrue,0 if sizeNew == 0 else levNT/sizeNew))
    
    levTR2,levRT2,levTN2,levNT2,sizeTrue2,sizeNew2,sizeRan2 = levDistance(shape,newStatements,trueStatements,conceptSpace,roleSpace,syn)          
    
    log.write("\n\tNums\n\n\tLevenshtein Distance From Reasoner to Random Data:     {}\n\tLevenshtein Distance From Random to Reasoner Data:     {}\n\tLevenshtein Distance From Reasoner to Predicted Data:  {}\n\tLevenshtein Distance From Prediction to Reasoner Data: {}\n".format(levTR2,levRT2,levTN2,levNT2)) 
    log.write("\n\tAverage Levenshtein Distance From Reasoner to Random Statement:    {}\n\tAverage Levenshtein Distance From Random to Reasoner Statement:    {}\n\tAverage Levenshtein Distance From Reasoner to Predicted Statement: {}\n\tAverage Levenshtein Distance From Prediction to Reasoner Statement:{}\n".format(levTR2/sizeTrue2,levRT2/sizeRan2,levTN2/sizeTrue2,0 if sizeNew2 == 0 else levNT2/sizeNew2))
    
    custTR,custRT,custTN,custNT,countTrue,countNew,countRan = customDistance(shape,newPreds,truePreds,conceptSpace,roleSpace,syn)
    
    log.write("\n\tCustom\n\n\tCustom Distance From Reasoner to Random Data:    {}\n\tCustom Distance From Random to Reasoner Data:    {}\n\tCustom Distance From Reasoner to Predicted Data: {}\n\tCustom Distance From Predicted to Reasoner Data: {}\n".format(custTR,custRT,custTN,custNT)) 
    log.write("\n\tAverage Custom Distance From Reasoner to Random Statement:    {}\n\tAverage Custom Distance From Random to Reasoner Statement:    {}\n\tAverage Custom Distance From Reasoner to Predicted Statement: {}\n\tAverage Custom Distance From Prediction to Reasoner Statement:{}\n".format(custTR/countTrue,custRT/countRan,custTN/countTrue,0 if countNew == 0 else custNT/countNew))
    
    return array([array([levTR,levRT,levTN,levNT,sizeTrue,sizeNew,sizeRan]),array([levTR2,levRT2,levTN2,levNT2,sizeTrue2,sizeNew2,sizeRan2]),array([custTR,custRT,custTN,custNT,countTrue,countNew,countRan])])
def trainingStats(log,mseNew,mse0,mseL):
    log.write("\n\tTraining Statistics\n\n\tPrediction\tMean Squared Error:\t{}\n\tTraining\tLearned Reduction MSE:\t{}\n\t\t\tIncrease MSE on Test:\t{}\n\t\t\tPercent Change MSE:\t{}\n".format(numpy.float32(mseNew),mse0-mseL,numpy.float32(mseNew)-mseL,(mseL - mse0)/mse0*100))
        
def shallowSystem(n_epochs0,learning_rate0,log,conceptSpace,roleSpace,allTheData,syn,n):
    KBs_test,KBs_train,X_train,X_test,y_train,y_test,truePreds,trueStatements = allTheData
    
    log.write("Stepwise LSTM\n\n\tFitting KBs to Reasoner Supports\n\n")
    print("")
    
    n_neurons0 = X_train.shape[2]
    
    X0 = tf.placeholder(tf.float32, shape=[None,KBs_train.shape[1],KBs_train.shape[2]])
    y0 = tf.placeholder(tf.float32, shape=[None,X_train.shape[1],X_train.shape[2]])
    
    outputs0, states0 = tf.nn.dynamic_rnn(tf.contrib.rnn.LSTMCell(num_units=n_neurons0), X0, dtype=tf.float32)
    
    loss0 = tf.losses.mean_squared_error(y0,outputs0)
    optimizer0 = tf.train.AdamOptimizer(learning_rate=learning_rate0)
    training_op0 = optimizer0.minimize(loss0)
    
    init0 = tf.global_variables_initializer()
    
    saver = tf.train.Saver()
    
    with tf.Session() as sess:
        init0.run()
        mse0 = 0
        mseL = 0
        for epoch in range(n_epochs0):  
            print("Piecewise System\tEpoch: {}".format(epoch))
            ynew,a = sess.run([outputs0,training_op0],feed_dict={X0: KBs_train,y0: X_train})
            mse = loss0.eval(feed_dict={outputs0: ynew, y0: X_train})
            if epoch == 0: mse0 = mse
            if epoch == n_epochs0 - 1: mseL = mse
            log.write("\t\tEpoch: {}\tMean Squared Error:\t{}\n".format(epoch,mse))
            if mse < 0.0001:
                mseL = mse
                break
        
        print("\nTesting first half\n")
        
        y_pred = sess.run(outputs0,feed_dict={X0: KBs_test,y0: X_test}) 
        mseNew = loss0.eval(feed_dict={outputs0: y_pred, y0: X_test})
        newPreds,newStatements = vecToStatements(y_pred,conceptSpace,roleSpace)        
        
        trainingStats(log,mseNew,mse0,mseL)
                      
        writeVectorFile("{}output/learnedSupportsP[{}].txt".format("" if syn else "sn",n),newStatements)
        
        numpy.savez("saves/halfway.npz" if syn else "ssaves/halfway.npz", y_pred)
      
    tf.reset_default_graph()
    
    log.write("\n\tFitting Reasoner Supports to KB Completion\n\n")
    
    n_neurons1 = y_train.shape[2]
    
    X1 = tf.placeholder(tf.float32, shape=[None,X_train.shape[1],X_train.shape[2]])
    y1 = tf.placeholder(tf.float32, shape=[None,y_train.shape[1],y_train.shape[2]])
    
    outputs1, states1 = tf.nn.dynamic_rnn(tf.contrib.rnn.LSTMCell(num_units=n_neurons1), X1, dtype=tf.float32)
    
    loss1 = tf.losses.mean_squared_error(y1,outputs1)
    optimizer1 = tf.train.AdamOptimizer(learning_rate=learning_rate0)
    training_op1 = optimizer1.minimize(loss1)    
    
    init1 = tf.global_variables_initializer()
    
    with tf.Session() as sess:    
        init1.run()
        mse0 = 0
        mseL = 0
        for epoch in range(n_epochs0): 
            print("Piecewise System\tEpoch: {}".format(epoch+n_epochs0))
            ynew,a = sess.run([outputs1,training_op1],feed_dict={X1: X_train,y1: y_train})
            mse = loss1.eval(feed_dict={outputs1: ynew, y1: y_train})
            if epoch == 0: mse0 = mse
            if epoch == n_epochs0 - 1: mseL = mse
            log.write("\t\tEpoch: {}\tMean Squared Error:\t{}\n".format(epoch+n_epochs0,mse))
            if mse < 0.0001:
                mseL = mse
                break
        
        print("\nTesting second half")
        y_pred = sess.run(outputs1,feed_dict={X1: X_test})  
        mseNew = loss1.eval(feed_dict={outputs1: y_pred, y1: y_test})
        
        trainingStats(log,mseNew,mse0,mseL)
        
        print("\nEvaluating Result")
        
        log.write("\n\tTESTING REASONER SUPPORT DATA\n\n")    
        
        newPreds,newStatements = vecToStatements(y_pred,conceptSpace,roleSpace)
        
        writeVectorFile("{}output/predictedOutLeftOverSupportTest[{}].txt".format("" if syn else "sn",n),newStatements)
        
        evals = distanceEvaluations(log,y_pred.shape,newPreds,truePreds,newStatements,trueStatements,conceptSpace,roleSpace,syn)        
        
        data = numpy.load("saves/halfway.npz" if syn else "ssaves/halfway.npz",allow_pickle=True)
        data = data['arr_0'] 
        
        log.write("\n\tTESTING SAVED SUPPORT DATA FROM PREVIOUS LSTM\n\n")
        
        y_pred = sess.run(outputs1,feed_dict={X1: data})
        mseNew = loss1.eval(feed_dict={outputs1: y_pred, y1: y_test})
        
        log.write("\n\tTesting Statistics\n\n\t\t\tIncrease MSE on Saved:\t{}\n".format(numpy.float32(mseNew)-mseL))        
        
        newPreds,newStatements = vecToStatements(y_pred,conceptSpace,roleSpace)
        
        writeVectorFile("{}output/predicteionSavedKBPipeliine[{}].txt".format("" if syn else "sn",n),newStatements)
        
        return evals,distanceEvaluations(log,y_pred.shape,newPreds,truePreds,newStatements,trueStatements,conceptSpace,roleSpace,syn)
        
def deepSystem(n_epochs2,learning_rate2,log,conceptSpace,roleSpace,allTheData,syn,n):
    KBs_test,KBs_train,X_train,X_test,y_train,y_test,truePreds,trueStatements = allTheData
    
    log.write("\nDeep LSTM\n\n\tFitting KBs to hidden layer to KB Completions\n\n")
    print("")
    
    X0 = tf.placeholder(tf.float32, shape=[None,KBs_train.shape[1],KBs_train.shape[2]])
    y1 = tf.placeholder(tf.float32, shape=[None,y_train.shape[1],y_train.shape[2]])
    
    outputs2, states2 = tf.nn.dynamic_rnn(tf.contrib.rnn.MultiRNNCell([tf.contrib.rnn.LSTMCell(num_units=X_train.shape[2]),tf.contrib.rnn.LSTMCell(num_units=y_train.shape[2])]), X0, dtype=tf.float32)
    
    loss2 = tf.losses.mean_squared_error(y1,outputs2)
    optimizer2 = tf.train.AdamOptimizer(learning_rate=learning_rate2)
    training_op2 = optimizer2.minimize(loss2)
    
    init2 = tf.global_variables_initializer()
    
    with tf.Session() as sess:    
        init2.run()
        mse0 = 0
        mseL = 0
        for epoch in range(n_epochs2): 
            print("Deep System\t\tEpoch: {}".format(epoch))
            ynew,a = sess.run([outputs2,training_op2],feed_dict={X0: KBs_train,y1: y_train})
            mse = loss2.eval(feed_dict={outputs2: ynew, y1: y_train})
            if epoch == 0: mse0 = mse
            if epoch == n_epochs2 - 1: mseL = mse
            log.write("\t\tEpoch: {}\tMean Squared Error:\t{}\n".format(epoch,mse))
            if mse < 0.0001:
                mseL = mse
                break
        
        print("\nEvaluating Result\n")
        
        y_pred = sess.run(outputs2,feed_dict={X0: KBs_test})  
        mseNew = loss2.eval(feed_dict={outputs2: y_pred, y1: y_test})
        
        trainingStats(log,mseNew,mse0,mseL)
        
        log.write("\n\tTESTING UNTRAINED KB DATA\n\n")    
          
        newPreds,newStatements = vecToStatements(y_pred,conceptSpace,roleSpace)
        
        writeVectorFile("output/predictionDeepArchitecture[{}].txt".format("" if syn else "sn",n),newStatements)
        
        return distanceEvaluations(log,y_pred.shape,newPreds,truePreds,newStatements,trueStatements,conceptSpace,roleSpace,syn)

def runOnce(log,epochs,learningRate,conceptSpace,roleSpace,syn,mix):
    
    if log == None: log = open(os.devnull,"w")
    
    if syn:
        if not os.path.isdir("output"): os.mkdir("output")
        KBs,supports,output = getSynDataFromFile('saves/data.npz')
        if mix:
            sKBs,ssupports,soutput,localMaps,stats = getSnoDataFromFile('ssaves/data.npz')
            allTheData = formatDataSyn2Sno(log,conceptSpace,roleSpace,KBs,supports,output,sKBs,ssupports,soutput,localMaps,stats)  
        else: allTheData =  formatDataSynth(log,conceptSpace,roleSpace,KBs,supports,output)
    else:
        if not os.path.isdir("snoutput"): os.mkdir("snoutput")
        KBs,supports,output,localMaps,stats = getSnoDataFromFile('ssaves/data.npz')
        if mix:
            sKBs,ssupports,soutput = getSynDataFromFile('saves/data.npz')
            allTheData = formatDataSno2Syn(log,conceptSpace,roleSpace,KBs,supports,output,sKBs,ssupports,soutput,localMaps,stats)
        else: allTheData = formatDataSno(log,conceptSpace,roleSpace,KBs,supports,output,localMaps,stats)
    
    shallowSystem(int(epochs/2),learningRate,log,conceptSpace,roleSpace,allTheData,syn,1)    
    
    tf.reset_default_graph()
    
    deepSystem(epochs,learningRate/2,log,conceptSpace,roleSpace,allTheData,syn,1)
    
    log.close()
    
    print("\nDone")

def runNthTime(log,epochs,learningRate,conceptSpace,roleSpace,nthData,syn):
    if log == None: log = open(os.devnull,"w")
    
    eval1,eval2 = shallowSystem(int(epochs/2),learningRate,log,conceptSpace,roleSpace,nthData,syn)    
    
    tf.reset_default_graph()
    
    eval3 = deepSystem(epochs,learningRate/2,log,conceptSpace,roleSpace,nthData,syn)
    
    tf.reset_default_graph()
    
    log.close()  
    
    return eval1,eval2,eval3
    
def formatDataN(KBs,supports,outputs,labels,sKBs,ssupports,soutputs):
    fileShapes1 = [3,124,48]

    KBs_test,KBs_train = repeatAndSplitKBs(KBs,fileShapes1[0],0.33)    
    KBs_test,a = repeatAndSplitKBs(sKBs,fileShapes1[0],0.33)

    testLabels = labels[:len(KBs_test)]
    trainLabels = labels[len(KBs_test):]    

    X_train,X_test, y_train,y_test = splitTensors(supports,output, 0.33)
    a,X_test,a,y_test = splitTensors(ssupports,soutput,0.33)

    X_train = pad(X_train,maxlen1=fileShapes1[0],maxlen2=fileShapes1[1])
    X_test = pad(X_test,maxlen1=fileShapes1[0],maxlen2=fileShapes1[1])

    y_train = pad(y_train,maxlen1=fileShapes1[0],maxlen2=fileShapes1[2])
    y_test = pad(y_test,maxlen1=fileShapes1[0],maxlen2=fileShapes1[2])

    print("KBs shape:\t\t{}\nExtended KBs shape:\t{}{}\nDependencies shape:\t{}{}\nOutput shape:\t\t{}{}\n\n".format(KBs.shape,KBs_train.shape,KBs_test.shape,X_train.shape,X_test.shape,y_train.shape,y_test.shape))
    log.write("KBs shape:\t\t{}\nExtended KBs shape:\t{}{}\nDependencies shape:\t{}{}\nOutput shape:\t\t{}{}\n\n".format(KBs.shape,KBs_train.shape,KBs_test.shape,X_train.shape,X_test.shape,y_train.shape,y_test.shape))

    truePreds,trueStatements = vecToStatements(y_test,conceptSpace,roleSpace)  

    return KBs_test,KBs_train,X_train,X_test,y_train,y_test,truePreds,trueStatements

def nTimesCrossValidate(n,epochs,learningRate,conceptSpace,roleSpace,syn,mix):
    if not os.path.isdir("crossValidationFolds"): os.mkdir("crossValidationFolds")
    if syn:
        if not os.path.isdir("output"): os.mkdir("output")
        KBs,supports,outputs = getSynDataFromFile('saves/data.npz')
        if mix:
            sKBs,ssupports,soutputs,localMaps,stats = getSnoDataFromFile('saves/data.npz')
            labels = collapseLabelMap(localMaps,stats[0][2],stats[1][2],stats[4][1])
            allTheData = crossValidationSplitAllData(n,KBs,supports,outputs,sKBs,ssupports,soutputs,labels,conceptSpace,roleSpace)
        else: allTheData = crossValidationSplitAllData(n,KBs,supports,outputs,None,None,None,None,conceptSpace,roleSpace)
    else:
        if not os.path.isdir("snoutput"): os.mkdir("snoutput")
        KBs,supports,outputs,localMaps,stats = getSnoDataFromFile('ssaves/data.npz')
        labels = collapseLabelMap(localMaps,stats[0][2],stats[1][2],stats[4][1])
        if mix:
            sKBs,ssupports,soutputs = getSynDataFromFile('saves/data.npz')
            allTheData = crossValidationSplitAllData(n,KBs,supports,outputs,sKBs,ssupports,soutputs,labels,conceptSpace,roleSpace)
        else: allTheData =  crossValidationSplitAllData(n,KBs,supports,outputs,None,None,None,labels,conceptSpace,roleSpace)
    
    evals = numpy.zeros((3,3,7),dtype=numpy.float64)
    for i in range(n):
        KBs_test = allTheData[0][i] ; KBs_train = allTheData[1][i] ; X_train = allTheData[2][i] ; X_test = allTheData[3][i] ; y_train = allTheData[4][i] ; y_test = allTheData[5][i] ; truePreds = allTheData[6][i] ; trueStatements = allTheData[7][i]
        evals = evals + runNthTime(open("crossValidationFolds/fold[{}].txt".format(i),"w"),epochs,learningRate,conceptSpace,roleSpace,(KBs_test,KBs_train,X_train,X_test,y_train,y_test,truePreds,trueStatements),syn)
    evals = evals / n
    
    avgResult = evals.tolist()
    
    log = open("crossValidationFolds/fold[avg].txt","w")
    
    levTR,levRT,levTN,levNT,sizeTrue,sizeNew,sizeRan = avgResult[0][0]
    levTR2,levRT2,levTN2,levNT2,sizeTrue2,sizeNew2,sizeRan2 = avgResult[0][1]
    custTR,custRT,custTN,custNT,countTrue,countNew,countRan = avgResult[0][2]
    
    log.write("Piecewise System Only Second Half\n")
    
    log.write("\n\tNo Nums\n\n\tLevenshtein Distance From Reasoner to Random Data:     {}\n\tLevenshtein Distance From Random to Reasoner Data:     {}\n\tLevenshtein Distance From Reasoner to Predicted Data:  {}\n\tLevenshtein Distance From Prediction to Reasoner Data: {}\n".format(levTR,levRT,levTN,levNT)) 
    log.write("\n\tAverage Levenshtein Distance From Reasoner to Random Statement:    {}\n\tAverage Levenshtein Distance From Random to Reasoner Statement:    {}\n\tAverage Levenshtein Distance From Reasoner to Predicted Statement: {}\n\tAverage Levenshtein Distance From Prediction to Reasoner Statement:{}\n".format(levTR/sizeTrue,levRT/sizeRan,levTN/sizeTrue,levNT/sizeNew))       
    
    log.write("\n\tNums\n\n\tLevenshtein Distance From Reasoner to Random Data:     {}\n\tLevenshtein Distance From Random to Reasoner Data:     {}\n\tLevenshtein Distance From Reasoner to Predicted Data:  {}\n\tLevenshtein Distance From Prediction to Reasoner Data: {}\n".format(levTR2,levRT2,levTN2,levNT2)) 
    log.write("\n\tAverage Levenshtein Distance From Reasoner to Random Statement:    {}\n\tAverage Levenshtein Distance From Random to Reasoner Statement:    {}\n\tAverage Levenshtein Distance From Reasoner to Predicted Statement: {}\n\tAverage Levenshtein Distance From Prediction to Reasoner Statement:{}\n".format(levTR2/sizeTrue2,levRT2/sizeRan2,levTN2/sizeTrue2,levNT2/sizeNew2))
    
    log.write("\n\tCustom\n\n\tCustom Distance From Reasoner to Random Data:    {}\n\tCustom Distance From Random to Reasoner Data:    {}\n\tCustom Distance From Reasoner to Predicted Data: {}\n\tCustom Distance From Predicted to Reasoner Data: {}\n".format(custTR,custRT,custTN,custNT)) 
    log.write("\n\tAverage Custom Distance From Reasoner to Random Statement:    {}\n\tAverage Custom Distance From Random to Reasoner Statement:    {}\n\tAverage Custom Distance From Reasoner to Predicted Statement: {}\n\tAverage Custom Distance From Prediction to Reasoner Statement:{}\n".format(custTR/countTrue,custRT/countRan,custTN/countTrue,custNT/countNew))
    
    levTR,levRT,levTN,levNT,sizeTrue,sizeNew,sizeRan = avgResult[1][0]
    levTR2,levRT2,levTN2,levNT2,sizeTrue2,sizeNew2,sizeRan2 = avgResult[1][1]
    custTR,custRT,custTN,custNT,countTrue,countNew,countRan = avgResult[1][2]
    
    log.write("\nPiecewise System Pipelined Data\n")
    
    log.write("\n\tNo Nums\n\n\tLevenshtein Distance From Reasoner to Random Data:     {}\n\tLevenshtein Distance From Random to Reasoner Data:     {}\n\tLevenshtein Distance From Reasoner to Predicted Data:  {}\n\tLevenshtein Distance From Prediction to Reasoner Data: {}\n".format(levTR,levRT,levTN,levNT)) 
    log.write("\n\tAverage Levenshtein Distance From Reasoner to Random Statement:    {}\n\tAverage Levenshtein Distance From Random to Reasoner Statement:    {}\n\tAverage Levenshtein Distance From Reasoner to Predicted Statement: {}\n\tAverage Levenshtein Distance From Prediction to Reasoner Statement:{}\n".format(levTR/sizeTrue,levRT/sizeRan,levTN/sizeTrue,levNT/sizeNew))       
    
    log.write("\n\tNums\n\n\tLevenshtein Distance From Reasoner to Random Data:     {}\n\tLevenshtein Distance From Random to Reasoner Data:     {}\n\tLevenshtein Distance From Reasoner to Predicted Data:  {}\n\tLevenshtein Distance From Prediction to Reasoner Data: {}\n".format(levTR2,levRT2,levTN2,levNT2)) 
    log.write("\n\tAverage Levenshtein Distance From Reasoner to Random Statement:    {}\n\tAverage Levenshtein Distance From Random to Reasoner Statement:    {}\n\tAverage Levenshtein Distance From Reasoner to Predicted Statement: {}\n\tAverage Levenshtein Distance From Prediction to Reasoner Statement:{}\n".format(levTR2/sizeTrue2,levRT2/sizeRan2,levTN2/sizeTrue2,levNT2/sizeNew2))
    
    log.write("\n\tCustom\n\n\tCustom Distance From Reasoner to Random Data:    {}\n\tCustom Distance From Random to Reasoner Data:    {}\n\tCustom Distance From Reasoner to Predicted Data: {}\n\tCustom Distance From Predicted to Reasoner Data: {}\n".format(custTR,custRT,custTN,custNT)) 
    log.write("\n\tAverage Custom Distance From Reasoner to Random Statement:    {}\n\tAverage Custom Distance From Random to Reasoner Statement:    {}\n\tAverage Custom Distance From Reasoner to Predicted Statement: {}\n\tAverage Custom Distance From Prediction to Reasoner Statement:{}\n".format(custTR/countTrue,custRT/countRan,custTN/countTrue,custNT/countNew))
    
    levTR,levRT,levTN,levNT,sizeTrue,sizeNew,sizeRan = avgResult[2][0]
    levTR2,levRT2,levTN2,levNT2,sizeTrue2,sizeNew2,sizeRan2 = avgResult[2][1]
    custTR,custRT,custTN,custNT,countTrue,countNew,countRan = avgResult[2][2]
    
    log.write("\nDeep System\n")
    
    log.write("\n\tNo Nums\n\n\tLevenshtein Distance From Reasoner to Random Data:     {}\n\tLevenshtein Distance From Random to Reasoner Data:     {}\n\tLevenshtein Distance From Reasoner to Predicted Data:  {}\n\tLevenshtein Distance From Prediction to Reasoner Data: {}\n".format(levTR,levRT,levTN,levNT)) 
    log.write("\n\tAverage Levenshtein Distance From Reasoner to Random Statement:    {}\n\tAverage Levenshtein Distance From Random to Reasoner Statement:    {}\n\tAverage Levenshtein Distance From Reasoner to Predicted Statement: {}\n\tAverage Levenshtein Distance From Prediction to Reasoner Statement:{}\n".format(levTR/sizeTrue,levRT/sizeRan,levTN/sizeTrue,levNT/sizeNew))       
    
    log.write("\n\tNums\n\n\tLevenshtein Distance From Reasoner to Random Data:     {}\n\tLevenshtein Distance From Random to Reasoner Data:     {}\n\tLevenshtein Distance From Reasoner to Predicted Data:  {}\n\tLevenshtein Distance From Prediction to Reasoner Data: {}\n".format(levTR2,levRT2,levTN2,levNT2)) 
    log.write("\n\tAverage Levenshtein Distance From Reasoner to Random Statement:    {}\n\tAverage Levenshtein Distance From Random to Reasoner Statement:    {}\n\tAverage Levenshtein Distance From Reasoner to Predicted Statement: {}\n\tAverage Levenshtein Distance From Prediction to Reasoner Statement:{}\n".format(levTR2/sizeTrue2,levRT2/sizeRan2,levTN2/sizeTrue2,levNT2/sizeNew2))
    
    log.write("\n\tCustom\n\n\tCustom Distance From Reasoner to Random Data:    {}\n\tCustom Distance From Random to Reasoner Data:    {}\n\tCustom Distance From Reasoner to Predicted Data: {}\n\tCustom Distance From Predicted to Reasoner Data: {}\n".format(custTR,custRT,custTN,custNT)) 
    log.write("\n\tAverage Custom Distance From Reasoner to Random Statement:    {}\n\tAverage Custom Distance From Random to Reasoner Statement:    {}\n\tAverage Custom Distance From Reasoner to Predicted Statement: {}\n\tAverage Custom Distance From Prediction to Reasoner Statement:{}\n".format(custTR/countTrue,custRT/countRan,custTN/countTrue,custNT/countNew))
    
    log.close()
    
    return avgResult

def crossValidationSplitAllData(n,KBs,supports,outputs,sKBs,ssupports,soutputs,localMaps,conceptSpace,roleSpace):
    
    fileShapes1 = [3,124,48]
    
    newKBs = numpy.empty([KBs.shape[0],3,KBs.shape[1]],dtype=numpy.float32)
    for i in range(len(newKBs)):
        for j in range(3):
            newKBs[i][j] = KBs[i]
            
    KBs = newKBs
    
    indexes = list(range(len(KBs)))
    random.shuffle(indexes)
    k, m = divmod(len(indexes), n)
    indexes = list(indexes[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))    
    
    crossKBsTest = numpy.empty((len(indexes),len(indexes[0]),len(KBs[0]),len(KBs[0][0])),dtype=numpy.ndarray)
    crossSupportsTest = numpy.empty(len(indexes),dtype=numpy.ndarray)
    crossOutputsTest = numpy.empty(len(indexes),dtype=numpy.ndarray)
    
    if localMaps != None:
        crossLabelsTest = numpy.empty(len(indexes),dtype=numpy.ndarray)
    else: crossLabelsTest = None
    
    if sKBs != None:
        scrossKBsTest = numpy.empty(len(indexes),dtype=numpy.ndarray)
        scrossSupportsTest = numpy.empty(len(indexes),dtype=numpy.ndarray)
        scrossOutputsTest = numpy.empty(len(indexes),dtype=numpy.ndarray)
    else:
        scrossKBsTest = None
        scrossSupportsTest = None
        scrossOutputsTest = None        
    
    for i in range(len(indexes)):
        KB = numpy.empty(len(indexes[i]),dtype=numpy.ndarray)
        support = numpy.empty(len(indexes[i]),dtype=numpy.ndarray)
        output = numpy.empty(len(indexes[i]),dtype=numpy.ndarray)
        if crossLabelsTest != None: labels = numpy.empty(len(indexes[i]),dtype=numpy.ndarray)
        else: labels = None
        if scrossKBsTest != None:
            sKB = numpy.empty(len(indexes[i]),dtype=numpy.ndarray)
            ssupport = numpy.empty(len(indexes[i]),dtype=numpy.ndarray)
            soutput = numpy.empty(len(indexes[i]),dtype=numpy.ndarray)
        else:
            sKB = None
            ssupport = None
            soutput = None      
        for j in range(len(indexes[i])):
            crossKBsTest[i][j] = KBs[indexes[i][j]]
            support[j] = supports[indexes[i][j]]
            output[j] = outputs[indexes[i][j]]
            if labels != None: 
                labels[j] = localMaps[indexes[i][j]]
            if sKB != None:
                sKB[j] = sKBs[indexes[i][j]]
                ssupport[j] = ssupports[indexes[i][j]]
                soutput[j] = soutputs[indexes[i][j]] 
        crossSupportsTest[i] = support
        crossOutputsTest[i] = output
        if crossLabelsTest != None: 
            crossLabels[i] = labels
        if scrossKBsTest != None:
            scrossKBs[i] = sKB
            scrossSupports[i] = ssupport
            scrossOutputs[i] = soutput
    
    for i in range(len(crossOutputsTest)):
        crossOutputsTest[i] = array(crossOutputsTest[i])
    
    crossKBsTrain = numpy.empty((n,len(KBs)-len(crossKBsTest[0]),len(KBs[0]),len(KBs[0][0])),dtype=numpy.ndarray)
    crossOutputsTrain = numpy.empty(n,dtype=numpy.ndarray)
    crossSupportsTrain = numpy.empty(n,dtype=numpy.ndarray)
    
    if localMaps != None:
        crossLabelsTrain = numpy.empty(len(indexes),dtype=numpy.ndarray)
    else: crossLabelsTrain = None
    
    if sKBs != None:
        scrossKBsTrain = numpy.empty(len(indexes),dtype=numpy.ndarray)
        scrossSupportsTrain = numpy.empty(len(indexes),dtype=numpy.ndarray)
        scrossOutputsTrain = numpy.empty(len(indexes),dtype=numpy.ndarray)
    else:
        scrossKBsTrain = None
        scrossSupportsTrain = None
        scrossOutputsTrain = None  
        
    for i in range(len(indexes)):
        crossOutputTrain = numpy.empty(len(KBs)-len(crossKBsTest[0]),dtype=numpy.ndarray)
        crossSupportTrain = numpy.empty(len(KBs)-len(crossKBsTest[0]),dtype=numpy.ndarray)        
        if crossLabelsTrain != None: labels = numpy.empty(len(KBs)-len(crossKBsTest[0]),dtype=numpy.ndarray)
        else: labels = None
        if scrossKBsTest != None:
            sKB = numpy.empty(len(KBs)-len(crossKBsTest[0]),dtype=numpy.ndarray)
            ssupport = numpy.empty(len(KBs)-len(crossKBsTest[0]),dtype=numpy.ndarray)
            soutput = numpy.empty(len(KBs)-len(crossKBsTest[0]),dtype=numpy.ndarray)
        else: sKB = None ; ssupport = None ; soutput = None      
        
        for j in range(len(crossKBsTrain[i])):
            train = list(set(range(len(KBs))).intersection(set(indexes[i])))
            for k in range(len(train)):
                crossKBsTrain[i][j] = KBs[train[k]]
                crossSupportTrain[j] = supports[train[k]]
                crossOutputTrain[j] = outputs[train[k]]
                if labels != None: 
                    labels[j] = localMaps[train[k]]
                if sKB != None:
                    sKB[j] = sKBs[train[i][k]]
                    ssupport[j] = ssupports[train[k]]
                    soutput[j] = soutputs[train[k]]
        crossSupportsTrain[i] = crossSupportTrain
        crossOutputsTrain[i] = crossOutputTrain
        if crossLabelsTrain != None: 
            crossLabelsTrain[i] = labels
        if scrossKBsTrain != None:
            scrossKBsTrain[i] = sKB
            scrossSupportsTrain[i] = ssupport
            scrossOutputsTrain[i] = soutput        
    
    for i in range(n):
        crossSupportsTrain[i] = pad(crossSupportsTrain[i],maxlen1=fileShapes1[0],maxlen2=fileShapes1[1])
        crossSupportsTest[i] = pad(crossSupportsTest[i],maxlen1=fileShapes1[0],maxlen2=fileShapes1[1])
    
        crossOutputsTrain[i] = pad(crossOutputsTrain[i],maxlen1=fileShapes1[0],maxlen2=fileShapes1[2])
        crossOutputsTest[i] = pad(crossOutputsTest[i],maxlen1=fileShapes1[0],maxlen2=fileShapes1[2])
        
    nTruePreds = numpy.empty(n,dtype=numpy.ndarray)
    nTrueStatements = numpy.empty(n,dtype=numpy.ndarray)
    for i in range(n):
        placeholder,KBn = vecToStatements(crossKBsTest[i],conceptSpace,roleSpace)
        nTruePreds[i],nTrueStatements[i] = vecToStatements(crossOutputsTest[i],conceptSpace,roleSpace)
        placeholder,inputs = vecToStatements(crossSupportsTest[i],conceptSpace,roleSpace)
    
        writeVectorFile("{}output/KBsIn[{}].txt".format("sn" if localMaps != None else "",i),KBn)
        writeVectorFile("{}output/supports[{}].txt".format("sn" if localMaps != None else "",i),inputs)
        writeVectorFile("{}output/reasonerCompletion[{}].txt".format("sn" if localMaps != None else "",i),nTrueStatements[i])        
    
    return crossKBsTest,crossKBsTrain,crossSupportsTrain,crossSupportsTest,crossOutputsTrain,crossOutputsTest,nTruePreds,nTrueStatements

if __name__ == "__main__":
    if len(sys.argv) == 3: 
        nTimesCrossValidate(n=10,epochs=int(sys.argv[1]),learningRate=float(sys.argv[2]),conceptSpace=21,roleSpace=8,syn=True,mix=False)
    else: 
        nTimesCrossValidate(n=10,epochs=20000,learningRate=0.0001,conceptSpace=21,roleSpace=8,syn=True,mix=False)    