# -*- coding: utf-8 -*-

import re

def structCmp(*fields):  # internal function; not for export
    return lambda self, other: cmp(type(self), type(other)) or \
			       cmp(tuple(getattr(self,  f) for f in fields),
				   tuple(getattr(other, f) for f in fields))

class LambdaError(ValueError): pass

class Atom(object):
    def __init__(self, name): self.name = name

    __cmp__ = structCmp("name")

    def __str__(self): return "'" + self.name

    def __repr__(self): return 'Atom(%r)' % (self.name,)

    def simplify(self): return self

    def eval(self): return None


class FreeVar(object):
    def __init__(self, name, expr):
	self.name = name
	self.expr = expr

    __cmp__ = structCmp("name", "expr")

    def __str__(self): return self.name

    def __repr__(self): return 'FreeVar(%r, %r)' % (self.name, self.expr)

    def simplify(self):
	return self.expr if isinstance(self.expr, Builtin) else self

    def eval(self): return self.expr


class BoundVar(object):
    def __init__(self, name, index):
	self.name = name
	self.index = index

    __cmp__ = structCmp("name", "index")

    def __repr__(self): return 'BoundVar(%r, %r)' % (self.name, self.index)

    def __str__(self): return self.name

    def simplify(self): return self

    def eval(self): return None


class Lambda(object):
    def __init__(self, args, expr):
	self.args = args
	self.expr = expr

    __cmp__ = structCmp("args", "expr")

    def __repr__(self): return 'Lambda(%r, %r)' % (self.args, self.expr)

    def __str__(self): return 'λ' + ' '.join(self.args) + '. ' + str(self.expr)

    def simplify(self): return Lambda(self.args, self.expr.simplify())

    def eval(self): return None

    def __call__(self, arg):
	def bind(i,e):
	    if isinstance(e, BoundVar) and e.index == i:
		return arg
	    elif isinstance(e, Expression):
		return Expression(*(bind(i,f) for f in e.expr))
	    elif isinstance(e, Lambda):
		return Lambda(e.args, bind(i+len(e.args), e.expr))
	    else:
		return e
	args2 = self.args[1:]
	if args2:
	    return Lambda(args2, bind(len(args2), self.expr))
	else:
	    return bind(0, self.expr)


class Expression(object):
    def __init__(self, *expr): self.expr = expr

    __cmp__ = structCmp("expr")

    def __repr__(self): return 'Expression' + repr(self.expr)

    def __str__(self):
	if len(self.expr) == 1:
	    return str(self.expr[0])
	def substr(e):
	    return ('(%s)' if isinstance(e, (Expression, Lambda)) else '%s') \
		    % (e,)
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
	    if len(self.expr) == 1:
		return None
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


class Builtin(object):
    def __init__(self, name, f, arity, args=()):
	self.name = name
	self.f = f
	self.arity = arity
	self.args = args

    __cmp__ = structCmp("name", "f", "arity", "args")

    def __repr__(self): return 'Builtin(%r, %r, %r, %r)' \
				% (self.name, self.f, self.arity, self.args)

    def __str__(self):
	if not self.args: return self.name
	def substr(e):
	    return ('(%s)' if isinstance(e, (Expression, Lambda)) else '%s') \
		    % (e,)
	return '<%s %s>' % (self.name, ' '.join(map(substr, self.args)))

    def simplify(self): return self

    def eval(self):
	if len(self.args) >= self.arity:
	    val = self.f(*self.args[:self.arity])
	    return Expression(val, *self.args[self.arity:]).simplify()
	else:
	    return None

    def __call__(self, arg):
	args = self.args + (arg,)
	if len(args) + 1 >= self.arity:
	    val = self.f(*args[:self.arity])
	    return Expression(val, *args[self.arity:]).simplify()
	else:
	    return Builtin(self.name, self.f, self.arity, self.args)


def mkexpr(*expr):
    if not expr:
	raise ValueError('empty argument list')
    elif len(expr) == 1:
	return expr[0]
    else:
	while isinstance(expr[0], Expression):
	    expr = expr[0].expr + expr[1:]
	return Expression(*expr)

def parseline(s, predef={}):
    # predef - dict of previously defined symbols
    defining = None
    stack = [[]]
    # Except for the first element, every element of `stack` is of the form
    # ['(', ...] or ['λ', args, outer_scope, ...] -- except while reading the
    # arguments to a lambda, in which case the top element is of the form ['λ',
    # ...].
    scope = {}
    # While inside a lambda, `scope` is a dict mapping bound variable names to
    # integers representing the depth of the lambda to which they are bound.
    expectColoneq = False
    inArgs = False
    for t in lex(s):
    	if expectColoneq:
	    if t != ':=':
		raise LambdaError('":=" expected after undefined variable at'
				  ' start of line')
	    expectColoneq = False
	elif inArgs:
	    if t in ('(', ')', 'λ', ':=') or t[0] == "'":
		raise LambdaError('invalid token in lambda argument list')
	    elif t == '.':
		args = stack[-1][1:]
		if not args:
		    raise LambdaError('no arguments for lambda')
		stack[-1] = ['λ', tuple(args), scope]
		newScope = {}
		for var in scope:
		    newScope[var] = scope[var] + len(args)
		for i, var in enumerate(reversed(args)):
		    if var != '_':
			newScope[var] = i
		scope = newScope
		inArgs = False
	    else:
		if t != '_' and t in stack[-1]:
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
			if not expr: raise LambdaError('empty parentheses')
			stack[-1].append(mkexpr(*expr))
			break
		    elif stack[-1][0] == 'λ':
			args = stack[-1][1]
			scope = stack[-1][2]
			expr = stack.pop()[3:]
			if not expr: raise LambdaError('empty lambda')
			stack[-1].append(Lambda(args, mkexpr(*expr)))
		    else: raise LambdaError('too many closing parentheses')
		else: raise LambdaError('too many closing parentheses')
	    elif t == 'λ':
		inArgs = True
		stack.append(['λ'])
	    elif t == '.':
		raise LambdaError('argument terminator outside argument list')
	    elif t == ':=':
		if len(stack) == 1 and len(stack[0]) == 1 \
		    and isinstance(stack[0][0], FreeVar) and defining is None:
		    defining = stack[0].pop().name
		else:
		    raise LambdaError('unexpected ":="')
	    elif t == '_':
		raise LambaError("special name '_' is unusable in expressions")
	    elif t[0] == "'": stack[-1].append(Atom(t[1:]))
	    elif t in scope:  stack[-1].append(BoundVar(t, scope[t]))
	    elif t in predef: stack[-1].append(FreeVar(t, predef[t]))
	    elif defining is None and stack == [[]]:
		defining = t
		expectColoneq = True
	    else: raise LambdaError('undefined variable %r' % (t,))
    if inArgs:
	raise LambdaError('expression terminated in middle of argument list')
    if not stack[-1]: return None
    while stack[-1][0] == 'λ':
	args = stack[-1][1]
	scope = stack[-1][2]
	expr = stack.pop()[3:]
	if not expr: raise LambdaError('empty lambda')
	stack[-1].append(Lambda(args, mkexpr(*expr)))
    if stack[-1][0] == '(': raise LambdaError('parentheses not closed')
    expr = mkexpr(*stack[-1])
    return (defining, expr) if defining is not None else expr

def lex(s):  # not for export?
    s = re.sub(r'(?:λ|\x5C)([A-Za-z]+)(?:\.|->|→)',
	       lambda m: 'λ' + ' '.join(m.group(1)) + '.',
	       s)
    for word in re.split(r'\s+|([()\x5C.]|λ|->|→|:=)', s):
	if   word is None or word == '': continue
	elif word == "'": raise LambdaError('invalid token "\'"')
	elif word in ('(', ')', ':='):    yield word
	elif word == 'λ' or word == '\\': yield 'λ'
	elif word in ('.', '->', '→'):    yield '.'
	else: yield word

TRUE  = Lambda(('x', 'y'), BoundVar('x', 1))
FALSE = Lambda(('x', 'y'), BoundVar('y', 0))

builtins = {
    "=": Builtin("=", lambda x,y: TRUE if x == y else FALSE, 2)
}
