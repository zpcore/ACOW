from ACOW import *


def main():
	a = automaton()
	a.INITIAL_STATE = 's0'
	a.DEST_STATE = 's6'
	a.STATE = {
	's0':{'v0':0,'v1':0,'v2':0,'v3':0},
	's1':{'v0':0,'v1':0,'v2':0,'v3':1},
	's2':{'v0':0,'v1':1,'v2':0,'v3':1},
	's3':{'v0':1,'v1':0,'v2':0,'v3':1},
	's4':{'v0':0,'v1':0,'v2':1,'v3':1},
	's5':{'v0':1,'v1':1,'v2':0,'v3':1},
	's6':{'v0':0,'v1':0,'v2':1,'v3':0},
	}
	a.DELTA = {
	's0': {'s0','s1'},
	's1': {'s1','s0','s2','s4'},
	's2': {'s3'},
	's3': {'s3','s5'},
	's4': {'s4'},
	's5': {'s6','s2'},
	}
	print(a)
	a.init()
	a.show()# show a pdf figure of the state space model

if __name__ == "__main__":
	main()
