import pisp

def expect(code, val):
  res = pisp.run(code)
  if res == val:
    return
  raise Exception(str(code)+" returned "+str(res)+", expected "+str(val))

expect("(+ 1 1)", 2)
expect("(first (quote (1 2 3)))", 1)
expect("(+ 1 (first (quote (1 2))))", 2)

# pisp doesn't support nth yet
# expect("(nth 3 (cons 2 (list 1 2 3 4)))", 3)

# Variable binding
# N.B. From here on a=5
expect("(def a 5)", None)
expect("(+ a 2)", 7)

# Let
expect("(let (b 4) (+ 1 b))", 5)

# Quoting
# Currently this returns a Symbol object
# expect("(quote b)", "b")

# Atom
expect("(atom (quote b))", True)
expect("(atom '(1 2 3))", [])

# Eq
# Currently does not work as 'b and 'b produce 2 different objects
# expect("(eq 'b 'b)", True)
expect("(eq 'b 'c)", [])

# Cons
expect("(cons 'a '(b c))", ["a", "b", "c"])

# Cond
expect("(cond ((eq 'a 'b) 1) ((atom 'a) 2))", 2)

# Lambda
expect("((lambda (x y) (+ x y)) 1 2)", 3)

print "All tests passed."
