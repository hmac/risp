import pisp

def expect(code, val):
  res = pisp.run(code)
  if res and res.val() == val:
    return
  raise Exception(str(code)+" returned "+str(res.val())+", expected "+str(val))

expect("(+ 1 1)", 2)
expect("(first (1 2 3))", 1)
expect("(+ 1 (first (1 2)))", 2)

# pisp doesn't support nth yet
# expect("(nth 3 (cons 2 (list 1 2 3 4)))", 3)

# Variable binding
# N.B. From here on a=5
expect("(def a 5)", 5)
expect("(+ a 2)", 7)

# Let
expect("(let (b 4) (+ 1 b))", 5)

# Quoting
expect("(quote b)", "b")



print "All tests passed."
