class Observer():
	def __init__(self,ob1=None , ob2 = None):
		self.output = SCQ
		self.input_1 = ob1
		self.input_2 = ob2
		self.rd_ptr_1 = 0
		self.rd_ptr_2 = 0 

"""
SCQ: Shared Connection Queue
"""
class SCQ():
	def __init__(self):
		self.wr_ptr = 0;
		self.queue = []

class ATOM(Observer):
	def __init__(self,input):
		self.input = input

class GLOBAL(Observer):
	def __init__(self,ob1,ub,lb=0):
		self.lb = lb
		self.ub = ub
		super().__init__(ob1)

class UNTIL(Observer):
	def __init__(self,ob1,ob2,ub,lb=0):
		self.lb = lb
		self.ub = ub
		super().__init__(ob1,ob2)

class NEG(Observer):
	def __init__(self,ob1):
		super().__init__(ob1)

class AND(Observer):
	def __init__(self,ob1,ob2):
		super().__init__(ob1,ob2)

