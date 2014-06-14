# -*- coding: utf-8 -*-
import lambdas

expr01 = lambdas.parseExpr(['(', 'λ', 'x', '.', 'x', 'x', ')',
			    '(', 'λ', 'x', 'y', '.', 'y', ')', "'a"])
print str(expr01)
print repr(expr01)
