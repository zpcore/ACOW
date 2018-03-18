# ------------------------------------------------------------
# Observer.py
# ----------------------------------
# 5 kinds of observers: G,&,!,U,Atomic
# Shared Connection Queue: SCQ
# ----------------------------------
# Author: Pei Zhang
# ------------------------------------------------------------
import logging, sys

# use level=logging.DEBUG to enable debug info
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
#logging.basicConfig(stream=sys.stderr, level=logging.CRITICAL)

class Observer():
	def __init__(self, ob1=None, ob2=None, queue_size=2000,name='Default'):
		self.scq = SCQ(name=name+'_SCQ',size=queue_size)
		self.name = name
		self.input_1, self.input_2 = ob1, ob2
		self.rd_ptr_1, self.rd_ptr_2 = 0, 0
		self.status_stack = []
		self.desired_time_stamp = 0
		self.return_verdict = True
		self.has_output = True
		self.parent = None # This attribute is used for AST optimization

	def write_result(self,data):
		self.scq.add(data)
		self.has_output = True
		self.return_verdict = data[1]

	def read_next(self,desired_time_stamp,observer_number=1):
		assert observer_number in (1,2), 'Error: wrong oberver number to read.'
		if observer_number == 1:
			return self.input_1.scq.try_read_and_fetch_data(self.rd_ptr_1,desired_time_stamp)
		else:
			return self.input_2.scq.try_read_and_fetch_data(self.rd_ptr_2,desired_time_stamp)

	# record status before do any operations to the SCQ every time
	def record_status(self):
		queue_addr = 0 if self.scq.wr_ptr == 0 else self.scq.wr_ptr-1
		self.status_stack.append([self.scq.wr_ptr, self.rd_ptr_1, self.rd_ptr_2,\
			self.desired_time_stamp, self.return_verdict, self.scq.queue[queue_addr]])

	# This method is used in backtracking
	def recede_status(self):
		self.scq.wr_ptr,self.rd_ptr_1,self.rd_ptr_2,\
			 self.desired_time_stamp, self.return_verdict,pre_content = self.status_stack.pop()
		self.scq.force_modify(pre_content)

###########################################################

class ATOM(Observer):
	def __init__(self,name):
		logging.debug('Initiate ATOMIC %s',name)
		super().__init__(name=name)
		self.type = 'ATOMIC'
		self.name= name

	def run(self,var,time):
		super().record_status()	
		res = [time,False] if var[self.name]==0 else [time,True]
		super().write_result(res)
		logging.debug('%s %s return: %s',self.type, self.name, res)
		

class NEG(Observer):
	def __init__(self,ob1):
		logging.debug('Initiate NEG Observer')
		super().__init__(ob1,name='!')
		self.type = 'NEG'
		self.input_1.parent = self

	def run(self):
		super().record_status()
		self.has_output = False
		isEmpty, time_stamp, verdict = super().read_next(self.desired_time_stamp)
		while(not isEmpty):
			res = [time_stamp,not verdict]
			self.desired_time_stamp = time_stamp+1
			super().write_result(res)
			logging.debug('%s return: %s',self.type, res)
			isEmpty, time_stamp, verdict = super().read_next(self.desired_time_stamp)


class AND(Observer):
	def __init__(self,ob1,ob2):
		logging.debug('Initiate AND Observer')
		super().__init__(ob1,ob2,name='&')
		self.type = 'AND'
		self.last_desired_time_stamp = 0
		self.input_1.parent = self
		self.input_2.parent = self

	def run(self):
		super().record_status()
		self.has_output = False
		isEmpty_1, time_stamp_1, verdict_1 = super().read_next(self.desired_time_stamp)
		isEmpty_2, time_stamp_2, verdict_2 = super().read_next(self.desired_time_stamp,2)
		while(not isEmpty_1 or not isEmpty_2):
			res = [-1,False]
			if(not isEmpty_1 and not isEmpty_2):
				if(verdict_1 and verdict_2):
					res = [min(time_stamp_1,time_stamp_2),True]
				elif(not verdict_1 and not verdict_2):
					res = [max(time_stamp_1,time_stamp_2),False]
				elif(verdict_1):
					res = [time_stamp_2,False]
				else:
					res = [time_stamp_1,False]
			elif(isEmpty_1):# q1 empty
				if(not verdict_2):
					res = [time_stamp_2,False]
			else:# q2 empty
				if(not verdict_1):
					res = [time_stamp_1,False]
			if(res[0]!=-1):
				super().write_result(res)
				self.desired_time_stamp = res[0]+1
				logging.debug('%s return: %s',self.type, res)
			else:
				break;
			isEmpty_1, time_stamp_1, verdict_1 = super().read_next(self.desired_time_stamp)
			isEmpty_2, time_stamp_2, verdict_2 = super().read_next(self.desired_time_stamp,2)

class OR(Observer):
	def __init__(self,ob1,ob2):
		logging.debug('Initiate OR Observer')
		super().__init__(ob1,ob2,name='|')
		self.type = 'OR'
		self.last_desired_time_stamp = 0
		self.input_1.parent = self
		self.input_2.parent = self

	def run(self):
		super().record_status()
		self.has_output = False
		isEmpty_1, time_stamp_1, verdict_1 = super().read_next(self.desired_time_stamp)
		isEmpty_2, time_stamp_2, verdict_2 = super().read_next(self.desired_time_stamp,2)
		while(not isEmpty_1 or not isEmpty_2):
			res = [-1,False]
			if(not isEmpty_1 and not isEmpty_2):
				if(verdict_1 or verdict_2):
					res = [max(time_stamp_1,time_stamp_2),True]
				elif(not verdict_1 and not verdict_2):
					res = [min(time_stamp_1,time_stamp_2),False]
				elif(verdict_1):
					res = [time_stamp_1,True]
				else:
					res = [time_stamp_2,True]
			elif(isEmpty_1):# q1 empty
				if(verdict_2):
					res = [time_stamp_2,True]
			else:# q2 empty
				if(verdict_1):
					res = [time_stamp_1,True]
			if(res[0]!=-1):
				super().write_result(res)
				self.desired_time_stamp = res[0]+1
				logging.debug('%s return: %s',self.type, res)
			else:
				break;
			isEmpty_1, time_stamp_1, verdict_1 = super().read_next(self.desired_time_stamp)
			isEmpty_2, time_stamp_2, verdict_2 = super().read_next(self.desired_time_stamp,2)

class GLOBAL(Observer):
	def __init__(self,ob1,ub,lb=0):
		logging.debug('Initiate GLOBAL Observer')
		super().__init__(ob1,name='G'+str(lb)+','+str(ub))
		self.type = 'GLOBAL'
		self.lb, self.ub = lb, ub
		self.m_up = 0
		self.pre = (-1,False) # must init as -1
		self.inner_status_stack = []
		self.input_1.parent = self

	def record_status(self):
		super().record_status()
		self.inner_status_stack.append([self.m_up, self.pre])

	def recede_status(self):
		super().recede_status()
		self.m_up, self.pre = self.inner_status_stack.pop()

	def run(self):
		self.record_status()		
		self.has_output = False
		isEmpty, time_stamp, verdict = super().read_next(self.desired_time_stamp)
		pre_time_stamp, pre_verdict = self.pre
		while(not isEmpty):
			self.desired_time_stamp = time_stamp + 1
			if verdict and not pre_verdict:
				self.m_up = pre_time_stamp + 1
			if verdict:
				if time_stamp-self.m_up >= self.ub-self.lb and time_stamp-self.ub >= 0:
					res = [time_stamp-self.ub,True]
					super().write_result(res)	
					logging.debug('%s return: %s',self.type, res)
			elif time_stamp-self.lb >= 0:
				res = [time_stamp-self.lb,False]
				super().write_result(res)
				logging.debug('%s return: %s',self.type, res)
			self.pre = (time_stamp, verdict)
			isEmpty, time_stamp, verdict = super().read_next(self.desired_time_stamp)

class FUTURE(Observer):
	def __init__(self,ob1,ub,lb=0):
		logging.debug('Initiate FUTURE Observer')
		super().__init__(ob1,name='F'+str(lb)+','+str(ub))
		self.type = 'FUTURE'
		self.lb, self.ub = lb, ub
		self.m_down = 0
		self.pre = (-1,True)
		self.inner_status_stack = []
		self.input_1.parent = self

	def record_status(self):
		super().record_status()
		self.inner_status_stack.append([self.m_down, self.pre])

	def recede_status(self):
		super().recede_status()
		self.m_down, self.pre = self.inner_status_stack.pop()

	def run(self):
		self.record_status()		
		self.has_output = False
		isEmpty, time_stamp, verdict = super().read_next(self.desired_time_stamp)
		pre_time_stamp, pre_verdict = self.pre
		while(not isEmpty):
			self.desired_time_stamp = time_stamp + 1
			if not verdict and pre_verdict:
				self.m_down = pre_time_stamp + 1
			if not verdict:
				if time_stamp-self.m_down >= self.ub-self.lb and time_stamp-self.ub >= 0:
					res = [time_stamp-self.ub,False]
					super().write_result(res)
					logging.debug('%s return: %s',self.type, res)
			elif time_stamp-self.lb >= 0:
				res = [time_stamp-self.lb,True]
				super().write_result(res)
				logging.debug('%s return: %s',self.type, res)
			self.pre = (time_stamp, verdict)
			isEmpty, time_stamp, verdict = super().read_next(self.desired_time_stamp)

class UNTIL(Observer):
	def __init__(self,ob1,ob2,ub,lb=0):
		logging.debug('Initiate UNTIL Observer')
		super().__init__(ob1,ob2,name='U'+str(lb)+','+str(ub))
		self.type = 'UNTIL'
		self.lb, self.ub = lb, ub
		self.pre = (-1,True)
		self.m_down = 0
		self.inner_status_stack = []
		self.input_1.parent = self
		self.input_2.parent = self
		
	
	def record_status(self):
		super().record_status()
		self.inner_status_stack.append([self.m_down, self.pre])

	def recede_status(self):
		super().recede_status()
		self.m_down, self.pre = self.inner_status_stack.pop()

	def run(self):
		self.record_status()	
		self.has_output = False
		isEmpty_1, time_stamp_1, verdict_1 = super().read_next(self.desired_time_stamp)
		isEmpty_2, time_stamp_2, verdict_2 = super().read_next(self.desired_time_stamp,2)
		pre_time_stamp_2, pre_verdict_2 = self.pre
		while(not isEmpty_1 and not isEmpty_2):
			res = [-1,False]
			tau = min(time_stamp_1,time_stamp_2)
			self.desired_time_stamp = tau + 1
			if pre_verdict_2 and not verdict_2:
				self.m_down = pre_time_stamp_2 + 1
			if verdict_2:
				res = [tau-self.lb,True]
			elif not verdict_1:
				res = [tau-self.lb,False]
			elif tau>=self.ub-self.lb+self.m_down:
				res = [tau-self.ub,False]
			if res[0]>=0:
				super().write_result(res)
				logging.debug('%s return: %s',self.type, res)
			self.pre = (time_stamp_2, verdict_2)
			isEmpty_1, time_stamp_1, verdict_1 = super().read_next(self.desired_time_stamp)
			isEmpty_2, time_stamp_2, verdict_2 = super().read_next(self.desired_time_stamp,2)

class WEAK_UNTIL(Observer):
	def __init__(self,ob1,ob2,ub,lb=0):
		logging.debug('Initiate WEAK UNTIL Observer')
		super().__init__(ob1,ob2,name='W'+str(lb)+','+str(ub))
		self.type = 'WEAK_UNTIL'
		self.lb, self.ub = lb, ub
		self.pre = (-1,True)
		self.m_down = 0
		self.inner_status_stack = []
		self.input_1.parent = self
		self.input_2.parent = self
	
	def record_status(self):
		super().record_status()
		self.inner_status_stack.append([self.m_down, self.pre])

	def recede_status(self):
		super().recede_status()
		self.m_down, self.pre = self.inner_status_stack.pop()

	def run(self):
		self.record_status()	
		self.has_output = False
		isEmpty_1, time_stamp_1, verdict_1 = super().read_next(self.desired_time_stamp)
		isEmpty_2, time_stamp_2, verdict_2 = super().read_next(self.desired_time_stamp,2)
		pre_time_stamp_2, pre_verdict_2 = self.pre
		while(not isEmpty_1 and not isEmpty_2):
			res = [-1,False]
			tau = min(time_stamp_1,time_stamp_2)
			self.desired_time_stamp = tau + 1
			if pre_verdict_2 and not verdict_2:
				self.m_down = pre_time_stamp_2 + 1
			if verdict_2:
				res = [tau-self.lb,True]
			elif not verdict_1:
				res = [tau-self.lb,False]
			elif tau>=self.ub-self.lb+self.m_down:
				res = [tau-self.ub,True] # The only difference from until
			if res[0]>=0:
				super().write_result(res)
				logging.debug('%s return: %s',self.type, res)
			self.pre = (time_stamp_2, verdict_2)
			isEmpty_1, time_stamp_1, verdict_1 = super().read_next(self.desired_time_stamp)
			isEmpty_2, time_stamp_2, verdict_2 = super().read_next(self.desired_time_stamp,2)

###########################################################
#SCQ: Shared Connection Queue
class SCQ():
	# Content structure: ([0]:timestamp, [1]:verdict)
	def __init__(self,name,size):
		self.name = name
		self.wr_ptr = 0;
		#self.queue = [[0 for x in range(2)] for y in range(size)] # revise the queue from list to array to speed up
		self.queue = [ [0,False] for y in range(size)] # revise the queue from list to array to speed up
		
	def add(self,data):
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
		return isEmpty,time_stamp,verdict