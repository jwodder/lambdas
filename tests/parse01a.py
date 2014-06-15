# -*- coding: utf-8 -*-
import sys
sys.path.insert(1, sys.path[0] + '/..')
import lambdas

expr01 = lambdas.parse("(λx. x x) (λxy.y) 'a")
print str(expr01)
print repr(expr01)
