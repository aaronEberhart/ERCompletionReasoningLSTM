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
    
def makeData(trials):
    seq_in = numpy.empty(trials,dtype=numpy.ndarray)
    seq_out = numpy.empty(trials,dtype=numpy.ndarray)
    if not os.path.isdir("output"): os.mkdir("output")
     
    for i in range(0,trials):
        
        

        generator = HardGenERator2(rGenerator=GenERator(numCType1=3,numCType2=2,numCType3=3,numCType4=2,numRoleSub=2,numRoleChains=1,conceptNamespace=10,roleNamespace=4),difficulty=1)     
        
        reasoner = ReasonER(generator,showSteps=True)
        
        reasoner.ERason()
        #negatives = NegativesGenERator(reasoner)    
        print(i,generator.conceptNamespace,generator.roleNamespace)
	
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
            
    numpy.savez("dataEasy", seq_in,seq_out)
    
    return seq_in,seq_out

def getDataFromFile():
    data = numpy.load('data.npz',allow_pickle=True)
    return data['arr_0'],data['arr_1']

def pad(arr,maxlen1=0,maxlen2=0):

    for i in range(0,len(arr)):
        if len(arr[i]) > maxlen1: maxlen1 = len(arr[i])
        for j in range(0,len(arr[i])):
            if len(arr[i][j]) > maxlen2: maxlen2 = len(arr[i][j])
    
    newarr = numpy.empty(shape=(len(arr),maxlen1,maxlen2),dtype=float)
    for i in range(0,len(arr)):
        for j in range(0,len(arr[i])):
            for k in range(0,len(arr[i][j])):
                newarr[i][j][k] = arr[i][j][k]

    return newarr

def vecToStatements(vec):    
    four = []
    statements = []
    
    for i in range(len(vec)):
        trial = []
        for j in range(len(vec[i])):
            step = []
            for k in range(len(vec[i][j])):
                if len(four) == 3:
                    four.append(vec[i][j][k])
                    stri = convertToStatement(four)
                    if stri != None: step.append(stri)
                    four = []                    
                else:
                    four.append(vec[i][j][k])
            if len(step) > 0: 
                trial.append(step)
                four = []                
        statements.append(trial)
        
    return statements

def convertToStatement(four):
    concepts = 106#13#
    roles = 56#7#
    new = []
    threshc = 1 / concepts
    threshr = -1 / roles
    for number in four:
        if isinstance(number,numpy.float32): 
            number = number.item()
            if (number > 0 and number < threshc) or (number < 0 and number > threshr): number = 0
        if number < 0:
            if int(number * roles * -1) == 0: pass
            else: new.append("R{}".format(int(number * roles * -1)))
        elif number > 0:
            if int(number * concepts) == 0: pass
            else: new.append("C{}".format(int(number * concepts)))   
            
    if len(new) == 2:
        return " ⊑ ".join(new)
    elif len(new) == 3:
        if four[1] > 0 and four[2] < 0 and four[3] > 0:
            return "{} ⊑ ∃{}.{}".format(new[0],new[1],new[2])
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

X,y = getDataFromFile()#makeData(1000)#

#numpy.random.shuffle(X)
#numpy.random.shuffle(y)

X_train, X_test, y_train, y_test = splitTensors(X, y, 0.33)

X_train = pad(X_train)
X_test = pad(X_test,maxlen1=X_train.shape[1],maxlen2=X_train.shape[2])#

y_train = pad(y_train)
y_test = pad(y_test,maxlen1=X_train.shape[1],maxlen2=y_train.shape[2])#

print(X_train.shape, X_test.shape, y_train.shape,  y_test.shape)

writeVectorFile("targetIn.txt",vecToStatements(X_test))
writeVectorFile("targetOut.txt",vecToStatements(y_test))

learning_rate = 0.0001
n_epochs = 100000
train_size = X_train.shape[0]
n_neurons = y_train.shape[2]# * X_train.shape[2]
n_layers = 1

X = tf.placeholder(tf.float32, shape=[None,X_train.shape[1],X_train.shape[2]])
y = tf.placeholder(tf.float32, shape=[None,y_train.shape[1],y_train.shape[2]])

basic_cell = tf.contrib.rnn.LSTMCell(num_units=n_neurons,use_peepholes=True)
multi_layer_cell = tf.contrib.rnn.MultiRNNCell([basic_cell] * n_layers)
outputs, states = tf.nn.dynamic_rnn(multi_layer_cell, X, dtype=tf.float32)
accuracy = tf.metrics.accuracy(y_train,y)

loss = tf.reduce_sum(tf.reduce_sum(tf.reduce_sum(tf.math.square(outputs - y))))/(tf.to_float(tf.size(y)))
optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
training_op = optimizer.minimize(loss)

init = tf.global_variables_initializer()

saver = tf.train.Saver()

with tf.Session() as sess:
    init.run()
    for epoch in range(n_epochs):  
        sess.run(training_op,feed_dict={X: X_train,y: y_train})
        print("Epoch: {}\tMean Squared Error: {}".format(epoch,loss.eval(feed_dict={X: X_train, y: y_train})))#epoch)#
    y_pred = sess.run(outputs,feed_dict={X: X_test})
    writeVectorFile("predictedOut.txtS",vecToStatements(y_pred))
    saver.save(sess, "model")
