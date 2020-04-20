# 基于单层搜索的模版AI

class Player:
    def __init__(self, isFirst):
        # 初始化
        self.isFirst = isFirst
        self.array = None
        self.platform = [[None for _ in range(8)] for _ in range(4)] if isFirst != None else None
        self.belong = [[isFirst if _ <= 3 else not isFirst for _ in range(8)] for _ in range(4)] if isFirst != None else None
        self.currentRound = 0

    def deepcopy(self):
        new = Player(None)
        new.platform = [[self.platform[i][j] for j in range(8)] for i in range(4)]
        new.belong = [[self.belong[i][j] for j in range(8)] for i in range(4)]
        return new
    
    def search(self, currentround, mode):
        # 按照当前盘面进行所有可能操作的搜索和价值判断
        
        def internal_value(player):
           # 价值函数, 核心代码, 价值定义为己方棋子之和减对方棋子之和
            value = 0
            for row in range(4):
                for column in range(8):
                    if player.belong[row][column] and player.platform[row][column] != None:
                        value += player.platform[row][column]
                    if not player.belong[row][column] and player.platform[row][column] != None:
                        value -= player.platform[row][column]
            return value

        def internal_best_direction(player, isSelf):
            # 从一个局面出发得到最好的方向及其对应的分数
            values={}
            for direction in range(4):
                new = player.deepcopy()
                if new.move(direction, isSelf): values[direction] = internal_value(new)
            max_value = values[max(values, key = lambda key: values[key])] if values else None
            direction = None
            for _ in values:
                if values[_] == max_value:
                    direction = _
            return direction, max_value
                    
        if mode == 'position':
            available = []
            for row in range(4):
                for column in range(8):
                    if not self.belong[row][column] and self.platform[row][column] == None:
                        available.append((row, column))
            available.append(self.get_next())
            # 生成可以放置的位置
            
            players = {}
            for position in available:
                players[position] = self.deepcopy()
                players[position].platform[position[0]][position[1]] = 2
            # 计算所有放置情况的盘面结果

            values = {position: internal_best_direction(players[position], self.isFirst)[1] for position in players}
                
            max_value = None
            choice = None
            for position in values:
                if values[position] != None:
                    choice = position
                    
            if choice != None: self.platform[choice[0]][choice[1]] = 2
            
        else:
            choice = internal_best_direction(self, True)[0]
            if choice != None: self.move(choice, True)

        return choice
    
    def move(self, direction, isSelf):
        # 按照方向移动, 同时返回棋盘是否改变
        myPhase = [{'p1': 'column', 'p2': 'row', 'r1': range(8), 'r2': range(4)},
                   {'p1': 'column', 'p2': 'row', 'r1': range(8), 'r2': range(3, -1, -1)},
                   {'p1': 'row', 'p2': 'column', 'r1': range(4), 'r2': range(8)},
                   {'p1': 'row', 'p2': 'column', 'r1': range(4), 'r2': range(7, -1, -1)}
                   ][direction]

        change = False
        myDict = {}  # 变量字典
        for myDict[myPhase['p1']] in myPhase['r1']:
            queue = []               # 用类队列实现合并
            position = (None, None)  # 队尾的位置
            count = 0                # 计数
            stable = []              # 遵循不可多次吃棋的规则
            exist = False            # 存在空方格
            for myDict[myPhase['p2']] in myPhase['r2']:
                if self.belong[myDict['row']][myDict['column']] != isSelf:
                    while count > len(queue): queue.append(None)
                    queue.append(self.platform[myDict['row']][myDict['column']])
                    position = (myDict['row'], myDict['column'])
                    exist = False
                elif self.platform[myDict['row']][myDict['column']] != None:
                    if queue == []:
                        queue.append(self.platform[myDict['row']][myDict['column']])
                        position = (myDict['row'], myDict['column'])
                        if exist: change = True
                    elif queue[-1] == None:  # 越界填补空位
                        queue[-1] = self.platform[myDict['row']][myDict['column']]
                        self.belong[position[0]][position[1]] = isSelf  # 修改领域归属
                        change = True
                    elif queue[-1] == self.platform[myDict['row']][
                        myDict['column']] and position not in stable:   # 不可多次吃棋
                        queue[-1] = self.platform[myDict['row']][myDict['column']] * 2
                        self.belong[position[0]][position[1]] = isSelf  # 修改领域归属
                        change = True
                        stable.append(position)
                    else:
                        queue.append(self.platform[myDict['row']][myDict['column']])
                        position = (myDict['row'], myDict['column'])
                        if exist: change = True
                else:
                    exist = True
                count += 1

            for myDict[myPhase['p2']] in myPhase['r2']:
                self.platform[myDict['row']][myDict['column']] = queue.pop(0) if queue != [] else None  # 更新地图

        return change

    def get_next(self):
        # 根据随机序列得到在本方领域允许下棋的位置
        available = []
        for row in range(4):
            for column in range(8):
                if self.belong[row][column] and self.platform[row][column] == None:
                    available.append((row, column))
        if available == []:
            return None
        else:
            return available[self.array[self.currentRound] % len(available)]

    def init_process(self, array):
        # 接受随机序列
        self.array = array

    def input_position(self, row, column):
        # 接受对方下棋的位置
        if (row, column) != (None, None):
            self.platform[row][column] = 2

    def input_direction(self, direction):
        # 接受对方合并的方向
        if direction is not None:
            self.move(direction, False)

    def output_position(self, currentRound):
        # 给出己方下棋的位置
        self.currentRound = currentRound        
        return self.search(currentRound, mode = 'position')

    def output_direction(self, currentRound):
        # 给出己方合并的方向
        self.currentRound = currentRound
        return self.search(currentRound, mode = 'direction')

    def show(self, platform, belong):
        # 打印棋盘, + 代表己方, - 代表对方
        return '\n'.join([' '.join([('+' if belong[row][column] else '-') + \
                                    str(platform[row][column] if platform[row][column] != None else 0).zfill(4) \
                                    for column in range(8)]) \
                          for row in range(4)])

    def __str__(self):
        return self.show(self.platform, self.belong)
    __repr__ = __str__
