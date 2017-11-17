# ------------------------------------------------------------
# search.py
# ----------------------------------
# Different search method
# ----------------------------------
# Author: Pei Zhang
# ------------------------------------------------------------
from .automaton import automaton
from .MTLparse import *

class Search():
	def __init__(self, automaton, agent='DFS'):
		assert agent in ('DFS','SED','DES'), 'Error: Agent not exist'
		self.agent = agent
		self.automaton = automaton
		self.current_time = 0

	def go_to_next_state(self,state):
		print('-----------Time: {0}------------'.format(self.current_time))
		for i in range(len(cnt2observer)):
			observer = cnt2observer[i]
			if(observer.type=='ATOMIC'):
				observer.run(self.automaton.state_map[state].var,self.current_time)
			else:
				observer.run()
		self.current_time += 1


	def is_state_acceptable(state):
		top = cnt2observer[len(cnt2observer)-1]
		return top.is_healthy

	def run(self,path=None):
		if self.agent == 'DFS':
			dfs()
		elif self.agent == 'SED':
			sed()
		else:
			self.des(path)

	# 'DES': Specify the path by ourselves
	def des(self,path):
		for state in path:
			self.go_to_next_state(state)

	# 'DFS': depth first search
	def dfs():
		pass

	# 'SED': Shortest edit distance
	def sed():
		pass