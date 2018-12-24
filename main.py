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
	reasoner = ReasonER(GenERator(numConceptTStatementsType1=50,numConceptTStatementsType2=50,numConceptTStatementsType3=50,numConceptTStatementsType4=50,numConceptAStatements=50,numRoleTStatements=50,numRoleAStatements=5,numRoleChainStatements=5))
	reasoner.ERason()
	print(reasoner.toString())