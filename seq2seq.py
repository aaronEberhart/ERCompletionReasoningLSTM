from commonFunctions import *

def getDataFromFile(filename,easy):
    print("Loading data from "+filename)
    data = numpy.load(filename,allow_pickle=True)
    return data['arr_0'],data['arr_1'],data['arr_2']
def makeData(trials,easy):
    seq_in = numpy.empty(trials,dtype=numpy.ndarray)
    seq_out = numpy.empty(trials,dtype=numpy.ndarray)
    kbs = numpy.empty([trials,80 if easy else 588],dtype=numpy.float32)
    if not os.path.isdir("output"): os.mkdir("output")
     
    for i in range(0,trials):
        
        print("Making Random-Sequetial KB"+str(i))
        
        if not os.path.isdir("output/Dataset/{}".format(i)): os.mkdir("output/Dataset/{}".format(i))
        
        gen = GenERator(numCType1=2,numCType2=1,numCType3=2,numCType4=1,numRoleSub=1,numRoleChains=1,conceptNamespace=10,roleNamespace=4,CTypeNull=[],CType1=[],CType2=[],CType3=[],CType4=[],roleSubs=[],roleChains=[])
        
        generator = HardGenERator2(rGenerator=gen,difficulty=1) if easy else HardGenERator2(rGenerator=GenERator(numCType1=25,numCType2=25,numCType3=25,numCType4=25,numRoleSub=15,numRoleChains=10,conceptNamespace=100,roleNamespace=50),difficulty=2)
        
        generator.genERate()
        
        if generator.conceptNamespace != conceptSpace or generator.roleNamespace != roleSpace:
            raise
        
        generator.toFunctionalSyntaxFile("<http://www.randomOntology.com/Synthetic/Sequential/random/{}/>".format(i),"output/Dataset/{}/KB{}.owl".format(i,i))
        
        kbs[i] = array(generator.toVector())
        
        reasoner = ReasonER(generator,showSteps=True)
        
        reasoner.ERason()
	
        dependencies = DependencyReducer(generator.getAllExpressions(),reasoner.sequenceLog,reasoner.KBsLog,reasoner.KBaLog)
        
        seq_in[i],seq_out[i] = dependencies.toVector(generator.conceptNamespace,generator.roleNamespace)

        if not os.path.isdir("output/Dataset/{}/sequence".format(i)): os.mkdir("output/Dataset/{}/sequence".format(i))
        if not os.path.isdir("output/Dataset/{}/KB during sequence".format(i)): os.mkdir("output/Dataset/{}/KB during sequence".format(i))        
        if len(reasoner.KBaLog) > 0 and not os.path.isdir("output/Dataset/{}/KB after sequence".format(i)): os.mkdir("output/Dataset/{}/KB after sequence".format(i))
        reasoner.toFunctionalSyntaxFile("<http://www.randomOntology.com/Synthetic/Sequential/random/{}/>".format(i),"output/Dataset/{}/completion{}.owl".format(i,i))
        generator.toStringFile("output/Dataset/{}/completedKB.txt".format(i))
        reasoner.toStringFile("output/Dataset/{}/completedKB.txt".format(i))        
        for j in range(0,len(dependencies.donelogs[0])):
            writeFile("output/Dataset/{}/sequence/reasonerStep{}.txt".format(i,j),dependencies.toString(dependencies.donelogs[0][j]))
        for j in range(0,len(dependencies.donelogs[1])):
            if len(reasoner.KBsLog[j]) > 0: writeFile("output/Dataset/{}/KB during sequence/reasonerStep{}.txt".format(i,j),dependencies.toString(dependencies.donelogs[1][j]))
        for j in range(0,len(dependencies.donelogs[2])):
            if len(reasoner.KBaLog[j]) > 0: writeFile("output/Dataset/{}/KB after sequence/reasonerStep{}.txt".format(i,j+len(reasoner.sequenceLog)),dependencies.toString(dependencies.donelogs[2][j]))
            
    numpy.savez("saves/dataEasy" if easy else 'saves/data', kbs,seq_in,seq_out)
    
    return kbs,seq_in,seq_out

def shallowSystem(n_epochs0,learning_rate0):
    log.write("Testing Stepwise Trained LSTM\n\nMapping KB to Reasoner Justifications\n\n")
    print("")
    
    train_size0 = KBs_train.shape[0]
    n_neurons0 = X_train.shape[2]
    n_layers0 = 1
    
    X0 = tf.placeholder(tf.float32, shape=[None,KBs_train.shape[1],KBs_train.shape[2]])
    y0 = tf.placeholder(tf.float32, shape=[None,X_train.shape[1],X_train.shape[2]])
    
    basic_cell0 = tf.contrib.rnn.LSTMBlockCell(num_units=n_neurons0)
    multi_layer_cell0 = tf.contrib.rnn.MultiRNNCell([basic_cell0] * n_layers0)
    outputs0, states0 = tf.nn.dynamic_rnn(multi_layer_cell0, X0, dtype=tf.float32)
    
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
            log.write("Epoch: {}\tMean Squared Error:\t{}\n".format(epoch,mse))
            if mse < 0.0001:
                mseL = mse
                break
        
        y_pred = sess.run(outputs0,feed_dict={X0: KBs_test,y0: X_test}) 
        mseNew = loss0.eval(feed_dict={outputs0: y_pred, y0: X_test})
        newPreds,newStatements = vecToStatements(y_pred,conceptSpace,roleSpace)
        
        log.write("\nTraining Statistics\n\nPrediction\tMean Squared Error:\t{}\nTraining\tLearned Reduction MSE:\t{}\n\t\tIncrease MSE on New:\t{}\n\t\tPercent Change MSE:\t{}\n\n".format(numpy.float32(mseNew),mse0-mseL,numpy.float32(mseNew)-mseL,(mseL - mse0)/mse0*100))
        
        writeVectorFile("output/KBFitEasy.txt" if easy else "output/KBFit.txt",newStatements)
        
        numpy.savez("saves/halfwayEasy.npz" if easy else "saves/halfway.npz", y_pred)
      
    tf.reset_default_graph()
    
    log.write("\nMapping Reasoner Justifications to KB Completion\n\n")
    
    train_size1 = X_train.shape[0]
    n_neurons1 = y_train.shape[2]
    
    X1 = tf.placeholder(tf.float32, shape=[None,X_train.shape[1],X_train.shape[2]])
    y1 = tf.placeholder(tf.float32, shape=[None,y_train.shape[1],y_train.shape[2]])
    
    basic_cell1 = tf.contrib.rnn.LSTMBlockCell(num_units=n_neurons1)
    multi_layer_cell1 = tf.contrib.rnn.MultiRNNCell([basic_cell1] * n_layers0)
    outputs1, states1 = tf.nn.dynamic_rnn(multi_layer_cell1, X1, dtype=tf.float32)
    
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
            log.write("Epoch: {}\tMean Squared Error:\t{}\n".format(epoch,mse))
            if mse < 0.0001:
                mseL = mse
                break
        
        y_pred = sess.run(outputs1,feed_dict={X1: X_test})  
        mseNew = loss1.eval(feed_dict={outputs1: y_pred, y1: y_test})
        
        log.write("\nTraining Statistics\n\nPrediction\tMean Squared Error:\t{}\nTraining\tLearned Reduction MSE:\t{}\n\t\tIncrease MSE on New:\t{}\n\t\tPercent Change MSE:\t{}\n".format(numpy.float32(mseNew),mse0-mseL,numpy.float32(mseNew)-mseL,(mseL - mse0)/mse0*100))
        
        log.write("\nTESTING REASONER SUPPORT DATA\n\n")    
          
        newPreds,newStatements = vecToStatements(y_pred,conceptSpace,roleSpace)
        distTRan,distRReal = levDistance(newStatements,trueStatements,conceptSpace,roleSpace)
        cdistTRan,cdistRReal = customDistance(newPreds,preds,conceptSpace,roleSpace)   
        
        log.write("Levenshtein Distance From Actual to Random Data:    {}\nLevenshtein Distance From Actual to Predicted Data: {}\n".format(distTRan,distRReal))
        
        log.write("\nCustom Distance From Actual to Random Data:    {}\nCustom Distance From Actual to Predicted Data: {}\n".format(cdistTRan,cdistRReal))
        
        writeVectorFile("output/predictedOutEasy.txt" if easy else "output/predictedOut.txt",newStatements)
        
        data = numpy.load("saves/halfwayEasy.npz" if easy else "saves/halfway.npz",allow_pickle=True)
        data = data['arr_0'] 
        
        log.write("\nTESTING PIPELINED KB DATA\n\n")
        
        y_pred = sess.run(outputs1,feed_dict={X1: data})
        newPreds,newStatements = vecToStatements(y_pred,conceptSpace,roleSpace)
        distTRan,distRReal = levDistance(newStatements,trueStatements,conceptSpace,roleSpace)
        cdistTRan,cdistRReal = customDistance(newPreds,preds,conceptSpace,roleSpace)
        
        log.write("Levenshtein Distance From Actual to Random Data:    {}\nLevenshtein Distance From Actual to Predicted Data: {}\n".format(distTRan,distRReal))
        
        log.write("\nCustom Distance From Actual to Random Data:    {}\nCustom Distance From Actual to Predicted Data: {}\n\n".format(cdistTRan,cdistRReal))    
        
        writeVectorFile("output/predictedOutPEasy.txt" if easy else "output/predictedOutP.txt",newStatements)
        
def deepSystem(n_epochs2,learning_rate2):
    log.write("Testing Deep LSTM\n\nMapping KB to hidden layer to KB Completion\n\n")
    print("")
    
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
            print("Deep System\t\tEpoch: {}".format(epoch))
            ynew,a = sess.run([outputs2,training_op2],feed_dict={X0: KBs_train,y1: y_train})
            mse = loss2.eval(feed_dict={outputs2: ynew, y1: y_train})
            if epoch == 0: mse0 = mse
            if epoch == n_epochs2 - 1: mseL = mse
            log.write("Epoch: {}\tMean Squared Error:\t{}\n".format(epoch,mse))
            if mse < 0.0001:
                mseL = mse
                break
        
        y_pred = sess.run(outputs2,feed_dict={X0: KBs_test})  
        mseNew = loss2.eval(feed_dict={outputs2: y_pred, y1: y_test})
        log.write("\nTraining Statistics\n\nPrediction\tMean Squared Error:\t{}\nTraining\tLearned Reduction MSE:\t{}\n\t\tIncrease MSE on New:\t{}\n\t\tPercent Change MSE:\t{}\n".format(numpy.float32(mseNew),mse0-mseL,numpy.float32(mseNew)-mseL,(mseL - mse0)/mse0*100))
        
        log.write("\nTESTING HOLDOUT KB DATA\n\n")    
          
        newPreds,newStatements = vecToStatements(y_pred,conceptSpace,roleSpace)
        distTRan,distRReal = levDistance(newStatements,trueStatements,conceptSpace,roleSpace)
        cdistTRan,cdistRReal = customDistance(newPreds,preds,conceptSpace,roleSpace)   
        
        log.write("Levenshtein Distance From Actual to Random Data:    {}\nLevenshtein Distance From Actual to Predicted Data: {}\n".format(distTRan,distRReal))
        
        log.write("\nCustom Distance From Actual to Random Data:    {}\nCustom Distance From Actual to Predicted Data: {}\n".format(cdistTRan,cdistRReal))
        
        writeVectorFile("output/predictedOutEasyC.txt" if easy else "output/predictedOutC.txt",newStatements)    
    
if __name__ == "__main__":
    generate = False
    easy = True
    
    if not os.path.isdir("saves"): os.mkdir("saves")
    if not os.path.isdir("output"): os.mkdir("output")
    if generate and os.path.isdir("output/Dataset"): shutil.rmtree("output/Dataset")
    if not os.path.isdir("output/Dataset"): os.mkdir("output/Dataset")
    
    log = open("log.txt","w")    
    
    trials = 1000
    conceptSpace = 13 if easy else 106
    roleSpace = 7 if easy else 56
    
    if len(sys.argv) == 3:
        epochs = int(sys.argv[1])
        learningRate = float(sys.argv[2])
    else:
        epochs = 20000 if easy else 5000
        learningRate = 0.001 if easy else 0.05 
    
    KBs,dependencies,output = makeData(trials,easy) if generate else getDataFromFile('saves/dataEasy.npz' if easy else 'saves/data.npz',easy)
    
    fileShapes1 = [4,368,92] if easy else [5,328,160]
    
    KBs_test,KBs_train = repeatAndSplitKBs(KBs,fileShapes1[0],0.33)
                            
    X_train, X_test, y_train, y_test = splitTensors(dependencies, output, 0.33)
    
    X_train = pad(X_train,maxlen1=fileShapes1[0],maxlen2=fileShapes1[1])
    X_test = pad(X_test,maxlen1=fileShapes1[0],maxlen2=fileShapes1[1])
    
    y_train = pad(y_train,maxlen1=fileShapes1[0],maxlen2=fileShapes1[2])
    y_test = pad(y_test,maxlen1=fileShapes1[0],maxlen2=fileShapes1[2])
    
    print("KBs shape:\t\t{}\nExtended KBs shape:\t{}{}\nDependencies shape:\t{}{}\nOutput shape:\t\t{}{}\n\n".format(KBs.shape,KBs_train.shape,KBs_test.shape,X_train.shape,X_test.shape,y_train.shape,y_test.shape))
    log.write("KBs shape:\t\t{}\nExtended KBs shape:\t{}{}\nDependencies shape:\t{}{}\nOutput shape:\t\t{}{}\n\n".format(KBs.shape,KBs_train.shape,KBs_test.shape,X_train.shape,X_test.shape,y_train.shape,y_test.shape))

    KBvec,KBstr = vecToStatements(KBs_test,conceptSpace,roleSpace)
    preds,trueStatements = vecToStatements(y_test,conceptSpace,roleSpace)
    placeholder,inputs = vecToStatements(X_test,conceptSpace,roleSpace)
    
    writeVectorFile("output/KBsInEasy.txt" if easy else "output/KBsIn.txt",KBstr)
    writeVectorFile("output/dependenciesEasy.txt" if easy else "output/dependencies.txt",inputs)
    writeVectorFile("output/targetOutEasy.txt" if easy else "output/targetOut.txt",trueStatements)
    
    shallowSystem(int(epochs/2),learningRate)
    
    tf.reset_default_graph()
    
    deepSystem(epochs,learningRate/2)
    
    log.close()
    
    print("\nDone")

