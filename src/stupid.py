# 基于单层搜索的模版AI

class Player:
    def __init__(self, isFirst):
        # 初始化
        self.array = None
        self.platform = [[None for _ in range(8)] for _ in range(4)]
        self.belong = [[isFirst if _ <= 3 else not isFirst for _ in range(8)] for _ in range(4)]
        self.currentRound = 0
    
    def search(self, currentround):
        #按照当前盘面进行所有可能操作的搜索和价值判断
        def internal_deepcopy(lst):
            #深层复制二维列表
            new=[]
            for i in lst:
                new.append(list(i))
            return new

        def internal_value(platform, belong):
           #价值函数
           value=0
           for row in range(4):
            for column in range(8):
                if belong[row][column] and platform[row][column] != None:
                    value+=platform[row][column]
                if not belong[row][column] and platform[row][column] != None:
                    value-=platform[row][column]
            return value
    
        def internal_move(platform, belong, direction, isSelf):
            # 按照方向移动, 同时返回棋盘是否改变以及改变之后的棋盘
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
                    if belong[myDict['row']][myDict['column']] != isSelf:
                        while count > len(queue): queue.append(None)
                        queue.append(platform[myDict['row']][myDict['column']])
                        position = (myDict['row'], myDict['column'])
                        exist = False
                    elif platform[myDict['row']][myDict['column']] != None:
                        if queue == []:
                            queue.append(platform[myDict['row']][myDict['column']])
                            position = (myDict['row'], myDict['column'])
                            if exist: change = True
                        elif queue[-1] == None:  # 越界填补空位
                            queue[-1] = platform[myDict['row']][myDict['column']]
                            belong[position[0]][position[1]] = isSelf  # 修改领域归属
                            change = True
                        elif queue[-1] == platform[myDict['row']][
                            myDict['column']] and position not in stable:   # 不可多次吃棋
                            queue[-1] = platform[myDict['row']][myDict['column']] * 2
                            belong[position[0]][position[1]] = isSelf  # 修改领域归属
                            change = True
                            stable.append(position)
                        else:
                            queue.append(platform[myDict['row']][myDict['column']])
                            position = (myDict['row'], myDict['column'])
                            if exist: change = True
                    else:
                        exist = True
                    count += 1
                for myDict[myPhase['p2']] in myPhase['r2']:
                    platform[myDict['row']][myDict['column']] = queue.pop(0) if queue != [] else None  # 更新地图

            return platform,belong,change

        def internal_available(platform, belong, another):
            #生成可以放置的位置
            available = []
            for row in range(4):
                for column in range(8):
                    if not belong[row][column] and platform[row][column] == None:
                        available.append((row, column))
            available.append(another)
            return available
        
        def internal_possible_place(platform, belong, available):
            #计算所有放置情况的盘面结果
            outcomes={}
            for i in available:
                outcomes[i]=[internal_deepcopy(platform),internal_deepcopy(belong)]
                outcomes[i][0][i[0]][i[1]]=2
            return outcomes

        def internal_possible_move(placed):
            #对于所有放置之后的结果计算移动之后的结果
            moved={}
            for position in placed:
                for direction in range(4):
                    platform=internal_deepcopy(placed[position][0])
                    belong=internal_deepcopy(placed[position][1])
                    platform,belong,change=internal_move(platform,belong, direction, True)
                    if change:
                        moved[(position,direction)]=[platform,belong]
            return moved
        available = internal_available(self.platform,self.belong,self.get_next())
        placed = internal_possible_place(self.platform,self.belong, available)
        moved = internal_possible_move(placed)
        for operation in moved:
            moved[operation]=internal_value(moved[operation][0],moved[operation][1])
        max_value=-99999
        best_operation=None
        for operation in moved:
           if moved[operation]>maxvalue:
               best_operation=moved[operation]

        return best_operation
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
        if (row, column) != (None, None): self.platform[row][column] = 2

    def input_direction(self, direction):
        # 接受对方合并的方向
        if direction is not None:
            self.move(direction, False)

    def output_position(self, currentRound):
        # 给出己方下棋的位置
        self.currentRound = currentRound        
        return search(currentRound)[0]

    def output_direction(self, currentRound):
        # 给出己方合并的方向
        self.currentRound = currentRound
        return search(currentRound)[1]

    def show(self):
        # 打印棋盘, + 代表己方, - 代表对方
        platform = ''
        for row in range(4):
            for column in range(8):
                platform += ('+' if self.belong[row][column] else '-') + \
                            str(self.platform[row][column] if self.platform[row][column] != None else 0).zfill(4) + ' '
            platform += '\n'
        print(platform[:-1])
