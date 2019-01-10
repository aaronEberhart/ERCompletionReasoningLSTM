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

if __name__ == "__main__":
	
	start = time.time()
	
	generator = GenERator()	
	
	reasoner = ReasonER(generator,showSteps=True)

	reasonerSteps = StepFindER(reasoner)
	
	negatives = NegativesGenERator(reasoner)
	
	writeFile("KB.txt",generator.toString()+reasoner.toString()+negatives.toString())
	writeFile("details.txt",reasoner.getLog()+reasonerSteps.toString())
	print("Time: {}seconds".format(time.time()-start))