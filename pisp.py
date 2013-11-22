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
		return lambda arr: arr[0]
	elif t == "last":
		return lambda arr: arr[-1]
	elif t == "rest":
		return lambda arr: arr[1:]
	elif t == "def":
		return lambda name,val: node.root().hoist(name.val(), val)
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
	else:
		return Literal(t, node)

def let(node,binding):
	node.hoist(binding[0].val(), binding[1].val())

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
	def __init__(self, value, node):
		self.value = value
		self.node = node
		self.resolved = False
	def val(self):
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
	def call(self):
		if len(self.children) == 0:
			return self.value
		if type(self.children[0].value) == type(lambda: None):
			# Special case for 'let'
			if self.children[0].value == let:
				let(self, self.children[1].call())
				return self.children[2].call()
			return self.children[0].value(*map(lambda c: c.value if c.value else c.call(),self.children[1:]))
		else:
			return map(lambda c: c.value if c.value else c.call(), self.children)

root = Node(None,None)
		

