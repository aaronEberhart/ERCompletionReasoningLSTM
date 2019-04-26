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

def makeData(trials):
    seq_in = numpy.empty(trials,dtype=numpy.ndarray)
    seq_out = numpy.empty(trials,dtype=numpy.ndarray)
    
    for i in range(0,trials):
        
        print(i)
        
        generator = HardGenERator2(rGenerator=GenERator(numCType1=2,numCType2=2,numCType3=2,numCType4=2,numRoleSub=2,numRoleChains=2,conceptNamespace=10,roleNamespace=6),difficulty=2)
        
        reasoner = ReasonER(generator,showSteps=True)
        
        negatives = NegativesGenERator(reasoner)
        
        dependencies = DependencyReducer(generator.getAllExpressions(),reasoner.sequenceLog,reasoner.KBsLog,reasoner.KBaLog)
        
        seq_in[i],seq_out[i] = dependencies.toVector(generator.conceptNamespace,generator.roleNamespace)
    
    numpy.savez("data", seq_in,seq_out)
    
    return seq_in,seq_out

def getDataFromFile():
    data = numpy.load('data.npz',allow_pickle=True)
    return data['arr_0'],data['arr_1']

def pad(arr,maxlen=0):

    for i in range(0,len(arr)):
        if len(arr[i][0]) > maxlen: maxlen = len(arr[i][0])
        
    
    newarr = numpy.empty(shape=(len(arr),len(arr[0]),maxlen),dtype=float)
    for i in range(0,len(arr)):
        for j in range(0,len(arr[i])):
            for k in range(0,len(arr[i][j])):
                newarr[i][j][k] = arr[i][j][k]

    return newarr

X,y = getDataFromFile()#makeData(1000)#

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)

y_train = pad(y_train)
y_test = pad(y_test,y_train.shape[2])
X_train = pad(X_train)
X_test = pad(X_test,X_train.shape[2])

print(X_train.shape, y_train.shape, X_test.shape, y_test.shape)

n_epochs = 2
train_size = X_train.shape[0]
n_neurons = X_train.shape[0]
n_layers = 1

X = tf.placeholder(tf.float32, shape=X_train.shape)
y = tf.placeholder(tf.int32, shape=y_train.shape)

basic_cell = tf.contrib.rnn.LSTMCell(num_units=n_neurons,use_peepholes=True)
multi_layer_cell = tf.contrib.rnn.MultiRNNCell([basic_cell] * n_layers)
outputs, states = tf.nn.dynamic_rnn(multi_layer_cell, X, dtype=tf.float32)

init = tf.global_variables_initializer()

with tf.Session() as sess:
    init.run()
    for epoch in range(n_epochs):
        for iteration in range(train_size):    
            sess.run(outputs,feed_dict={X: X_train,y: y_train})
        acc_train = accuracy.eval(feed_dict={X: X_train, y: y_train})
        acc_test = accuracy.eval(feed_dict={X: X_test, y: y_test})
        print(epoch, "Train accuracy:", acc_train, "Test accuracy:", acc_test)        