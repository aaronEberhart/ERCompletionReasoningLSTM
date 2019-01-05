from GenERator import *

def runStatementTests():
	
	t = ConceptStatement(1,False,Concept('d',[2]),Concept('e',[2]))
	t.complete('⊓')
	
	cr = ConceptRole('e',Role('c',[0,2]),t)
	s = ConceptStatement(0,True,ConceptRole('e',Role('a',[0,2]),Concept('b',[2])),cr)
	s.complete('⊑')
	
	print(s.toString())
	
	rs = RoleStatement(0,True,Role('a',[0,1]),Role('b',[0,1]))
	rs.addToConsequent(Role('c',[1,2]))	
	rs.addToAntecedent(Role('d',[1,2]))
	rs.addToConsequent(Role('e',[2,3]))
	rs.addToConsequent(Role('g',[3,4]))
	rs.addToAntecedent(Role('f',[2,3]))
	rs.addToAntecedent(Role('h',[3,4]))	
	rs.complete('⊑')
	
	print(rs.toString())
	
	print()

def runPredTests():
	
	x = Concept('concept',['a'])
	print(x.toString())
	
	y = Role('role',["gfdfd",'a'])
	print(y.toString())
	
	aa = ConceptRole('e',Role('role',['b','a']),Concept('concept',['a']))
	print(aa.toString())

	ab = ConceptRole('e',Role('role',['c','b']),aa)
	print(ab.toString())
	
	rc = RoleChain(0,Role('a',[0,1]),Role('b',[1,2]))
	print(rc.toString())

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
		
	try:
		rcc = RoleChain(0,Role('a',[0,1]),Role('b',[2,2]))
		print(rcc.toString())
	except Exception as ex:
		print(ex)
	
	try:
		rcc = RoleChain(0,Role('a',[0,1]),Role('b',[1]))
		print(rcc.toString())
	except Exception as ex:
		print(ex)
	
	try:
		rcc = RoleChain(0,Role('a',[0,1]))
		rcc.appendRoles([Role('b',[2,2])])
		print(rcc.toString())
	except Exception as ex:
		print(ex)
		
	print()
