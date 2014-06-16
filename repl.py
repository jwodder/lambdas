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
	### TODO: Make this handle filenames with spaces
	if len(words) != 2:
	    print 'ERROR: ":import" must be followed by a filename'
	    continue
	### TODO: Make this handle errors thrown by parseFile
	(bindings, exprList) = lambdas.parseFile(words[1], bindings)
	for expr in exprList:
	    while expr is not None:
		print expr
		if raw_input() == '':
		    expr = expr.eval()
		else:
		    break

    else:
	if words[0] == ':repr':
	    showRepr = True
	    words = words[1:]
	    if not words:
	        print 'ERROR: ":repr" must be followed by an expression'
		continue
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
