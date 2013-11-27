# Theoretically we should only need to implement a small set of primitive
# functions and we can thereafter define all other functions in lisp code
# in terms of the primitives.
# This page: http://www.eecs.berkeley.edu/~bh/ssch27/appendix-funlist.html
# lists the following functions as "Special forms" which I take to mean
# "cannot be implemented in lisp":
# and
# begin
# cond
# define (def)
# if
# lambda
# let
# or
# quote

# I'm also using this: http://languagelog.ldc.upenn.edu/myl/ldc/llog/jmc.pdf
# Which defines the following primitives:
# quote
# atom
# eq
# car (first)
# cdr (rest)
# cons

import re

# Format result
# <a> => a
# 1.0 => 1.0
# [1, 2, 3] => (1 2 3)
# [<a>, <b>, <c>] => (a b c)
def format(res):
	if isinstance(res, int) or isinstance(res, float):
		return res
	if isinstance(res, Symbol):
		return res.val()
	if isinstance(res, list):
		return reduce(lambda acc,e: acc+str(e)+" ", map(format, res), "(")+")"

# Convert static symbols to strings
def conv_sym(arg):
	if isinstance(arg, Symbol) and arg.static is True:
		return arg.val()
	if isinstance(arg, list):
		return map(conv_sym, arg)
	return arg

# Parses and executes the contents of the file given
def load(file):
	data = open(file, "r").read()
	lines = filter(lambda l: l != '', data.split("\n"))
	for l in lines:
		res = run(l)
		print res

# Parses and executes the code string given
def run(code):
	node = parse_exp(code)
	res = node.call()
	res = conv_sym(res)
	return res

def parse_exp(str):
	arr = str_to_array(str)
	node = parse(arr)
	return node

def tokenise(t, node):
	if type(t) == list:
		return t
	if is_number(t):
		return float(t)
	if t == "+":
		return lambda a,b: a+b
	elif t == "-":
		return lambda a,b: a-b
	elif t == "*":
		return lambda a,b: a*b
	elif t == "/":
		return lambda a,b: a/b
	elif t == "first":
		return lambda arr: arr[0]
	elif t == "last":
		return lambda arr: arr[-1]
	elif t == "rest":
		return lambda arr: arr[1:]
	elif t == "cons":
		# (const 'a '(b c)) => (a b c)
		return lambda a,arr: [a]+arr
	elif t == "def":
		return defn
		# return lambda name,val: node.root().hoist(name.value, val.val())
	elif t == "let":
		# The way S-expressions are currently evaluated
		# (from the inside out) means that by the time this
		# function is called, the variables it is meant to
		# define have already been used (or attemped to be used)
		# and so an error has probably already occurred as they will
		# have been treated as strings.
		# So we have to treat let differently, and handle it during Node.call
		# when the 2nd argument is yet to be evaluated.
		return let
	elif t == "quote":
		# (quote x) returns x
		# (quote a) => a
		# (quote (a b c)) => (a b c)
		return quote
	elif t == "atom":
		# (atom x) returns the atom True is the value of x is an atom or the empty list
		# Otherwise it returns ()
		# (atom (quote a)) => True
		# (atom (quote (a b c))) => ()
		# (atom (quote ())) => True
		# Once again, this can't be done with a simple lambda
		# We need to examine the node for the 1st argument and ensure that it is
		# 	a) an atom (i.e. not a list)
		# 	or
		# 	b) an empty list
		return atom
	elif t == "eq":
		# (eq 'a 'a) => True
		# (eq 'a 'b) => ()
		return lambda a,b: True if a == b else []
	elif t == "cond":
		# (cond ((eq 'b 'b) 'first)
		#   		((atom 'a) 'second))
		return cond
	elif t == "lambda":
		return make_lambda
	else:
		return Symbol(t, node)

def let(node,binding):
	node.hoist(binding[0].value.value, binding[1].call())

def quote(arg):
	# If arg node is list, do not call it. Extract elements and return list.
	if arg.children != []:
		elems = map(lambda c: c.value if c.value else quote(c), arg.children)
		def resolve(list):
			for e in list:
				if type(e) == type(Symbol(None, None)):
					e.static = True
				elif type(e) != type(lambda: None) and not is_number(e):
					resolve(e)
			return list
		elems = resolve(elems)
		return elems
	else:
		if isinstance(arg.value, Symbol):
			arg.value.static = True
	return arg.value

def atom(arg):
	# If arg is an array with 1+ elems, return []
	# Else return True
	if type(arg) is list and len(arg) > 0:
		return []
	else:
		return True

def defn(name_node, val_node, node):
	# name_node must be a Symbol
	node.root().hoist(name_node.value.value, val_node.call())

def cond(args):
	conditions = map(lambda c: c.children[0], args)
	expressions = map(lambda c: c.children[1], args)
	first_true_index = next(conditions.index(node) for node in conditions if node.call() == True)
	exp = expressions[first_true_index]
	if exp:
		return exp.call()
	else:
		return None

def make_lambda(args, expr, node):
	def function(*_args):
		[node.hoist(pair[0].value, pair[1]) for pair in zip(args, _args)]
		return expr.call()
	return function

def is_number(s):
  try:
    float(s)
    return True
  except ValueError:
    return False

def ev(arg):
	"""evaluate the argument given. Int -> Int, Symbol -> (value contained) etc"""
	if type(arg) is int or type(arg) is float:
		return arg
	elif arg.__class__ is Symbol:
		return arg.val()
	elif arg.__class__ is Node:
		return arg.call()

def str_to_array(str):
	# Convert '... to (quote ...)
	match = re.search("'\(", str)
	while match != None:
		start = match.start()
		_start = start-1 if start > 0 else 0
		str = str[0:_start] + insert_quote(str, start+1)
		match = re.search("'\(", str)

	# Convert 'a to (quote a)
	match = re.search("'\w+?", str)
	while match != None:
		s = match.start()
		e = match.end()
		str = str[0:s] + "(quote " + str[s+1:e] + ")" + str[e:]
		match = re.search("'\w+?", str)

	str = re.sub("\(", " ( ", str)
	str = re.sub("\)", " ) ", str)
	return str.split()

# Turns '(1 2 3) into (quote (1 2 3))
def insert_quote(text, start):
	counter = 1
	end = start
	while counter > 0:
		end += 1
		c = text[end]
		if c == "(":
			counter += 1
		elif c == ")":
			counter -= 1
	return " (quote "+text[start:end]+")"+text[end:]

def parse(arr):
	global root
	cur_node = root
	for token in arr:
		if token == "(":
			cur_node.push(Node(None,cur_node))
			cur_node = cur_node.children[-1]
		elif token == ")":
			cur_node = cur_node.parent
		else:
			cur_node.push(Node(tokenise(token, cur_node), cur_node))
	return root.children[-1]

class Symbol:
	"""represents symbols, like a, b, etc"""
	def __init__(self, value, node):
		self.value = value
		self.node = node
		self.static = False # if true, will not attempt to resolve itself.
	def __repr__(self):
		return "<"+str(self.val())+">"
	def val(self):
		if self.static:
			return self.value
		if self.node:
			return self.node.resolve(self.value)
		else:
			return self.value

class Node:
	"""issa node"""
	def __init__(self, value, parent):
		self.value = value
		self.parent = parent
		self.children = []
		self.context = {}

	def root(self):
		if self.parent == None:
			return self
		else:
			return self.parent.root()
	def push(self, node):
		self.children.append(node)
	def resolve(self, name):
		if name in self.context.keys():
			return self.context[name]
		if not self.parent:
			return None
		return self.parent.resolve(name)
	def hoist(self, name, val):
		self.context[name] = val
	def call(self):
		if len(self.children) == 0:
			return self.value
		func = self.children[0].call()
		# If 1st elem is a variable, it should represent a function, so extract it
		if isinstance(func, Symbol):
			val = func.val()
			if not isinstance(val, type(lambda: None)):
				raise Exception(str(val)+" is not a function")
			func = val
		if type(func) == type(lambda: None):
			# Special case for 'let'
			if func == let:
				binding = self.children[1].children
				let(self, binding)
				return self.children[2].call()
			# Special case for 'quote'
			if func == quote:
				return quote(self.children[1])
			# Special case for 'atom'
			if func == atom:
				return atom(self.children[1].call())
			# Special case for 'def'
			if func == defn:
				defn(self.children[1], self.children[2], self)
				return None
			# Special case for 'cond'
			if func == cond:
				return cond(self.children[1:])
			if func == make_lambda:
				params = quote(self.children[1])
				expr = self.children[2]
				return make_lambda(params, expr, self)
			return func(*map(lambda c: ev(c.value) if c.value else c.call(),self.children[1:]))
		else:
			# According to the Scheme spec, all unquoted lists must start with a function
			raise Exception(str(func)+" is not a function")
			return None
			# return map(lambda c: c.value if c.value else c.call(), self.children)

root = Node(None,None)
		

