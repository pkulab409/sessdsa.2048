from libchessboard import Chessboard as C

c = C([])

if not hasattr(c, "add_dbg"):
    print("Did you forget to export function add_dbg ?")

def build(b):
    global c
    ls = b.split("\n")
    for y, l in enumerate(ls):
        for x, ll in enumerate(l.split(" ")):
            bel = ll[0] == "+"
            val = int(ll[1:])
            c.add_dbg(bel, (y, x), val)


build('''+01 +03 +01 +00 -01 -02 -00 -00
+02 +06 -05 -02 -03 -06 -01 -00
+03 +01 +03 +05 -04 -05 -02 -02
+01 +04 +02 +01 -02 -01 -03 -02''')

c.move(False, 3)

assert repr(c) == '''+01 +03 +01 +00 -00 -00 -01 -02
+02 +06 -05 +00 -02 -03 -06 -01
+03 +01 +03 +05 -00 -04 -05 -03
+01 +04 +02 +01 -02 -01 -03 -02'''