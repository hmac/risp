import re

def run(code):
	node = parse_exp(code)
	return node.call().value

def parse_exp(str):
	arr = str_to_array(str)
	node = parse(arr)
	return node

def tokenise(t, node):
	if type(t) == list:
		return t
	if is_number(t):
		return Literal(int(t))
	if t == "+":
		return lambda a,b: Literal(a.value+b.value)
	elif t == "-":
		return lambda a,b: Literal(a.value-b.value)
	elif t == "*":
		return lambda a,b: Literal(a.value*b.value)
	elif t == "/":
		return lambda a,b: Literal(a.value/b.value)
	elif t == "first":
		return lambda arr: arr[0]
	elif t == "last":
		return lambda arr: arr[-1]
	elif t == "rest":
		return lambda arr: arr[1:]
	elif t == "def":
		return lambda name,val: node.root().hoist(name.value, val)
	elif t == "let":
		# The way S-expressions are currently evaluated
		# (from the inside out) means that by the time this
		# function is called, the variables it is meant to
		# define have already been used (or attemped to be used)
		# and so an error has probably already occurred as they will
		# have been treated as strings.
		# We'd have to somehow detect when we come across a 'let'
		# function in the Node.call method so that we don't try to
		# evaluate the contained expression before the variables have been set.
		pass
	else:
		res = node.resolve(t)
		if res:
			return res
		return Literal(t)

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def str_to_array(str):
	str = re.sub("\(", " ( ", str)
	str = re.sub("\)", " ) ", str)
	return str.split()

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
	def __init__(self, value):
		self.value = value

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
	def to_a():
		if len(self.children) == 0:
			return self.value
		else:
			map(lambda c: c.to_a, self.children)
	def call(self):
		if len(self.children) == 0:
			return self.value
		if type(self.children[0].value) == type(lambda: None):
			return self.children[0].value(*map(lambda c: c.value if c.value else c.call(),self.children[1:]))
		else:
			return map(lambda c: c.value if c.value else c.call(), self.children)

root = Node(None,None)
		

