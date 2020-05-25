MAXTIME = 5     # 最大时间限制
ROUNDS = 500    # 总回合数
REPEAT = 10     # 单循环轮数

ROWS = 4        # 行总数
COLUMNS = 8     # 列总数
MAXLEVEL = 14   # 总级别数

SLEEP = 0.3       # 直播等待时间

ARRAY = list(range(ROUNDS))  # 随机(?)列表

NAMES = {_: str(2 ** _).zfill(4) for _ in range(MAXLEVEL)}  # 将内在级别转换为显示对象的字典
NAMES[0] = '0000'

class _DIRECTIONS(list):
    def __init__(self):
        super().__init__(['up', 'down', 'left', 'right'])
    def __getitem__(self, key):
        return super().__getitem__(key) if key in range(4) else 'unknown'
DIRECTIONS = _DIRECTIONS()      # 换算方向的字典

PLAYERS = {True: 'player 0', False: 'player 1'}  # 换算先后手名称的字典

PICTURES = ['nanami', 'ayase']  # 游戏图片名称
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


# 棋子

from collections import namedtuple

'''
-> 初始化棋子
-> 参数: belong   归属, 为bool, True代表先手
-> 参数: position 位置, 为tuple
-> 参数: value    数值, 为int
'''

Chessman = namedtuple('Chessman', 'belong position value')

# 棋盘

class Chessboard:
    def __init__(self, array):
        '''
        -> 初始化棋盘
        '''
        self.array = array  # 随机序列
        self.board = {}  # 棋盘所有棋子
        self.belongs = {True: [], False: []}  # 双方的棋子位置
        self.decision = {True: (), False: ()}  # 双方上一步的决策
        self.time = {True: 0, False: 0}  # 双方剩余的时长
        self.anime = []  # 动画效果
        

    def add(self, belong, position, value = 1):
        '''
        -> 在指定位置下棋
        '''
        belong = position[1] < COLUMNS // 2  # 重定义棋子的归属
        self.belongs[belong].append(position)
        self.board[position] = Chessman(belong, position, value)

    def move(self, belong, direction):
        '''
        -> 向指定方向合并, 返回是否变化
        '''
        self.anime = []
        def inBoard(position):  # 判断是否在棋盘内
            return position[0] in range(ROWS) and position[1] in range(COLUMNS)
        def isMine(position):   # 判断是否在领域中
            return belong if position[1] < COLUMNS // 2 else not belong
        def theNext(position):  # 返回下一个位置
            delta = [(-1,0), (1,0), (0,-1), (0,1)][direction]
            return (position[0] + delta[0], position[1] + delta[1])
        def conditionalSorted(chessmanList):  # 返回根据不同的条件排序结果
            if direction == 0: return sorted(chessmanList, key = lambda x:x[0], reverse = False)
            if direction == 1: return sorted(chessmanList, key = lambda x:x[0], reverse = True )
            if direction == 2: return sorted(chessmanList, key = lambda x:x[1], reverse = False)
            if direction == 3: return sorted(chessmanList, key = lambda x:x[1], reverse = True )
            return []
        def move_one(chessman, eaten):  # 移动一个棋子并返回是否移动, eaten是已经被吃过的棋子位置
            nowPosition = chessman.position
            nextPosition = theNext(nowPosition)
            while inBoard(nextPosition) and isMine(nextPosition) and nextPosition not in self.board:  # 跳过己方空格
                nowPosition = nextPosition
                nextPosition = theNext(nextPosition)
            if inBoard(nextPosition) and nextPosition in self.board and nextPosition not in eaten \
                    and chessman.value == self.board[nextPosition].value:  # 满足吃棋条件
                self.anime.append(chessman.position + nextPosition)
                self.belongs[belong].remove(chessman.position)
                self.belongs[belong if nextPosition in self.belongs[belong] else not belong].remove(nextPosition)
                self.belongs[belong].append(nextPosition)
                self.board[nextPosition] = Chessman(belong, nextPosition, chessman.value + 1)
                del self.board[chessman.position]
                eaten.append(nextPosition)
                return True
            elif nowPosition != chessman.position:  # 不吃棋但移动了
                self.anime.append(chessman.position + nowPosition)
                self.belongs[belong].remove(chessman.position)
                self.belongs[belong].append(nowPosition)
                self.board[nowPosition] = Chessman(belong, nowPosition, chessman.value)
                del self.board[chessman.position]
                return True
            else:  # 未发生移动
                return False
        eaten = []
        change = False
        for _ in conditionalSorted(self.belongs[belong]):
            if move_one(self.board[_], eaten): change = True
        return change

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
        return sorted(map(lambda x: self.board[x].value, self.belongs[belong]))

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
        if not belong: available.reverse()  # 后手序列翻转
        return available[self.array[currentRound] % len(available)] if available != [] else ()

    def updateDecision(self, belong, decision):
        '''
        -> 更新决策
        '''
        self.decision[belong] = decision

    def getDecision(self, belong):
        '''
        -> 返回上一步的决策信息
        -> 无决策为(), 位置决策为position, 方向决策为(direction,)
        -> 采用同类型返回值是为了和优化库统一接口
        '''
        return self.decision[belong]

    def updateTime(self, belong, time):
        '''
        -> 更新剩余时间
        '''
        self.time[belong] = time

    def getTime(self, belong):
        '''
        -> 返回剩余时间
        '''
        return self.time[belong]

    def getAnime(self):
        '''
        -> 返回动画效果辅助信息
        '''
        return self.anime

    def copy(self):
        '''
        -> 返回一个对象拷贝
        '''
        new = Chessboard(self.array)
        new.board = self.board.copy()
        new.belongs[True] = self.belongs[True].copy()
        new.belongs[False] = self.belongs[False].copy()
        new.decision = self.decision.copy()
        new.time = self.time.copy()
        new.anime = self.anime.copy()
        return new

    def getRaw(self):
        '''
        -> 返回一个代表棋盘的二维列表, 元素为(value, belong)
        '''
        return [[(self.getValue((row, column)), self.getBelong((row, column)))
                 for column in range(COLUMNS)] for row in range(ROWS)]

    def __repr__(self):
        '''
        -> 打印棋盘, + 代表先手, - 代表后手
        '''       
        return '\n'.join([' '.join([('+' if self.getBelong((row, column)) else '-') + str(self.getValue((row, column))).zfill(2) \
                                   for column in range(COLUMNS)]) \
                         for row in range(ROWS)])
    __str__ = __repr__
