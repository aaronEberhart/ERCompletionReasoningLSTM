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
	
	reasoner = ReasonER(GenERator())
	reasoner.ERason()
	print(reasoner.toString())
	