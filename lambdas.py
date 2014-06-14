# -*- coding: utf-8 -*-

class LambdaError(ValueError): pass

class Atom(object):
    def __init__(self, name): self.name = name

    def __cmp__(self, other):
	return cmp(type(self), type(other)) or cmp(self.name, other.name)

    def __str__(self): return "'" + self.name

    def __repr__(self): return 'Atom(%r)' % (self.name,)

    def simplify(self): return self

    def eval(self): return None


class FreeVar(object):
    def __init__(self, name, expr):
	self.name = name
	self.expr = expr

    def __str__(self): return self.name

    def __repr__(self): return 'FreeVar(%r, %r)' % (self.name, self.expr)

    def simplify(self): return self

    def eval(self): return self.expr


class BoundVar(object):
    def __init__(self, name, index):
	self.name = name
	self.index = index

    def __repr__(self): return 'BoundVar(%r, %r)' % (self.name, self.index)

    def __str__(self): return self.name

    def simplify(self): return self

    def eval(self): return None


class Lambda(object):
    def __init__(self, args, expr):
	self.args = args
	self.expr = expr

    def __repr__(self): return 'Lambda(%r, %r)' % (self.args, self.expr)

    def __str__(self): return 'λ' + ' '.join(self.args) + '. ' + str(self.expr)

    def simplify(self): return Lambda(self.args, self.expr.simplify())

    def eval(self): return None

    ### def __call__(self, arg): ...


class Expression(object):
    def __init__(self, *expr): self.expr = expr

    def __repr__(self): return 'Expression' + repr(self.expr)

    def __str__(self):
	if len(self.expr) == 1:
	    return str(self.expr[0])
	def substr(e):
	    if isinstance(e, (Expression, Lambda)):
		return '(' + str(e) + ')'
	    else:
		return str(e)
	return ' '.join(map(substr, self.expr))

    def simplify(self):
	expr = self.expr
	while isinstance(expr[0], Expression):
	    expr = expr[0].expr + expr[1:]
	expr = map(lambda e: e.simplify(), expr)
	return expr[0] if len(expr) == 1 else Expression(*expr)

    def eval(self):
	first = self.expr[0].simplify()
	expr = self.expr[1:]
        if callable(first):
	    if len(self.expr) == 1: return None
	    val = first(expr[0])
	    expr = expr[1:]
	else:
	    val = first.eval()
	if val is None:
	    return None
	elif isinstance(val, Expression):
	    return Expression(*(val.expr + expr))
	else:
	    return Expression(val, *expr)


def parseExpr(tokens, predef={}):
    # predef - dict of previously defined symbols
    stack = [[]]
    # Except for the first element, every element of `stack` is of the form
    # ['(', ...] or ['λ', args, outer_scope, ...] -- except while reading the
    # arguments to a lambda, in which case the top element is of the form ['λ',
    # ...].
    scope = {}
    # While inside a lambda, `scope` is a dict mapping bound variable names to
    # integers representing the depth of the lambda to which they are bound.
    inArgs = False

    for t in tokens:
	if inArgs:
	    if t in ('(', ')', 'λ') or t[0] == "'":
		raise LambdaError('invalid token in lambda argument list')
	    elif t == '.':
		### The lexer should also map '->' and '→' to '.'
		args = stack[-1][1:]
		if not args:
		    raise LambdaError('no arguments for lambda')
		stack[-1] = ['λ', tuple(args), scope]
		newScope = {}
		for var in scope:
		    newScope[var] = scope[var] + len(args)
		for i, var in enumerate(reversed(args)):
		    newScope[var] = i
		scope = newScope
		inArgs = False
	    else:
		if t in stack[-1]:
		    raise LambdaError('same name used for multiple arguments'
				      ' to lambda')
		stack[-1].append(t)

	else:
	    if t == '(':
		stack.append(['('])

	    elif t == ')':
		while stack and stack[-1]:
		    if stack[-1][0] == '(':
			expr = stack.pop()[1:]
			if not expr:
			    raise LambdaError('empty parentheses')
			stack[-1].append(Expression(*expr))
			break
		    elif stack[-1][0] == 'λ':
			args = stack[-1][1]
			scope = stack[-1][2]
			expr = stack.pop()[3:]
			if not expr:
			    raise LambdaError('empty lambda')
			stack[-1].append(Lambda(args, Expression(*expr)))
		    else:
			raise LambdaError('too many closing parentheses')
		else:
		    raise LambdaError('too many closing parentheses')

	    elif t == 'λ':
		### The lexer should also map '\\' to 'λ'
		inArgs = True
		stack.append(['λ'])

	    elif t == '.':
		raise LambdaError('argument terminator outside of argument list')

	    #elif t == "'":
		### error; this should be caught by the lexer

	    elif t[0] == "'":
		stack[-1].append(Atom(t[1:]))

	    else:
		if t in scope:
		    stack[-1].append(BoundVar(t, scope[t]))
		elif t in predef:
		    stack[-1].append(FreeVar(t, predef[t]))
		else:
		    raise LambdaError('undefined variable %r' % (t,))

    if inArgs:
	raise LambdaError('expression terminated in middle of argument list')
    while stack and stack[-1]:
	if stack[-1][0] == '(':
	    raise LambdaError('parentheses not closed')
	elif stack[-1][0] == 'λ':
	    args = stack[-1][1]
	    scope = stack[-1][2]
	    expr = stack.pop()[3:]
	    if not expr:
		raise LambdaError('empty lambda')
	    stack[-1].append(Lambda(args, Expression(*expr)))
	else:
	    break
    return Expression(*stack[-1]) if stack[-1] else None
