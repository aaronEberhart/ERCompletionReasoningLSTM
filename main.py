import os,sys
me = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,me+"/Generator")
sys.path.insert(0,me+"/Reasoner")

from Statement import *

def runStatementTests():
	
	s = ConceptStatement(0,0,True)
	s.addToAntecedent(ConceptRole('e',Role('a',[0,1]),Concept('b',[1])))
	t = ConceptStatement(1,2,False)
	t.addToAntecedent(Concept('d',[2]))
	t.addToConsequent(Concept('e',[2]))
	s.addToConsequent(ConceptRole('e',Role('c',[0,2]),t))
	print(s.toString())

def runPredTests():
	
	x = Concept('concept',['a'])
	print(x.toString())
	
	y = Role('role',["gfdfd",'a'])
	print(y.toString())
	
	aa = ConceptRole('e',Role('role',['b','a']),Concept('concept',['a']))
	print(aa.toString())

	ab = ConceptRole('e',Role('role',['c','b']),aa)
	print(ab.toString())

	print()

	try:
		w = Concept(True,[5,5])
		print(w.toString())
	except Exception as ex:
		print(ex)
	
	try:
		a = Concept(True,[[5]])
		print(a.toString())
	except Exception as ex:
		print(ex)
	
	try:
		b = Role(786,[65756])
		print(b.toString())
	except Exception as ex:
		print(ex)
	
	try:
		c = Role(786,65756)
		print(c.toString())
	except Exception as ex:
		print(ex)
		
	try:
		cr = ConceptRole(786,Concept(765,[5465]),Role(453,[45646,6876]))
		print(cr.toString())
	except Exception as ex:
		print(ex)
		
	try:
		cra = ConceptRole(786,Role(453,[45646,1]),Concept(765,[1]))
		print(cra.toString())
	except Exception as ex:
		print(ex)
		
		
if __name__ == "__main__":
	#runPredTests()
	runStatementTests()