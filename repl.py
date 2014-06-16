import lambdas

bindings = dict(lambdas.builtins)
while True:
    line = raw_input('> ')
    while line[-1] == '\\':
	line = line[:-1] + raw_input('... ')
    if line == ':quit': break
    try:
	expr = lambdas.parseline(line, bindings)
    except lambdas.LambdaError, e:
	print "ERROR: %s" % (e,)
	continue
    if isinstance(expr, tuple):
	bindings[expr[0]] = expr[1]
    else:
	while expr is not None:
	    print expr
	    if raw_input() == '': expr = expr.eval()
	    else: break
