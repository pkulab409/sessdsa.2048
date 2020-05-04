# 单循环赛工具

import constants as c

def main(playerList,
         savepath = None,
         livequeue = None,
         toSave = True,
         toReport = True,
         toGet = False,
         REPEAT = c.REPEAT,
         MAXTIME = c.MAXTIME,
         ROUNDS = c.ROUNDS):
    '''
    主函数
    -> 参数: playerList 参赛队伍的模块列表, 支持绝对路径, 相对路径, 和已读取的类. 例如 playerList = ['player.py', 'player.py']
    -> 参数: savepath 比赛文件夹的保存路径, 支持相对路径, 支持函数返回值, 默认为在当前目录创建
    -> 参数: livequeue 直播进程通讯用的队列
    -> 参数: toSave 是否保存对局记录
    -> 参数: toReport 是否生成统计报告
    -> 参数: toGet 是否返回平台对象
    -> 参数: REPEAT 单循环轮数
    -> 参数: MAXTIME 总时间限制
    -> 参数: ROUNDS 总回合数
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
                return result
            return wrappedFunc
        return decorator
    
    # 导入全部ai模块
    import sys
    memory = sys.path.copy()
    Players = []
    for count in range(len(playerList)):
        if isinstance(playerList[count], str):
            path = playerList[count]
            sys.path = [os.path.dirname(os.path.abspath(path))]
            Players.append(__import__(os.path.splitext(os.path.basename(path))[0]).Player)
        else:
            Players.append(playerList[count])
    sys.path = memory
    
    # 进行成绩记录的准备    
    matchResults = []
    playerResults = {}
    for count in range(len(playerList)):
        playerResults[count] = {True: {'win': [],
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
                                'path': playerList[count]}
            
    def update(matchResults, playerResults, result):  # 更新成绩记录
        matchResults.append('name: %s -> player%d to player%d -> %d rounds'
                            % (result['name'],
                               result[True]['index'][0],
                               result[False]['index'][0],
                               result['rounds']))
        for isFirst in [True, False]:
            for _ in result[isFirst]:
                if _ != 'index' and result[isFirst][_]:
                    playerResults[result[isFirst]['index'][0]][isFirst][_].append(result['name'] if _ != 'time' else result[isFirst]['time'])


    # 生成对象并重载其方法, 返回状态
    def create(count, isFirst):
        @timeoutManager(MAXTIME * 1.1)
        def new():
            try:
                begin = time.perf_counter()
                player = Players[count](isFirst, c.ARRAY)
                end = time.perf_counter()
                state = {'player': player,
                         'path': playerResults[count]['path'],
                         'time': end - begin,
                         'error': False,
                         'index': (count, isFirst)}
            except:
                state = {'player': None,
                         'path': playerResults[count]['path'],
                         'time': 0,
                         'error': True,
                         'index': (count, isFirst)}
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
    
    # 开始游戏, 单循环先后手多次比赛
    kwargs = {'livequeue': livequeue,
              'toSave': toSave,
              'MAXTIME': MAXTIME,
              'ROUNDS': ROUNDS}
    platforms = {}
    for count1 in range(len(playerList)):
        for count2 in range(count1 + 1, len(playerList)):
            platforms[(count1, count2)] = []
            platforms[(count2, count1)] = []
            for _ in range(REPEAT):
                states = {True: create(count1, True), False: create(count2, False)}
                platforms[(count1, count2)].append(Platform({'match': match,
                                                            True: states[True],
                                                            False:states[False]}, **kwargs))
                update(matchResults, playerResults, platforms[(count1, count2)][-1].play())
                
                states = {True: create(count2, True), False: create(count1, False)}
                platforms[(count2, count1)].append(Platform({'match': match,
                                                            True: states[True],
                                                            False:states[False]}, **kwargs))
                update(matchResults, playerResults, platforms[(count2, count1)][-1].play())
                
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
        for count in playerResults:
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

    if toGet: return platforms
