import os,sys,time
me = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,me+"/Generator")
sys.path.insert(0,me+"/Reasoner")

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

def runExperiment(i):
	start = time.time()
	
	generator = GenERator()	
	
	reasoner = ReasonER(generator,showSteps=True)

	reasonerSteps = StepFindER(reasoner)
	
	negatives = NegativesGenERator(reasoner)
	
	writeFile("owl/{}funcSynt.owl".format(i),reasoner.toFunctionalSyntax("<http://www.randomOntology.com/not/a/real/IRI/>"))
	writeFile("output/{}KB.txt".format(i),generator.toString()+reasoner.toString()+negatives.toString())
	writeFile("output/{}details.txt".format(i),formatStatistics(start,generator,reasoner,negatives)+reasoner.getLog()+reasonerSteps.toString())

if __name__ == "__main__":
	if not os.path.isdir("output"): os.mkdir("output")
	if not os.path.isdir("owl"): os.mkdir("owl")
	for i in range(0,1):
		runExperiment(i)