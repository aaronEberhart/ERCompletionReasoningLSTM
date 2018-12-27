"""
⊑ ⊓ ⊔ ≡ ∘ ¬
"""

import os,sys
me = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,me+"/Generator")
sys.path.insert(0,me+"/Reasoner")

from GenERator import *
from ReasonER import *

if __name__ == "__main__":	
	reasoner = ReasonER(GenERator(numConceptTStatementsType1=50,numConceptTStatementsType2=25,numConceptTStatementsType3=15,numConceptTStatementsType4=10, numConceptAStatements=0,\
	                              numRoleTStatements=15,numRoleAStatements=0,numRoleChainStatements=5,conceptNamespace=25,roleNameSpace=25,termNamespace=5),\
	                    showSteps=False)
	reasoner.ERason()
	print(reasoner.toString())