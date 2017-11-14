# ------------------------------------------------------------
# MTLparse.py
#
# Parser for MTL formula.
# Construct observer abstract syntax tree
# ------------------------------------------------------------
import ply.yacc as yacc
from MTLlex import tokens
import Observer as ob
import sys

operator_cnt = 0
cnt2observer={}

def record_operators(ob):
	global operator_cnt
	cnt2observer[operator_cnt] = ob
	operator_cnt += 1

def p_MTL_operators(p):
	'''
	expression 	: expression AND expression
				| NEG expression
				| expression UNTIL LBRACK NUMBER COMMA NUMBER RBRACK expression
				| GLOBAL LBRACK NUMBER RBRACK expression
				| GLOBAL LBRACK NUMBER COMMA NUMBER RBRACK expression
	'''
	if p[1] == '!':
		p[0] = ob.NEG(p[2])
		record_operators(p[0])
	elif len(p)>2 and p[2] == '&':
	 	p[0] = ob.AND(p[1],p[3])
	elif p[1] == 'G' and len(p) == 6:
		p[0] = ob.GLOBAL(p[5],ub=p[3])
	elif p[1] == 'G' and len(p)==8:
		p[0] = ob.GLOBAL(p[6],lb=p[3],ub=p[5])
	elif p[2] == 'U':
		p[0] = ob.UNTIL(p[1],p[8],lb=p[4],ub=p[6])
	else:
		raise Exception('Syntax error in type! Cannot find matching format.')
		sys.exit(0)
	record_operators(p[0])

def p_paren_token(p):
	'''expression : LPAREN expression RPAREN'''
	p[0] = p[2]

def p_atomic_token(p):
	'''expression : ATOMIC'''
	p[0] = ob.ATOM(p[1])
	record_operators(p[0])
	print('IMPORT ATOMIC:{0}'.format(p[1]))

precedence = (
	('left', 'AND'),
	('left', 'GLOBAL', 'UNTIL'),	
	('left', 'NEG'),
	('left', 'LPAREN', 'RPAREN','ATOMIC','LBRACK','RBRACK'),
)

# Error rule for syntax errors
def p_error(p):
	print("Syntax error in input!")

# Build the parser
parser = yacc.yacc()

# TODO: optimize the AST