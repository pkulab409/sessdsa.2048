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

time0 = 0  # player0已用时间
time1 = 0  # player1已用时间

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

class Player0:
    
    @timeManager(0)
    def init_process(self, array):
        pass
    
    @timeManager(0)
    def input_position(self, row, column):
        pass

    @timeManager(0)
    def input_direction(self, direction):
        pass
    
    @timeManager(0)
    def output_position(self):
        pass
    
    @timeManager(0)
    def output_direction(self):
        pass
    

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


# 对战平台

class Platform:
    
    def __init__(self, rounds, array, maxtime, player0, player1):
        '''
        -> rounds: 总回合数, 为一个正的int
        -> array: 随机序列, 为一个长度等于总回合数的list
        -> maxtime: 一方的总时间限制, 单位为s
        -> player1: 参赛队伍1, Player1对象
        -> player2: 参赛队伍2, Player2对象
        '''
        self.rounds = rounds                            # 总回合数
        self.array = array                              # 随机序列
        self.maxtime = maxtime                          # 总时间限制
        self.winner = None                              # 胜利者
        self.violator = None                            # 违规者
        self.timeout = None                             # 超时者
        self.end = None                                 # 终局者
        self.player = [player0, player1]                # 参赛AI
        self.position = [(None, None),(None, None)]     # 下棋位置
        self.direction = [None, None]                   # 合并方向
        self.currentRound = 0                           # 当前轮数
        self.change = False                             # 监控棋盘是否改变
        self.next = (None, None)                        # 按照随机序列得到的下一个位置
        self.record = [{'position':[], 'direction':[]}, {'position':[], 'direction':[]}]    # 记录决策
        self.belong = [[0 if _ <= 3 else 1 for _ in range(8)] for _ in range(4)]            # 记录领域信息
        self.platform = [[None for _ in range(8)] for _ in range(4)]                        # 记录棋子信息
        
    def game_start(self):
        self.player[0].init_process(self.array)
        self.player[1].init_process(self.array)
        # 载入随机序列
        
        for _ in range(self.rounds):
            self.currentRound = _                           # 记录当前轮数, 从0开始
            
            self.next = self.get_next(0)                    # 按照随机序列得到下一个位置
            self.player[0].input_direction(self.direction[1])
            self.position[0] = self.player[0].output_position()
            if self.checkTime(0): break                     # 判断是否超时
            if self.checkViolate(0, 'position'): break      # 判断是否违规
            self.update(0, 'position')                      # 更新棋盘 
            self.record[0]['position'].append(self.position[0])

            self.next = self.get_next(1)                    # 按照随机序列得到下一个位置
            self.player[1].input_position(*self.position[0])
            self.position[1] = self.player[1].output_position()
            if self.checkTime(1): break                     # 判断是否超时
            if self.checkViolate(1, 'position'): break      # 判断是否违规
            self.update(1, 'position')                      # 更新棋盘 
            self.record[1]['position'].append(self.position[1])
            
            self.player[0].input_position(*self.position[1])
            self.direction[0] = self.player[0].output_direction()
            if self.checkTime(0): break                     # 判断是否超时
            self.update(0, 'direction')                     # 更新棋盘
            if self.checkViolate(0, 'direction'): break     # 判断是否违规
            self.record[0]['direction'].append(self.direction[0])
            
            self.player[1].input_direction(self.direction[0])
            self.direction[1] = self.player[1].output_direction()
            if self.checkTime(1): break                     # 判断是否超时
            self.update(1, 'direction')                     # 更新棋盘
            if self.checkViolate(1, 'direction'): break     # 判断是否违规
            self.record[1]['direction'].append(self.direction[1])
            
            
            if self.checkEnd(): break      # 判断是否进入终局
            
        else:  # 总回合数耗尽
            self.scoring()      # 计分
            return

        self.comment()          # 得到winner
        self.go_on()            # 胜方继续游戏
        self.scoring()          # 计分

    def checkTime(self, playerNumber):
        if globals()['time%d' % playerNumber] >= self.maxtime:
            self.timeout = playerNumber
            return True
        else:
            return False

    def checkViolate(self, playerNumber, name):
        '''
        -> 违规有三种情形:
        -> 输出格式错误
        -> 选择的方格在可选范围之外
        -> 选择的方向使得合并前后棋盘没有变化
        '''
        if name == 'position':
            
            if not (isinstance(self.position[playerNumber], tuple) and len(self.position[playerNumber]) == 2):
                self.violator = playerNumber
                return True
            
            row, column = self.position[playerNumber]
            if row in range(4) and column in range(8) and self.platform[row][column] == None and \
                           (self.belong[row][column] == self.player[not playerNumber] or self.position[playerNumber] == self.next):
                return False
            else:
                self.violator = playerNumber
                return True

        else:
            if self.change:
                return False
            else:
                self.violator = playerNumber
                return True

    def update(self, playerNumber, name):
        '''
        -> 优化完毕, 但是验证起来有点费劲了
        -> 实在不行就逐情况验证吧
        '''
        def move(self, playerNumber):  # 合并, 同时返回棋盘是否改变
            
            change = False
            myPhase = [{'p1':'column', 'p2':'row', 'r1':range(8), 'r2':range(4), 'delta_c':0, 'delta_r':1},
                       {'p1':'column', 'p2':'row', 'r1':range(8), 'r2':reversed(range(4)), 'delta_c':0, 'delta_r':-1},
                       {'p1':'row', 'p2':'column', 'r1':range(8), 'r2':range(4), 'delta_c':1, 'delta_r':0},
                       {'p1':'row', 'p2':'column', 'r1':reversed(range(8)), 'r2':range(4), 'delta_c':-1, 'delta_r':0}
                      ][self.direction[playerNumber]]
             
            for locals()[myPhase['p1']] in myPhase['r1']:
                queue = []      # 用类队列实现合并
                count = 0       # 计数
                stable = []     # 遵循不可多次吃棋的规则
                for locals()[myPhase['p2']] in myPhase['r2']:
                    if self.belong[row][column] != playerNumber:  # 苟非吾之所有
                        while count > len(queue): queue.append(None)
                        queue.append(self.platform[row][column])
                    elif self.platform[row][column] != None:
                        if queue == []:
                            queue.append(self.platform[row][column])
                        elif queue[-1] == None:  # 越界填补空位
                            change = True
                            queue[-1] = self.platform[row][column]
                            self.belong[row-myPhase['delta_r']][column-myPhase['delta_c']] = playerNumber  # 修改领域归属
                        elif queue[-1] == self.platform[row][column] and len(queue) not in stable:  # 不可多次吃棋
                            change = True
                            queue[-1] = self.platform[row][column] * 2
                            self.belong[row-myPhase['delta_r']][column-myPhase['delta_c']] = playerNumber  # 修改领域归属
                            stable.append(len(queue))
                        else:
                            queue.append(self.platform[row][column])
                    count += 1
                    
                if change:
                    for locals()[myPhase['p2']] in myPhase['r2']:
                        self.platform[row][column] = queue.pop(0) if queue != [] else None  # 更新地图

     
        if name == 'position':
            self.platform[self.position[playerNumber][0]][self.position[playerNumber][1]] = 2
        else:
            self.change = move(self, playerNumber)

    def checkEnd(self):
        '''
        -> 终局条件:
        -> 某方可并范围中没有空方格且任一本方棋子都没有数值相等的相邻棋子
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
                    
        self.end = 0
        return True

    def comment(self):
        for _ in (self.timeout, self.violator, self.end):
            if _ != None:
                self.winner = 0 if _ == 1 else 1
                return

    def scoring(self):
        score0 = dict(zip([2**_ for _ in range(15)], [0 for _ in range(15)]))
        score1 = dict(zip([2**_ for _ in range(15)], [0 for _ in range(15)]))
        for column in range(8):
            for row in range(4):
                if self.belong[row][column] == 0 and self.platform[row][column] != None:
                    score0[self.platform[row][column]] += 1
                elif self.belong[row][column] == 1 and self.platform[row][column] != None:
                    score1[self.platform[row][column]] += 1
        # 获取所有棋子
        self.score = (score0, score1)
        print('score of player 0 is', score0)
        print('score of player 1 is', score1)
        
        for _ in reversed(range(15)):
            if score0[2**_] > score1[2**_] and self.winner == None:
                self.winner = 0
                break
            if score0[2**_] < score1[2**_] and self.winner == None:
                self.winner = 0
                break
        else:
            if self.winner == None: raise Exception('Tied')  # 平局

    def go_on(self):
        '''
        -> winner继续游戏
        '''
        pass
        
    def get_next(self, playerNumber):
        '''
        -> 根据随机序列得到在本方领域允许下棋的位置
        '''
        pass

    def review(self):
        '''
        -> 用于复盘
        -> 可以接上UI
        '''
        pass
        
            
if __name__ == '__main__':
    player0 = Player0()
    player1 = Player1()
    platform = Platform(3, None, 3, player0, player1)
    platform.game_start()
