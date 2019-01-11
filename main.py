"""
⊑ ⊓ ⊔ ≡ ∘ ¬
"""

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

def runExperiment(i):
	start = time.time()
	
	generator = GenERator()	
	
	reasoner = ReasonER(generator,showSteps=True)

	reasonerSteps = StepFindER(reasoner)
	
	negatives = NegativesGenERator(reasoner)
	
	writeFile("output/{}KB.txt".format(i),generator.toString()+reasoner.toString()+negatives.toString())
	writeFile("output/{}details.txt".format(i),reasoner.getLog()+reasonerSteps.toString())
	
	print("KB {} Time: {}seconds".format(i,time.time()-start))	

if __name__ == "__main__":
	
	for i in range(0,1000):
		runExperiment(i)