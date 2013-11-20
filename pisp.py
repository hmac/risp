import re

def parse_exp(str):
	arr = str_to_array(str)
	node = parse(arr)

def tokenise(t, node):
	if type(t) == list:
		return t
	if str(int(t)) == t:
		return Literal(int(t))
	if t == "+":
		return lambda a,b: Literal(a.value+b.value)
	elif t == "-":
		return lambda a,b: Literal(a.value-b.value)
	else:
		res = node.resolve(t)
		if res:
			return res
		return Literal(t)


def str_to_array(str):
	str = re.sub("\(", " ( ", str)
	str = re.sub("\)", " ) ", str)
	return str.split()

def parse(arr):
	cur_node = global_root
	for token in arr:
		if token == "(":
			cur_node.push Node(nil,cur_node)
			cur_node = cur_node.children[-1]
		elif token == ")":
			cur_node = cur_node.parent
		else:
			cur_node.push Node.new(tokenise(token, cur_node), cur_node)
	return global_root

class Literal:
	"""its a literal"""
	def __init__(self, val):
		self.val = val

class Node:
	"""issa node"""
	def __init__(self, value, parent):
		self.value = value
		self.parent = parent
		self.children = []
		self.context = {}
	def root:
		if self.parent == nil:
			return self
		else:
			return self.parent.root
	def push(node):
		self.children.append(node)
	def resolve(name):
		if name in self.context.keys():
			return self.context[name]
		if !self.parent:
			return nil
		return self.parent.resolve(name)
	def hoist(name, val):
		self.context[name] = val
	def to_a:
		if len(self.children) == 0:
			return self.value
		else
			map(lambda c: c.to_a, self.children)
	def call:
		if len(self.children) == 0:
			return self.value
		if type(self.children[0]value) == type(lambda: None):
			self.children[0].value.call *map(lambda c: c.value || c.call,self.children[1:])
		else:
			map(lambda c: c.value if c.value else c.call, self.children)

global global_root = Node(nil,nil)
		

