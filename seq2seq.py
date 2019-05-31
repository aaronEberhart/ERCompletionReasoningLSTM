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
    
def makeData(trials,easy):
    seq_in = numpy.empty(trials,dtype=numpy.ndarray)
    seq_out = numpy.empty(trials,dtype=numpy.ndarray)
    kbs = numpy.empty([trials,80 if easy else 588],dtype=numpy.float32)
    if not os.path.isdir("output"): os.mkdir("output")
     
    for i in range(0,trials):
        
        print(i)
        
        generator = HardGenERator2(rGenerator=GenERator(numCType1=2,numCType2=1,numCType3=2,numCType4=1,numRoleSub=1,numRoleChains=1,conceptNamespace=10,roleNamespace=4),difficulty=1) if easy else \
                    HardGenERator2(rGenerator=GenERator(numCType1=25,numCType2=25,numCType3=25,numCType4=25,numRoleSub=15,numRoleChains=10,conceptNamespace=100,roleNamespace=50),difficulty=2)
        
        generator.genERate()
        
        kbs[i] = array(generator.toVector())
        
        reasoner = ReasonER(generator,showSteps=True)
        
        reasoner.ERason()
	
        dependencies = DependencyReducer(generator.getAllExpressions(),reasoner.sequenceLog,reasoner.KBsLog,reasoner.KBaLog)
        
        seq_in[i],seq_out[i] = dependencies.toVector(generator.conceptNamespace,generator.roleNamespace)
        
        
        if not os.path.isdir("output/{}".format(i)): os.mkdir("output/{}".format(i))
        if not os.path.isdir("output/{}/sequence".format(i)): os.mkdir("output/{}/sequence".format(i))
        if not os.path.isdir("output/{}/KB during sequence".format(i)): os.mkdir("output/{}/KB during sequence".format(i))
        if len(reasoner.KBaLog) > 0 and not os.path.isdir("output/{}/KB after sequence".format(i)): os.mkdir("output/{}/KB after sequence".format(i))
        generator.toStringFile("output/{}/completedKB.txt".format(i))
        reasoner.toStringFile("output/{}/completedKB.txt".format(i))        
        for j in range(0,len(dependencies.donelogs[0])):
            writeFile("output/{}/sequence/reasonerStep{}.txt".format(i,j),dependencies.toString(dependencies.donelogs[0][j]))
        for j in range(0,len(dependencies.donelogs[1])):
            if len(reasoner.KBsLog[j]) > 0: writeFile("output/{}/KB during sequence/reasonerStep{}.txt".format(i,j),dependencies.toString(dependencies.donelogs[1][j]))
        for j in range(0,len(dependencies.donelogs[2])):
            if len(reasoner.KBaLog[j]) > 0: writeFile("output/{}/KB after sequence/reasonerStep{}.txt".format(i,j+len(reasoner.sequenceLog)),dependencies.toString(dependencies.donelogs[2][j]))
        
            
    numpy.savez("dataEasyX" if easy else 'dataX', kbs,seq_in,seq_out)
    
    return kbs,seq_in,seq_out

def getDataFromFile(easy):
    data = numpy.load('dataEasyX.npz' if easy else 'data.npz',allow_pickle=True)
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

easy = True
KBs,dependencies,output = getDataFromFile(easy)#makeData(1000,easy)#

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

writeVectorFile("KBsInEasy.txt" if easy else "KBsIn.txt",KBstr)
writeVectorFile("targetInEasy.txt" if easy else "targetIn.txt",inputs)
writeVectorFile("targetOutEasy.txt" if easy else "targetOut.txt",trueStatements)

learning_rate0 = 0.0001 if easy else 0.005
n_epochs0 = 50000 if easy else 5000
train_size0 = KBs_train.shape[0]
n_neurons0 = X_train.shape[2]
n_layers0 = 1

X0 = tf.placeholder(tf.float32, shape=[None,KBs_train.shape[1],KBs_train.shape[2]])
y0 = tf.placeholder(tf.float32, shape=[None,X_train.shape[1],X_train.shape[2]])

basic_cell0 = tf.contrib.rnn.GRUCell(num_units=n_neurons0)
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
    numpy.savez("halfwayEasy" if easy else "halfway",y_pred)
    mseNew = loss0.eval(feed_dict={outputs0: y_pred, y0: X_test})
    
    print("\nTraining Statistics\n\nPrediction\tMean Squared Error:\t{}\nTraining\tLearned Reduction MSE:\t{}\n\t\tIncrease MSE on New:\t{}\n\t\tPercent Change MSE:\t{}\n".format(numpy.float32(mseNew),mse0-mseL,numpy.float32(mseNew)-mseL,(mseL - mse0)/mse0*100))
    
    print("\nEvaluating Model\n")
    
    newPreds,newStatements = vecToStatements(y_pred,easy)
    distTRan,distRRan,distRReal = levDistance(newStatements,inputs,easy)
    cdistTRan,cdistRRan,cdistRReal = 0,0,0#customDistance(newPreds,X_test,easy)    
        
    print("Levenshtein Distance From Actual to Random Data:    {}\nLevenshtein Distance From Predicted to Random Data: {}\nLevenshtein Distance From Actual to Predicted Data: {}\n".format(distTRan,distRRan,distRReal))
    
    print("Custom Distance From Actual to Random Data:    {}\nCustom Distance From Predicted to Random Data: {}\nCustom Distance From Actual to Predicted Data: {}\n".format(cdistTRan,cdistRRan,cdistRReal))
    
    writeVectorFile("KBFitEasy.txt" if easy else "KBFit.txt",newStatements)
    
tf.reset_default_graph()

learning_rate1 = 0.0005 if easy else 0.005
n_epochs1 = 50000 if easy else 5000
train_size1 = X_train.shape[0]
n_neurons1 = y_train.shape[2]
n_layers1 = 1

X1 = tf.placeholder(tf.float32, shape=[None,X_train.shape[1],X_train.shape[2]])
y1 = tf.placeholder(tf.float32, shape=[None,y_train.shape[1],y_train.shape[2]])

basic_cell1 = tf.contrib.rnn.GRUCell(num_units=n_neurons1)
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
    
    writeVectorFile("predictedOutEasy.txt" if easy else "predictedOut.txt",newStatements)
    
    #saver.save(sess, "model.easy" if easy else "model")  
    
    data = numpy.load("halfwayEasy.npz" if easy else "halfway.npz",allow_pickle=True)
    data = data['arr_0'] 
    
    print("TESTING PIPELINE DATA\n")
    
    y_pred = sess.run(outputs1,feed_dict={X1: data})
    newPreds,newStatements = vecToStatements(y_pred,easy)
    distTRan,distRRan,distRReal = levDistance(newStatements,trueStatements,easy)
    cdistTRan,cdistRRan,cdistRReal = customDistance(newPreds,preds,easy)
    
    print("Levenshtein Distance From Actual to Random Data:    {}\nLevenshtein Distance From Predicted to Random Data: {}\nLevenshtein Distance From Actual to Predicted Data: {}\n".format(distTRan,distRRan,distRReal))
    
    print("Custom Distance From Actual to Random Data:    {}\nCustom Distance From Predicted to Random Data: {}\nCustom Distance From Actual to Predicted Data: {}\n".format(cdistTRan,cdistRRan,cdistRReal))    
    
    writeVectorFile("predictedOutFitEasy.txt" if easy else "predictedOutFit.txt",newStatements)