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
Player0.__init__ = timeManager(0)(Player0.__init__)
Player0.output = timeManager(0)(Player0.output)        
Player1.__init__ = timeManager(1)(Player1.__init__)
Player1.output = timeManager(1)(Player1.output)


# 平台

class Platform:
    
    def __init__(self, player0, player1):
        '''
        初始化, player0 和 player1 为两个参赛AI
        '''
        self.rounds = c.ROUNDS              # 总回合数
        self.maxtime = c.MAXTIME            # 总时间限制
        self.winner = None                  # 胜利者
        self.violator = None                # 违规者
        self.timeout = None                 # 超时者
        self.player = [player0, player1]    # 参赛AI
        self.currentRound = 0               # 当前轮数
        self.change = False                 # 监控棋盘是否改变
        self.next = (None, None)            # 按照随机序列得到的下一个位置
        self.log = []                       # 日志, &d 决策 decision, &p 棋盘 platform, &e 事件 event
        self.board = c.Chessboard(c.ARRAY)  # 棋盘
        
    def game_start(self):
        
        for _ in range(self.rounds):
            self.currentRound = _                                   # 记录当前轮数, 从0开始
            
            self.next = self.board.getNext(True, _)                 # 按照随机序列得到下一个位置
            position = self.player[0].output(_, self.board.copy(), 'position')
            if self.checkTime(0): break                             # 判断是否超时
            self.log.append('&d%d:player 0 set position %s' % (_, str(position)))
            if self.checkViolate(0, 'position', position): break    # 判断是否违规
            self.board.add(True, position)                          # 更新棋盘 
            self.log.append('&p%d:\n' % _ + self.board.__repr__())
            
            self.next = self.board.getNext(False, _)                # 按照随机序列得到下一个位置
            position = self.player[1].output(_, self.board.copy(), 'position')
            if self.checkTime(1): break                             # 判断是否超时
            self.log.append('&d%d:player 1 set position %s' % (_, str(position)))
            if self.checkViolate(1, 'position', position): break    # 判断是否违规
            self.board.add(False, position)                         # 更新棋盘
            self.log.append('&p%d:\n' % _ + self.board.__repr__())
            
            direction = self.player[0].output(_, self.board.copy(), 'direction')
            if self.checkTime(0): break                             # 判断是否超时
            self.log.append('&d%d:player 0 set direction %s' % (_, c.DIRECTIONS[direction]))
            self.change = self.board.move(True, direction)          # 更新棋盘
            if self.checkViolate(0, 'direction', direction): break  # 判断是否违规
            self.log.append('&p%d:\n' % _ + self.board.__repr__())
            
            direction = self.player[1].output(_, self.board.copy(), 'direction')
            if self.checkTime(1): break                             # 判断是否超时
            self.log.append('&d%d:player 1 set direction %s' % (_, c.DIRECTIONS[direction]))
            self.change = self.board.move(False, direction)         # 更新棋盘
            if self.checkViolate(1, 'direction', direction): break  # 判断是否违规
            self.log.append('&p%d:\n' % _ + self.board.__repr__())
            
        else:  # 总回合数耗尽
            self.scoring()      # 计分
            return
        
        self.comment()          # 得到winner
        self.go_on()            # 胜方继续游戏
        self.scoring()          # 计分

    def checkTime(self, playerNumber):
        if globals()['time%d' % playerNumber] >= self.maxtime:
            self.log.append('&e:player %d time out' % playerNumber)
            if self.winner == None: self.timeout = playerNumber
            return True
        else:
            return False

    def checkViolate(self, playerNumber, name, value):
        '''
        -> 违规有三种情形:
        -> 输出格式错误
        -> 选择的方格在可选范围之外
        -> 选择的方向使得合并前后棋盘没有变化
        '''
        if name == 'position':
            
            if not (isinstance(value, tuple) and len(value) == 2 and value[0] in range(c.ROWS) and value[1] in range(c.COLUMNS)):
                self.log.append('&e:player %d violate by illegal output of position' % playerNumber)
                if self.winner == None: self.violator = playerNumber
                return True
            
            if self.board.getValue(value) == 0 and (self.board.getBelong(value) == playerNumber or value == self.next):
                return False
            else:
                self.log.append('&e:player %d violate by not achievable position' % playerNumber)
                if self.winner == None: self.violator = playerNumber
                return True

        else:
            if value not in range(4):
                self.log.append('&e:player %d violate by illegal output of direction' % playerNumber)
                if self.winner == None: self.violator = playerNumber
                return True
            elif self.change:
                return False
            else:
                self.log.append('&e:player %d violate by not achievable direction' % playerNumber)
                if self.winner == None: self.violator = playerNumber
                return True
            self.change = False

    def comment(self):
        for _ in (self.timeout, self.violator):
            if _ != None:
                self.winner = 0 if _ == 1 else 1
                self.log.append('&e:player %d win' % self.winner)
                return

    def scoring(self):
        result0 = self.board.getScore(True)
        result1 = self.board.getScore(False)
        score0 = {}
        score1 = {}
        for level in range(1, c.MAXLEVEL):
            score0[level] = result0.count(level)
            score1[level] = result1.count(level)
        # 获取所有棋子并计数
        
        self.score = (score0, score1)
        if self.winner == None:
            for _ in reversed(range(1, c.MAXLEVEL)):
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
            
            self.next = self.board.getNext(self.winner == 0, _)               # 按照随机序列得到下一个位置
            position = self.player[self.winner].output(_, self.board.copy(), 'position')
            if self.checkTime(self.winner): break                             # 判断是否超时
            self.log.append('&d%d:player %d set position %s' % (_, self.winner, str(position)))
            if self.checkViolate(self.winner, 'position', position): break    # 判断是否违规
            self.board.add(self.winner == 0, position)                        # 更新棋盘 
            self.log.append('&p%d:\n' % _ + self.board.__repr__())

            direction = self.player[self.winner].output(_, self.board.copy(), 'direction')
            if self.checkTime(self.winner): break                             # 判断是否超时
            self.log.append('&d%d:player %d set direction %s' % (_, self.winner, c.DIRECTIONS[direction]))
            self.change = self.board.move(self.winner == 0, direction)        # 更新棋盘
            if self.checkViolate(self.winner, 'direction', direction): break  # 判断是否违规
            self.log.append('&p%d:\n' % _ + self.board.__repr__())
        self.log.append('&e:winner ending...')

                    
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
        print('player', self.winner, 'win')
        print('=' * 50)
        
        while True:
            choice = input('save record...(y/n): ')
            if choice == 'y':
                self.savelog()
                break
            elif choice == 'n':
                break

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
        file.write('=' * 34 + '\n|{:^10s}|{:^10s}|{:^10s}|\n'.format('timeout', 'violator', 'winner') + \
                   '-' * 34 + '\n|{:^10s}|{:^10s}|{:^10s}|\n'.format(myDict[self.timeout], myDict[self.violator], myDict[self.winner]) + \
                   '=' * 34 + '\n')
        file.write('=' * 60 + '\n|%6s|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|\n' % ('player', *range(1, c.MAXLEVEL)) + \
                   '-' * 60 + '\n|%6d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|\n' % (0, *self.score[0].values()) + \
                   '-' * 60 + '\n|%6d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|\n' % (1, *self.score[1].values()) + \
                   '=' * 60 + '\n')
        file.flush()
        file.write('{:*^45s}\n'.format('complete record'))
        for log in self.log:
            file.write(log + '\n')  # '&'表示一条log的开始
            file.flush()
        file.close()

        
if __name__ == '__main__':
    # 开始游戏
    player0 = Player0(True, c.ARRAY)
    player1 = Player1(False, c.ARRAY)
    platform = Platform(player0, player1)
    platform.game_start()
    platform.review()
