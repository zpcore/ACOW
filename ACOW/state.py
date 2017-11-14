class state():
	def __init__(self, name, var = {}):
		self.name = name
		self.next = set()
		self.var = var

	def __repr__(self):
		return self.name
