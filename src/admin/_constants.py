MAXTIME = 5     # 最大时间限制
ROUNDS = 500    # 总回合数
REPEAT = 10     # 单循环轮数

ROWS = 4        # 行总数
COLUMNS = 8     # 列总数
MAXLEVEL = 14   # 总级别数

ARRAY = list(range(ROUNDS))  # 随机(?)列表

class _DIRECTIONS(list):
    def __init__(self):
        super().__init__(['up', 'down', 'left', 'right'])
    def __getitem__(self, key):
        return super().__getitem__(key) if key in range(4) else 'unknown'
DIRECTIONS = _DIRECTIONS()     # 换算方向的字典

PLAYERS = {True: 'player 0',
           False: 'player 1'}  # 换算先后手名称的字典

# 棋盘

class Chessboard:
    def __init__(self, array, board = None, decision = None, time = None):
        '''
        -> 初始化棋盘
        '''
        self.array = array      # 随机序列
        if board:       # 初始棋盘
            self.board = board
        else:
            self.board = [int(_ >= ROWS * COLUMNS // 2) for _ in range(ROWS * COLUMNS)]
        if decision:    # 双方上一步的决策
            self.decision = decision
        else:
            self.decision = [(), ()]
        if time:        # 双方剩余的时长
            self.time = time
        else:
            self.time = [0, 0]

    def add(self, belong, position, value = 1):
        '''
        -> 在指定位置下棋
        '''
        _belong = position[1] < COLUMNS // 2
        _position = position[0] + position[1] * ROWS
        _value = 2 * value + int(not _belong)
        self.board[_position] = _value

    def move(self, belong, direction):
        '''
        -> 向指定方向合并, 返回是否变化
        '''
        def move_one(row, column):  # 一次移动
            nonlocal eat, change  # 非局部变量
            p0 = row + column * ROWS
            if ((self.board[p0] % 2 == 0) ^ belong) or self.board[p0] < 2: return  # 非己方或空格
            p1, p2 = p0, theNext(p0)
            while True:  # 跳过己方空格
                if (not (0 <= p2 < ROWS * COLUMNS)) or ((self.board[p2] % 2 == 0) ^ belong) or self.board[p2] >= 2: break
                p1, p2 = p2, theNext(p2)
            if (0 <= p2 < ROWS * COLUMNS) and self.board[p2] // 2 == self.board[p0] // 2 and p2 != eat:  # 满足吃棋条件
                self.board[p2] = self.board[p0] + 2
                self.board[p0] = int(p0 >= ROWS * COLUMNS // 2)
                eat, change = p2, True
            elif p1 != p0:  # 不吃棋但移动了
                self.board[p1] = self.board[p0]
                self.board[p0] = int(p0 >= ROWS * COLUMNS // 2)
                change = True
                
        if direction not in range(4): return False
        eat, change = None, False
        if direction == 0:
            theNext = lambda _p: _p - 1 if _p % ROWS != 0 else -1
            for column in range(COLUMNS):
                for row in range(ROWS):
                    move_one(row, column)       
        elif direction == 1:
            theNext = lambda _p: _p + 1 if (_p + 1) % ROWS != 0 else -1
            for column in range(COLUMNS):
                for row in range(ROWS - 1, -1, -1):
                    move_one(row, column)
        elif direction == 2:
            theNext = lambda _p: _p - ROWS
            for row in range(ROWS):
                for column in range(COLUMNS):
                    move_one(row, column)
        else:
            theNext = lambda _p: _p + ROWS
            for row in range(ROWS):
                for column in range(COLUMNS - 1, -1, -1):
                    move_one(row, column)
        return change

    def getBelong(self, position):
        '''
        -> 返回归属
        '''
        return self.board[position[0] + position[1] * ROWS] % 2 == 0

    def getValue(self, position):
        '''
        -> 返回数值
        '''
        return self.board[position[0] + position[1] * ROWS] // 2

    def getScore(self, belong):
        '''
        -> 返回某方的全部棋子数值列表
        '''
        return sorted([self.board[_position] // 2 for _position in range(ROWS * COLUMNS)
                       if (self.board[_position] % 2 == 1) ^ belong and self.board[_position] >= 2])

    def getNone(self, belong):
        '''
        -> 返回某方的全部空位列表
        '''
        return [(row, column) for row in range(ROWS) for column in range(COLUMNS) \
                if ((column < COLUMNS // 2) == belong) and self.board[row + column * ROWS] < 2]
    
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
        self.decision[int(not belong)] = decision

    def getDecision(self, belong):
        '''
        -> 返回上一步的决策信息
        -> 无决策为(), 位置决策为position, 方向决策为(direction,)
        -> 采用同类型返回值是为了和优化库统一接口
        '''
        return self.decision[int(not belong)]

    def updateTime(self, belong, time):
        '''
        -> 更新剩余时间
        '''
        self.time[int(not belong)] = time

    def getTime(self, belong):
        '''
        -> 返回剩余时间
        '''
        return self.time[int(not belong)]

    def copy(self):
        '''
        -> 返回一个对象拷贝
        '''
        return Chessboard(self.array, self.board.copy(), self.decision.copy(), self.time.copy())

    def __repr__(self):
        '''
        -> 打印棋盘, + 代表先手, - 代表后手
        '''       
        return '\n'.join([' '.join([('+' if self.getBelong((row, column)) else '-') + str(self.getValue((row, column))).zfill(2) \
                                   for column in range(COLUMNS)]) \
                         for row in range(ROWS)])
    __str__ = __repr__
