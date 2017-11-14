class Observer():
	def __init__(self,ob1=None , ob2 = None):
		self.output = SCQ
		self.input_1 = ob1
		self.input_2 = ob2
		self.rd_ptr_1 = 0
		self.rd_ptr_2 = 0
		self.status_stack = []
		self.desired_time_stamp_1 = 0
		self.desired_time_stamp_2 = 0

	def write_result(self,input):
		self.SCQ.add(input)

	def read_next(self,desired_time_stamp,observer_number=1):
		assert observer_number in (1,2), 'Error: wrong oberver number to read.'
		if observer_number == 1:
			return self.input_1.SCQ.try_read_and_fetch_data(self,rd_ptr_1,desired_time_stamp)
		else:
			return self.input_2.SCQ.try_read_and_fetch_data(self,rd_ptr_2,desired_time_stamp)

	# record status before do any operations to the SCQ every time
	def record_status(self):
		status_stack.append([self.SCQ.wr_ptr,self.rd_ptr_1,self.rd_ptr_2,self.SCQ.queue[wr_ptr]])

	# This method is used in backtracking
	def recede_status(self):
		self.SCQ.wr_ptr,self.rd_ptr_1,self.rd_ptr_2, pre_content = status_stack.pop()
		self.SCQ.force_modify(pre_content)



class ATOM(Observer):
	def __init__(self,name):
		self.type = 'ATOMIC'
		# feed data use self.name as the key
		self.name = name

class GLOBAL(Observer):
	def __init__(self,ob1,ub,lb=0):
		self.type = 'GLOBAL'
		self.lb = lb
		self.ub = ub
		super().__init__(ob1)


class UNTIL(Observer):
	def __init__(self,ob1,ob2,ub,lb=0):
		self.type = 'UNTIL'
		self.lb = lb
		self.ub = ub
		super().__init__(ob1,ob2)

class NEG(Observer):
	def __init__(self,ob1):
		self.type = 'NEG'
		super().__init__(ob1)

	def run():
		res = ob1.read_next(self.desired_time_stamp_1)
		while(res[0]==False):
			write_result([res[1][0],not res[1][1]])
			self.desired_time_stamp_1 = res[1][0]+1
			res = ob1.read_next(self.desired_time_stamp_1)

class AND(Observer):
	def __init__(self,ob1,ob2):
		self.type = 'AND'
		super().__init__(ob1,ob2)


"""
SCQ: Shared Connection Queue
"""
class SCQ():
	# Content structure: ([0]:timestamp, [1]:verdict)
	def __init__(self):
		self.wr_ptr = 0;
		self.queue = []

	def add(self,input):
		if self.wr_ptr == 0 or self.queue[wr_ptr][1] != input[1]:
			self.queue[wr_ptr][:] = input
			self.wr_ptr += 1
		else:
			# Aggregation
			self.queue[wr_ptr][0] = input[0]

	def force_modify(self,input):
		self.queue[self.wr_ptr] = input

	def try_read_and_fetch_data(self,rd_ptr,desired_time_stamp):
		isEmpty = False
		result = [-1,0]
		while rd_ptr<self.wr_ptr and self.queue[rd_ptr][0]<desired_time_stamp:
			rd_ptr += 1
		if rd_ptr == self.wr_ptr:
			isEmpty = True
		else:
			result = self.queue[rd_ptr]
		return isEmpty,result
		


