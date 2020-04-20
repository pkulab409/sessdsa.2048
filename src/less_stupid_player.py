# 基于单层搜索的模版AI

class Player:
    def __init__(self, isFirst):
        # 初始化
        self.array = None
        self.platform = [[None for _ in range(8)] for _ in range(4)]
        self.belong = [[isFirst if _ <= 3 else not isFirst for _ in range(8)] for _ in range(4)]
        self.currentRound = 0
        self.isFirst=isFirst
    
    def search_position(self, currentround):
        #按照当前盘面进行所有可能操作的搜索和价值判断,给出放置位置
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
                    platform[myDict['row']][myDict['column']] = queue.pop(0) if queue != [] else None

            return platform,belong,change

        def internal_possible_place(platform, belong, another, isFirst,array,currentRound):
            #计算所有放置情况的盘面结果
            if isFirst:
                outcomes={}
                available1 = []
                for row in range(4):
                    for column in range(8):
                        if not belong[row][column] and platform[row][column] == None:
                            available1.append((row, column))
                if another!=None:
                    available1.append(another)
                for position1 in available1:
                    available2 = []
                    for row in range(4):
                        for column in range(8):
                            if belong[row][column] and platform[row][column] == None and (row,column)!=position1:
                                available2.append((row, column))
                    available_enemy = []
                    for row in range(4):
                        for column in range(8):
                            if not belong[row][column] and platform[row][column] == None and (row,column)!=position1:
                                available_enemy.append((row, column))
                    if available_enemy == []:
                        pass
                    else:
                        enemy_next=available_enemy[array[currentRound] % len(available_enemy)]
                        available2.append(enemy_next)
                    for position2 in available2:
                        outcomes[(position1,position2)]=[internal_deepcopy(platform),internal_deepcopy(belong)]
                        outcomes[(position1,position2)][0][position1[0]][position1[1]]=2
                        outcomes[(position1,position2)][0][position2[0]][position2[1]]=2
                return outcomes
            else:    
                available = []
                for row in range(4):
                    for column in range(8):
                        if not belong[row][column] and platform[row][column] == None:
                            available.append((row, column))
                if another!=None:
                    available.append(another)
                outcomes={}
                for i in available:
                    outcomes[(i,1)]=[internal_deepcopy(platform),internal_deepcopy(belong)]
                    outcomes[(i,1)][0][i[0]][i[1]]=2
                return outcomes

        def internal_possible_move(placed,isFirst):
            #对于所有放置之后的结果计算移动之后的结果
            moved={}
            if isFirst:
                for position in placed:
                    for direction in range(4):
                        platform=internal_deepcopy(placed[position][0])
                        belong=internal_deepcopy(placed[position][1])
                        platform,belong,change=internal_move(platform,belong, direction, True)
                        if change:
                            moved[(position,direction)]=[platform,belong]
                return moved
            else:
                for position in placed:
                    for direction1 in range(4):
                        platform1=internal_deepcopy(placed[position][0])
                        belong1=internal_deepcopy(placed[position][1])
                        platform1,belong1,change1=internal_move(platform1,belong1, direction1, False)
                        if change1:
                            for direction2 in range(4):
                                platform2=internal_deepcopy(platform1)
                                belong2=internal_deepcopy(belong1)
                                platform2,belong2,change2=internal_move(platform2,belong2, direction2, True)
                                if change2:    
                                    moved[(position,direction1,direction2)]=[platform2,belong2]
                return moved
        another=self.get_next()
        placed= internal_possible_place(self.platform,self.belong,another,self.isFirst,self.array,currentround)
        moved = internal_possible_move(placed,self.isFirst)
        for operation in moved:
            moved[operation]=internal_value(moved[operation][0],moved[operation][1])

        available = []
        for row in range(4):
            for column in range(8):
                if not self.belong[row][column] and self.platform[row][column] == None:
                     available.append((row, column))
        available.append(self.get_next)        

        values={}
        for operation in moved:
            values[operation[0][0]]=[0,0]
        for operation in moved:
            values[operation[0][0]][0]+=moved[operation]
            values[operation[0][0]][1]+=1
        for position in values:
            values[position]=float(values[position][0])/values[position][1]

        best_position=None
        max_value=-99999
        for position in values:
           if values[position]>max_value:
               best_position=position

        return best_position
    def search_direction(self,currentround):
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
                    platform[myDict['row']][myDict['column']] = queue.pop(0) if queue != [] else None

            return platform,belong,change

        def internal_possible_move(platform,belong):
            #对于现有盘面计算可能移动之后的结果
            moved={}
            for direction1 in range(4):
                platform1=internal_deepcopy(platform)
                belong1=internal_deepcopy(belong)
                platform1,belong1,change=internal_move(platform1,belong1, direction1,True)
                if change:
                    moved[direction1]=[platform1,belong1]

            return moved
           
        moved=internal_possible_move(self.platform,self.belong)
        values={}
        for move in moved:
            moved[move]=internal_value(moved[move][0],moved[move][1])
        for move in moved:
            values[move]=[0,0]
        for move in moved:
            values[move][0]+=moved[move]
            values[move][1]+=1
        for direction in values:
            values[direction]=float(values[direction][0])/values[direction][1]
        best_direction=None
        max_value=-99999
        for direction in values:
            if values[direction]>max_value:
               best_direction=direction
        return best_direction
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
        position=self.search_position(currentRound)
        if position!=None:
            row, column = position
            self.platform[row][column] = 2
        return position

    def output_direction(self, currentRound):
        # 给出己方合并的方向
        self.currentRound = currentRound
        direction=self.search_direction(currentRound)
        if direction!=None:    
            self.move(direction,True)
        return direction

    def show(self):
        # 打印棋盘, + 代表己方, - 代表对方
        platform = ''
        for row in range(4):
            for column in range(8):
                platform += ('+' if self.belong[row][column] else '-') + \
                            str(self.platform[row][column] if self.platform[row][column] != None else 0).zfill(4) + ' '
            platform += '\n'
        print(platform[:-1])
