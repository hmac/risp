require "./lisp"

def expect(code, val)
  res = run(code).value
  raise "#{code} produced #{res}, expected #{val}" if res != val
end

expect "(+ 1 1)", 2
expect "(first (1 2 3))", 1
expect "(+ 1 (first (1 2)))", 2
expect "(nth 3 (cons 2 (list 1 2 3 4)))", 3

puts "All tests passed."
