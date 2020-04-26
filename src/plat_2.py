# 用于程序的对战平台接口
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
        '''
        一局比赛, 返回player表现报告
        '''
        check = [self.checkState(True), self.checkState(False)]
        if sum(check) == 0:  # 双方合法加载
            self.doublePlay()
        elif sum(check) == 1:  # 一方合法加载
            self.currentRound = -1
            self.winner = not check[0]
            self.singlePlay()
        else:  # 双方非法加载
            if self.timeout == None:
                self.error = 'both'
            if self.error == None:
                self.timeout = 'both'
            self.save()
        return {True: {'index': self.states[True]['index'], 'win': self.winner == True, 'lose': self.winner == False, 'violate': self.violator == True, \
                       'timeout': self.timeout in [True, 'both'], 'error': self.error in [True, 'both'], 'time': self.states[True]['time']}, \
                False: {'index': self.states[False]['index'], 'win': self.winner == False, 'lose': self.winner == True, 'violate': self.violator == False, \
                       'timeout': self.timeout in [False, 'both'], 'error': self.error in [False, 'both'], 'time': self.states[False]['time']}, \
                'name': self.name, 'rounds': self.currentRound + 1}
              
    def doublePlay(self):
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

        self.singlePlay() # 胜者继续
        
    def singlePlay(self):
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
        self.save()  # 保存
        
    def checkState(self, isFirst):
        if self.states[isFirst]['time'] >= self.maxtime:  # 超时
            self.log.append('&e:player %d time out' % (0 if isFirst else 1))
            if self.winner == None: self.timeout = isFirst
            return True
        if self.states[isFirst]['error']:  # 抛出异常
            self.log.append('&e:player %d run time error' % (0 if isFirst else 1))
            if self.winner == None: self.error = isFirst
            return True
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

        # 保存对局信息, 可以用analyser.py解析
        self.name = repr(hash(time.perf_counter()))  # 对局名称
        file = open('%s/%s.txt' % (self.states['match'], self.name),'w')
        myDict = {True:'player 0', False:'player 1', None:'None', 'both':'both'}  # 协助转换为字符串
        title = 'player0: %s from module %s\n' % (self.states[True]['index'], self.states[True]['module']) + \
                'player1: %s from module %s\n' % (self.states[False]['index'], self.states[False]['module']) + \
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

        
def main(playerList):
    '''
    -> 主函数
    -> 参数: playerList 参赛队伍的模块名称列表
    '''

    # 存放log文件的文件夹
    import os
    match = time.strftime('%Y-%m-%d %H-%M-%S', time.localtime())
    os.mkdir('%s' % match)

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
    from functools import wraps
    import threading
    def timeoutManager(maxtime, isFirst = None):
        def decorator(func):
            @wraps(func)
            def wrappedFunc(*args, **kwargs):
                result = Result(func)
                thread = threading.Thread(target = result.call, args = (*args, ), kwargs = {**kwargs})
                thread.setDaemon(True)
                thread.start()
                thread.join(maxtime - states[isFirst]['time'] if isFirst != None else maxtime)
                if isinstance(result.result, Timeout) and isFirst != None:
                    states[isFirst]['time'] = maxtime
                return result.result
            return wrappedFunc
        return decorator
    
    # 监测运行状态的装饰器
    def stateManager(isFirst):
        import traceback
        def decorator(func):
            @timeoutManager(c.MAXTIME * 1.1, isFirst)
            @wraps(func)
            def wrappedFunc(*args, **kwargs):
                try:
                    begin = time.perf_counter()
                    result = func(*args, **kwargs)
                    end = time.perf_counter()
                    states[isFirst]['time'] += end - begin
                except:
                    traceback.print_exc()
                    result = None
                    states[isFirst]['error'] = True
                return result
            return wrappedFunc
        return decorator
    
    # 导入全部ai模块
    Players = {name: __import__(name).Player for name in playerList}
    
    # 进行成绩记录的准备    
    matchResults = []
    playerResults = {}
    for count in range(len(playerList)):
        playerResults[count] = {True: {'win': [], 'lose': [], 'violate': [], 'timeout': [], 'error': [], 'time': []}, \
                                False: {'win': [], 'lose': [], 'violate': [], 'timeout': [], 'error': [], 'time': []}, 'module': playerList[count]}
            
    def update(matchResults, playerResults, result):
        matchResults.append('name: %s -> player%d to player%d -> %d rounds' % (result['name'], result[True]['index'][0], result[False]['index'][0], result['rounds']))
        for isFirst in [True, False]:
            for _ in result[isFirst]:
                if _ != 'index' and result[isFirst][_]:
                    playerResults[result[isFirst]['index'][0]][isFirst][_].append(result['name'] if _ != 'time' else result[isFirst]['time'])


    # 生成对象并重载其方法, 返回状态
    def create(count, isFirst):
        @timeoutManager(c.MAXTIME * 1.1)
        def new():
            try:
                begin = time.perf_counter()
                player = Players[playerResults[count]['module']](isFirst, c.ARRAY)
                end = time.perf_counter()
                state = {'player': player, 'module': playerResults[count]['module'], 'time': end - begin, 'error': False, 'index': (count, isFirst)}
            except:
                state = {'player': None, 'module': playerResults[count]['module'], 'time': 0, 'error': True, 'index': (count, isFirst)}
            return state
        
        state = new()
        if isinstance(state, Timeout):
            print(2)
            state = {'player': None, 'module': playerResults[count]['module'], 'time': c.MAXTIME * 1.1, 'error': True, 'index': (count, isFirst)}
        elif state['player'] != None:
            state['player'].output = stateManager(isFirst)(state['player'].output)
            
        return state
            
    # 开始游戏, 单循环先后手多次比赛
    for count1 in range(len(playerList)):
        for count2 in range(count1 + 1, len(playerList)):
            for _ in range(c.REPEAT):
                states = {True: create(count1, True), False: create(count2, False)}
                update(matchResults, playerResults, Platform({'match': match, True: states[True], False:states[False]}).play())
                states = {True: create(count2, True), False: create(count1, False)}
                update(matchResults, playerResults, Platform({'match': match, True: states[True], False:states[False]}).play())
                
    
    # 统计全部比赛并归档到一个总文件中
    f = open('%s/_.txt' % match, 'w')
    f.write('=' * 50 + '\n')
    f.write('total matches: %d\n' % len(matchResults))
    f.write('\n'.join(matchResults))
    f.write('\n' + '=' * 50 + '\n')
    f.flush()
    for count in playerResults:
        f.write('player%s from module %s\n\n' % (count, playerResults[count]['module']))
        player = playerResults[count][True]
        f.write('offensive cases: \n\n\taverage time: %.3f\n\twin rate: %.2f%%\n\twin: %d at \n\t\t%s\n\tlose: %d at \n\t\t%s\n\tviolate: %d at \n\t\t%s\n\ttimeout: %d at \n\t\t%s\n\terror: %d at \n\t\t%s\n' % \
                (sum(player['time']) / len(player['time']) if player['time'] != [] else 0, 100 * len(player['win']) / c.REPEAT / (len(playerResults) - 1), \
                 len(player['win']), '\n\t\t'.join(player['win']), \
                 len(player['lose']), '\n\t\t'.join(player['lose']), len(player['violate']), '\n\t\t'.join(player['violate']), \
                 len(player['timeout']), '\n\t\t'.join(player['timeout']), len(player['error']), '\n\t\t'.join(player['error'])))
        player = playerResults[count][False]
        f.write('defensive cases: \n\n\taverage time: %.3f\n\twin rate: %.2f%%\n\twin: %d at \n\t\t%s\n\tlose: %d at \n\t\t%s\n\tviolate: %d at \n\t\t%s\n\ttimeout: %d at \n\t\t%s\n\terror: %d at \n\t\t%s\n' % \
                (sum(player['time']) / len(player['time']) if player['time'] != [] else 0, 100 * len(player['win']) / c.REPEAT / (len(playerResults) - 1), \
                 len(player['win']), '\n\t\t'.join(player['win']), \
                 len(player['lose']), '\n\t\t'.join(player['lose']), len(player['violate']), '\n\t\t'.join(player['violate']), \
                 len(player['timeout']), '\n\t\t'.join(player['timeout']), len(player['error']), '\n\t\t'.join(player['error'])))
        f.write('=' * 50 + '\n')
        f.flush()
    f.close()
