import os,sys,time
me = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,me+"/Generator")
sys.path.insert(0,me+"/Reasoner")

from HardGenERator2 import *
from HardGenERator import *
from GenERator import *
from ReasonER import *
from NegativesGenERator import *
from StepFindER import *

def writeFile(filename,data):
	file = open(filename,"w")
	file.write(data)
	file.close()

def formatStatistics(start,gen,reas,neg):
	genStats = gen.getStatistics()
	reasStats = reas.getStatistics()
	negStats = neg.getStatistics()
	return "KB {} Time: {}seconds\nRandom Seed: {}\nGeneratorStats:\n\tStatements: {}\n\tPredicates:\n\t\t{} unique\n\t\t{} total\n\tConcepts:\n\t\t{} unique\n\t\t{} total\n\tRoles:\n\t\t{} unique\n\t\t{} total\nReasonerStats:\n\tStatements: {}\n\tPredicates:\n\t\t{} unique\n\t\t{} total\n\tConcepts:\n\t\t{} unique\n\t\t{} total\n\tRoles:\n\t\t{} unique\n\t\t{} total\nNegativesStats:\n\tStatements: {}\n\tPredicates:\n\t\t{} unique\n\t\t{} total\n\tConcepts:\n\t\t{} unique\n\t\t{} total\n\tRoles:\n\t\t{} unique\n\t\t{} total\n".format(i,time.time()-start,gen.seed, \
	              len(gen.CType1)+len(gen.CType2)+len(gen.CType3)+len(gen.CType4)+len(gen.roleChains)+len(gen.roleSubs),genStats[0][1][1],genStats[0][2][1],genStats[1][1][1],genStats[1][2][1],genStats[2][1][1],genStats[2][2][1], \
	              len(reas.knownCType1)+len(reas.knownCType3),reasStats[0][1][1],reasStats[0][2][1],reasStats[1][1][1],reasStats[1][2][1],reasStats[2][1][1],reasStats[2][2][1], \
	              len(neg.notCType1)+len(neg.notCType2)+len(neg.notCType3)+len(neg.notCType4)+len(neg.notRoleChains)+len(neg.notRoleSubs),negStats[0][1][1],negStats[0][2][1],negStats[1][1][1],negStats[1][2][1],negStats[2][1][1],negStats[2][2][1])

def keepTrying(listy,y):
	return not any(x.consequent.name == y for x in listy)

def writeFileI(i,generator,reasoner,reasonerSteps,negatives,start):
	if not os.path.isdir("output/{}".format(i)): os.mkdir("output/{}".format(i))
	if not os.path.isdir("output/{}/sequence".format(i)): os.mkdir("output/{}/sequence".format(i))
	if not os.path.isdir("output/{}/KB during sequence".format(i)): os.mkdir("output/{}/KB during sequence".format(i))
	if len(reasoner.KBaLog) > 0 and not os.path.isdir("output/{}/KB after sequence".format(i)): os.mkdir("output/{}/KB after sequence".format(i))
	writeFile("owl/{}funcSyntKB.owl".format(i),reasoner.genToFunctionalSyntax("<http://www.randomOntology.com/not/a/real/IRI/>"))
	writeFile("owl/{}funcSyntKBCompleted.owl".format(i),reasoner.toFunctionalSyntax("<http://www.randomOntology.com/not/a/real/IRI/>"))
	for j in range(0,len(reasoner.sequenceLog)):
		writeFile("output/{}/sequence/reasonerStep{}.txt".format(i,j),reasoner.getSequenceLogI(j))
	for j in range(0,len(reasoner.KBsLog)):
		if len(reasoner.KBsLog[j]) > 0: writeFile("output/{}/KB during sequence/reasonerStep{}.txt".format(i,j),reasoner.getKBsLogI(j))
	for j in range(0,len(reasoner.KBaLog)):
		if len(reasoner.KBaLog[j]) > 0: writeFile("output/{}/KB after sequence/reasonerStep{}.txt".format(i,j+len(reasoner.sequenceLog)),reasoner.getKBaLogI(j))
	writeFile("output/{}/completedKB.txt".format(i),generator.toString()+reasoner.toString()+negatives.toString())
	writeFile("output/{}/completedReasonerDetails.txt".format(i),formatStatistics(start,generator,reasoner,negatives)+reasoner.getRuleCountString()+reasoner.getLog()+reasonerSteps.toString())	
	#if len(reasoner.KBaLog) < 1: print("after error")
	if len(reasoner.sequenceLog) != 100: print("seq error")

def runExperiment(i,diff):
	
	start = 0
	
	tryAgain = True 
	
	while tryAgain:
		
		start = time.time()
		
		generator = HardGenERator2(rGenerator=GenERator(numCType1=25,numCType2=25,numCType3=25,numCType4=25,numRoleSub=10,numRoleChains=10,conceptNamespace=100,roleNamespace=20),difficulty=diff)
		
		generator.genERate()
		
		tryAgain = keepTrying(generator.CType1,generator.rGenerator.conceptNamespace-1) # not len(reasoner.KBaLog) > 0 #
		
	reasoner = ReasonER(generator,showSteps=True)	 
	
	reasonerSteps = StepFindER(reasoner)
	
	negatives = NegativesGenERator(reasoner)
	
	writeFileI(i,generator,reasoner,reasonerSteps,negatives,start)	

if __name__ == "__main__":
	if not os.path.isdir("output"): os.mkdir("output")
	if not os.path.isdir("owl"): os.mkdir("owl")
	for i in range(0,1000):
		print(i)
		runExperiment(i,50)
