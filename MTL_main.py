from ACOW import *

# User defined automaton
def define_automaton():
	a = automaton()
	a.INITIAL_STATE = 's0'
	a.DEST_STATE = 's15'
	a.STATE = {
	's0':{'f':0,'g':0,'c':0,'w':0},
	's1':{'f':0,'g':0,'c':0,'w':1},
	's2':{'f':0,'g':0,'c':1,'w':0},
	's3':{'f':0,'g':0,'c':1,'w':1},
	's4':{'f':0,'g':1,'c':0,'w':0},
	's5':{'f':0,'g':1,'c':0,'w':1},
	's6':{'f':0,'g':1,'c':1,'w':0},
	's7':{'f':0,'g':1,'c':1,'w':1},
	's8':{'f':1,'g':0,'c':0,'w':0},
	's9':{'f':1,'g':0,'c':0,'w':1},
	's10':{'f':1,'g':0,'c':1,'w':0},
	's11':{'f':1,'g':0,'c':1,'w':1},
	's12':{'f':1,'g':1,'c':0,'w':0},
	's13':{'f':1,'g':1,'c':0,'w':1},
	's14':{'f':1,'g':1,'c':1,'w':0},
	's15':{'f':1,'g':1,'c':1,'w':1},
	}
	a.DELTA = {
	's0': {'s8','s9','s10','s12'},
	's1': {'s9','s11','s13'},
	's2': {'s10','s11','s14'},
	's3': {'s11','s15'},
	's4': {'s12','s13','s14'},
	's5': {'s13','s15'},
	's6': {'s14','s15'},
	's7': {'s15'},
	's8': {'s0'},
	's9': {'s0','s1'},
	's10': {'s0','s2'},
	's11': {'s3','s2','s1'},
	's12': {'s4','s0'},
	's13': {'s5','s1','s4'},
	's14': {'s6','s2','s4'},
	's15': {'s7','s3','s5','s6'},
	}
	print(a)
	return a


def main():
	a = define_automaton()
	a.init()
	a.show()# show a .pdf figure of the state space model
	MTL = '!(g&c&!f)&!(g&w&!f)&!(!g&!c&f)&!(!g&!w&f)'
	top_node = parser.parse(MTL)
	solution = Search(a,agent='DFS')
	#solution.run(['s0','s1','s4','s1','s2','s3','s5','s6'])
	solution.run()

if __name__ == "__main__":
	main()
