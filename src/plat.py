# 对战平台接口
# 有bug可以找@SophieARG讨论

from player import Player as Player0  # 先手
from player import Player as Player1  # 后手
import constants as c                 # 游戏常数

import time
import functools

def timeManager(playerNumber):  # 计算用时的装饰器
    def decorator(func):
        @functools.wraps(func)
        def wrappedFunc(*args, **kwargs):
            begin = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            globals()['time%d' % playerNumber] += end - begin
            return result
        return wrappedFunc
    return decorator

time0 = 0  # player0已用时间
time1 = 0  # player1已用时间

# 重载方法, 加上计时功能
Player0.init_process = timeManager(0)(Player0.init_process)
Player0.input_position = timeManager(0)(Player0.input_position)
Player0.input_direction = timeManager(0)(Player0.input_direction)
Player0.output_position = timeManager(0)(Player0.output_position)
Player0.output_direction = timeManager(0)(Player0.output_direction)
        
Player1.init_process = timeManager(1)(Player1.init_process)
Player1.input_position = timeManager(1)(Player1.input_position)
Player1.input_direction = timeManager(1)(Player1.input_direction)
Player1.output_position = timeManager(1)(Player1.output_position)
Player1.output_direction = timeManager(1)(Player1.output_direction)

# 对战平台

class Platform:
    
    def __init__(self, player0, player1):
        '''
        初始化, player0 和 player1 为两个参赛AI
        '''
        self.rounds = c.ROUNDS                          # 总回合数
        self.array = c.ARRAY                            # 随机序列
        self.maxtime = c.MAXTIME                        # 总时间限制
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
        self.log = []                                   # 日志, &d 决策 decision, &p 棋盘 platform, &e 事件 event
        self.belong = c.INIT_BELONG                     # 记录领域信息
        self.platform = c.INIT_PLATFORM                 # 记录棋子信息
        
    def game_start(self):
        self.player[0].init_process(self.array)
        self.player[1].init_process(self.array)
        # 载入随机序列
        
        for _ in range(self.rounds):
            self.currentRound = _                           # 记录当前轮数, 从0开始
            
            self.next = self.get_next(0)                    # 按照随机序列得到下一个位置
            self.player[0].input_direction(self.direction[1])
            self.position[0] = self.player[0].output_position(_)
            if self.checkTime(0): break                     # 判断是否超时
            self.log.append('&d%d:player 0 set position %s' % (_, str(self.position[0])))
            if self.checkViolate(0, 'position'): break      # 判断是否违规
            self.update(0, 'position')                      # 更新棋盘 
            self.log.append('&p%d:\n' % _ + self.__repr__())
            
            self.next = self.get_next(1)                    # 按照随机序列得到下一个位置
            self.player[1].input_position(*self.position[0])
            self.position[1] = self.player[1].output_position(_)
            if self.checkTime(1): break                     # 判断是否超时
            self.log.append('&d%d:player 1 set position %s' % (_, str(self.position[1])))
            if self.checkViolate(1, 'position'): break      # 判断是否违规
            self.update(1, 'position')                      # 更新棋盘 
            self.log.append('&p%d:\n' % _ + self.__repr__())
            
            self.player[0].input_position(*self.position[1])
            self.direction[0] = self.player[0].output_direction(_)
            if self.checkTime(0): break                     # 判断是否超时
            self.log.append('&d%d:player 0 set direction %s' % (_, c.DIRECTIONS[self.direction[0]]))
            self.update(0, 'direction')                     # 更新棋盘
            if self.checkViolate(0, 'direction'): break     # 判断是否违规
            self.log.append('&p%d:\n' % _ + self.__repr__())
            
            self.player[1].input_direction(self.direction[0])
            self.direction[1] = self.player[1].output_direction(_)
            if self.checkTime(1): break                     # 判断是否超时
            self.log.append('&d%d:player 1 set direction %s' % (_, c.DIRECTIONS[self.direction[1]]))
            self.update(1, 'direction')                     # 更新棋盘
            if self.checkViolate(1, 'direction'): break     # 判断是否违规
            self.log.append('&p%d:\n' % _ + self.__repr__())
            
            if self.checkEnd(): break      # 判断是否进入终局
            
        else:  # 总回合数耗尽
            self.scoring()      # 计分
            return
        
        self.comment()          # 得到winner
        self.go_on()            # 胜方继续游戏
        self.scoring()          # 计分

    def checkTime(self, playerNumber):
        if globals()['time%d' % playerNumber] >= self.maxtime:
            if self.winner == None:
                self.log.append('&e:player %d time out' % playerNumber)
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
                if self.winner == None:
                    self.log.append('&e:player %d violate by illegal output of position' % playerNumber)
                    self.violator = playerNumber
                return True
            
            row, column = self.position[playerNumber]
            if row in range(c.ROWS) and column in range(c.COLUMNS) and self.platform[row][column] == 0 and \
                           (self.belong[row][column] == 1 - playerNumber or self.position[playerNumber] == self.next):
                return False
            else:
                if self.winner == None:
                    self.log.append('&e:player %d violate by not achievable position' % playerNumber)
                    self.violator = playerNumber
                return True

        else:
            if self.direction[playerNumber] not in range(4):
                self.log.append('&e:player %d violate by illegal output of direction' % playerNumber)
                self.violator = playerNumber
                return True
            elif self.change:
                return False
            else:
                if self.winner == None:
                    self.log.append('&e:player %d violate by not achievable direction' % playerNumber)
                    self.violator = playerNumber
                return True
            self.change = False

    def update(self, playerNumber, name):
        '''
        -> 优化完毕, 但是验证起来有点费劲了
        -> 实在不行就逐情况验证吧
        '''
        def move(self, playerNumber):  # 合并, 同时返回棋盘是否改变
            
            myPhase = [{'p1':'column', 'p2':'row', 'r1':range(c.COLUMNS), 'r2':range(c.ROWS)},
                       {'p1':'column', 'p2':'row', 'r1':range(c.COLUMNS), 'r2':range(c.ROWS - 1, -1, -1)},
                       {'p1':'row', 'p2':'column', 'r1':range(c.ROWS), 'r2':range(c.COLUMNS)},
                       {'p1':'row', 'p2':'column', 'r1':range(c.ROWS), 'r2':range(c.COLUMNS - 1, -1, -1)}
                      ][self.direction[playerNumber]]
            
            change = False
            myDict = {}  # 变量字典
            for myDict[myPhase['p1']] in myPhase['r1']:
                queue = []                  # 用类队列实现合并
                position = (None, None)     # 队尾的位置
                count = 0                   # 计数
                stable = []                 # 遵循不可多次吃棋的规则
                exist = False               # 存在空方格
                for myDict[myPhase['p2']] in myPhase['r2']:
                    if self.belong[myDict['row']][myDict['column']] != playerNumber:  # 苟非吾之所有
                        while count > len(queue): queue.append(0)
                        queue.append(self.platform[myDict['row']][myDict['column']])
                        position = (myDict['row'], myDict['column'])
                        exist = False
                    elif self.platform[myDict['row']][myDict['column']] != 0:
                        if queue == []:
                            queue.append(self.platform[myDict['row']][myDict['column']])
                            position = (myDict['row'], myDict['column'])
                            if exist: change = True
                        elif queue[-1] == 0:  # 越界填补空位
                            queue[-1] = self.platform[myDict['row']][myDict['column']]
                            self.belong[position[0]][position[1]] = playerNumber  # 修改领域归属
                            change = True
                        elif queue[-1] == self.platform[myDict['row']][myDict['column']] and position not in stable:  # 不可多次吃棋
                            queue[-1] = self.platform[myDict['row']][myDict['column']] + 1
                            self.belong[position[0]][position[1]] = playerNumber  # 修改领域归属
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
                    self.platform[myDict['row']][myDict['column']] = queue.pop(0) if queue != [] else 0  # 更新地图
                    
            return change
        
        if name == 'position':
            self.platform[self.position[playerNumber][0]][self.position[playerNumber][1]] = 1
        else:
            if self.direction[playerNumber] in range(4):
                self.change = move(self, playerNumber)

    def checkEnd(self):
        '''
        -> 终局条件:
        -> 某方可并范围中没有空方格且任一本方棋子都没有数值相等的相邻棋子
        -> 只有先手才有可能在此时终局
        '''
        for row in range(c.ROWS):
            for column in range(c.COLUMNS - 1):
                if self.belong[row][column] == 0 or self.belong[row][column+1] == 0:
                    if self.platform[row][column] == self.platform[row][column+1] \
                               or self.platform[row][column] == 0 or self.platform[row][column+1] == 0:
                        return False
                    
        for column in range(c.COLUMNS):
            for row in range(c.ROWS - 1):
                if self.belong[row][column] == 0 or self.belong[row+1][column] == 0:
                    if self.platform[row][column] == self.platform[row+1][column] \
                               or self.platform[row][column] == 0 or self.platform[row+1][column] == 0:
                        return False
                    
        self.log.append('&e:player 0 end')
        self.end = 0
        return True

    def comment(self):
        for _ in (self.timeout, self.violator, self.end):
            if _ != None:
                self.winner = 0 if _ == 1 else 1
                self.log.append('&e:player %d win' % self.winner)
                return

    def scoring(self):
        score0 = dict(zip(range(c.MAXLEVEL), [0 for _ in range(c.MAXLEVEL)]))
        score1 = dict(zip(range(c.MAXLEVEL), [0 for _ in range(c.MAXLEVEL)]))
        for column in range(c.COLUMNS):
            for row in range(c.ROWS):
                if self.belong[row][column] == 0:
                    score0[self.platform[row][column]] += 1
                elif self.belong[row][column] == 1:
                    score1[self.platform[row][column]] += 1
        # 获取所有棋子
        self.score = (score0, score1)
        if self.winner == None:
            for _ in reversed(range(c.MAXLEVEL)):
                self.log.append('&e:check level %d' % _)
                if score0[_] > score1[_]:
                    self.winner = 0
                    self.log.append('&e:player 0 win by level %d (%d to %d)' % (_, score0[_], score1[_]))
                    break
                if score0[_] < score1[_]:
                    self.winner = 1
                    self.log.append('&e:player 1 win by level %d (%d to %d)' % (_, score1[_], score0[_]))
                    break
                self.log.append('&e:level %d tied by %d' % (_, score0[_]))
            else:
                if self.winner == None:
                    self.log.append('&e:tied')
                    raise Exception('Tied')  # 平局

    def go_on(self):
        '''
        -> winner继续游戏
        '''
        self.log.append('&e:winner going on...')
        for _ in range(self.currentRound + 1, self.rounds):
            self.currentRound = _
            
            self.next = self.get_next(self.winner)                    # 按照随机序列得到下一个位置
            self.player[self.winner].input_direction(None)
            self.position[self.winner] = self.player[self.winner].output_position(_)
            if self.checkTime(self.winner): break                     # 判断是否超时
            self.log.append('&d%d:player %d set position %s' % (_, self.winner, str(self.position[self.winner])))
            if self.checkViolate(self.winner, 'position'): break      # 判断是否违规
            self.update(self.winner, 'position')                      # 更新棋盘 
            self.log.append('&p%d:\n' % _ + self.__repr__())

            self.player[self.winner].input_position(None, None)
            self.direction[self.winner] = self.player[self.winner].output_direction(_)
            if self.checkTime(self.winner): break                     # 判断是否超时
            self.log.append('&d%d:player %d set direction %s' % (_, self.winner, c.DIRECTIONS[self.direction[self.winner]]))
            self.update(self.winner, 'direction')                     # 更新棋盘
            if self.checkViolate(self.winner, 'direction'): break     # 判断是否违规
            self.log.append('&p%d:\n' % _ + self.__repr__())
        self.log.append('&e:winner ending...')

    def get_next(self, playerNumber):
        '''
        -> 根据随机序列得到在本方领域允许下棋的位置
        -> 样例算法:
        -> 按照行列获得己方全部可放置位置, 通过对随机数求余数的方法得到结果
        '''
        available = []
        for row in range(c.ROWS):
            for column in range(c.COLUMNS):
                if self.belong[row][column] == playerNumber and self.platform[row][column] == 0:
                    available.append((row, column))
        if available == []:
            return None
        else:
            return available[self.array[self.currentRound] % len(available)]
                    
    def review(self):
        '''
        -> 用于复盘
        '''
        while True:
            choice = input('for complete record...(y/n): ')
            if choice == 'y':
                print('\n'.join(self.log))
                break
            elif choice == 'n':
                break
            
        print('=' * 50)    
        print('total rounds are', self.currentRound + 1)
        print('score of player 0 is', self.score[0])
        print('score of player 1 is', self.score[1])
        print('time of player 0 is', time0)
        print('time of player 1 is', time1)
        
        if self.timeout != None: print('player', self.timeout, 'time out')
        elif self.violator != None: print('player', self.violator, 'violate')
        elif self.end != None: print('player', self.end, 'end')
        print('player', self.winner, 'win')
        print('=' * 50)
        
        while True:
            choice = input('save record...(y/n): ')
            if choice == 'y':
                self.savelog()
                break
            elif choice == 'n':
                break

    def __str__(self):
        # 打印棋盘, + 代表先手, - 代表后手
        platform = ''
        for row in range(c.ROWS):
            for column in range(c.COLUMNS):
                platform += ('+' if self.belong[row][column] == 0 else '-') + str(self.platform[row][column]).zfill(2) + ' '
            platform += '\n'
        return platform[:-1]
    __repr__ = __str__

    def savelog(self):
        '''
        -> 保存对局信息
        -> 保存的信息可以用analyser.py解析
        '''
        filename = input('filename: ')
        file = open('%s.txt' % filename,'w')
        myDict = {0:'player 0', 1:'player 1', None:'None'}  # 协助转换为字符串
        title = 'name: %s\n' % filename + \
                'time: %s\n' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + \
                '{:*^45s}\n'.format('basic record')
        file.write(title)
        file.write('=' * 45 + '\n|{:^10s}|{:^10s}|{:^10s}|{:^10s}|\n'.format('timeout', 'violator', 'end', 'winner') + \
                   '-' * 45 + '\n|{:^10s}|{:^10s}|{:^10s}|{:^10s}|\n'.format(myDict[self.timeout], myDict[self.violator], myDict[self.end], myDict[self.winner]) + \
                   '=' * 45 + '\n')
        file.write('=' * 64 + '\n|%6s|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|\n' % ('player', *range(14)) + \
                   '-' * 64 + '\n|%6d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|\n' % (0, *self.score[0].values()) + \
                   '-' * 64 + '\n|%6d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|\n' % (1, *self.score[1].values()) + \
                   '=' * 64 + '\n')
        file.flush()
        file.write('{:*^45s}\n'.format('complete record'))
        for log in self.log:
            file.write(log + '\n')  # '&'表示一条log的开始
            file.flush()
        file.close()

        
if __name__ == '__main__':
    # 开始游戏
    player0 = Player0(True)
    player1 = Player1(False)
    platform = Platform(player0, player1)
    platform.game_start()
    platform.review()
