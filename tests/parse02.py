# -*- coding: utf-8 -*-
import lambdas

expr01 = lambdas.parseExpr(['λ', 'x', 'y', '.', 'x',
			    '(', 'λ', 'z', '.', 'λ', 'y', '.', 'y', ')'])
print str(expr01)
print repr(expr01)