from Predicate import *

x = Concept('concept',[345])
x.display()

y = Role('role',["gfdfd",'a'])
y.display()

try:
	z = Predicate(True,[5,5])
	z.display()
except Exception as ex:
	print(ex)

try:
	w = Concept(True,[5,5])
	w.display()
except Exception as ex:
	print(ex)

try:
	a = Concept(True,[[5]])
	a.display()
except Exception as ex:
	print(ex)

try:
	b = Role(786,[65756])
	b.display()
except Exception as ex:
	print(ex)

try:
	c = Role(786,65756)
	c.display()
except Exception as ex:
	print(ex)
