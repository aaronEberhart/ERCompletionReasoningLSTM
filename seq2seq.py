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

import tensorflow as tf
tf.logging.set_verbosity(tf.logging.ERROR)

from numpy import array
from keras.models import Model
from keras.layers import Input
from keras.layers import LSTM
from keras.layers import Dense
from keras.layers import RepeatVector
from keras.layers import TimeDistributed

generator = HardGenERator2(rGenerator=GenERator(numCType1=25,numCType2=25,numCType3=25,numCType4=25,numRoleSub=15,numRoleChains=10,conceptNamespace=100,roleNamespace=25),difficulty=10)

reasoner = ReasonER(generator,showSteps=True)

negatives = NegativesGenERator(reasoner)

dependencies = DependencyReducer(generator.getAllExpressions(),reasoner.sequenceLog,reasoner.KBsLog,reasoner.KBaLog)

seq_in,maxin,seq_out,maxout = dependencies.toVector(generator.conceptNamespace,generator.roleNamespace)


# define input sequence
#seq_in = array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
# reshape input into [samples, timesteps, features]
n_in = len(seq_in)
seq_in = array(seq_in).reshape((1,n_in,4))
print(seq_in)

# prepare output sequence
seq_out = array(seq_in)[:, 1:, :]
n_out = n_in - 1

# define encoder
visible = Input(shape=(n_in,1))
encoder = LSTM(100, activation='relu')(visible)

# define reconstruct decoder
decoder1 = RepeatVector(n_in)(encoder)
decoder1 = LSTM(100, activation='relu', return_sequences=True)(decoder1)
decoder1 = TimeDistributed(Dense(1))(decoder1)

# define predict decoder
decoder2 = RepeatVector(n_out)(encoder)
decoder2 = LSTM(100, activation='relu', return_sequences=True)(decoder2)
decoder2 = TimeDistributed(Dense(1))(decoder2)

# tie it together
model = Model(inputs=visible, outputs=[decoder1, decoder2])
model.compile(optimizer='adam', loss='mse')

# fit model
model.fit(seq_in, [seq_in,seq_out], epochs=300, verbose=0)

# demonstrate prediction
yhat = model.predict(seq_in, verbose=0)
print(yhat)

