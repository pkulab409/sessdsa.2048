from collections import namedtuple
import copy

ROWS = 4        # 行总数
COLUMNS = 8     # 列总数
ROUNDS = 1000   # 总回合数
MAXTIME = 2     # 总时间限制
MAXLEVEL = 14   # 总级别数
REPEAT = 10     # 交替轮数

ARRAY = list(range(ROUNDS))  # 随机(?)列表

NAMES = {_: str(2 ** _).zfill(4) for _ in range(MAXLEVEL)}  # 将内在级别转换为显示对象的字典
NAMES[0] = '0000'

DIRECTIONS = {0: 'up', 1: 'down', 2: 'left', 3: 'right', None: 'None'}    # 换算方向的字典

PLAYERS = ['nanami', 'ayase']   # 游戏图片名称
LENGTH = 100                    # 格子的边长
PADX = PADY = 10                # 边界填充的距离
WORD_SIZE = (5, 2)              # 标签大小
FONT = ('Verdana', 40, 'bold')  # 文字字体

COLOR_BACKGROUND = '#92877d'    # 全局背景色
COLOR_NONE = '#9e948a'          # 初始界面方格色

COLOR_CELL = {'+': '#eee4da', '-': '#f2b179'}  # 双方的方格色
COLOR_WORD = {'+': '#776e65', '-': '#f9f6f2'}  # 双方的文字色

KEY_BACKWARD = "\'[\'"  # 回退
KEY_FORWARD = "\']\'"   # 前进

# 只读机参数
_LIST_SLOTS = ('__len__', '__getitem__', '__iter__', '__contains__')
_DICT_SLOTS = _LIST_SLOTS + ('keys', 'values', 'items')


# 棋子
'''
-> 初始化棋子
-> 参数: belong   归属, 为bool, True代表先手
-> 参数: position 位置, 为tuple
-> 参数: value    数值, 为int
'''
Chessman = namedtuple('Chessman', 'belong,position,value', defaults=(1, ))

# 棋盘

class Chessboard:
    def __init__(self, array):
        '''
        -> 初始化棋盘
        '''
        self.array = array  # 随机序列
        self.board = {}  # 棋盘所有棋子
        self.belongs = {True:[], False:[]}  # 双方的棋子位置

    def apply(self, to_add, to_delete=()):
        """
        执行当前操作
        Params:
            to_add: iterable(Chessman), 待添加的棋子
            to_delete: iterable(Chessman), 待删除的棋子
        """
        # 统一删除
        delete_pos = set(x.position for x in to_delete)
        self.belongs = {
            k: [x for x in v if x not in delete_pos]
            for k, v in self.belongs.items()
        }
        for pos in delete_pos:
            del self.board[pos]
        # 统一添加
        for chessman in to_add:
            self.belongs[chessman.belong].append(chessman.position)
            self.board[chessman.position] = chessman

    def add(self, belong, position, value=1, apply=True):
        '''
        -> 在指定位置下棋
        -> 若apply为false则只返回棋子本身
        '''
        belong = position[1] < COLUMNS // 2  # 棋子的归属
        chessman = Chessman(belong, position, value)
        if apply:
            self.apply([chessman])
        else:
            return chessman

    def move(self, belong, direction, apply=True):
        '''
        -> 向指定方向合并, 返回是否变化
        -> 若apply为false则只返回操作集
        '''
        to_add, to_delete = {}, {}

        def inBoard(position):  # 判断是否在棋盘内
            return position[0] in range(ROWS) and position[1] in range(COLUMNS)
        def isMine(position):   # 判断是否在领域中
            return belong if position[1] < COLUMNS // 2 else not belong
        def theNext(position):  # 返回下一个位置
            delta = [(-1,0), (1,0), (0,-1), (0,1)][direction]
            return (position[0] + delta[0], position[1] + delta[1])
        def conditionalSorted(chessmanList):  # 返回根据不同的条件排序结果
            if direction == None: return []
            if direction == 0: return sorted(chessmanList, key = lambda x:x[0], reverse = False)
            if direction == 1: return sorted(chessmanList, key = lambda x:x[0], reverse = True )
            if direction == 2: return sorted(chessmanList, key = lambda x:x[1], reverse = False)
            if direction == 3: return sorted(chessmanList, key = lambda x:x[1], reverse = True )
        def occupied(position):  # 返回指定位置的当前棋子
            return to_add.get(position, None if position in to_delete else
                              self.board.get(position))
        def removeChess(position): # 移除指定位置棋子
            if position in to_add:
                del to_add[position]
            else:
                to_delete[position]=self.board[position]
        def move_one(chessman, eaten):  # 移动一个棋子并返回是否移动, eaten是已经被吃过的棋子位置
            nowPosition = chessman.position
            nextPosition = theNext(nowPosition)
            nextChess = occupied(nextPosition)
            while inBoard(nextPosition) and isMine(nextPosition) and not nextChess:  # 跳过己方空格
                nowPosition = nextPosition
                nextPosition = theNext(nextPosition)
                nextChess = occupied(nextPosition)
            if inBoard(nextPosition) and nextChess and nextPosition not in eaten \
                    and chessman.value == nextChess.value:  # 满足吃棋条件
                removeChess(chessman.position)
                removeChess(nextPosition)
                to_add[nextPosition]=Chessman(belong, nextPosition, chessman.value + 1)
                if chessman.position in to_add:
                    del to_add[chessman.position]
                else:
                    to_delete[chessman.position]=chessman
                eaten.append(nextPosition)
                return True
            elif nowPosition != chessman.position:  # 不吃棋但移动了
                to_add[nowPosition]=(Chessman(belong, nowPosition, chessman.value))
                to_delete[chessman.position]=chessman
                return True
            else:  # 未发生移动
                return False
        eaten = []
        change = False
        for _ in conditionalSorted(self.belongs[belong]):
            if move_one(self.board[_], eaten): change = True
        if apply:
            self.apply(to_add.values(), to_delete.values())
            return change
        return to_add.values(), to_delete.values()

    def getBelong(self, position):
        '''
        -> 返回归属
        '''
        return self.board[position].belong if position in self.board else position[1] < COLUMNS // 2

    def getValue(self, position):
        '''
        -> 返回数值
        '''
        return self.board[position].value if position in self.board else 0

    def getScore(self, belong):
        '''
        -> 返回某方的全部棋子数值列表
        '''
        return list(map(lambda x: self.board[x].value, self.belongs[belong]))

    def getNone(self, belong):
        '''
        -> 返回某方的全部空位列表
        '''
        return [(row, column) for row in range(ROWS) for column in range(COLUMNS) \
                if ((column < COLUMNS // 2) == belong) and (row, column) not in self.board]

    def getNext(self, belong, currentRound):
        '''
        -> 根据随机序列得到在本方领域允许下棋的位置
        '''
        available = self.getNone(belong)
        return available[self.array[currentRound] % len(available)] if available != [] else None

    def copy(self):
        '''
        -> 返回一个只读棋盘
        -> 可通过再次调用copy函数转换为真实棋盘拷贝
        '''
        myself = self
        fake_globals = {'slots': {}}

        # 闭包只读机

        class _helper:
            """
            基础只读机
            可设定指定参数穿透至原对象，或对原对象进行深拷贝
            原对象: fake_globals[id(self)]
            可穿透参数: fake_globals['slots'][id(self)]
            """

            def __init__(self, obj, fake_globals, slots):
                fake_globals[id(self)] = obj
                fake_globals['slots'][id(self)] = slots

            def __getattr__(self, i):
                if not i in fake_globals['slots'][id(self)]:
                    raise AttributeError(i)
                return getattr(fake_globals[id(self)], i)

            def copy(self):
                return copy.deepcopy(fake_globals[id(self)])

        class _list(_helper):
            def __init__(self, obj, fake_globals):
                super().__init__(obj, fake_globals, _LIST_SLOTS)

        class _dict(_helper):
            def __init__(self, obj, fake_globals):
                super().__init__(obj, fake_globals, _DICT_SLOTS)

        class _chessboard(_helper):
            """
            只读棋盘
            穿透功能：get[Action]
            """

            def __init__(self, obj, fake_globals):
                super().__init__(obj, fake_globals,
                                 ('getBelong', 'getValue', 'getScore',
                                  'getNone', 'getNext', '__str__', '__repr__'))
                # 设置内部只读参数
                self.array = _list(obj.array, fake_globals)
                self.board = _dict(obj.board, fake_globals)
                self.belongs = {
                    key: _list(obj.belongs[key], fake_globals)
                    for key in range(2)
                }

            def move(self, belong, direction):
                """ 判断是否可移动 """
                return any(self.movedItems(belong, direction))

            def movedItems(self, belong, direction):
                """ 返回一次移动操作集 """
                return fake_globals[id(self)].move(belong, direction, False)

        rBoard = _chessboard(myself, fake_globals)
        return rBoard

    def __repr__(self):
        '''
        -> 打印棋盘, + 代表先手, - 代表后手
        '''
        return '\n'.join([' '.join([('+' if self.getBelong((row, column)) else '-') + str(self.getValue((row, column))).zfill(2) \
                                   for column in range(COLUMNS)]) \
                         for row in range(ROWS)])
    __str__ = __repr__
