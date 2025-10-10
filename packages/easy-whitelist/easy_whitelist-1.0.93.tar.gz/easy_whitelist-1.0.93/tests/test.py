import sys
import foo

from foo import inc

for _ in range(10):
    foo.inc()
    inc()
    print('-' * 50)


foo.inc = foo.new_inc

for _ in range(10):
    foo.inc()
    inc()
    print('-' * 50)
