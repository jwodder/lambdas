# -*- coding: utf-8 -*-
import sys
sys.path.insert(1, sys.path[0] + '/..')
import lambdas

exprStr = "(λx. x x) (λxy.y) 'a"

expr = lambdas.parseline(exprStr)
while expr is not None:
    print str(expr)
    expr = expr.eval()
