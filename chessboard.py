import sys
assert sys.version_info.major == 3
if sys.version_info.minor >= 8:
    '''
    You don't need to patch the dll
    '''
    from libchessboard import Chessboard
else:
    from libchessboard7 import Chessboard
    Chessboard.__repr__ = Chessboard.repr
