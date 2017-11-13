class state():
	def __init__(self, name, var = {}):
		self.name = name
		self.next = set()
		self.var = var

	def __repr__(self):
		return self.name
	# def __init__(self, name, variables):
	# 	self.name = name
	# 	self.var = variables

	# def add_next(self,state):
	# 	self.next.add(state)
