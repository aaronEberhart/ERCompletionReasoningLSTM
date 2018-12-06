class Term:
	
	def __init__(self,t):
		self.checkTerm(t)
		self.term = t
	
	def getTerm(self):
		return self.term
	
	def setTerm(self,t):
		self.term = t
	
	def toString(self):
		return str(self.term)
	
	def checkTerm(self,t):
		if not isinstance(t,(int,float,complex,str,bool)): raise Exception("Invalid Term")
	
class Terms(Term):
	
	def __init__(self,args):
		self.checkTerms(args)
		self.terms = [Term(term) for term in args]
	
	def checkTerms(self,terms):
		if not isinstance(terms,list): raise Exception("Invalid Terms")
	
	def toString(self):
		ret = ""
		for i in range(0, len(self.terms)):
			ret = ret + self.terms[i].toString()
			if i != len(self.terms) - 1:
				ret = ret + ","
		return ret
	
	def getTerm(self,i):
		return self.terms[i].getTerm()
	
	def setTerm(self,i,term):
		x = Term(term)
		self.terms[i] = x
	
	def len(self):
		return len(self.terms)