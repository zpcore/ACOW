import ply.yacc as yacc
from MTLlex import tokens
import Observer as ob

def p_MTL_operators(p):
	'''
	expression : expression AND expression
				| NEG expression
				| UNTIL LBRACK NUMBER COMMA NUMBER RBRACK expression
				| GLOBAL LBRACK NUMBER RBRACK expression
				| GLOBAL LBRACK NUMBER COMMA NUMBER RBRACK expression
	'''
	if p[1] == '!':
		p[0] = ob.NEG(p[2])
	elif len(p)>2 and p[2] == '&':
	 	p[0] = ob.AND(p[1],p[3])
	elif p[1] == 'G':
		if(len(p)==6):
			p[0] = ob.GLOBAL(ob1=p[5],ub=p[3])
		elif(len(p)==7):
			p[0] = ob.GLOBAL(p[6],lb=p[3],ub=p[5])
	elif p[1] == 'U':
		p[0] = ob.UNTIL(p[6],lb=p[3],ub=p[5])
	else:
		print('Syntax error in type')

def p_paren_token(p):
	'''expression : LPAREN expression RPAREN'''
	p[0] = p[2]

def p_atomic_token(p):
	'''expression : ATOMIC'''
	p[0] = ob.ATOM(p[1])
	print('LOAD ATOMIC:{0}'.format(p[1]))

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
# while True:
# 	try:
# 		s = raw_input('calc > ')
# 	except EOFError:
# 		break
# 	if not s: continue
# 	result = parser.parse(s)
# 	print(result)