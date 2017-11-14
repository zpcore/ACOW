import ply.lex as lex
import ply.yacc as yacc

from MTLlex import lexer
from MTLparse import parser

data = '''
a1 U[1,2] !a0&G[1,3]a3
'''
print('MTL Formula:',data)

# Test lex
print('\nLex Test:')
lexer.input(data)
for tok in lexer:
	print(tok)

# Test parser
print('\nParser Test:')
result = parser.parse(data)
print(result)