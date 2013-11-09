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
  def initialize(tokens)
    tokens.shift # First token is (
    tokens.pop # Last token is )
    @func = tokenise(tokens.shift)
    @args = tokens.map { |t| tokenise(t) }
  end

  def call(*args)
    # A negative arity implies an optional number of arguments (i.e. a splat)
    # -1 => 0+ arguments
    # -2 => 1+ arguments
    # etc.
    n = @func.arity.abs - 1
    if @func.arity == @args.count or (@func.arity < 0 and @args.count > n)
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
  _str = str_to_array(str)
  while _str.length > 1
    _str = parse(_str)
  end
  _str.first
end

def tokenise(t)
  return t if t.is_a? Expr
  if t.to_i.to_s == t
    return t.to_i
  end
  case t
  when "+"
    Proc.new { |a, b| a+b }
  when "-"
    Proc.new { |a, b| a-b }
  when "*"
    Proc.new { |a, b| a*b }
  when "/"
    Proc.new { |a, b| a/b }
  when "first"
    Proc.new { |a, *b| a }
  end
end

def str_to_array(str)
  str.gsub(/([()])/, ' \1 ')  # Expand brackets so all tokens are separated by spaces
    .split " "                # Convert string to array of tokens
end

def parse(arr)
  close = arr.index ")"
  open = close - arr[0..close].reverse.index("(")
  expr_tokens = arr [open..close]
  arr[0...open] + [Expr.new(expr_tokens)] + arr[close+1..arr.length-1]
end
