# ------------------------------------------------------------
# Observer.py
# ----------------------------------
# 5 kinds of observers: G,&,!,U,Atomic
# Shared Connection Queue: SCQ
# ----------------------------------
# Author: Pei Zhang
# ------------------------------------------------------------
import logging, sys

# Comment this line to disable debug info
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

class Observer():
	def __init__(self, ob1=None, ob2=None):
		self.scq = SCQ(size=200)#depth of the queue is 200
		self.input_1 = ob1
		self.input_2 = ob2
		self.rd_ptr_1 = 0
		self.rd_ptr_2 = 0
		self.status_stack = []
		self.desired_time_stamp_1 = 0
		self.desired_time_stamp_2 = 0
		self.is_healthy = True

	def write_result(self,data):
		self.scq.add(data)
		if data[1] == False:
			self.is_healthy = False # Should I reset the status???

	def read_next(self,desired_time_stamp,observer_number=1):
		assert observer_number in (1,2), 'Error: wrong oberver number to read.'
		if observer_number == 1:
			return self.input_1.scq.try_read_and_fetch_data(self.rd_ptr_1,desired_time_stamp)
		else:
			return self.input_2.scq.try_read_and_fetch_data(self.rd_ptr_2,desired_time_stamp)

	# record status before do any operations to the SCQ every time
	def record_status(self):
		if self.scq.wr_ptr == 0:#at the beginning
			self.status_stack.append([0,0,0,(0,False)])
		else:
			self.status_stack.append([self.scq.wr_ptr,self.rd_ptr_1,self.rd_ptr_2,self.scq.queue[self.scq.wr_ptr-1]])

	# This method is used in backtracking
	def recede_status(self):
		self.scq.wr_ptr,self.rd_ptr_1,self.rd_ptr_2, pre_content = status_stack.pop()
		self.scq.force_modify(pre_content)

###########################################################
class ATOM(Observer):
	def __init__(self,name):
		logging.debug('Initiate ATOMIC %s',name)
		self.type = 'ATOMIC'
		# feed data use self.name as the key
		self.name = name
		super().__init__()
	def run(self,var,time):
		res = (time,False) if var==0 else (time,True)
		super().record_status()
		super().write_result(res)
		logging.debug('%s %s return: %s',self.type, self.name, res)


class GLOBAL(Observer):
	def __init__(self,ob1,ub,lb=0):
		logging.debug('Initiate GLOBAL Observer')
		self.type = 'GLOBAL'
		self.lb = lb
		self.ub = ub
		super().__init__(ob1)

class UNTIL(Observer):
	def __init__(self,ob1,ob2,ub,lb=0):
		logging.debug('Initiate UNTIL Observer')
		self.type = 'UNTIL'
		self.lb = lb
		self.ub = ub
		super().__init__(ob1,ob2)

class NEG(Observer):
	def __init__(self,ob1):
		logging.debug('Initiate NEG Observer')
		self.type = 'NEG'
		super().__init__(ob1)

	def run(self):
		read = super().read_next(self.desired_time_stamp_1)
		while(read[0]==False):
			res = (read[1][0],not read[1][1])
			super().write_result(res)
			logging.debug('%s return: %s',self.type, res)
			self.desired_time_stamp_1 = read[1][0]+1
			read = super().read_next(self.desired_time_stamp_1)
			

class AND(Observer):
	def __init__(self,ob1,ob2):
		logging.debug('Initiate AND Observer')
		self.type = 'AND'
		super().__init__(ob1,ob2)


###########################################################
"""
SCQ: Shared Connection Queue
"""
class SCQ():
	# Content structure: ([0]:timestamp, [1]:verdict)
	def __init__(self,size):
		self.wr_ptr = 0;
		self.queue = [[0 for x in range(2)] for y in range(size)] # revise the queue from list to array to speed up

	def add(self,data):
		# push data into the SCQ
		if self.wr_ptr == 0 or self.queue[self.wr_ptr][1] != data[1]:
			self.queue[self.wr_ptr][:] = data
			self.wr_ptr += 1
		else:
			# Aggregation
			self.queue[self.wr_ptr][0] = data[0]

	def force_modify(self,data):
		# modify SCQ content for backtracking
		self.queue[self.wr_ptr] = data

	# Searching for interval that contains info time_stamp >= desired_time_stamp
	def try_read_and_fetch_data(self,rd_ptr,desired_time_stamp):
		#logging.debug('SCQ: wr_ptr: %d, rd_ptr: %d, dt: %d',self.wr_ptr,rd_ptr,desired_time_stamp)
		isEmpty = False
		result = [-1,False]
		while rd_ptr<self.wr_ptr and self.queue[rd_ptr][0]<desired_time_stamp:
			rd_ptr += 1
		if rd_ptr == self.wr_ptr:
			isEmpty = True
			if rd_ptr > 0:
				rd_ptr -= 1
		else:
			result = self.queue[rd_ptr]
			#print('scq return result:',result)
		return isEmpty,result
		


