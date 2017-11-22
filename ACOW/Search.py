# ------------------------------------------------------------
# search.py
# ----------------------------------
# Different search method
# ----------------------------------
# Author: Pei Zhang
# ------------------------------------------------------------
from random import shuffle
from .automaton import automaton
from .MTLparse import *
import logging, sys

# Comment this line to disable debug info
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

class Search():
	def __init__(self, automaton, agent='DFS'):
		assert agent in ('DFS','SED','DES'), 'Error: Agent not exist'
		self.agent = agent
		self.automaton = automaton
		self.current_time = 0
		self.trace = []

	def backtrack(self):
		self.current_time -= 1
		for i in range(len(cnt2observer)):
			observer = cnt2observer[i]	
			observer.recede_status()

	def go_to_next_state(self,state):
		logging.debug('----------- Time: %d, State: %s ----------',self.current_time,state)
		for i in range(len(cnt2observer)):
			observer = cnt2observer[i]
			if(observer.type=='ATOMIC'):				
				observer.run(state.var,self.current_time)
			else:
				observer.run()
		self.current_time += 1
		logging.debug('')


	def is_state_acceptable(self):
		top = cnt2observer[len(cnt2observer)-1]
		return top.return_verdict

	def run(self,path=None):
		if self.agent == 'DFS':
			if(self.dfs(self.automaton.state_map[self.automaton.INITIAL_STATE],0)):
				print('Find Feasible Track:',self.trace)
			else:
				print('No Feasible Track Found.')
		elif self.agent == 'SED':
			self.sed()
		else:
			self.des(path)

	# 'DES': Specify the path by ourselves
	def des(self,path):
		for state in path:
			self.go_to_next_state(self.automaton.state_map[state])

	# 'DFS': Depth first search
	def dfs(self,current_state,step_len):
		self.trace.append(current_state.name)
		self.go_to_next_state(current_state)
		if not self.is_state_acceptable():
			self.backtrack()
			del self.trace[-1]
			return False
		elif current_state.name==self.automaton.DEST_STATE:
			return True
		else:
			step_len += 1
			keys = [x for x in current_state.next]
			shuffle(keys)
			for state in keys:
				if(self.dfs(state,step_len)):
					return True
			self.backtrack()
			del trace[-1]
			return False

	# 'SED': Shortest edit distance
	def sed():
		pass