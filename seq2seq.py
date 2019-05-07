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
    if not os.path.isdir("output"): os.mkdir("output")
     
    for i in range(0,trials):
        
        generator = HardGenERator2(rGenerator=GenERator(numCType1=2,numCType2=1,numCType3=2,numCType4=1,numRoleSub=1,numRoleChains=1,conceptNamespace=10,roleNamespace=4),difficulty=1) if easy else \
                    HardGenERator2(rGenerator=GenERator(numCType1=25,numCType2=25,numCType3=25,numCType4=25,numRoleSub=15,numRoleChains=10,conceptNamespace=100,roleNamespace=50),difficulty=2)
        
        reasoner = ReasonER(generator,showSteps=True)
        
        reasoner.ERason()
          
        #print(i,generator.conceptNamespace,generator.roleNamespace)
	
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
            
    numpy.savez("dataEasy" if easy else 'data', seq_in,seq_out)
    
    return seq_in,seq_out

def getDataFromFile(easy):
    data = numpy.load('dataEasy.npz' if easy else 'data.npz',allow_pickle=True)
    return data['arr_0'],data['arr_1']

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
    statements = []
    
    for i in range(len(vec)):
        trial = []
        for j in range(len(vec[i])):
            step = []
            for k in range(len(vec[i][j])):
                if len(four) == 3:
                    four.append(vec[i][j][k])
                    stri = convertToStatement(four,easy)
                    if stri != None: step.append(stri)
                    four = []                    
                else:
                    four.append(vec[i][j][k])
            if len(step) > 0: 
                trial.append(step)
                four = []                
        statements.append(trial)
        
    return statements

def convertToStatement(four,easy):
    concepts = 13 if easy else 106
    roles = 7 if easy else 56
    new = []
    threshc = 0.5 / concepts
    threshr = -0.5 / roles
    for number in four:
        if isinstance(number,numpy.float32): 
            number = number.item()
            if (number > 0 and number < threshc) or (number < 0 and number > threshr): number = 0
        if number < 0 and number >= -1:
            if int(number * roles * -1) == 0: pass
            else: new.append("R{}".format(int(number * roles * -1)))
        elif number > 0 and number <= 1:
            if int(number * concepts) == 0: pass
            else: new.append("C{}".format(int(number * concepts)))   
            
    if len(new) == 2:
        return " ⊑ ".join(new)
    elif len(new) == 3:
        if four[1] > 0 and four[2] < 0 and four[3] > 0:
            return "{} ⊑ ∃{}.{}".format(new[0],new[1],new[2])
        elif four[1] > 0 and four[0] < 0 and four[2] > 0:
            return "∃{}.{} ⊑ {}".format(new[0],new[1],new        [2])
        elif four[1] > 0 and four[0] > 0 and four[2] > 0:
            return "{} ⊓ {} ⊑ {}".format(new[0],new[1],new[2])
        elif four[1] < 0 and four[0] < 0 and four[2] < 0:
            return "{} ∘ {} ⊑ {}".format(new[0],new[1],new[2])
    else:
        return None
    
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


def finalDistance(newStatements,trueStatements,easy):
    
    rando = []
    
    for i in range(0,len(trueStatements)):
        kb = []
        for j in range(0,len(trueStatements[i])):
            step = []
            gen = GenERator(numCType1=len(trueStatements[i][j])//2,numCType2=0,numCType3=len(trueStatements[i][j]) - len(trueStatements[i][j])//2,numCType4=0,numRoleSub=0,numRoleChains=0,conceptNamespace=13,roleNamespace=7) if easy else GenERator(numCType1=len(trueStatements)/2,numCType2=0,numCType3=len(trueStatements)/2,numCType4=0,numRoleSub=0,numRoleChains=0,conceptNamespace=106,roleNamespace=56)
            gen.genERate()
            for k in range(0,len(gen.CType1)):
                step.append(gen.CType1[k].toString())
            for k in range(0,len(gen.CType3)):
                step.append(gen.CType3[k].toString())
            kb.append(step)
        rando.append(kb)
        
    trueStr = [["\t".join([z for z in y]) for y in x] for x in trueStatements]
    newStr = [["\t".join([z for z in y]) for y in x] for x in newStatements]
    randoStr = [["\t".join([z for z in y]) for y in x] for x in rando]
    
    levTR = 0
    levNR = 0
    levTN = 0
    
    for i in range(len(trueStr)):
        for j in range(len(trueStr[i])):
            levTR = levTR + levenshtein(trueStr[i][j],randoStr[i][j])
            levNR = levNR + (levenshtein(newStr[i][j],randoStr[i][j]) if len(newStr[i]) > j else levenshtein("",randoStr[i][j]))
            levTN = levTN + (levenshtein(trueStr[i][j],newStr[i][j]) if len(newStr[i]) > j else levenshtein(trueStr[i][j],""))
    
    return levTR,levNR,levTN

easy = True
fileShapes = [4,336,80] if easy else [8,2116,324]

X,y = getDataFromFile(easy)#makeData(1000,easy)#

X_train, X_test, y_train, y_test = splitTensors(X, y, 0.33)

X_train = pad(X_train,maxlen1=fileShapes[0],maxlen2=fileShapes[1])
X_test = pad(X_test,maxlen1=fileShapes[0],maxlen2=fileShapes[1])

y_train = pad(y_train,maxlen1=fileShapes[0],maxlen2=fileShapes[2])
y_test = pad(y_test,maxlen1=fileShapes[0],maxlen2=fileShapes[2])

print(X_train.shape, X_test.shape, y_train.shape,  y_test.shape)

trueStatements = vecToStatements(y_test,easy)

writeVectorFile("targetInEasy.txt" if easy else "targetIn.txt",vecToStatements(X_test,easy))
writeVectorFile("targetOutEasy.txt" if easy else "targetOut.txt",trueStatements)

learning_rate = 0.001 if easy else 0.01
n_epochs = 10000 if easy else 1000
train_size = X_train.shape[0]
n_neurons = y_train.shape[2]
n_layers = 1

X = tf.placeholder(tf.float32, shape=[None,X_train.shape[1],X_train.shape[2]])
y = tf.placeholder(tf.float32, shape=[None,y_train.shape[1],y_train.shape[2]])

basic_cell = tf.contrib.rnn.LSTMCell(num_units=n_neurons)#,use_peepholes=True)
multi_layer_cell = tf.contrib.rnn.MultiRNNCell([basic_cell] * n_layers)
outputs, states = tf.nn.dynamic_rnn(multi_layer_cell, X, dtype=tf.float32)

loss = tf.losses.mean_squared_error(y,outputs)#tf.reduce_sum(tf.reduce_sum(tf.reduce_sum(tf.math.square(outputs - y))))/(tf.to_float(tf.size(y)))
optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
training_op = optimizer.minimize(loss)

init = tf.global_variables_initializer()

saver = tf.train.Saver()

with tf.Session() as sess:
    init.run()
    mse0 = 0
    mseL = 0
    for epoch in range(n_epochs):  
        ynew,a = sess.run([outputs,training_op],feed_dict={X: X_train,y: y_train})
        mse = loss.eval(feed_dict={outputs: ynew, y: y_train})
        if epoch == 0: mse0 = mse
        if epoch == n_epochs - 1: mseL = mse
        print("Epoch: {}\tMean Squared Error:\t{}".format(epoch,mse))
        if mse < 0.0001:
            mseL = mse
            break
    y_pred = sess.run(outputs,feed_dict={X: X_test})
    mseNew = loss.eval(feed_dict={outputs: y_pred, y: y_test})
    newStatements = vecToStatements(y_pred,easy)
    distTRan,distRRan,distRReal = finalDistance(newStatements,trueStatements,easy)
    
    print("\nPrediction\tMean Squared Error:\t{}\nTraining\tLearned Reduction MSE:\t{}\n\t\tIncrease MSE on New:\t{}\n\t\tPercent Change MSE:\t{}\n".format(numpy.float32(mseNew),mse0-mseL,numpy.float32(mseNew)-mseL,(mseL - mse0)/mse0*100))
    
    print("Levenshtein Distance From Actual to Random Data:    {}\nLevenshtein Distance From Predicted to Random Data: {}\nLevenshtein Distance From Actual to Predicted Data: {}\n".format(distTRan,distRRan,distRReal))
    
    writeVectorFile("predictedOutEasy.txt" if easy else "predictedOut.txt",newStatements)
    
    saver.save(sess, "model.easy" if easy else "model")
