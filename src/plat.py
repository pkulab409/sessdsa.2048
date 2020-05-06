import constants as c  # 导入游戏常数
import time

# 平台

class Platform:
    def __init__(self, states, match, livequeue, toSave, MAXTIME, ROUNDS):
        '''
        初始化
        -> 参数: states 保存先后手方模块元信息的字典
        -> 参数: match 比赛名称
        -> 参数: livequeue 直播通信队列
        -> 参数: toSave 是否保存为记录文件
        -> 参数: MAXTIME 最大时间限制
        -> 参数: ROUNDS 总回合数
        '''
        
        # 生成覆盖随机序列
        from random import randrange
        c.ARRAY = tuple(randrange(720720) for _ in range(ROUNDS))
        
        # 超时异常
        class Timeout(Exception):
            pass

        # 返回值
        class Result:
            def __init__(self, func):
                self.func = func
                self.result = Timeout()
            def call(self, *args, **kwargs):
                self.result = self.func(*args, **kwargs)
                
        # 超时退出的装饰器
        import threading
        def timeoutManager(maxtime, isFirst):
            def decorator(func):
                def wrappedFunc(*args, **kwargs):
                    result = Result(func)
                    thread = threading.Thread(target = result.call, args = (*args, ), kwargs = {**kwargs})
                    thread.setDaemon(True)
                    thread.start()
                    thread.join(maxtime - self.states[isFirst]['time'])
                    if isinstance(result.result, Timeout): self.states[isFirst]['time'] = maxtime
                    return result.result
                return wrappedFunc
            return decorator
        
        # 监测运行状态的装饰器
        import traceback
        def stateManager(isFirst):
            def decorator(func):
                @timeoutManager(MAXTIME * 1.1, isFirst)
                def wrappedFunc(*args, **kwargs):
                    try:
                        begin = time.perf_counter()
                        result = func(*args, **kwargs)
                        end = time.perf_counter()
                        self.states[isFirst]['time'] += end - begin
                    except:
                        result = None
                        self.states[isFirst]['error'] = True
                        self.states[isFirst]['exception'] = traceback.format_exc()
                    return result
                return wrappedFunc
            return decorator

        # 重载对象方法
        for isFirst in [True, False]:
            states[isFirst]['player'].__init__ = stateManager(isFirst)(states[isFirst]['player'].__init__)
            states[isFirst]['player'].output = stateManager(isFirst)(states[isFirst]['player'].output)


        # 构建一个日志类, 可以实现直播功能
        class Log(list):
            def __init__(self, parent):
                list.__init__(self, [])
                self.parent = parent
                Log.add = Log._add if parent.livequeue != None else list.append

            def _add(self, log):
                self.append(log)
                self.parent.livequeue.put(self.parent)
                time.sleep(c.SLEEP)
                
        self.states = states                # 参赛AI运行状态
        self.match = match                  # 比赛名称
        self.livequeue = livequeue          # 直播工具
        self.toSave = toSave                # 保存记录文件
        self.maxtime = MAXTIME              # 最大时间限制
        self.rounds = ROUNDS                # 总回合数
        self.winner = None                  # 胜利者
        self.violator = None                # 违规者
        self.timeout = None                 # 超时者
        self.error = None                   # 报错者
        self.currentRound = 0               # 当前轮数
        self.change = False                 # 监控棋盘是否改变
        self.next = (None, None)            # 按照随机序列得到的下一个位置
        self.board = c.Chessboard(c.ARRAY)  # 棋盘
        self.log = Log(self)                # 日志, &d 决策 decision, &p 棋盘 platform, &e 事件 event

    def play(self):
        '''
        一局比赛, 返回player表现报告
        '''
        
        for isFirst in [True, False]:
            self.states[isFirst]['player'].__init__(isFirst, c.ARRAY)
            
        # 检查双方是否合法加载
        fail = [self.checkState(True), self.checkState(False)]
        if sum(fail) == 0:  # 双方合法加载
            self.start()
        elif sum(fail) == 1:  # 一方合法加载
            self.winner = not fail[0]
        else:  # 双方非法加载
            if self.timeout == None:
                self.error = 'both'
            if self.error == None:
                self.timeout = 'both'

        self.save()  # 计分并保存
            
        return {True:  {'index': self.states[True]['index'],
                        'win': self.winner == True,
                        'lose': self.winner == False,
                        'violate': self.violator == True,
                        'timeout': self.timeout in [True, 'both'],
                        'error': self.error in [True, 'both'],
                        'time': self.states[True]['time'] - self.states[True]['time0'],
                        'exception': self.states[True]['exception']},
                False: {'index': self.states[False]['index'],
                        'win': self.winner == False,
                        'lose': self.winner == True,
                        'violate': self.violator == False,
                        'timeout': self.timeout in [False, 'both'],
                        'error': self.error in [False, 'both'],
                        'time': self.states[False]['time'] - self.states[False]['time0'],
                        'exception': self.states[False]['exception']},
                'name': self.name,
                'rounds': self.currentRound}
              
    def start(self):
        '''
        进行比赛
        '''
        
        def get_position(isFirst, currentRound):
            self.next = self.board.getNext(isFirst, currentRound)  # 按照随机序列得到下一个位置
            position = self.states[isFirst]['player'].output(currentRound, self.board.copy(), 'position')  # 获取输出
            if self.checkState(isFirst): return True  # 判断运行状态
            self.log.add('&d%d:%s set position %s' % (currentRound, c.PLAYERS[isFirst], str(position)))  # 记录
            if self.checkViolate(isFirst, 'position', position): return True  # 判断是否违规
            self.board.add(isFirst, position)  # 更新棋盘
            self.log.add('&p%d:\n' % currentRound + self.board.__repr__())  # 记录
            return False

        def get_direction(isFirst, currentRound):
            direction = self.states[isFirst]['player'].output(currentRound, self.board.copy(), 'direction')  # 获取输出
            if self.checkState(isFirst): return True  # 判断运行状态
            self.log.add('&d%d:%s set direction %s' % (currentRound, c.PLAYERS[isFirst], c.DIRECTIONS[direction]))  # 记录
            self.change = self.board.move(isFirst, direction)  # 更新棋盘
            if self.checkViolate(isFirst, 'direction', direction): return True  # 判断是否违规
            self.log.add('&p%d:\n' % currentRound + self.board.__repr__())  # 记录
            return False

        # 进行比赛
        for _ in range(self.rounds):
            if get_position(True, _): break
            if get_position(False, _): break
            if get_direction(True, _): break
            if get_direction(False, _): break

        # 记录总轮数
        self.currentRound = _ + 1
        
        # 得到winner
        for _ in (self.timeout, self.violator, self.error):
            if _ != None:
                self.winner = not _
                self.log.add('&e:%s win' % (c.PLAYERS[self.winner]))
        
    def checkState(self, isFirst):
        '''
        检查是否超时和报错
        '''
        
        if self.states[isFirst]['time'] >= self.maxtime:  # 超时
            self.log.add('&e:%s time out' % (c.PLAYERS[isFirst]))
            self.timeout = isFirst
            return True
        if self.states[isFirst]['error']:  # 抛出异常
            self.log.add('&e:%s run time error' % (c.PLAYERS[isFirst]))
            self.error = isFirst
            return True
        return False

    def checkViolate(self, isFirst, mode, value):
        '''
        检查是否非法输出
        -> 违规有三种情形:
        -> 输出格式错误
        -> 选择的方格在可选范围之外
        -> 选择的方向使得合并前后棋盘没有变化
        '''
        
        if mode == 'position':
            if not (isinstance(value, tuple) and len(value) == 2 and value[0] in range(c.ROWS) and value[1] in range(c.COLUMNS)):
                self.log.add('&e:%s violate by illegal output of position' % (c.PLAYERS[isFirst]))
                self.violator = isFirst
                return True
            if self.board.getValue(value) == 0 and (self.board.getBelong(value) != isFirst or value == self.next):
                return False
            else:
                self.log.add('&e:%s violate by not achievable position' % (c.PLAYERS[isFirst]))
                self.violator = isFirst
                return True
        else:
            if value not in range(4):
                self.log.add('&e:%s violate by illegal output of direction' % (c.PLAYERS[isFirst]))
                self.violator = isFirst
                return True
            elif self.change:
                return False
            else:
                self.log.add('&e:%s violate by not achievable direction' % (c.PLAYERS[isFirst]))
                self.violator = isFirst
                return True
            self.change = False

    def save(self):
        '''
        计分并保存比赛记录
        '''
        
        # 获取所有棋子并计数
        results = {True: self.board.getScore(True), False: self.board.getScore(False)}
        scores = {True: {}, False: {}}
        for level in range(1, c.MAXLEVEL):
            scores[True][level] = results[True].count(level)
            scores[False][level] = results[False].count(level)

        # 比较比分
        if self.winner == None:
            for _ in reversed(range(1, c.MAXLEVEL)):
                self.log.add('&e:check level %d' % _)
                if scores[True][_] == scores[False][_]:
                    self.log.add('&e:level %d tied by %d' % (_, scores[True][_]))
                else:
                    self.winner = scores[True][_] > scores[False][_]
                    self.log.add('&e:%s win by level %d (%d to %d)' % (c.PLAYERS[self.winner], _, scores[True][_], scores[False][_]))
                    break
            else:
                self.log.add('&e:tied')

        # 保存对局信息, 可以用analyser.py解析
        self.name = repr(hash(time.perf_counter()))  # 对局名称
        if self.toSave:
            file = open('%s/%s.txt' % (self.match, self.name),'w')
            myDict = {True:'player 0', False:'player 1', None:'None', 'both':'both'}  # 协助转换为字符串
            title = 'player0: %d from path %s\n' % (self.states[True]['index'][0], self.states[True]['path']) + \
                    'player1: %d from path %s\n' % (self.states[False]['index'][0], self.states[False]['path']) + \
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
