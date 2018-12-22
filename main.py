"""
⊑ ⊓ ⊔ ≡ ∘ ¬
"""

import os,sys
me = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,me+"/Generator")
sys.path.insert(0,me+"/Reasoner")

from test import *

if __name__ == "__main__":
	
	gen = GenERator()
	gen.genERate()
	print(gen.toString())
	