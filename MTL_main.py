from ACOW import *

# User defined automaton
def define_automaton():
	a = automaton()
	#sg = StateGen(3,'s','a')
	a.INITIAL_STATE = 's2'
	a.DEST_STATE = 's3'
	#a.STATE, a.DELTA = sg.gen_aut()
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
	MTL = '(a0 U[2](G[1] a1) )'
	top_node = parser.parse(MTL)
	cnt2observer = MTLparse.optimize() # comment this line if you don't want to optimze the AST
	solution = Search(a,cnt2observer,agent='DES')
	solution.run(['s0','s0','s0','s1','s1','s1','s1','s1','s1','s1','s3','s2','s2','s3','s2','s3','s3','s3','s3','s2','s2','s3','s3','s3','s3','s0','s1','s1','s1','s0','s0'])

if __name__ == "__main__":
	main()
