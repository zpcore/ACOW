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
	def __init__(self, ob1=None, ob2=None, name=None):
		self.scq = SCQ(name=name+'_SCQ',size=20)#depth of the queue is 10
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
			self.status_stack.append([0,0,0,True,0,0,[0,False]])
		else:
			self.status_stack.append([self.scq.wr_ptr, self.rd_ptr_1, self.rd_ptr_2, self.is_healthy,\
				self.desired_time_stamp_1, self.desired_time_stamp_2, self.scq.queue[self.scq.wr_ptr-1]])

	# This method is used in backtracking
	def recede_status(self):
		self.scq.wr_ptr,self.rd_ptr_1,self.rd_ptr_2, self.is_healthy, self.desired_time_stamp_1,\
		self.desired_time_stamp_2, pre_content = self.status_stack.pop()
		#print(self.scq.wr_ptr,self.rd_ptr_1,pre_content)
		self.scq.force_modify(pre_content)

###########################################################
class ATOM(Observer):
	def __init__(self,name):
		logging.debug('Initiate ATOMIC %s',name)
		self.type = 'ATOMIC'
		self.name= name
		# feed data use self.name as the key
		super().__init__(name=name)

	def run(self,var,time):
		super().record_status()
		res = [time,False] if var[self.name]==0 else [time,True]
		super().write_result(res)
		logging.debug('%s %s return: %s',self.type, self.name, res)


class GLOBAL(Observer):
	def __init__(self,ob1,ub,lb=0):
		logging.debug('Initiate GLOBAL Observer')
		self.type = 'GLOBAL'
		self.lb = lb
		self.ub = ub
		self.m_up = 0
		self.verdict_pre = False
		super().__init__(ob1,name='G')

	def run(self):
		super().record_status()	
		isEmpty, time_stamp, verdict = super().read_next(self.desired_time_stamp_1)
		while(not isEmpty):
			#res = [0,False]
			self.desired_time_stamp_1 = time_stamp+1
			if verdict and not self.verdict_pre:
				self.m_up = time_stamp
			if verdict:
				if time_stamp-self.m_up >= self.ub-self.lb:
					res = [time_stamp-self.ub,True]
					super().write_result(res)
					logging.debug('%s return: %s',self.type, res)
			elif time_stamp-self.lb >= 0:
				res = [time_stamp-self.lb,False]
				super().write_result(res)
				logging.debug('%s return: %s',self.type, res)
			self.verdict_pre = verdict
			isEmpty, time_stamp, verdict = super().read_next(self.desired_time_stamp_1)



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
		super().__init__(ob1,name='NEG')

	def run(self):
		super().record_status()
		isEmpty, time_stamp, verdict = super().read_next(self.desired_time_stamp_1)
		while(not isEmpty):
			res = [time_stamp,not verdict]
			self.desired_time_stamp_1 = time_stamp+1
			super().write_result(res)
			logging.debug('%s return: %s',self.type, res)
			isEmpty, time_stamp, verdict = super().read_next(self.desired_time_stamp_1)
			

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
	def __init__(self,name,size):
		self.name = name
		self.wr_ptr = 0;
		#self.queue = [[0 for x in range(2)] for y in range(size)] # revise the queue from list to array to speed up
		self.queue = [ [0,False] for y in range(size)] # revise the queue from list to array to speed up
		
	def add(self,data):
		#print('add operation:',self.name)
		# push data into the SCQ
		if self.wr_ptr ==0:
			self.queue[0] = data
			self.wr_ptr += 1
		elif self.queue[self.wr_ptr-1][1] != data[1]:
			self.queue[self.wr_ptr] = data			
			self.wr_ptr += 1
		else:
			# Aggregation
			self.queue[self.wr_ptr-1] = data
		#print(self.queue)

	def force_modify(self,data):
		# modify SCQ content for backtracking
		if self.wr_ptr > 0:
			self.queue[self.wr_ptr-1] = data

	# Searching for interval that contains info time_stamp >= desired_time_stamp
	def try_read_and_fetch_data(self,rd_ptr,desired_time_stamp):
		#logging.debug('SCQ: wr_ptr: %d, rd_ptr: %d, dt: %d',self.wr_ptr,rd_ptr,desired_time_stamp)
		isEmpty = False
		time_stamp = -1
		verdict = False
		while rd_ptr<self.wr_ptr and self.queue[rd_ptr][0]<desired_time_stamp:
			rd_ptr += 1
		if rd_ptr == self.wr_ptr:
			isEmpty = True
			if rd_ptr > 0:
				rd_ptr -= 1
		else:
			time_stamp, verdict = self.queue[rd_ptr]
		return isEmpty,time_stamp, verdict
		


