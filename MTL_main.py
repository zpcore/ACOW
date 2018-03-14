from ACOW import *

# User defined automaton
def define_automaton():
	a = automaton()
	a.INITIAL_STATE = 's2'
	a.DEST_STATE = 's3'
	a.STATE = {
	's0':{'a0':0,'a1':0},
	's1':{'a0':0,'a1':1},
	's2':{'a0':1,'a1':0},
	's3':{'a0':1,'a1':1},
	}
	a.DELTA = {
	's0': {'s0','s1','s2','s3'},
	's1': {'s0','s1','s2','s3'},
	's2': {'s0','s1','s2','s3'},
	's3': {'s0','s1','s2','s3'},
	}
	print(a)
	return a


def main():
	a = define_automaton()
	a.init()
	#a.show()# show a .pdf figure of the state space model
	MTL = 'F[1](!G[1]a0)'
	top_node = parser.parse(MTL)
	solution = Search(a,agent='DES')
	solution.run(['s2','s2','s2','s0'])

if __name__ == "__main__":
	main()
