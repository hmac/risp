# This is not really a proper lisp interpreter
# Beyond lists, it has no concept of symbols
# It has no support for macros
# It has a very limited set of primitive functions
# It's effectively useless

# Lisp code is nested S-expressions
# An S-expression is an opening bracket, a function name, 1 or more arguments and a closing bracket
# Arguments can be literals, variables, functions, S-expressions or lists
# (+ 1 2) 
# => 3
# (+ (+ 1 2) 3) 
# => 6

# There are also lists
# Lists are like S-expressions without the function
# They are just a list of literals, variables, functions, lists or S-expressions
# Lists are denoted with a ' before the (
# '(1 2 3 4)
# Example usage:
# (first '(1 2 3 4)) => 1
# (map (+ 5) '(1 2 3)) => (6 7 8)

# We need a parser to read the program as text and covert the text to some sort of 
# syntax tree


def parse_expr(str)
  arr = str_to_array(str)
  node = parse arr
end

def tokenise(t)
  return t if t.is_a? Array
  if t.to_i.to_s == t
    return Literal.new(t.to_i)
  end
  case t
  when "+"
    Proc.new { |a, b| Literal.new(a.value+b.value) }
  when "-"
    Proc.new { |a, b| Literal.new(a.value-b.value) }
  when "*"
    Proc.new { |a, b| Literal.new(a.value*b.value) }
  when "/"
    Proc.new { |a, b| Literal.new(a.value/b.value) }
  when "first"
    Proc.new { |arr| arr.first }
  when "last"
    Proc.new { |arr| arr[-1] }
  when "rest"
    Proc.new { |arr| arr[1..-1] }
  when "cons"
    Proc.new { |a, arr| [a] + arr }
  when "list"
    Proc.new { |*a| a }
  when "nth"
    Proc.new { |n, arr| arr[n.value] }
  when "append"
    Proc.new { |*a| a.inject { |acc, e| acc + e } }
  end
end

def str_to_array(str)
  str.gsub(/([()])/, ' \1 ')  # Expand brackets so all tokens are separated by spaces
    .split " "                # Convert string to array of tokens
    # .gsub("' (", "'(")        # Join ' ( together into one '( token
end

def parse(arr)
  root = Node.new(nil,nil)
  cur_node = root
  arr.each do |token|
    if token == "("
      cur_node.push Node.new(nil,cur_node)
      cur_node = cur_node.children.last
    else 
      if token == ")"
      cur_node = cur_node.parent
      else
        cur_node.push Node.new(tokenise(token), cur_node)
      end
    end
  end
  root.children.first
end

# Convenience eval method
def run(code)
  parse_expr(code).call
end

class Literal
  def initialize(val)
    @value = val
  end
  def value
    @value
  end
  
end

class Node
  def initialize(value, parent)
    @parent = parent
    @value = value
    @children = []
  end
  def root?
    @parent.nil?
  end
  def value
    @value
  end
  def parent
    @parent
  end
  def children
    @children
  end
  def [](index)
    @children ? @children[index] : nil
  end
  def length
    @children ? @children.length : 0
  end
  def push(node)
    @children.push node
  end
  def to_a
    @children.empty? ? @value : @children.map { |c| c.to_a }
  end
  def call
    return @value if @children.empty?
    if @children[0].value.is_a? Proc
      @children[0].value.call *@children[1..-1].map { |c| c.value || c.call }
    else
      @children.map { |c| c.value.nil? ? c.call : c.value }
    end
  end
end
