class Player:
    def __init__(self, isFirst):
        # 初始化
        self.array = None
        self.platform = [[None for _ in range(8)] for _ in range(4)]
        self.belong = [[isFirst if _ <= 3 else not isFirst for _ in range(8)] for _ in range(4)]
        self.currentRound = 0
        
    def move(self, direction, isSelf): 
        # 按照方向移动, 同时返回棋盘是否改变
        myPhase = [{'p1':'column', 'p2':'row', 'r1':range(8), 'r2':range(4)},
                   {'p1':'column', 'p2':'row', 'r1':range(8), 'r2':range(3, -1, -1)},
                   {'p1':'row', 'p2':'column', 'r1':range(4), 'r2':range(8)},
                   {'p1':'row', 'p2':'column', 'r1':range(4), 'r2':range(7, -1, -1)}
                  ][direction]
        
        change = False
        myDict = {}  # 变量字典
        for myDict[myPhase['p1']] in myPhase['r1']:
            queue = []                  # 用类队列实现合并
            position = (None, None)     # 队尾的位置
            count = 0                   # 计数
            stable = []                 # 遵循不可多次吃棋的规则
            for myDict[myPhase['p2']] in myPhase['r2']:
                if self.belong[myDict['row']][myDict['column']] != isSelf:
                    while count > len(queue):
                        change = True   # 发生改变的情况1
                        queue.append(None)
                    queue.append(self.platform[myDict['row']][myDict['column']])
                    position = (myDict['row'], myDict['column'])
                elif self.platform[myDict['row']][myDict['column']] != None:
                    if queue == []:
                        queue.append(self.platform[myDict['row']][myDict['column']])
                        position = (myDict['row'], myDict['column'])
                    elif queue[-1] == None:  # 越界填补空位
                        queue[-1] = self.platform[myDict['row']][myDict['column']]
                        self.belong[position[0]][position[1]] = isSelf  # 修改领域归属
                    elif queue[-1] == self.platform[myDict['row']][myDict['column']] and position not in stable:   # 不可多次吃棋
                        queue[-1] = self.platform[myDict['row']][myDict['column']] * 2
                        self.belong[position[0]][position[1]] = isSelf  # 修改领域归属
                        stable.append(position)
                    else:
                        queue.append(self.platform[myDict['row']][myDict['column']])
                        position = (myDict['row'], myDict['column'])
                count += 1
                
            if count > len(queue): change = True   # 发生改变的情况2
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
        if (row, column) != (None, None): self.platform[row][column] = 2

    def input_direction(self, direction):
        # 接受对方合并的方向
        if direction != None: self.move(direction, False)
    
    def output_position(self):
        # 给出己方下棋的位置
        available = []
        for row in range(4):
            for column in range(8):
                if not self.belong[row][column] and self.platform[row][column] == None:
                    available.append((row, column))
                    
        another = self.get_next()  # 在本方的允许处
        self.currentRound += 1
        if another != None:
            row, column = another
            self.platform[row][column] = 2
            return another
        
        if available == []:
            return None
        else:
            from random import choice
            row, column = choice(available)
            self.platform[row][column] = 2
            return row, column
    
    def output_direction(self):
        # 给出己方合并的方向
        from random import shuffle
        directionList = [0, 1, 2, 3]
        shuffle(directionList)
        for direction in directionList:
            if self.move(direction, True): return direction

    def show(self):
        # 打印棋盘, + 代表己方, - 代表对方
        platform = ''
        for row in range(4):
            for column in range(8):
                platform += ('+' if self.belong[row][column] else '-') + \
                str(self.platform[row][column] if self.platform[row][column] != None else 0).zfill(4) + ' '
            platform += '\n'
        print(platform[:-1])
