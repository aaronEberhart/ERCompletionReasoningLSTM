from Predicate import *

x = Concept('concept',[345])
x.display()

y = Role('role',["gfdfd",'a'])
y.display()

try:
	z = Concept(True,[5,5])
	z.display()
except Exception as ex:
	print(ex)

try:
	y = Role(786,[65756])
	y.display()
except Exception as ex:
	print(ex)