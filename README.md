Risp
=====

A very basic lisp interpreter targeting Scheme. Supports `let`, `quote`, `atom`, `def`, `cond` and `lambda` as special forms, and `+`, `-`, `*`, `/`, `first`, `last`, `rest` and `cons` as native functions.

Lisp code is interpreted by parsing it, constructing a tree of `Node` objects and then evaluating them from the inside out. It's a very naïve, rudimentary approach, but then the original implementation was written in a couple of hours on the train, so it doesn't aspire to greatness (or even usefulness).
