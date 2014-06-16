# -*- coding: utf-8 -*-
import sys
sys.path.insert(1, sys.path[0] + '/..')
import lambdas

expr01 = lambdas.parseline('S:=λxyz.(x z)(y z)')
print '(%r, %s)' % expr01
print repr(expr01)
