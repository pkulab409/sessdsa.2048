# <!>--平台的pass部分待补充--<!>

# 对战平台接口
# 有bug可以找@SophieARG讨论

# 参赛队伍的AI请写在Player类里
# 须实现五个方法:
#
# init_process(self, array):
#   -> 接受随机序列
#   -> 参数: array随机序列, 为一个长度等于总回合数的list
#
# input_position(self, row, column):
#   -> 接受对方下棋的位置
#   -> 参数: row行, 从上到下为0到3的int; column列, 从左到右为0到7的int
#   -> 说明: row = None, column = None 表示第一轮先手
#
# input_direction(self, direction):
#   -> 接受对方合并的方向
#   -> 参数: direction = 0, 1, 2, 3 对应 上, 下, 左, 右
#   -> 说明: direction = None 表示第一轮先手
#
# output_position(self):
#   -> 给出己方下棋的位置
#   -> 返回: row行, 从上到下为0到3的int; column列, 从左到右为0到7的int
#
# output_direction(self):
#   -> 给出己方合并的方向
#   -> 返回: direction = 0, 1, 2, 3 对应 上, 下, 左, 右
#
# 其余的方法与属性请自行设计
# AI中不允许出现对全局变量time1和time2的手动修改, 因为这是作弊哦!

import time
import functools

time1 = 0  # player1已用时间
time2 = 0  # player2已用时间

def timeManager(playerNumber):  # 计算用时的装饰器
    def decorator(func):
        @functools.wraps(func)
        def wrappedFunc(*args, **kwargs):
            begin = time.time()
            func(*args, **kwargs)
            end = time.time()
            globals()['time%d' % playerNumber] += end - begin
        return wrappedFunc
    return decorator

# AI编写位置

class Player1:
    
    @timeManager(1)
    def init_process(self, array):
        pass
    
    @timeManager(1)
    def input_position(self, row, column):
        pass

    @timeManager(1)
    def input_direction(self, direction):
        pass
    
    @timeManager(1)
    def output_position(self):
        pass
    
    @timeManager(1)
    def output_direction(self):
        pass
    

class Player2:

    @timeManager(2)
    def init_process(self, array):
        pass

    @timeManager(2)
    def input_position(self, row, column):
        pass

    @timeManager(2)
    def input_direction(self, direction):
        pass
    
    @timeManager(2)
    def output_position(self):
        pass
    
    @timeManager(2)
    def output_direction(self):
        pass


# 对战平台

class Platform:
    
    def __init__(self, rounds, array, maxtime, player1, player2):
        '''
        -> rounds: 总回合数, 为一个正的int
        -> array: 随机序列, 为一个长度等于总回合数的list
        -> maxtime: 一方的总时间限制, 单位为s
        -> player1: 参赛队伍1, Player1对象
        -> player2: 参赛队伍2, Player2对象
        '''
        self.rounds = rounds            # 总回合数
        self.array = array              # 随机序列
        self.maxtime = maxtime          # 总时间限制
        self.winner = None              # 胜利者
        self.violator = None            # 违规者
        self.timeout = None             # 超时者
        self.end = None                 # 终局者
        self.player1 = player1          # player1
        self.player2 = player2          # player2
        self.position1 = (None, None)   # player1的下棋位置
        self.position2 = (None, None)   # player2的下棋位置
        self.direction1 = None          # player1的合并方向
        self.direction2 = None          # player2的合并方向
        self.currentRound = 0           # 当前轮数
        self.change = False             # 监控棋盘是否改变
        self.next = (None, None)        # 按照随机序列得到的下一个位置
        self.record1 = {'position':[], 'direction':[]}                            # 记录player1的决策
        self.record2 = {'position':[], 'direction':[]}                            # 记录player2的决策
        self.belong = [[1 if _ <= 3 else 2 for _ in range(8)] for _ in range(4)]  # 记录领域信息
        self.platform = [[None for _ in range(8)] for _ in range(4)]              # 记录棋子信息
        
    def game_start(self):
        self.player1.init_process(self.array)
        self.player2.init_process(self.array)
        # 载入随机序列
        
        for _ in range(self.rounds):
            self.currentRound = _   # 记录当前轮数, 从0开始
            
            self.player1.input_direction(self.direction2)
            self.position1 = self.player1.output_position()
            if self.checkTime(self.player1): break     # 判断是否超时
            if self.checkViolate(1): break             # 判断是否违规
            self.update(1)                             # 更新棋盘 
            self.record1['position'].append(self.position1)
            
            self.player2.input_position(*self.position1)
            self.position2 = self.player2.output_position()
            if self.checkTime(self.player2): break     # 判断是否超时
            if self.checkViolate(2): break             # 判断是否违规
            self.update(2)                             # 更新棋盘 
            self.record2['position'].append(self.position2)
            
            self.player1.input_position(*self.position2)
            self.direction1 = self.player1.output_direction()
            if self.checkTime(self.player1): break     # 判断是否超时
            self.update(3)                             # 更新棋盘
            if self.checkViolate(3): break             # 判断是否违规
            self.record1['direction'].append(self.direction1)
            
            self.player2.input_direction(self.direction1)
            self.derection2 = self.player2.output_direction()
            if self.checkTime(self.player2): break     # 判断是否超时
            self.update(4)                             # 更新棋盘
            if self.checkViolate(4): break             # 判断是否违规
            self.record2['direction'].append(self.direction2)
            
            
            if self.checkEnd(): break      # 判断是否进入终局
            
        else:  # 总回合数耗尽
            self.scoring()      # 计分
            return

        self.comment()          # 得到winner
        self.go_on()            # 胜方继续游戏
        self.scoring()          # 计分

    def checkTime(self, player):
        if (time1 if player == self.player1 else time2) >= self.maxtime:
            self.timeout = player
            return True
        else:
            return False

    def checkViolate(self, phase):
        '''
        -> 违规有三种情形:
        -> 输出格式错误
        -> 选择的方格在可选范围之外
        -> 选择的方向使得合并前后棋盘没有变化
        '''
        if phase == 1:
            self.next = self.get_next(self.player1)
            
            if not (isinstance(self.position1, tuple) and len(self.position1) == 2):
                self.violator = self.player1
                return True
            
            row, column = self.position1
            if row in range(4) and column in range(8) and self.platform[row][column] == None and \
                           (self.belong[row][column] == self.player2 or self.position1 == self.next):
                return False
            else:
                self.violator = self.player1
                return True
            
        elif phase == 2:
            self.next = self.get_next(self.player2)
            
            if not (isinstance(self.position2, tuple) and len(self.position2) == 2):
                self.violator = self.player2
                return True
            
            row, column = self.position2
            if row in range(4) and column in range(8) and self.platform[row][column] == None and \
                           (self.belong[row][column] == self.player1 or self.position2 == self.next):
                return False
            else:
                self.violator = self.player2
                return True

        elif phase == 3:
            if self.change:
                return False
            else:
                self.violator = self.player1
                return True

        else:
            if self.change:
                return False
            else:
                self.violator = self.player2
                return True

    def update(self, phase):
        '''
        -> 这里的实现有点长, 如果有优化之必要请动手
        -> 但是最好不要改变参数和返回值
        '''
        def move(self, player):  # 合并, 同时返回棋盘是否改变
            
            def is_mine(self, me):
                def func(row, column):
                    return self.belong[row][column] == me
                return func
            
            direction = self.direction1 if player == self.player1 else self.direction2
            me = 1 if player == self.player1 else 2
            is_mine = is_mine(self, me)  # 构建判断是否在本方领域的函数
            change = False
            
            if direction == 0:  # 向上
                for column in range(8):
                    stack = []  # 用类队列实现合并
                    for row in range(4):
                        if not is_mine:
                            while row > len(stack): stack.append(None)
                            stack.append(self.platform[row][column])
                        elif self.platform[row][column] != None:
                            if stack == []:
                                stack.append(self.platform[row][column])
                            elif stack[-1] == None:
                                change = True
                                stack[-1] = self.platform[row][column]
                                self.belong[row-1][column] = me  # 修改领域归属
                            elif stack[-1] == self.platform[row][column]:
                                change = True
                                stack[-1] = self.platform[row][column] * 2
                                self.belong[row-1][column] = me  # 修改领域归属
                            else:
                                stack.append(self.platform[row][column])
                    if change:
                        for row in range(4):
                            self.platform[row][column] = stack.pop(0) if stack != [] else None  # 更新地图
                            
            elif direction == 1:  # 向下
                for column in range(8):
                    stack = []  # 用类队列实现合并
                    for row in range(3, -1, -1):
                        if not is_mine:
                            while 3 - row > len(stack): stack.append(None)
                            stack.append(self.platform[row][column])
                        elif self.platform[row][column] != None:
                            if stack == []:
                                stack.append(self.platform[row][column])
                            elif stack[-1] == None:
                                change = True
                                stack[-1] = self.platform[row][column]
                                self.belong[row+1][column] = me  # 修改领域归属
                            elif stack[-1] == self.platform[row][column]:
                                change = True
                                stack[-1] = self.platform[row][column] * 2
                                self.belong[row+1][column] = me  # 修改领域归属
                            else:
                                stack.append(self.platform[row][column])
                    if change:
                        for row in range(3, -1, -1):
                            self.platform[row][column] = stack.pop(0) if stack != [] else None  # 更新地图
            
            elif direction == 2:  # 向左
                for row in range(4):
                    stack = []  # 用类队列实现合并
                    for column in range(8):
                        if not is_mine:
                            while column > len(stack): stack.append(None)
                            stack.append(self.platform[row][column])
                        elif self.platform[row][column] != None:
                            if stack == []:
                                stack.append(self.platform[row][column])
                            elif stack[-1] == None:
                                change = True
                                stack[-1] = self.platform[row][column]
                                self.belong[row][column-1] = me  # 修改领域归属
                            elif stack[-1] == self.platform[row][column]:
                                change = True
                                stack[-1] = self.platform[row][column] * 2
                                self.belong[row][column-1] = me  # 修改领域归属
                            else:
                                stack.append(self.platform[row][column])
                    if change:
                        for column in range(8):
                            self.platform[row][column] = stack.pop(0) if stack != [] else None  # 更新地图
                            
            else:  # 向右
                for row in range(4):
                    stack = []  # 用类队列实现合并
                    for column in range(7, -1, -1):
                        if not is_mine:
                            while 7 - column > len(stack): stack.append(None)
                            stack.append(self.platform[row][column])
                        elif self.platform[row][column] != None:
                            if stack == []:
                                stack.append(self.platform[row][column])
                            elif stack[-1] == None:
                                change = True
                                stack[-1] = self.platform[row][column]
                                self.belong[row][column+1] = me  # 修改领域归属
                            elif stack[-1] == self.platform[row][column]:
                                change = True
                                stack[-1] = self.platform[row][column] * 2
                                self.belong[row][column+1] = me  # 修改领域归属
                            else:
                                stack.append(self.platform[row][column])
                    if change:
                        for column in range(7, -1, -1):
                            self.platform[row][column] = stack.pop(0) if stack != [] else None  # 更新地图
            return change
     
        if phase == 1:
            self.platform[self.position1[0]][self.position1[1]] = 2
        elif phase == 2:
            self.platform[self.position2[0]][self.position2[1]] = 2
        elif phase == 3:
            self.change = move(self, self.player1)
        else:
            self.change = move(self, self.player2)

    def checkEnd(self):
        '''
        -> 终局条件:
        -> 某方领域中不存在空格且该方任意棋子均不存在数值相等的相邻棋子
        -> 只有先手才有可能在此时终局
        '''
        for row in range(4):
            for column in range(7):
                if self.belong[row][column] == 1 or self.belong[row][column+1] == 1:
                    if self.platform[row][column] == self.platform[row][column+1] \
                               or self.platform[row][column] == None or self.platform[row][column+1] == None:
                        return False
                    
        for column in range(8):
            for row in range(3):
                if self.belong[row][column] == 1 or self.belong[row+1][column] == 1:
                    if self.platform[row][column] == self.platform[row+1][column] \
                               or self.platform[row][column] == None or self.platform[row+1][column] == None:
                        return False
                    
        self.end = self.player1
        return True

    def comment(self):
        for _ in (self.timeout, self.violator, self.end):
            if _ != None:
                self.winner = self.player1 if _ == self.player2 else self.player2
                return

    def scoring(self):
        score1 = dict(zip([2**_ for _ in range(15)], [0 for _ in range(15)]))
        score2 = dict(zip([2**_ for _ in range(15)], [0 for _ in range(15)]))
        for column in range(8):
            for row in range(4):
                if self.belong[row][column] == 1 and self.platform[row][column] != None:
                    score1[self.platform[row][column]] += 1
                elif self.belong[row][column] == 2 and self.platform[row][column] != None:
                    score2[self.platform[row][column]] += 1
        # 获取所有棋子
        self.score1 = score1
        self.score2 = score2
        print('score of player 1 is', score1)
        print('score of player 2 is', score2)
        for _ in range(14, -1, -1):
            if score1[2**_] > score2[2**_] and self.winner == None:
                self.winner = self.player1
                break
            if score1[2**_] < score2[2**_] and self.winner == None:
                self.winner = self.player2
                break
        else:
            raise Exception('Tied')

    def go_on(self):
        '''
        -> winner继续游戏
        '''
        pass
        
    def get_next(self, player):
        '''
        -> 根据随机序列得到在本方领域允许的地方
        '''
        pass

    def review(self):
        '''
        -> 用于复盘
        -> 可以接上UI
        -> 先pass了
        '''
        pass
        
            
if __name__ == '__main__':
    player1 = Player1()
    player2 = Player2()
    platform = Platform(3, None, 3, player1, player2)
    platform.game_start()
    
