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

import re

# Parses and executes the contents of the file given
def load(file):
	data = open(file, "r").read()
	lines = filter(lambda l: l != '', data.split("\n"))
	for l in lines:
		res = run(l)
		if res != None:
			print(res.val())

# Parses and executes the code string given
def run(code):
	node = parse_exp(code)
	res = node.call()
	return res

def parse_exp(str):
	arr = str_to_array(str)
	node = parse(arr)
	return node

def tokenise(t, node):
	if type(t) == list:
		return t
	if is_number(t):
		return Literal(int(t), node)
	if t == "+":
		return lambda a,b: Literal(a.val()+b.val(), node)
	elif t == "-":
		return lambda a,b: Literal(a.val()-b.val(), node)
	elif t == "*":
		return lambda a,b: Literal(a.val()*b.val(), node)
	elif t == "/":
		return lambda a,b: Literal(a.val()/b.val(), node)
	elif t == "first":
		return lambda arr: arr.val()[0]
	elif t == "last":
		return lambda arr: arr.val()[-1]
	elif t == "rest":
		return lambda arr: arr.val()[1:]
	elif t == "def":
		return lambda name,val: node.root().hoist(name.val(), val.val())
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
		# return lambda a: Literal(a.val(), node)
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
	else:
		return Literal(t, node)

def let(node,binding):
	node.hoist(binding[0].val(), binding[1].val())

def quote(arg):
	# If arg is list, do not call it. Extract elements and return list.
	if arg.children != []:
		elems = map(lambda c: c.value if c.value else c.call(),arg.children)
		return Literal(elems, None)
	else:
		return arg.value

def atom(arg):
	# If arg is an array with 1+ elems, return []
	# Else return True
	if type(arg.val()) == list and len(arg.val()) > 0:
		return Literal([], None)
	else:
		return Literal(True, None)

def is_number(s):
  try:
    float(s)
    return True
  except ValueError:
    return False


def str_to_array(str):
	# Convert '... to (quote ...)
	match = re.search("'\(", str)
	while match != None:
		start = match.start()
		str = str[0:start-1] + insert_quote(str, start+1)
		match = re.search("'\(", str)

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

class Literal:
	"""its a literal"""
	def __init__(self, value, node):
		self.value = value
		self.node = node
		self.resolved = False
	def val(self):
		if type(self.value) == list or type(self.value) == bool:
			return self.value
		if self.resolved:
			return self.value
		if is_number(self.value):
			self.resolved = True
			self.value = float(self.value)
			return self.value
		res = self.node.resolve(self.value)
		if res:
			self.resolved = True
			self.value = res
			return self.value
		else:
			# Should probably raise an error here
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
		return Literal(val, None)
	def call(self):
		if len(self.children) == 0:
			return self.value
		if type(self.children[0].value) == type(lambda: None):
			# Special case for 'let'
			if self.children[0].value == let:
				bindings = map(lambda c: c.value if c.value else c.call(), self.children[1].children)
				let(self, bindings)
				return self.children[2].call()
			# Special case for 'quote'
			if self.children[0].value == quote:
				return quote(self.children[1])
			# Special case for 'atom'
			if self.children[0].value == atom:
				return atom(self.children[1].call())
			return self.children[0].value(*map(lambda c: c.value if c.value else c.call(),self.children[1:]))
		else:
			# According to the Scheme spec, all unquoted lists must start with a function
			raise Exception(str(self.children[0].value)+" is not a function")
			return None
			# return map(lambda c: c.value if c.value else c.call(), self.children)

root = Node(None,None)
		

