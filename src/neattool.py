# 肥宅快乐调试工具
# "不管py还是html, 肥宅总是希望一局跑完能调用个接口然后坐在那儿一局一局地看"
# 请在analyser.py中熟悉键盘操作

import constants as c
import round_match
import analyser
import os


def main(playerList,
         savepath,
         mode = 0,
         toReport = True,
         debug = False,
         REPEAT = c.REPEAT,
         MAXTIME = c.MAXTIME,
         ROUNDS = c.ROUNDS):

    assert not os.path.exists(savepath) , 'file %s exists' % savepath
    matchList = [mode]
    platforms = round_match.main(playerList,
                                 savepath = savepath,
                                 toSave = True,
                                 toReport = toReport,
                                 toGet = True,
                                 debug = debug,
                                 REPEAT = REPEAT,
                                 MAXTIME = MAXTIME,
                                 ROUNDS = ROUNDS)
    for indexs in platforms:
        for platform in platforms[indexs]:
            matchList.append({'path': savepath + '/' + platform.name + '.txt',
                              'topText': playerList[indexs[0]] + ' vs ' + playerList[indexs[1]],
                              'bottomText': 'match ' + platform.name})

    analyser.GameScreen(matchList)
