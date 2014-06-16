import lambdas

bindings = dict(lambdas.builtins)
while True:
    try:
	line = raw_input('> ')
	if line == '': continue
	while line[-1] == '\\':
	    line = line[:-1] + raw_input('... ')
    except EOFError:
	print
	break
    line = line.strip()
    if line == '': continue
    elif line == ':quit': break
    elif line == ':defs':
	for name in sorted(bindings.keys()):
	    print '%s := %s' % (name, bindings[name])
    else:
	words = line.split()
	if words[0] == ':repr':
	    showRepr = True
	    words = words[1:]
	else:
	    showRepr = False
	line = ' '.join(words)
	try:
	    expr = lambdas.parseline(line, bindings)
	except lambdas.LambdaError, e:
	    print 'ERROR: %s' % (e,)
	    continue
	if showRepr:
	    #print repr(expr)
	    # Are there any circumstances in which a non-strict `repr` would be
	    # desirable?
	    print repr(lambdas.evaluate(expr, lambdas.builtin_limit))
	elif isinstance(expr, tuple):
	    bindings[expr[0]] = expr[1]
	else:
	    while expr is not None:
		print expr
		if raw_input() == '':
		    expr = expr.eval()
		else:
		    break
