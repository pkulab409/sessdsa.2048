# 检查module2的Chessboard是否实现了module1的Chessboard功能
# 请在plat中引用testboard中的Chessboard
# 再进行一局round_match: main(['testboard.py'] * 2, MAXTIME = 10000, debug = True)即可检查

module1 = 'constants'
module2 = 'libchessboard'

class Chessboard:
    def __init__(self, array):
        self.c1 = __import__(module1).Chessboard(array)
        self.c2 = __import__(module2).Chessboard(array)
        
        class Nothing: pass
        names = {'method': [], 'attr': []}  # 存储方法与属性的字典
        for name in set(dir(self.c1)) - set(dir(Nothing())):
            names['method' if callable(self.c1.__getattribute__(name)) else 'attr'].append(name)
        names['method'].remove('copy')
        
        def check():  # 检查属性的函数
            for attr in names['attr']:
                assert self.c1.__getattribute__(attr) == self.c2.__getattribute__(attr), \
                    attr + '\npy\n%s\nc\n%s' % (self.c1.__getattribute__(attr), self.c2.__getattribute__(attr))
                
        def func(method):  # 检查方法的闭包
            def wrappedFunc(*args, **kwargs):
                c1 = self.c1.__getattribute__(method)(*args, **kwargs)
                c2 = self.c2.__getattribute__(method)(*args, **kwargs)
                # print(method, *args, **kwargs)  # 此行输出接口的调用情况
                # check() # 对于c的实现, 属性不检查
                if method == 'getScore': c2.sort()  # 手动排序
                assert c1 == c2, method + '\npy\n%s\nc\n%s\n' % (c1, c2)
                return c1
            return wrappedFunc

        for method in names['method']:
            self.__setattr__(method, func(method))

    def __repr__(self):
        assert repr(self.c1) == repr(self.c2), '\npy\n%s\nc\n%s\n' % (self.c1, self.c2)
        return repr(self.c1)
    __str__ = __repr__

    def copy(self):  # 假拷贝
        assert repr(self.c1.copy()) == repr(self.c2.copy()), \
               '\npy\n%s\nc\n%s\n' % (self.c1.copy(), self.c2.copy())
        return self

import constants as c

class Player(__import__('player').Player): # 耍接口的Player
    def __init__(self, isFirst, array):
        super().__init__(isFirst, array)
        
    def output(self, currentRound, board, mode):
        for row in range(c.ROWS):
            for column in range(c.COLUMNS):
                board.getBelong((row, column))
                board.getValue((row, column))
        for isFirst in [True, False]:
            board.getScore(isFirst)
            board.getNone(isFirst)
            board.getNext(isFirst, currentRound)
            board.getDecision(isFirst)
            # board.getTime(isFirst)  # 时间不一样, 不检查
        # board.getAnime()  # 还没装, 不检查
        return super().output(currentRound, board.c1.copy(), mode)
        
