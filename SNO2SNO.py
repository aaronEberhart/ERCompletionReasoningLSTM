import os,sys,time
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

import re
import fileinput
import numpy
import tensorflow as tf

tf.logging.set_verbosity(tf.logging.ERROR)
'''
from tensorflow.contrib.layers import fully_connected
from sklearn.model_selection import train_test_split
from math import sqrt
from numpy import concatenate
from pandas import read_csv
from pandas import DataFrame
from pandas import concat
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
'''
import tensorflow as tf
from tensorflow.contrib import rnn

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
        #print("easy\t",line)
                
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
        print (line,end='')
    
    return outf
    
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

def getDataFromFile(easy):
    data = numpy.load('ssaves/dataEasyX.npz' if easy else 'ssaves/data.npz',allow_pickle=True)
    return data['arr_0'],data['arr_1'],data['arr_2']

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

def vecToStatements(vec,easy):    
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
                    pred,stri = convertToStatement(four,easy)
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

def convertToStatement(four,easy):
    concepts = 13 if easy else 106
    roles = 7 if easy else 56
    new = []
    threshc = 0.45 / concepts
    threshr = -0.45 / roles
    for number in four:
        if isinstance(number,numpy.float32): 
            number = number.item()
            #if (number > 0 and number < threshc) or (number < 0 and number > threshr): number = 0
        if number < 0 and number >= -1:
            if int(number * roles * -1) == 0: pass
            else: new.append("R{}".format(int(number * roles * -1)))
        elif number > 0 and number <= 1:
            if int(number * concepts) == 0: pass
            else: new.append("C{}".format(int(number * concepts)))   

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

def levDistance(newStatements,trueStatements,easy):
    
    rando = []
    
    for i in range(0,len(trueStatements)):
        kb = []
        for j in range(0,len(trueStatements[i])):
            step = []
            gen = GenERator(numCType1=len(trueStatements[i][j])//2,numCType2=0,numCType3=len(trueStatements[i][j]) - len(trueStatements[i][j])//2,numCType4=0,numRoleSub=0,numRoleChains=0,conceptNamespace=13,roleNamespace=7) if easy else GenERator(numCType1=len(trueStatements[i][j])//2,numCType2=0,numCType3=len(trueStatements[i][j]) - len(trueStatements[i][j])//2,numCType4=0,numRoleSub=0,numRoleChains=0,conceptNamespace=106,roleNamespace=56)
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
    levNR = 0
    levTN = 0
    
    for i in range(len(trueStr)):
        for j in range(len(trueStr[i])):
            levTR = levTR + levenshtein(trueStr[i][j],randoStr[i][j])
            levNR = levNR + (levenshtein(newStr[i][j],randoStr[i][j]) if len(newStr[i]) > j else levenshtein("",randoStr[i][j]))
            levTN = levTN + (levenshtein(trueStr[i][j],newStr[i][j]) if len(newStr[i]) > j else levenshtein(trueStr[i][j],""))
    
    return levTR,levNR,levTN

def custom(s1, s2, easy):
   
    if len(s1) < len(s2): return custom(s2,s1,easy)
    
    dist = 0
    
    for k in range(len(s1)):
        string1 = s1[k]
        string2 = s2[k] if len(s2) > k else ""
        if string2 == "":
            dist = dist + (20 if easy else 166) + int(''.join(x for x in string1 if x.isdigit()))
        else:
            if (string1[0] == 'C' and string2[0] == 'R') or (string1[0] == 'R' and string2[0] == 'C'): dist = dist + (20 if easy else 166)
            dist = dist + abs(int(''.join(x for x in string1 if x.isdigit())) -  int(''.join(x for x in string2 if x.isdigit())))
                
    
    return dist

def customDistance(newPred,truePred,easy):
    
    rando = []
    
    for i in range(0,len(truePred)):
        kb = []
        for j in range(0,len(truePred[i])):
            step = []
            gen = GenERator(numCType1=len(truePred[i][j])//2,numCType2=0,numCType3=len(truePred[i][j]) - len(truePred[i][j])//2,numCType4=0,numRoleSub=0,numRoleChains=0,conceptNamespace=13,roleNamespace=7) if easy else GenERator(numCType1=len(truePred[i][j])//2,numCType2=0,numCType3=len(truePred[i][j]) - len(truePred[i][j])//2,numCType4=0,numRoleSub=0,numRoleChains=0,conceptNamespace=106,roleNamespace=56)
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
                custTR = custTR + custom(truePred[i][j][k],rando[i][j][k],easy)
                custTN = custTN + (custom(truePred[i][j][k],newPred[i][j][k],easy) if (len(newPred[i]) > j and len(newPred[i][j]) > k) else custom(truePred[i][j][k],"",easy))
    for i in range(len(newPred)):
        for j in range(len(newPred[i])):
            for k in range(len(newPred[i][j])):
                custNR = custNR + (custom(newPred[i][j][k],rando[i][j][k],easy) if (len(rando[i]) > j and len(rando[i][j]) > k) else custom(newPred[i][j][k],"",easy))
                
    
    return custTR,custNR,custTN

def repeatAndSplitKBs(kbs,steps,splitSize):
    newKBs = numpy.empty([kbs.shape[0],steps,kbs.shape[1]],dtype=numpy.float32)
    for i in range(len(newKBs)):
        for j in range(steps):
            newKBs[i][j] = kbs[i]
    return numpy.split(newKBs,[int(len(newKBs)*splitSize)])

def fsOWLReader(filename):
    file = open(filename,'r')
    
    line = file.readline()
    while "Declaration" not in line:
        line = file.readline()
    
    classes = 0
    classDict = {}
    labelDict = {}
    roles = 0
    roleDict = {}
    CType1=[]
    CType2=[]
    CType3=[]
    CType4=[]
    roleSubs=[]
    roleChains=[]
    
    
    while "Declaration" in line:
        if "Class" in line: 
            classes = classes + 1
            classDict[line[18:-3]] = classes
        elif 'Object' in line: 
            roles = roles + 1
            roleDict[line[27:-3]] = roles
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
                roleSubs.append(rs)
            else: 
                line = line.split()
                #print(line)
                rs = RoleStatement(len(roleChains),True,Role(roleDict[line[0]],[0,1]),Role(roleDict[line[1]],[0,1]))
                rs.complete('⊑')
                roleChains.append(rs)
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
    
    info = [['c',classes,classDict],['r',roles,roleDict],['cs',len(CType1),len(CType2),len(CType3),len(CType4)],['rs',len(roleSubs),len(roleChains)],['l',labelDict]]
        
    return [CType1,CType2,CType3,CType4],[roleSubs,roleChains],info


'''TODO'''
def makeKBFromSamples(concepts,roles,info,easy):
    
    start = 0
    allowedCNames = []
    allowedRNames = []
    
    while isinstance(start,int):
        start = random.randint(1,info[0][1])
        for intersection in concepts[1]:
            if intersection.antecedent.antecedent.name == start or intersection.antecedent.consequent.name == start or intersection.consequent.name == start:
                start = intersection
                allowedCNames.append(intersection.antecedent.antecedent.name) 
                allowedCNames.append(intersection.antecedent.consequent.name)
                allowedCNames.append(intersection.consequent.name)
                break
    
    #4 2 8 2
    #2 2
    
    numCType1 = 4 if easy else 10
    numCType2 = 2 if easy else 10
    numCType3 = 8 if easy else 10
    numCType4 = 2 if easy else 10
    numRoleSubs = 2 if easy else 4
    numRoleChains = 2 if easy else 4
    
    CType1 = []
    CType2 = [start]
    CType3 = []
    CType4 = []
    roleSubs = []
    roleChains = []
    
    while len(CType1) < numCType1:
        inclusion = random.choice(concepts[0])
        if inclusion in CType1: pass
        elif inclusion.antecedent.name in allowedCNames or inclusion.consequent.name in allowedCNames:
            CType1.append(inclusion)
            allowedCNames.append(inclusion.antecedent.name)
            allowedCNames.append(inclusion.consequent.name)
               
    allowedCNames = list(dict.fromkeys(allowedCNames))
    i = 0
    
    while len(CType2) < numCType2:
        intersection = concepts[1][i]
        if intersection in CType2: i = i + 1
        elif intersection.antecedent.antecedent.name in allowedCNames or intersection.antecedent.consequent.name in allowedCNames or intersection.consequent.name in allowedCNames:
            CType2.append(intersection)
            allowedCNames.append(intersection.antecedent.antecedent.name) 
            allowedCNames.append(intersection.antecedent.consequent.name)
            allowedCNames.append(intersection.consequent.name)
            i = 0
        elif i < len(concepts[1])-1: i = i + 1
        else: raise
            
    allowedCNames = list(dict.fromkeys(allowedCNames))
    
    while len(CType3) < numCType3:
        restriction = random.choice(concepts[2])
        if restriction in CType4: pass
        elif restriction.consequent.concept.name in allowedCNames or restriction.antecedent.name in allowedCNames:
            CType3.append(restriction)
            allowedCNames.append(restriction.consequent.concept.name)
            allowedRNames.append(restriction.consequent.role.name)
            allowedCNames.append(restriction.antecedent.name)
            
    allowedCNames = list(dict.fromkeys(allowedCNames))
    allowedRNames = list(dict.fromkeys(allowedRNames))          
            
    while len(CType4) < numCType4:
        restriction = random.choice(concepts[3])
        if restriction in CType4: pass
        elif restriction.antecedent.concept.name in allowedCNames or restriction.consequent.name in allowedCNames:
            CType4.append(restriction)
            allowedCNames.append(restriction.antecedent.concept.name)
            allowedRNames.append(restriction.antecedent.role.name)
            allowedCNames.append(restriction.consequent.name)
    
    allowedCNames = list(dict.fromkeys(allowedCNames))
    allowedRNames = list(dict.fromkeys(allowedRNames))
            
    
    
    generator = HardGenERator2(rGenerator=GenERator(CType1=CType1,CType2=CType2,CType3=CType3,CType4=CType4,roleSubs=roleSubs,roleChains=roleChains))
    
    generator.hasRun = True


    
def sampleDataHardGenerator2Format(trials,easy,x):
    concepts,roles,info = x
    seq_in = numpy.empty(trials,dtype=numpy.ndarray)
    seq_out = numpy.empty(trials,dtype=numpy.ndarray)
    kbs = numpy.empty([trials,80 if easy else 588],dtype=numpy.float32)
    if not os.path.isdir("snoutput"): os.mkdir("snoutput")

    for i in range(0,trials):

        print(i)

        generator = makeKBFromSamples(concepts,roles,info,easy)
        
        kbs[i] = array(generator.toVector())

        reasoner = ReasonER(generator,showSteps=True)

        reasoner.ERason()

        dependencies = DependencyReducer(generator.getAllExpressions(),reasoner.sequenceLog,reasoner.KBsLog,reasoner.KBaLog)

        seq_in[i],seq_out[i] = dependencies.toVector(generator.conceptNamespace,generator.roleNamespace)

        if not os.path.isdir("snoutput/{}".format(i)): os.mkdir("snoutput/{}".format(i))
        if not os.path.isdir("snoutput/{}/sequence".format(i)): os.mkdir("snoutput/{}/sequence".format(i))
        if not os.path.isdir("snoutput/{}/KB during sequence".format(i)): os.mkdir("snoutput/{}/KB during sequence".format(i))
        if len(reasoner.KBaLog) > 0 and not os.path.isdir("snoutput/{}/KB after sequence".format(i)): os.mkdir("snoutput/{}/KB after sequence".format(i))
        generator.toStringFile("snoutput/{}/completedKB.txt".format(i))
        reasoner.toStringFile("snoutput/{}/completedKB.txt".format(i))        
        for j in range(0,len(dependencies.donelogs[0])):
            writeFile("snoutput/{}/sequence/reasonerStep{}.txt".format(i,j),dependencies.toString(dependencies.donelogs[0][j]))
        for j in range(0,len(dependencies.donelogs[1])):
            if len(reasoner.KBsLog[j]) > 0: writeFile("snoutput/{}/KB during sequence/reasonerStep{}.txt".format(i,j),dependencies.toString(dependencies.donelogs[1][j]))
        for j in range(0,len(dependencies.donelogs[2])):
            if len(reasoner.KBaLog[j]) > 0: writeFile("snoutput/{}/KB after sequence/reasonerStep{}.txt".format(i,j+len(reasoner.sequenceLog)),dependencies.toString(dependencies.donelogs[2][j]))


    numpy.savez("ssaves/dataEasyX" if easy else 'ssaves/dataX', kbs,seq_in,seq_out)

    return kbs,seq_in,seq_out    
    

print()

'''13,7'''

if not os.path.isdir("ssaves"): os.mkdir("ssaves")
if not os.path.isdir("snoutput"): os.mkdir("snoutput")
easy = True

KBs,dependencies,output = sampleDataHardGenerator2Format(1000,easy,fsOWLReader(normalizeFS("SNOMED/SNOMED2012fs.owl","SNOMED/SNOrMED2012fs.owl")))

fileShapes1 = [4,324,84] if easy else [8,2116,324]

KBs_test,KBs_train = repeatAndSplitKBs(KBs,fileShapes1[0],0.33)
                        
X_train, X_test, y_train, y_test = splitTensors(dependencies, output, 0.33)

X_train = pad(X_train,maxlen1=fileShapes1[0],maxlen2=fileShapes1[1])
X_test = pad(X_test,maxlen1=fileShapes1[0],maxlen2=fileShapes1[1])

y_train = pad(y_train,maxlen1=fileShapes1[0],maxlen2=fileShapes1[2])
y_test = pad(y_test,maxlen1=fileShapes1[0],maxlen2=fileShapes1[2])

print("",KBs.shape,"\n",KBs_train.shape,KBs_test.shape,'\n',X_train.shape,X_test.shape,"\n",y_train.shape,y_test.shape)

KBvec,KBstr = vecToStatements(KBs_test,easy)
preds,trueStatements = vecToStatements(y_test,easy)
placeholder,inputs = vecToStatements(X_test,easy)

writeVectorFile("snoutput/KBsInEasy.txt" if easy else "snoutput/KBsIn.txt",KBstr)
writeVectorFile("snoutput/targetInEasy.txt" if easy else "snoutput/targetIn.txt",inputs)
writeVectorFile("snoutput/targetOutEasy.txt" if easy else "snoutput/targetOut.txt",trueStatements)

learning_rate0 = 0.0001 if easy else 0.005
n_epochs0 = 100000 if easy else 5000
train_size0 = KBs_train.shape[0]
n_neurons0 = X_train.shape[2]
n_layers0 = 1

X0 = tf.placeholder(tf.float32, shape=[None,KBs_train.shape[1],KBs_train.shape[2]])
y0 = tf.placeholder(tf.float32, shape=[None,X_train.shape[1],X_train.shape[2]])

basic_cell0 = tf.contrib.rnn.LSTMBlockCell(num_units=n_neurons0)
multi_layer_cell0 = tf.contrib.rnn.MultiRNNCell([basic_cell0] * n_layers0)
outputs0, states0 = tf.nn.dynamic_rnn(multi_layer_cell0, X0, dtype=tf.float32)

loss0 = tf.losses.mean_squared_error(y0,outputs0)#tf.reduce_sum(tf.reduce_sum(tf.reduce_sum(tf.math.square(outputs - y))))/(tf.to_float(tf.size(y)))
optimizer0 = tf.train.AdamOptimizer(learning_rate=learning_rate0)
training_op0 = optimizer0.minimize(loss0)

init0 = tf.global_variables_initializer()

saver = tf.train.Saver()


with tf.Session() as sess:
    init0.run()
    mse0 = 0
    mseL = 0
    for epoch in range(n_epochs0):  
        ynew,a = sess.run([outputs0,training_op0],feed_dict={X0: KBs_train,y0: X_train})
        mse = loss0.eval(feed_dict={outputs0: ynew, y0: X_train})
        if epoch == 0: mse0 = mse
        if epoch == n_epochs0 - 1: mseL = mse
        print("Epoch: {}\tMean Squared Error:\t{}".format(epoch,mse))
        if mse < 0.0001:
            mseL = mse
            break
    y_pred = sess.run(outputs0,feed_dict={X0: KBs_test})
    numpy.savez("ssaves/halfwayEasy" if easy else "ssaves/halfway",y_pred)
    mseNew = loss0.eval(feed_dict={outputs0: y_pred, y0: X_test})
    
    print("\nTraining Statistics\n\nPrediction\tMean Squared Error:\t{}\nTraining\tLearned Reduction MSE:\t{}\n\t\tIncrease MSE on New:\t{}\n\t\tPercent Change MSE:\t{}\n".format(numpy.float32(mseNew),mse0-mseL,numpy.float32(mseNew)-mseL,(mseL - mse0)/mse0*100))
    
    print("\nEvaluating Model\n")
    
    newPreds,newStatements = vecToStatements(y_pred,easy)
    distTRan,distRRan,distRReal = 0,0,0#levDistance(newStatements,inputs,easy)
    cdistTRan,cdistRRan,cdistRReal = 0,0,0#customDistance(newPreds,X_test,easy)    
        
    print("Levenshtein Distance From Actual to Random Data:    {}\nLevenshtein Distance From Predicted to Random Data: {}\nLevenshtein Distance From Actual to Predicted Data: {}\n".format(distTRan,distRRan,distRReal))
    
    print("Custom Distance From Actual to Random Data:    {}\nCustom Distance From Predicted to Random Data: {}\nCustom Distance From Actual to Predicted Data: {}\n".format(cdistTRan,cdistRRan,cdistRReal))
    
    writeVectorFile("snoutput/KBFitEasy.txt" if easy else "snoutput/KBFit.txt",newStatements)
    
tf.reset_default_graph()

learning_rate1 = 0.0001 if easy else 0.005
n_epochs1 = 100000 if easy else 5000
train_size1 = X_train.shape[0]
n_neurons1 = y_train.shape[2]
n_layers1 = 1

X1 = tf.placeholder(tf.float32, shape=[None,X_train.shape[1],X_train.shape[2]])
y1 = tf.placeholder(tf.float32, shape=[None,y_train.shape[1],y_train.shape[2]])

basic_cell1 = tf.contrib.rnn.LSTMBlockCell(num_units=n_neurons1)
multi_layer_cell1 = tf.contrib.rnn.MultiRNNCell([basic_cell1] * n_layers1)
outputs1, states1 = tf.nn.dynamic_rnn(multi_layer_cell1, X1, dtype=tf.float32)

loss1 = tf.losses.mean_squared_error(y1,outputs1)#tf.reduce_sum(tf.reduce_sum(tf.reduce_sum(tf.math.square(outputs - y))))/(tf.to_float(tf.size(y)))
optimizer1 = tf.train.AdamOptimizer(learning_rate=learning_rate1)
training_op1 = optimizer1.minimize(loss1)

init1 = tf.global_variables_initializer()

with tf.Session() as sess:    
    init1.run()
    mse0 = 0
    mseL = 0
    for epoch in range(n_epochs1):  
        ynew,a = sess.run([outputs1,training_op1],feed_dict={X1: X_train,y1: y_train})
        mse = loss1.eval(feed_dict={outputs1: ynew, y1: y_train})
        if epoch == 0: mse0 = mse
        if epoch == n_epochs1 - 1: mseL = mse
        print("Epoch: {}\tMean Squared Error:\t{}".format(epoch,mse))
        if mse < 0.0001:
            mseL = mse
            break
    
    y_pred = sess.run(outputs1,feed_dict={X1: X_test})  
    mseNew = loss1.eval(feed_dict={outputs1: y_pred, y1: y_test})
    print("\nTraining Statistics\n\nPrediction\tMean Squared Error:\t{}\nTraining\tLearned Reduction MSE:\t{}\n\t\tIncrease MSE on New:\t{}\n\t\tPercent Change MSE:\t{}\n".format(numpy.float32(mseNew),mse0-mseL,numpy.float32(mseNew)-mseL,(mseL - mse0)/mse0*100))
    
    print("\nTESTING HOLDOUT DATA\n")    
      
    newPreds,newStatements = vecToStatements(y_pred,easy)
    distTRan,distRRan,distRReal = levDistance(newStatements,trueStatements,easy)
    cdistTRan,cdistRRan,cdistRReal = customDistance(newPreds,preds,easy)   
    
    print("Levenshtein Distance From Actual to Random Data:    {}\nLevenshtein Distance From Predicted to Random Data: {}\nLevenshtein Distance From Actual to Predicted Data: {}\n".format(distTRan,distRRan,distRReal))
    
    print("Custom Distance From Actual to Random Data:    {}\nCustom Distance From Predicted to Random Data: {}\nCustom Distance From Actual to Predicted Data: {}\n".format(cdistTRan,cdistRRan,cdistRReal))
    
    writeVectorFile("snoutput/predictedOutEasy.txt" if easy else "snoutput/predictedOut.txt",newStatements)
    
    #saver.save(sess, "model.easy" if easy else "model")  
    
    data = numpy.load("ssaves/halfwayEasy.npz" if easy else "ssaves/halfway.npz",allow_pickle=True)
    data = data['arr_0'] 
    
    print("TESTING PIPELINE DATA\n")
    
    y_pred = sess.run(outputs1,feed_dict={X1: data})
    newPreds,newStatements = vecToStatements(y_pred,easy)
    distTRan,distRRan,distRReal = levDistance(newStatements,trueStatements,easy)
    cdistTRan,cdistRRan,cdistRReal = customDistance(newPreds,preds,easy)
    
    print("Levenshtein Distance From Actual to Random Data:    {}\nLevenshtein Distance From Predicted to Random Data: {}\nLevenshtein Distance From Actual to Predicted Data: {}\n".format(distTRan,distRRan,distRReal))
    
    print("Custom Distance From Actual to Random Data:    {}\nCustom Distance From Predicted to Random Data: {}\nCustom Distance From Actual to Predicted Data: {}\n".format(cdistTRan,cdistRRan,cdistRReal))    
    
    writeVectorFile("snoutput/predictedOutFitEasy.txt" if easy else "snoutput/predictedOutFit.txt",newStatements)

tf.reset_default_graph()

learning_rate2 = 0.0001 if easy else 0.005
n_epochs2 = 100000 if easy else 5000
train_size2 = X_train.shape[0]
n_neurons2 = y_train.shape[2]
n_layers2 = 1

X0 = tf.placeholder(tf.float32, shape=[None,KBs_train.shape[1],KBs_train.shape[2]])
y1 = tf.placeholder(tf.float32, shape=[None,y_train.shape[1],y_train.shape[2]])

basic_cell1 = [tf.contrib.rnn.LSTMBlockCell(num_units=X_train.shape[2]),tf.contrib.rnn.LSTMBlockCell(num_units=y_train.shape[2])]
multi_layer_cell2 = tf.contrib.rnn.MultiRNNCell(basic_cell1)
outputs2, states2 = tf.nn.dynamic_rnn(multi_layer_cell2, X0, dtype=tf.float32)

loss2 = tf.losses.mean_squared_error(y1,outputs2)#tf.reduce_sum(tf.reduce_sum(tf.reduce_sum(tf.math.square(outputs - y))))/(tf.to_float(tf.size(y)))
optimizer2 = tf.train.AdamOptimizer(learning_rate=learning_rate2)
training_op2 = optimizer2.minimize(loss2)

init2 = tf.global_variables_initializer()

with tf.Session() as sess:    
    init2.run()
    mse0 = 0
    mseL = 0
    for epoch in range(n_epochs2):  
        ynew,a = sess.run([outputs2,training_op2],feed_dict={X0: KBs_train,y1: y_train})
        mse = loss2.eval(feed_dict={outputs2: ynew, y1: y_train})
        if epoch == 0: mse0 = mse
        if epoch == n_epochs2 - 1: mseL = mse
        print("Epoch: {}\tMean Squared Error:\t{}".format(epoch,mse))
        if mse < 0.0001:
            mseL = mse
            break
    
    y_pred = sess.run(outputs2,feed_dict={X0: KBs_test})  
    mseNew = loss2.eval(feed_dict={outputs2: y_pred, y1: y_test})
    print("\nTraining Statistics\n\nPrediction\tMean Squared Error:\t{}\nTraining\tLearned Reduction MSE:\t{}\n\t\tIncrease MSE on New:\t{}\n\t\tPercent Change MSE:\t{}\n".format(numpy.float32(mseNew),mse0-mseL,numpy.float32(mseNew)-mseL,(mseL - mse0)/mse0*100))
    
    print("\nTESTING HOLDOUT DATA\n")    
      
    newPreds,newStatements = vecToStatements(y_pred,easy)
    distTRan,distRRan,distRReal = levDistance(newStatements,trueStatements,easy)
    cdistTRan,cdistRRan,cdistRReal = customDistance(newPreds,preds,easy)   
    
    print("Levenshtein Distance From Actual to Random Data:    {}\nLevenshtein Distance From Predicted to Random Data: {}\nLevenshtein Distance From Actual to Predicted Data: {}\n".format(distTRan,distRRan,distRReal))
    
    print("Custom Distance From Actual to Random Data:    {}\nCustom Distance From Predicted to Random Data: {}\nCustom Distance From Actual to Predicted Data: {}\n".format(cdistTRan,cdistRRan,cdistRReal))
    
    writeVectorFile("snoutput/predictedOutEasyC.txt" if easy else "snoutput/predictedOutC.txt",newStatements)
    
    saver.save(sess, "ssaves/modelC.easy" if easy else "ssaves/modelC") 
    '''
    data = numpy.load("halfwayEasy.npz" if easy else "halfway.npz",allow_pickle=True)
    data = data['arr_0'] 
    
    print("TESTING PIPELINE DATA\n")
    
    y_pred = sess.run(outputs1,feed_dict={X1: data})
    newPreds,newStatements = vecToStatements(y_pred,easy)
    distTRan,distRRan,distRReal = levDistance(newStatements,trueStatements,easy)
    cdistTRan,cdistRRan,cdistRReal = 0,0,0#customDistance(newPreds,preds,easy)
    
    print("Levenshtein Distance From Actual to Random Data:    {}\nLevenshtein Distance From Predicted to Random Data: {}\nLevenshtein Distance From Actual to Predicted Data: {}\n".format(distTRan,distRRan,distRReal))
    
    print("Custom Distance From Actual to Random Data:    {}\nCustom Distance From Predicted to Random Data: {}\nCustom Distance From Actual to Predicted Data: {}\n".format(cdistTRan,cdistRRan,cdistRReal))    
    
    writeVectorFile("predictedOutFitEasy.txt" if easy else "predictedOutFit.txt",newStatements)
    '''
