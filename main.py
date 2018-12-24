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
	reasoner = ReasonER(GenERator(numConceptTStatementsType1=10,numConceptTStatementsType2=10,numConceptTStatementsType3=10,numConceptTStatementsType4=10, numConceptAStatements=5,\
	                              numRoleTStatements=15,numRoleAStatements=15,numRoleChainStatements=10,conceptNamespace=25,roleNameSpace=50,termNamespace=5),\
	                    showSteps=False)
	reasoner.ERason()
	print(reasoner.toString())