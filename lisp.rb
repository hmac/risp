# Lisp code is nested S-expressions
# An S-expression is an opening bracket, a function name, 1 or more arguments and a closing bracket
# Arguments can be literals, variables, functions or S-expressions
# (+ 1 2) 
# => 3
# (+ (+ 1 2) 3) 
# => 6

# We need a parser to read the program as text and covert the text to some sort of 
# syntax tree

# This class represents an S-expression
# It has a function
# and one or more arguments
class Expr
  def initialize(str)
    data = str.reject { |c| c == " " }
    data.shift # First char is (
    data.pop # Last char is )
    @func = tokenise(data.shift)
    @args = data.map { |t| tokenise(t) }
  end

  def call(*args)
    if @func.arity == @args.count
      @args.map! { |a| a.is_a?(Expr) ? a.call : a }
      @func.call *@args
    else
      unless args.nil? or args.empty?
        @args += args.map { |t| tokenise(t) }
        self.call
      else
        nil
      end
    end
  end
end

def parse_expr(str)
  _str = str
  while _str.index(")") != nil
    _str = parse(_str)
  end
  _str.first
end

def parse(str)
  str = str.split("") unless str.is_a? Array
  close = str.index ")"
  open = close - str[0..close].reverse.index("(")
  expr_str = str[open..close]
  new_str = str[0...open] + [Expr.new(expr_str)] + str[close+1..str.length-1]
end

def tokenise(t)
  return t if t.is_a? Expr
  if t.to_i.to_s == t
    return t.to_i
  end
  case t
  when "+"
    lambda { |a, b| a+b }
  when "-"
    lambda { |a, b| a-b }
  when "*"
    lambda { |a, b| a*b }
  when "/"
    lambda { |a, b| a/b }
  when "first"
    lambda { |a, *b| a }
  end
end
