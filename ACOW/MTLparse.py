# ------------------------------------------------------------
# MTLparse.py
#
# Parser for MTL formula.
# Construct observer abstract syntax tree
# ------------------------------------------------------------
import ply.yacc as yacc
from .MTLlex import tokens
from .Observer import *
import sys

__all__ = ['cnt2observer', 'parser']

operator_cnt = 0
cnt2observer={}

def record_operators(ob):
	global operator_cnt
	cnt2observer[operator_cnt] = ob
	operator_cnt += 1

def p_MTL_operators(p):
	'''
	expression 	: expression AND expression
				| expression OR expression
				| NEG expression
				| GLOBAL LBRACK NUMBER RBRACK expression
				| GLOBAL LBRACK NUMBER COMMA NUMBER RBRACK expression
				| FUTURE LBRACK NUMBER RBRACK expression
				| FUTURE LBRACK NUMBER COMMA NUMBER RBRACK expression
				| expression UNTIL LBRACK NUMBER RBRACK expression
				| expression UNTIL LBRACK NUMBER COMMA NUMBER RBRACK expression
				| expression WEAK_UNTIL LBRACK NUMBER RBRACK expression
				| expression WEAK_UNTIL LBRACK NUMBER COMMA NUMBER RBRACK expression			
	'''
	if p[1] == '!':
		p[0] = NEG(p[2])
	elif len(p)>2 and p[2] == '&':
	 	p[0] = AND(p[1],p[3])
	elif len(p)>2 and p[2] == '|':
	 	p[0] = OR(p[1],p[3])
	elif p[1] == 'G' and len(p) == 6:
		p[0] = GLOBAL(p[5],ub=p[3])
	elif p[1] == 'G' and len(p)==8:
		p[0] = GLOBAL(p[7],lb=p[3],ub=p[5])
	elif p[1] == 'F' and len(p) == 6:
		p[0] = FUTURE(p[5],ub=p[3])
	elif p[1] == 'F' and len(p)==8:
		p[0] = FUTURE(p[7],lb=p[3],ub=p[5])
	elif p[2] == 'U' and len(p)==7:
		p[0] = UNTIL(p[1],p[6],ub=p[4])
	elif p[2] == 'U' and len(p)==9:
		p[0] = UNTIL(p[1],p[8],lb=p[4],ub=p[6])
	elif p[2] == 'W' and len(p)==7:
		p[0] = WEAK_UNTIL(p[1],p[6],ub=p[4])
	elif p[2] == 'W' and len(p)==9:
		p[0] = WEAK_UNTIL(p[1],p[8],lb=p[4],ub=p[6])
	else:
		raise Exception('Syntax error in type! Cannot find matching format.')
		sys.exit(0)
	record_operators(p[0])

def p_paren_token(p):
	'''expression : LPAREN expression RPAREN'''
	p[0] = p[2]

def p_atomic_token(p):
	'''expression : ATOMIC'''
	p[0] = ATOM(p[1])
	record_operators(p[0])

precedence = (
	('left', 'AND', 'OR'),
	('left', 'GLOBAL', 'FUTURE', 'UNTIL','WEAK_UNTIL'),	
	('left', 'NEG'),
	('left', 'LPAREN', 'RPAREN','ATOMIC','LBRACK','RBRACK'),
)

# Error rule for syntax errors
def p_error(p):
	print("Syntax error in input!")

# Build the parser
parser = yacc.yacc()

# TODO: Optimize the AST (Build AST first and then optimize. Finally map the observer to AST)
def optimize():
	# Map inorder traverse to observer node, use '(' and ')' to represent boundry
	def inorder(root,m):
		if(root==None):
			return []
		link = ['(']
		link.extend(inorder(root.input_1,m))
		link.extend([root.name])
		link.extend(inorder(root.input_2,m))
		link.append(')')
		tup = tuple(link)
		if(tup in m):
			# find left of right branch of pre node
			if(root.parent.input_1==root):
				root.parent.input_1 = m[tup]
			else:
				root.parent.input_2 = m[tup]
		else:
			m[tup] = root
		return link

	# inorder traverse from the top node
	top = cnt2observer[len(cnt2observer)-1]
	inorder(top,{})
	return sort_node()

###############################################################
# Sort the processing node sequence, the sequence is stored in stack
def sort_node():
	top = cnt2observer[len(cnt2observer)-1]
	# collect used node from the tree
	def checkTree(root, graph):
		if(root==None):
			return
		checkTree(root.input_1, graph);
		graph.add(root)
		checkTree(root.input_2, graph);

	graph=set()
	checkTree(top,graph)

	def topologicalSortUtil(root, visited, stack):
		if(root!=None and not visited[root]):
			visited[root] = True
			[topologicalSortUtil(i,visited,stack) for i in(root.input_1, root.input_2)]
			stack.insert(0,root)

	def topologicalSort(root, graph):
		visited = {}
		for node in graph:
			visited[node]=False 
		stack = []
		[topologicalSortUtil(node,visited,stack) for node in graph]
		stack.reverse()
		return stack

	stack = topologicalSort(top,graph)
	return stack