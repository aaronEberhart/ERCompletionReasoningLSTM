import os,sys,time
me = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,me+"/Generator")
sys.path.insert(0,me+"/Reasoner")

import random
import numpy

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

def writeFile(filename,data):
    file = open(filename,"w")
    file.write(data)
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

def convertToStatement(four,conceptSpace,roleSpace):
    
    new = []
    for number in four:
        if isinstance(number,numpy.float32): 
            number = number.item()
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

def levDistance(newStatements,trueStatements,conceptSpace,roleSpace):
    
    rando = []
    
    for i in range(0,len(trueStatements)):
        kb = []
        for j in range(0,len(trueStatements[i])):
            step = []
            gen = GenERator(numCType1=len(trueStatements[i][j])//2,numCType2=0,numCType3=len(trueStatements[i][j]) - len(trueStatements[i][j])//2,numCType4=0,numRoleSub=0,numRoleChains=0,conceptNamespace=conceptSpace,roleNamespace=roleSpace)
            gen.genERate()
            for k in range(0,len(gen.CType1)):
                step.append(gen.CType1[k].toString())
            for k in range(0,len(gen.CType3)):
                step.append(gen.CType3[k].toString())
            kb.append(step)
        rando.append(kb)
        
    trueStr = [["".join([z for z in y]) for y in x] for x in trueStatements]
    newStr = [["".join([z for z in y]) for y in x] for x in newStatements]
    randoStr = [["".join([z for z in y]) for y in x] for x in rando]
    
    levTR = 0
    levTN = 0
    
    for i in range(len(trueStr)):
        for j in range(len(trueStr[i])):
            levTR = levTR + levenshtein(trueStr[i][j],randoStr[i][j])
            levTN = levTN + (levenshtein(trueStr[i][j],newStr[i][j]) if len(newStr[i]) > j else levenshtein(trueStr[i][j],""))
    
    return levTR,levTN

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

def customDistance(newPred,truePred,conceptSpace,roleSpace):
    
    rando = []
    
    for i in range(0,len(truePred)):
        kb = []
        for j in range(0,len(truePred[i])):
            step = []
            gen = GenERator(numCType1=len(truePred[i][j])//2,numCType2=0,numCType3=len(truePred[i][j]) - len(truePred[i][j])//2,numCType4=0,numRoleSub=0,numRoleChains=0,conceptNamespace=conceptSpace,roleNamespace=roleSpace)
            gen.genERate()
            for k in range(0,len(gen.CType1)):
                step.append([gen.CType1[k].antecedent.toString(),gen.CType1[k].consequent.toString()])
            for k in range(0,len(gen.CType3)):
                step.append([gen.CType3[k].antecedent.toString(),gen.CType3[k].consequent.role.toString(),gen.CType3[k].consequent.concept.toString()])
            kb.append(step)
        rando.append(kb)
    
    custTR = 0
    custNR = 0
    custTN = 0
    
    for i in range(len(truePred)):
        for j in range(len(truePred[i])):
            for k in range(len(truePred[i][j])):
                custTR = custTR + (custom(truePred[i][j][k],rando[i][j][k],conceptSpace,roleSpace) if (len(rando[i]) > j and len(rando[i][j]) > k) else custom(truePred[i][j][k],[""]*len(truePred[i][j][k]),conceptSpace,roleSpace))
                custTN = custTN + (custom(truePred[i][j][k],newPred[i][j][k],conceptSpace,roleSpace) if (len(newPred[i]) > j and len(newPred[i][j]) > k) else custom(truePred[i][j][k],[""]*len(truePred[i][j][k]),conceptSpace,roleSpace))
    
    return custTR,custTN

def repeatAndSplitKBs(kbs,steps,splitSize):
    newKBs = numpy.empty([kbs.shape[0],steps,kbs.shape[1]],dtype=numpy.float32)
    for i in range(len(newKBs)):
        for j in range(steps):
            newKBs[i][j] = kbs[i]
    return numpy.split(newKBs,[int(len(newKBs)*splitSize)])

def getDataFromFile(filename,easy):
    data = numpy.load(filename,allow_pickle=True)
    return data['arr_0'],data['arr_1'],data['arr_2']
