# 调试工具

import constants as c

def main(playerList,
         savepath = None,
         livequeue = None,
         toSave = True,
         toReport = True,
         toGet = False,
         debug = True,
         REPEAT = c.REPEAT,
         MAXTIME = c.MAXTIME,
         ROUNDS = c.ROUNDS):
    '''
    主函数
    -> 参数: playerList 两个队伍, playerList = [(path, time0), (path, time0)]
    -> 参数: savepath 比赛文件夹的保存路径, 支持相对路径, 支持函数返回值, 默认为在当前目录创建
    '''
    
    import time
    from plat import Platform
    
    '''
    第一部分, 构建存放log文件的文件夹
    '''
    
    import os
    if callable(savepath):
        match = savepath()
    elif isinstance(savepath, str):
        match = savepath
    else:
        match = time.strftime('%Y-%m-%d %H-%M-%S', time.localtime())
    count = 0
    while True:  # 文件夹存在则创立副本
        count += 1
        try:
            _match = '_%d' % count if count != 1 else ''
            os.mkdir(match + _match)
            match += _match
            break
        except FileExistsError:
            continue

    '''
    第二部分, 生成用于比赛的对象
    '''

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
                if isinstance(result.result, Timeout) and isFirst != None: states[isFirst]['time'] = maxtime
                return result.result
            return wrappedFunc
        return decorator
    
    # 监测运行状态的装饰器
    import traceback
    def stateManager(isFirst):
        def decorator(func):
            @timeoutManager(MAXTIME * 1.1, isFirst)
            @wraps(func)
            def wrappedFunc(*args, **kwargs):
                try:
                    begin = time.perf_counter()
                    result = func(*args, **kwargs)
                    end = time.perf_counter()
                    states[isFirst]['time'] += end - begin
                except:
                    result = None
                    states[isFirst]['error'] = True
                    Error[states[isFirst]['index'][0]] = traceback.format_exc()
                return result
            return wrappedFunc
        return decorator
    
    # 导入全部ai模块
    import sys
    memory = sys.path.copy()
    Players = {}
    for player in playerList:
        path = os.path.abspath(player[0])
        sys.path = [os.path.dirname(path)]
        if path not in Players:
            Players[path] = __import__(os.path.splitext(os.path.basename(path))[0]).Player
    sys.path = memory
    
    # 进行成绩记录的准备
    matchResults = []
    playerResults = [{True: {'win': [],
                             'lose': [],
                             'violate': [],
                             'timeout': [],
                             'error': [],
                             'time': []},
                      False: {'win': [],
                              'lose': [],
                              'violate': [],
                              'timeout': [],
                              'error': [],
                              'time': []},
                      'path': playerList[_][0]} for _ in range(2)]
    Errors = [{}, {}]
            
    def update(matchResults, playerResults, Errors, result):  # 更新成绩记录
        matchResults.append('name: %s -> player%d to player%d -> %d rounds'
                            % (result['name'],
                               result[True]['index'][0],
                               result[False]['index'][0],
                               result['rounds']))
        for isFirst in [True, False]:
            for _ in result[isFirst]:
                if _ != 'index' and result[isFirst][_]:
                    count = result[isFirst]['index'][0]
                    playerResults[count][isFirst][_].append(result['name'] if _ != 'time' else (result[isFirst]['time'] - playerList[count][1]))

        for _ in range(2): Errors[_][result['name']] = Error[_]


    # 生成对象并重载其方法, 返回状态
    def create(count, isFirst):
        @timeoutManager(MAXTIME * 1.1)
        def new():
            try:
                begin = time.perf_counter()
                player = Players[os.path.abspath(playerResults[count]['path'])](isFirst, c.ARRAY)
                end = time.perf_counter()
                state = {'player': player,
                         'path': playerResults[count]['path'],
                         'time': end - begin + playerList[count][1],
                         'error': False,
                         'index': (count, isFirst)}
            except:
                state = {'player': None,
                         'path': playerResults[count]['path'],
                         'time': playerList[count][1],
                         'error': True,
                         'index': (count, isFirst)}
                Error[count] = traceback.format_exc()
            return state
        
        state = new()
        if isinstance(state, Timeout):
            state = {'player': None,
                     'path': playerResults[count]['path'],
                     'time': MAXTIME * 1.1,
                     'error': False,
                     'index': (count, isFirst)}
        elif state['player'] != None:
            state['player'].output = stateManager(isFirst)(state['player'].output)
            
        return state

    '''
    第三部分, 比赛
    '''
    
    # 开始游戏, 先后手多次比赛
    kwargs = {'livequeue': livequeue,
              'toSave': toSave,
              'MAXTIME': MAXTIME,
              'ROUNDS': ROUNDS}
    platforms = {(0,1): [], (1,0): []}
    for _ in range(REPEAT):
        Error = [None, None]
        states = {True: create(0, True), False: create(1, False)}
        platforms[(0, 1)].append(Platform({'match': match,
                                           True: states[True],
                                           False:states[False]}, **kwargs))
        update(matchResults, playerResults, Errors, platforms[(0, 1)][-1].play())

        Error = [None, None]
        states = {True: create(1, True), False: create(0, False)}
        platforms[(1, 0)].append(Platform({'match': match,
                                           True: states[True],
                                           False:states[False]}, **kwargs))
        update(matchResults, playerResults, Errors, platforms[(1, 0)][-1].play())
                
    '''
    第四部分, 统计比赛结果
    '''
    
    # 统计全部比赛并归档到一个总文件中
    if toReport:
        f = open('%s/_.txt' % match, 'w')
        f.write('=' * 50 + '\n')
        f.write('total matches: %d\n' % len(matchResults))
        f.write('\n'.join(matchResults))
        f.write('\n' + '=' * 50 + '\n')
        f.flush()
        for count in range(2):
            f.write('player%s from path %s\n\n' % (count, playerResults[count]['path']))
            player = playerResults[count][True]
            f.write('''offensive cases:
    average time: %.3f
        win rate: %.2f%%
        win: %d at
            %s
        lose: %d at
            %s
        violate: %d at
            %s
        timeout: %d at
            %s
        error: %d at
            %s
'''            %(sum(player['time']) / len(player['time']) if player['time'] != [] else 0,
                 100 * len(player['win']) / REPEAT / (len(playerResults) - 1),
                 len(player['win']),
                 '\n            '.join(player['win']),
                 len(player['lose']),
                 '\n            '.join(player['lose']),
                 len(player['violate']),
                 '\n            '.join(player['violate']),
                 len(player['timeout']),
                 '\n            '.join(player['timeout']),
                 len(player['error']),
                 '\n            '.join(player['error'])))
            player = playerResults[count][False]
            f.write('''defensive cases:
    average time: %.3f
        win rate: %.2f%%
        win: %d at
            %s
        lose: %d at
            %s
        violate: %d at
            %s
        timeout: %d at
            %s
        error: %d at
            %s
'''            %(sum(player['time']) / len(player['time']) if player['time'] != [] else 0,
                 100 * len(player['win']) / REPEAT / (len(playerResults) - 1),
                 len(player['win']),
                 '\n            '.join(player['win']),
                 len(player['lose']),
                 '\n            '.join(player['lose']),
                 len(player['violate']),
                 '\n            '.join(player['violate']),
                 len(player['timeout']),
                 '\n            '.join(player['timeout']),
                 len(player['error']),
                 '\n            '.join(player['error'])))
            f.write('=' * 50 + '\n')
            f.flush()
        f.close()

    if debug:
        f = open('%s/_Exceptions.txt' % match, 'w')
        for count in range(2):
            f.write('player%s from path %s\n\n' % (count, playerResults[count]['path']))
            for name in Errors[count]:
                f.write(' -> ' + name + '\n')
                f.write(Errors[count][name] if Errors[count][name] else 'pass\n')
                f.write('\n')
            f.write('=' * 50 + '\n')
            f.flush()
        f.close()
        
    if toGet: return platforms
