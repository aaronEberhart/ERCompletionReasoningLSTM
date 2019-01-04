"""
⊑ ⊓ ⊔ ≡ ∘ ¬
"""

import os,sys
me = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,me+"/Generator")
sys.path.insert(0,me+"/Reasoner")

from GenERator import *
from ReasonER import *
from NegativesGenERator import *

if __name__ == "__main__":
	
	generator = GenERator()
	
	reasoner = ReasonER(generator)
	
	result = NegativesGenERator(reasoner)
	
	print(result.toString())