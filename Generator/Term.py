from abc import *

class Term:
	
	def __init__(self,t):
		if not self.validTerm(t): raise Exception("Invalid Term")
		self.term = t
	
	def getTerm(self):
		return self.term
	
	def setTerm(self,t):
		self.term = t
	
	def toString(self):
		return str(self.term)
	
	@staticmethod
	def validTerm(t):
		return isinstance(t,(int,float,complex,str,bool))
	
class Terms(Term):
	
	def __init__(self,args):
		if not Terms.validTerms(args): raise Exception("Invalid Terms")
		self.terms = [Term(term) for term in args]
	
	@staticmethod
	def validTerms(terms):
		return isinstance(terms,list)
	
	def toString(self):
		ret = ""
		for i in range(0, len(self.terms)):
			ret = ret + Term.toString(self.getTerm(i))
			if i != len(self.terms) - 1:
				ret = ret + ","
		return ret
	
	def getTerm(self,i):
		return self.terms[i]
	
	def setTerm(self,i,term):
		x = Term(term)
		self.terms[i] = x
	
	def len(self):
		return len(self.terms)