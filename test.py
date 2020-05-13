#!/usr/bin/env python3

import sys
if "c" in sys.argv:
    from constants import Chessboard as C
else:
    from libchessboard import Chessboard as C

if not hasattr(C, "add_dbg"):
    from collections import namedtuple
    Chessman = namedtuple('Chessman', 'belong position value')

    def add_dbg(self, belong, position, value):
        self.belongs[belong].append(position)
        self.board[position] = Chessman(belong, position, value)
    C.add_dbg = add_dbg

c = C(range(128))


def build(b):
    global c
    ls = b.split("\n")
    for y, l in enumerate(ls):
        for x, ll in enumerate(l.split(" ")):
            bel = ll[0] == "+"
            val = int(ll[1:])
            c.add_dbg(bel, (y, x), val)


build('''\
+01 +03 +01 +00 -01 -02 -00 -00
+02 +06 -05 -02 -03 -06 -01 -00
+03 +01 +03 +05 -04 -05 -02 -02
+01 +04 +02 +01 -02 -01 -03 -02''')
assert repr(c) == '''\
+01 +03 +01 +00 -01 -02 -00 -00
+02 +06 -05 -02 -03 -06 -01 -00
+03 +01 +03 +05 -04 -05 -02 -02
+01 +04 +02 +01 -02 -01 -03 -02'''
c.move(False, 3)
print(repr(c))
assert repr(c) == '''\
+01 +03 +01 +00 -00 -00 -01 -02
+02 +06 -05 +00 -02 -03 -06 -01
+03 +01 +03 +05 -00 -04 -05 -03
+01 +04 +02 +01 -02 -01 -03 -02'''

assert c.getBelong((0, 0)) == True
assert c.getBelong((0, 3)) == True
assert c.getBelong((1, 2)) == False
assert c.getNone(True) == [(0, 3), (1, 3)]
assert c.getNone(False) == [(0, 4), (0, 5), (2, 4)]
assert c.getNext(True, 0) == (0, 3)
assert c.getNext(True, 1) == (1, 3)
assert c.getNext(False, 0) == (2, 4)
assert c.getNext(False, 1) == (0, 5)
assert c.getNext(False, 2) == (0, 4)

c.add_dbg(False, (0, 3), 4)
assert repr(c) == '''\
+01 +03 +01 -04 -00 -00 -01 -02
+02 +06 -05 +00 -02 -03 -06 -01
+03 +01 +03 +05 -00 -04 -05 -03
+01 +04 +02 +01 -02 -01 -03 -02'''
assert c.getNext(True, 0) == (1, 3)
assert c.getNext(False, 0) == (2, 4)

c.move(False, 3)

assert repr(c) == '''\
+01 +03 +01 +00 -00 -04 -01 -02
+02 +06 -05 +00 -02 -03 -06 -01
+03 +01 +03 +05 -00 -04 -05 -03
+01 +04 +02 +01 -02 -01 -03 -02'''
