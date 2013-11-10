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

# This class represents an S-expression
# It has a function
# and one or more arguments
class Expr
  def initialize(tokens)
    # First token is (
    # Last token is )
    tokens = tokens[1..-2]
    @func = tokenise(tokens[0])
    @args = tokens.drop(1).map { |t| tokenise(t) }
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
  return t if t.is_a? Expr or t.is_a? Array
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
    Proc.new { |n, arr| arr[n] }
  when "append"
    Proc.new { |a*| a.inject { |acc, e| acc + e } }
  end
end

def list(tokens)
  # First token is '(
  # Last token is )
  tokens[1..-2].map { |e| tokenise e }
end

def str_to_array(str)
  str.gsub(/([()])/, ' \1 ')  # Expand brackets so all tokens are separated by spaces
    .gsub("' (", "'(")        # Join ' ( together into one '( token
    .split " "                # Convert string to array of tokens
end

def parse(arr)
  close = arr.index ")" # Find first closing bracket
  # Find corresponding opening bracket
  first_expr_bracket = arr[0..close].reverse.index("(")
  first_list_bracket = arr[0..close].reverse.index("'(") || arr.length
  if first_list_bracket < first_expr_bracket
    # We've found a list
    open = close - first_list_bracket
    list_tokens = arr[open..close]
    arr[0...open] + [list(list_tokens)] + arr[close+1..-1]
  else
    # We've found an expression
    open = close - first_expr_bracket
    expr_tokens = arr[open..close] # Get tokens inside these two brackets
    arr[0...open] + [Expr.new(expr_tokens)] + arr[close+1..arr.length-1] # Convert tokens to an expression
  end
end

# Convenience eval method
def run(code)
  parse_expr(code).call
end
