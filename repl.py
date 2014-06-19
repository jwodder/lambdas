#!/usr/bin/python
# -*- coding: utf-8 -*-
import cStringIO
import readline
import lambdas

bindings = dict(lambdas.builtins)
last = None
while True:
    try:
	line = raw_input('λ> ')
	if line == '': continue
	while line[-1] == '\\':
	    line = line[:-1] + raw_input('... ')
    except EOFError:
	print
	break
    line  = line.strip()
    words = line.split()

    if line == '': continue

    elif line == ':quit': break

    elif words[0] == ':def':
	names = words[1:] if words[1:] else sorted(bindings.keys())
	for name in names:
	    val = bindings.get(name, 'UNDEFINED')
	    if isinstance(val, lambdas.Builtin):
		val = '<builtin>'
	    print '%s := %s' % (name, val)

    elif words[0] == ':import':
	impLine = cStringIO.StringIO(line)
	(bindings, exprList) = lambdas.parseFile(impLine, bindings)
	for expr in exprList:
	    last = lambdas.evaluate(expr, lambdas.builtin_limit)
	    print last

    else:
	modifier = None
	giveup = False
	if words[0] in (':repr', ':step'):
	    modifier = words.pop(0)
	    if not words:
		print 'ERROR: %r requires an expression' % (modifier,)
		continue
	for i,w in enumerate(words):
	    if w == ':last':
		if last is None:
		    print 'ERROR: no previous expression'
		    giveup = True
		    break
		else:
		    words[i] = str(last)
	if giveup: continue
	line = ' '.join(words)
	try:
	    expr = lambdas.parseline(line, bindings)
	except lambdas.LambdaError, e:
	    print 'ERROR: %s' % (e,)
	    continue
	if isinstance(expr, tuple):
	    bindings[expr[0]] = last = expr[1]
	    if modifier == ':repr':
		print repr(last)
	elif modifier == ':repr':
	    #print repr(expr)
	    # Are there any circumstances in which a non-strict `repr` would be
	    # desirable?
	    last = lambdas.evaluate(expr, lambdas.builtin_limit)
	    print repr(last)
	elif modifier == ':step':
	    while expr is not None:
		last = expr
		print expr
		if raw_input() == '':
		    expr = expr.eval()
		else:
		    break
	else:
	    last = lambdas.evaluate(expr, lambdas.builtin_limit)
	    print last
