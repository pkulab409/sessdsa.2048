# 用于对接前端的对战平台接口
# 有bug可以找@SophieARG讨论

import constants as c  # 导入游戏常数
import time

# 平台

class Platform:
    def __init__(self, states):
        '''
        初始化, player0 和 player1 为两个参赛AI
        '''
        self.rounds = c.ROUNDS              # 总回合数
        self.maxtime = c.MAXTIME            # 总时间限制
        self.winner = None                  # 胜利者
        self.violator = None                # 违规者
        self.timeout = None                 # 超时者
        self.error = None                   # 运行出错者
        self.currentRound = 0               # 当前轮数
        self.change = False                 # 监控棋盘是否改变
        self.next = (None, None)            # 按照随机序列得到的下一个位置
        self.log = []                       # 日志, &d 决策 decision, &p 棋盘 platform, &e 事件 event
        self.board = c.Chessboard(c.ARRAY)  # 棋盘
        self.states = states                # 参赛AI运行状态
        
    def play(self):
        for _ in range(self.rounds):
            self.currentRound = _                                      # 记录当前轮数, 从0开始
            
            self.next = self.board.getNext(True, _)                    # 按照随机序列得到下一个位置
            position = self.states[True]['player'].output(_, self.board.copy(), 'position')
            if self.checkState(True): break                            # 判断运行状态
            self.log.append('&d%d:player 0 set position %s' % (_, str(position)))
            if self.checkViolate(True, 'position', position): break    # 判断是否违规
            self.board.add(True, position)                             # 更新棋盘 
            self.log.append('&p%d:\n' % _ + self.board.__repr__())
            
            self.next = self.board.getNext(False, _)                   # 按照随机序列得到下一个位置
            position = self.states[False]['player'].output(_, self.board.copy(), 'position')
            if self.checkState(False): break                           # 判断运行状态
            self.log.append('&d%d:player 1 set position %s' % (_, str(position)))
            if self.checkViolate(False, 'position', position): break   # 判断是否违规
            self.board.add(False, position)                            # 更新棋盘
            self.log.append('&p%d:\n' % _ + self.board.__repr__())
            
            direction = self.states[True]['player'].output(_, self.board.copy(), 'direction')
            if self.checkState(True): break                            # 判断运行状态
            self.log.append('&d%d:player 0 set direction %s' % (_, c.DIRECTIONS[direction]))
            self.change = self.board.move(True, direction)             # 更新棋盘
            if self.checkViolate(True, 'direction', direction): break  # 判断是否违规
            self.log.append('&p%d:\n' % _ + self.board.__repr__())
            
            direction = self.states[False]['player'].output(_, self.board.copy(), 'direction')
            if self.checkState(False): break                           # 判断运行状态
            self.log.append('&d%d:player 1 set direction %s' % (_, c.DIRECTIONS[direction]))
            self.change = self.board.move(False, direction)            # 更新棋盘
            if self.checkViolate(False, 'direction', direction): break # 判断是否违规
            self.log.append('&p%d:\n' % _ + self.board.__repr__())
            
        else:  # 总回合数耗尽
            self.save()      # 保存
            return
        
        # 得到winnwr
        for _ in (self.timeout, self.violator, self.error):
            if _ != None:
                self.winner = False if _ else True
                self.log.append('&e:player %d win' % (0 if self.winner else 1))

        # 胜方继续游戏
        self.log.append('&e:winner going on...')
        for _ in range(self.currentRound + 1, self.rounds):
            self.currentRound = _
            
            self.next = self.board.getNext(self.winner, _)                    # 按照随机序列得到下一个位置
            position = self.states[self.winner]['player'].output(_, self.board.copy(), 'position')
            if self.checkState(self.winner): break                            # 判断运行状态
            self.log.append('&d%d:player %d set position %s' % (_, 0 if self.winner else 1, str(position)))
            if self.checkViolate(self.winner, 'position', position): break    # 判断是否违规
            self.board.add(self.winner, position)                             # 更新棋盘 
            self.log.append('&p%d:\n' % _ + self.board.__repr__())

            direction = self.states[self.winner]['player'].output(_, self.board.copy(), 'direction')
            if self.checkState(self.winner): break                            # 判断运行状态
            self.log.append('&d%d:player %d set direction %s' % (_, 0 if self.winner else 1, c.DIRECTIONS[direction]))
            self.change = self.board.move(self.winner, direction)             # 更新棋盘
            if self.checkViolate(self.winner, 'direction', direction): break  # 判断是否违规
            self.log.append('&p%d:\n' % _ + self.board.__repr__())
        self.log.append('&e:winner ending...')
        
        self.save()          # 保存

    def checkState(self, isFirst):
        if self.states[isFirst]['time'] >= self.maxtime:
            self.log.append('&e:player %d time out' % (0 if isFirst else 1))
            if self.winner == None: self.timeout = isFirst
            return True
        elif self.states[isFirst]['error']:
            self.log.append('&e:player %d run time error' % (0 if isFirst else 1))
            if self.winner == None: self.error = isFirst
            return True
        else:
            return False

    def checkViolate(self, isFirst, mode, value):
        '''
        -> 违规有三种情形:
        -> 输出格式错误
        -> 选择的方格在可选范围之外
        -> 选择的方向使得合并前后棋盘没有变化
        '''
        if mode == 'position':
            
            if not (isinstance(value, tuple) and len(value) == 2 and value[0] in range(c.ROWS) and value[1] in range(c.COLUMNS)):
                self.log.append('&e:player %d violate by illegal output of position' % (0 if isFirst else 1))
                if self.winner == None: self.violator = isFirst
                return True
            
            if self.board.getValue(value) == 0 and (self.board.getBelong(value) != isFirst or value == self.next):
                return False
            else:
                self.log.append('&e:player %d violate by not achievable position' % (0 if isFirst else 1))
                if self.winner == None: self.violator = isFirst
                return True

        else:
            if value not in range(4):
                self.log.append('&e:player %d violate by illegal output of direction' % (0 if isFirst else 1))
                if self.winner == None: self.violator = isFirst
                return True
            elif self.change:
                return False
            else:
                self.log.append('&e:player %d violate by not achievable direction' % (0 if isFirst else 1))
                if self.winner == None: self.violator = isFirst
                return True
            self.change = False

    def save(self):
        # 获取所有棋子并计数
        results = {True: self.board.getScore(True), False: self.board.getScore(False)}
        scores = {True: {}, False: {}}
        for level in range(1, c.MAXLEVEL):
            scores[True][level] = results[True].count(level)
            scores[False][level] = results[False].count(level)

        # 比较比分
        if self.winner == None:
            for _ in reversed(range(1, c.MAXLEVEL)):
                self.log.append('&e:check level %d' % _)
                if scores[True][_] > scores[False][_]:
                    self.winner = True
                    self.log.append('&e:player 0 win by level %d (%d to %d)' % (_, scores[True][_], scores[False][_]))
                    break
                if scores[True][_] < scores[False][_]:
                    self.winner = False
                    self.log.append('&e:player 1 win by level %d (%d to %d)' % (_, scores[False][_], scores[True][_]))
                    break
                self.log.append('&e:level %d tied by %d' % (_, scores[True][_]))
            else:
                if self.winner == None:
                    self.log.append('&e:tied')
                    raise Exception('Tied')  # 平局

        # 保存对局信息, 可以用analyser.py解析
        file = open('%s.txt' % hash(time.perf_counter()),'w')
        myDict = {True:'player 0', False:'player 1', None:'None'}  # 协助转换为字符串
        title = 'player0: %s\n' % self.states[True] + \
                'player1: %s\n' % self.states[False] + \
                'time: %s\n' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + \
                '{:*^45s}\n'.format('basic record')
        file.write(title)
        file.write('=' * 45 + '\n|{:^10s}|{:^10s}|{:^10s}|{:^10s}|\n'.format('timeout', 'violator', 'error', 'winner') + \
                   '-' * 45 + '\n|{:^10s}|{:^10s}|{:^10s}|{:^10s}|\n'.format(myDict[self.timeout], myDict[self.violator], myDict[self.error], myDict[self.winner]) + \
                   '=' * 45 + '\n')
        file.write('=' * 60 + '\n|%6s|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|\n' % ('player', *range(1, c.MAXLEVEL)) + \
                   '-' * 60 + '\n|%6d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|\n' % (0, *[scores[True][_] for _ in range(1, c.MAXLEVEL)]) + \
                   '-' * 60 + '\n|%6d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|\n' % (1, *[scores[False][_] for _ in range(1, c.MAXLEVEL)]) + \
                   '=' * 60 + '\n')
        file.flush()
        file.write('{:*^45s}\n'.format('complete record'))
        for log in self.log:
            file.write(log + '\n')  # '&'表示一条log的开始
            file.flush()
        file.close()

        
def main(playerDict):
    '''
    -> 主函数
    -> 参数: playerDict 参赛队伍的模块名称字典, 示例 {'player': 3, ...} 表示3个使用'player'模块的队伍...
    '''

    # 监测运行状态的装饰器
    from functools import wraps
    def stateManager(index):
        def decorator(func):
            @wraps(func)
            def wrappedFunc(*args, **kwargs):
                begin = time.perf_counter()
                result = func(*args, **kwargs)
                end = time.perf_counter()
                states[index]['time'] += end - begin
                try:
                    pass
                except:
                    states[index]['error'] = True
                return result
            return wrappedFunc
        return decorator
    
    # 导入全部ai模块
    Players = {name: __import__(name).Player for name in playerDict}  
    
    # 生成player对象并构建运行状态字典
    states = {}
    count = 0
    for name in playerDict:
        for _ in range(playerDict[name]):
            for isFirst in [True, False]:
                states[(count, isFirst)] = {'player': Players[name](isFirst, c.ARRAY), 'name': name, 'time': 0, 'error': False}
            count += 1

    # 重载对象方法
    for index in states:
        states[index]['player'].__init__ = stateManager(index)(states[index]['player'].__init__)
        states[index]['player'].output = stateManager(index)(states[index]['player'].output)
    
    # 开始游戏, 单循环先后手多次比赛
    for count1 in range(count):
        for count2 in range(count1 + 1, count):
            for _ in range(c.REPEAT):
                Platform({True: states[(count1, True)], False:states[(count2, False)]}).play()
                Platform({True: states[(count2, True)], False:states[(count1, False)]}).play()
