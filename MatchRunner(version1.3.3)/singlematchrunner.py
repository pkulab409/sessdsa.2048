# -*- coding: utf-8 -*-
"""
Created on Mon Jun  1 22:54:49 2020

@author: 田晨霄
"""
# -*- coding: utf-8 -*-
"""
Created on Thu May 28 18:02:36 2020
@author: 田晨霄
"""

###两个人进行一场比赛，一共20局比赛，每局500回合，前10局一方先，后10局另外一方先，输出该场比赛的胜者
import constants as c
import random
import information as inf
def main(playerList,
         savepath = None,
         livequeue = None,
         toSave = True,
         toReport = True,
         toGet = False,
         debug = False,
         REPEAT = c.REPEAT,
         MAXTIME = c.MAXTIME,
         ROUNDS = c.ROUNDS):
    print("s")
    '''
    主函数
    -> 参数: playerList 参赛队伍的模块列表, 支持绝对路径, 相对路径, 和已读取的类. 例如 playerList = ['player.py', 'player.py']
    -> 参数: savepath 比赛文件夹的保存路径, 支持相对路径, 支持函数返回值, 默认为在当前目录创建
    -> 参数: livequeue 直播进程通讯用的队列
    -> 参数: toSave 是否保存对局记录
    -> 参数: toReport 是否生成统计报告
    -> 参数: toGet 是否返回平台对象
    -> 参数: debug 是否打印报错信息
    -> 参数: REPEAT 单循环轮数
    -> 参数: MAXTIME 总时间限制
    -> 参数: ROUNDS 总回合数
    '''
    ###CODES1该轮参数代码者的文件夹名字###
    ###CODES2备用参赛代码者的文件夹名字###
    import time
    from plat import Platform
    
    '''
    第一部分, 构建存放log文件的文件夹
    '''
    
    import os
    if callable(savepath): match = savepath()
    elif isinstance(savepath, str): match = savepath
    else: match = time.strftime('%Y-%m-%d %H-%M-%S', time.localtime())
    
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
    第二部分, 导入模块并准备成绩记录
    '''
#    import os
#    fileList1 = os.listdir(CODES1)
#    if CODES2:
#        fileList2=os.listdir(CODES2)
#        
#    for i in range(2):
#        playerList.append("players"+"/"+fileList[i])
   # playerList.append(fileList[i])
    # 导入全部ai模块
    import sys
    Players = []
    time0 = [0 for count in range(len(playerList))]
    for count in range(len(playerList)):
        if isinstance(playerList[count], tuple):  # 指定初始时间
            time0[count] = playerList[count][1]
            playerList[count] = playerList[count][0]
        if isinstance(playerList[count], str):  # 路径
            path = playerList[count]
            sys.path.insert(0, os.path.dirname(os.path.abspath(path)))
            module = os.path.splitext(os.path.basename(path))[0]
            Players.append(__import__(module).Player)
            sys.path.pop(0)
            del sys.modules[module]
        else:  # 已读取的类
            Players.append(playerList[count])
    
    # 进行成绩记录的准备    
    matchResults = {'basic': [], 'exception': []}
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
                      'path': playerList[count]} for count in range(len(playerList))]
            
    def update(matchResults, playerResults, result):  # 更新成绩记录
        matchResults['basic'].append('name: %s -> player%d to player%d -> %d rounds'
                                    % (result['name'],
                                       result[True]['index'][0],
                                       result[False]['index'][0],
                                       result['rounds']))
        matchResults['exception'].append((result['name'], result[True]['exception'], result[False]['exception']))
        for isFirst in [True, False]:
            for _ in result[isFirst]:
                if _ not in  ['index', 'exception'] and result[isFirst][_]:
                    playerResults[result[isFirst]['index'][0]][isFirst][_].append(result['name'] if _ != 'time' else result[isFirst]['time'])
                    
    '''
    第三部分, 比赛
    '''
    
    # 开始游戏, 单循环先后手多次比赛
    kwargs = {'match': match,
              'livequeue': livequeue,
              'toSave': toSave,
              'MAXTIME': MAXTIME,
              'ROUNDS': ROUNDS}
    platforms = {}
    platforms[(0, 1)] = []
    platforms[(1, 0)] = []
    for _ in range(REPEAT):
        print(inf.information[playerResults[0]["path"][11:-3]]+" "+"vs"+" "+inf.information[playerResults[1]["path"][11:-3]]+":"+str(len(playerResults[0][True]["win"])+len(playerResults[0][False]["win"]))+" "+":"+" "+str(len(playerResults[1][True]["win"])+len(playerResults[1][False]["win"])))
        for isFirst in [True, False]:
            counts = (0, 1) if isFirst else (1, 0)
            trueCount, falseCount = counts
            platforms[counts].append(Platform({True: {'player': object.__new__(Players[trueCount]),
                                                      'path': playerList[trueCount],
                                                      'time': time0[trueCount],
                                                      'time0': time0[trueCount],
                                                      'error': False,
                                                      'exception': None,
                                                      'index': (trueCount, True)},
                                               False: {'player': object.__new__(Players[falseCount]),
                                                       'path': playerList[falseCount],
                                                       'time': time0[falseCount],
                                                       'time0': time0[falseCount],
                                                       'error': False,
                                                       'exception': None,
                                                       'index': (falseCount, False)}}, **kwargs))
            update(matchResults, playerResults, platforms[counts][-1].play())  
    A=len(playerResults[0][True]['win'])+len(playerResults[0][False]['win'])
    B=len(playerResults[1][True]['win'])+len(playerResults[1][False]['win'])
    winner=""
    if A>B:
        winner=playerResults[0]["path"]
    elif A<B:
        winner=playerResults[1]["path"]
    else:
        Key=random.randint(0,1)
        if Key==0:
            temp=Platform({True: {'player': object.__new__(Players[0]),
                                                      'path': playerList[0],
                                                      'time': time0[0],
                                                      'time0': time0[0],
                                                      'error': False,
                                                      'exception': None,
                                                      'index': (0, True)},
                                               False: {'player': object.__new__(Players[1]),
                                                       'path': playerList[1],
                                                       'time': time0[1],
                                                       'time0': time0[1],
                                                       'error': False,
                                                       'exception': None,
                                                       'index': (1, False)}}, **kwargs)
            exresult=temp.play()
            update(matchResults, playerResults, exresult) 
            print(inf.information[playerResults[0]["path"][11:-3]]+" "+"vs"+" "+inf.information[playerResults[1]["path"][11:-3]]+":"+str(len(playerResults[0][True]["win"])+len(playerResults[0][False]["win"]))+" "+":"+" "+str(len(playerResults[1][True]["win"])+len(playerResults[1][False]["win"])))
            if exresult[True]['win']==1:
                winner=playerList[0]
                A=A+1
            else:
                winner=playerList[1]
                B=B+1
        else:
            temp=Platform({True: {'player': object.__new__(Players[1]),
                                                      'path': playerList[1],
                                                      'time': time0[1],
                                                      'time0': time0[1],
                                                      'error': False,
                                                      'exception': None,
                                                      'index': (1, True)},
                                               False: {'player': object.__new__(Players[0]),
                                                       'path': playerList[0],
                                                       'time': time0[0],
                                                       'time0': time0[0],
                                                       'error': False,
                                                       'exception': None,
                                                       'index': (0, False)}}, **kwargs)
            exresult=temp.play()
            update(matchResults, playerResults, exresult)
            print(inf.information[playerResults[0]["path"][11:-3]]+" "+"vs"+" "+inf.information[playerResults[1]["path"][11:-3]]+":"+str(len(playerResults[0][True]["win"])+len(playerResults[0][False]["win"]))+" "+":"+" "+str(len(playerResults[1][True]["win"])+len(playerResults[1][False]["win"])))
            if exresult[True]['win']==1:
                winner=playerList[1]
                B=B+1
            else:
                winner=playerList[0]
                A=A+1
        
            
        
    '''
    第四部分, 统计比赛结果
    '''
    
    # 统计全部比赛并归档到一个总文件中
    if toReport:
        f = open('%s/_.txt' % match, 'w')
        f.write('=' * 50 + '\n')
        f.write('total matches: %d\n' % len(matchResults['basic']))
        f.write('\n'.join(matchResults['basic']))
        f.write('\n' + '=' * 50 + '\n')
        f.flush()
        for count in range(len(playerList)):
            f.write('player%s from path %s\n\n' % (count, playerResults[count]['path'][0:11]+inf.information[playerResults[count]['path'][11:-3]]+".py"))
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

    # 打印报错信息
    if debug:
        f = open('%s/_Exceptions.txt' % match, 'w')
        for metamatch in matchResults['exception']:
            f.write('-> %s\n\n' % metamatch[0])
            f.write('offensive:\n')
            f.write(metamatch[1] if metamatch[1] else 'pass\n')
            f.write('\ndefensive:\n')
            f.write(metamatch[2] if metamatch[2] else 'pass\n')
            f.write('=' * 50 + '\n')
            f.flush()
        f.close()

    # 返回全部平台
    if toGet: return [platforms,A,B,winner]