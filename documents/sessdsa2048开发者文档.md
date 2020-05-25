# SESSDSA.2048开发者文档

本文档是`SESSDSA.2048开发者文档.pdf`的复刻。<del>你一定很好奇为什么是先有的pdf文档再有的md文档</del>

## 1.对战平台

对战平台的接口并不直接对外暴露。**如果您是对抗算法开发者，可以略过这个部分的说明；如果您是前端开发者或赛制工具开发者，可能需要了解对战平台的接口和数据协议以利于您的开发。**

### A.说明对象

`plat.py`的`Platform`类。

### B.类变量

1. `self.states`:       参赛ai的运行状态，为`dict`类型，遵循states的数据协议。
2. `self.match`:        比赛名称（保存路径），为有效`str`的格式路径。
3. `self.livequeue`:    用于直播线程通信的队列，为`queue.Queue`类型。
4. `self.toSave`:       是否保存记录文件，为`bool`类型。
5. `self.maxtime`:      最大时间限制，为`int`类型。
6. `self.rounds`:       总回合数，为`int`类型。
7. `self.winner`:       胜利者，为`bool`类型或者`None`；为`True`代表先手，为`False`代表后手，为`None`代表无。
8. `self.violator`:     违规者，为`bool`类型或者`None`；为`True`代表先手，为`False`代表后手，为`None`代表无。
9. `self.timeout`:      超时者，为`bool`类型或者`None`或者字符串`'both'`；为`True`代表先手，为`False`代表后手，为`None`代表无，为`'both'`代表先后手。
10. `self.error`:       报错者，为`bool`类型或者`None`或者字符串`'both'`；为`True`代表先手，为`False`代表后手，为`None`代表无，为`'both'`代表先后手。
11. `self.currentRound`:当前轮数，为`int`类型，值为`0`代表第一轮。
12. `self.change`:      某次操作中棋盘是否发生改变，为`bool`类型。
13. `self.next`:        根据随机序列得到的下一个位置，为tuple类型，遵循position的数据协议。在极特殊的情况下，self.next=(`None`, `None`)，代表在先后手方初始化的过程中抛出了异常。
14. `self.board`:       棋盘，为`Chessboard`类的实例。
15. `self.log`:         日志，为平台内定义的`Log`类的实例。`Log`类继承`list`类，可以依据`list`类的接口操作逐条存储的日志记录。单条日志记录遵循`log`的数据协议。
16. `self.name`:        本局比赛的名称，为`repr`格式的哈希字符串。

### C.类方法

1. `__init__(self, states, match, livequeue, toSave, MAXTIME, ROUNDS)`初始化平台对象，为参赛 ai 重载方法使其具有计时与捕获异常的功能。参数表如下
    1. `states`与`self.states`遵循相同约定，但是参赛ai对象应当只实例化而未经初始化。(即使用`object.__new__(cls)`实例化对象)
    2. `match`与`self.match`遵循相同约定。
    3. `livequeue`与`self.livequeue`遵循相同约定。
    4. `toSave`与`self.toSave`遵循相同约定。
    5. `MAXTIME`与`self.maxtime`遵循相同约定。
    6. `ROUNDS`与`self.rounds`遵循相同约定。
2. `play(self)`初始化参赛ai并进行单局比赛，返回比赛报告。返回值遵循result的数据协议。
3. `start(self)`进行比赛，**不支持外部调用**。
4. `checkState(self, isFirst)`检查超时和报错，**不支持外部调用**。
5. `checkViolate(self, isFirst, mode, value)`检查非法输出，**不支持外部调用**。
6. `save(self)`保存比赛记录文件，遵循记录保存数据协议，**不支持外部调用**。

### D.数据协议

1. states

   ```Python
    states = {
        True: {
            'player': player,
            'path': path,
            'time': time,
            'time0': time0,
            'error': error,
            'exception' : exception,
            'index': index
        },
        False: {
            'player': player,
            'path': path,
            'time': time,
            'time0': time0,
            'error': error,
            'exception' : exception,
            'index': index
        }
    }
    ```

    键True与False分别代表先后手，其对应的值是其运行状态，说明如下
    1. `player`参赛ai对象，为参赛队伍提供的类的实例。
    2. `path`参赛队伍提供的类的路径或者类本身(视读取的时候是按路径读取还是按类读取)，为有效的`str`格式路径或类。
    3. `time`参赛ai的当前时间，为`float`类型。
    4. `time0`参赛ai的时间零点，为`int`或`float`类型，通过调节此变量可以实现对特定参赛ai的总时间限制进行修改。
    5. `error`参赛ai是否抛出异常，为`bool`类型。
    6. `exception`参赛ai运行时抛出的异常信息，为标准traceback字符串或者(当未抛出异常时)`None`。
    7. `index`参赛ai的编号，为`tuple`类型，遵循index的数据协议。
2. log

    单条log记录由&起始。分为三类
    1. &d? : ... 某方作出决策

        这里的?与...分别为当前轮数与决策说明。
        作为例子，在第一轮先手方选择向右合并，将会生成记录

        ```text
        &d0: player 0 set direction right
        ```

        而在第五轮后手方选择在(1, 4)下棋，将会生成记录

        ```text
        &d4: player 1 set position (1, 4)
        ```

    2. &p? : ... 当前棋盘

        这里的?与...分别为当前轮数与棋盘的repr格式。
        作为例子，第 43 轮的某个棋盘记录为

        ```text
        &p42:
        +00 +00 +00 +03 +02 −00 −00 −00
        +00 +00 +01 +02 −03 −01 −00 −00
        +00 +05 +03 +01 −05 −03 −01 −00
        +00 +00 +01 +05 −02 −02 −04 −01
        ```

    3. &e: ... 游戏事件触发

        这里的...为事件说明。游戏事件有：违规、超时、报错、胜利、计分、平局。
        作为例子，列举一些记录如下

        ```text
        &e: player 1 violate by illegal output of direction
        &e: player 0 win
        ```

3. result

    ```Python
    result= {
        True: {
            'index' : index,
            'win': win,
            'lose': lose,
            'violate': violate,
            'timeout': timeout,
            'error': error,
            'time': time,
            'exception': exception
        },
        False: {
            'index' : index,
            'win': win,
            'lose': lose,
            'violate': violate,
            'timeout': timeout,
            'error': error,
            'time': time,
            'exception': exception
        },
        'name' : name,
        'rounds' : rounds
    }
    ```

    键name与rounds对应的值分别为本局比赛名称与比赛实际进行总轮数，分别遵循self.name和self.rounds的约定。键True与False分别代表先后手，其对应的值是其表现报告，说明如下
    1. index 参赛ai的编号，为tuple类型，遵循index的数据协议。
    2. win 是否胜利，为bool类型。
    3. lose 是否失败，为bool类型。
    4. violate 是否违规，为bool类型。
    5. timeout 是否超时，为bool类型。
    6. error 是否报错，为bool类型。
    7. time 参赛ai总运行时间，为int或float类型。
    8. exception 参赛ai运行时抛出的异常信息，为标准traceback字符串或者(当未抛出异常时)None。
4. position

    position = (row, column)

    row, column为int类型，代表位置的行、列坐标

5. index

    index = (count, isFirst)

    其中count为int类型，是按顺序编定的参赛模块编号；isFirst为bool类型，代表是否先手。

6. 比赛记录保存

    比赛记录将保存为标准txt文件，包含该局比赛的元信息和全部日志记录。比赛记录从上而下分别记录了模块的路径(或模块本身)、比赛时间、比赛结果和全部比赛日志。此比赛记录可以被复盘工具解析并实现可视化，利于开发者进行调试。

## 2.单循环赛工具

此工具可以实现数个参赛队伍之间进行指定重复次数的先后手交替单循环比赛，并在指定文件夹中将比赛记录归档整理，同时具有对全部比赛的统计功能。

### A.说明对象

`round_match.py`的`main`函数

### B.参数表

```Python
main(
    playerList,
    savepath = None,
    livequeue = None,
    toSave = True,
    toReport = True,
    toGet = False,
    debug = False,
    REPEAT = c.REPEAT,
    MAXTIME = c.MAXTIME,
    ROUNDS = c.ROUNDS
)
```

1. 必填参数 playerList:参赛队伍的模块列表

    playerList = [module, module, ... ]
    module 支持绝对路径、相对路径和已读取的类。
    以下都是正确调用的例子。

    ```Python
    >>> main(['some/absolute/path/to/player.py',
    ... 'another/absolute/path/to/player.py'])
    >>> main(['../player.py'] * 3)
    >>> from player import Player as p
    >>> main(['player.py', p])
    ```

    如果将某个module改为元组(module, time0)，将指定该模块计时零点为time0(此值默认为 0)，通过调整计时零点可以延长或缩短对特定模块的时间限制。使用的例子如下。

    ```Python
    >>> # 给第二个模块的时间限制+1s
    >>> main(['player.py', ('player.py', -1)])
    ```

2. 可选参数 `savepath`:比赛文件夹的保存路径

    `savepath` 支持绝对路径、相对路径和函数返回值；当参数缺省时，在当前
    文件夹下生成以当前时间命名的比赛文件夹。
    以下都是正确调用的例子。

    ```Python
    >>> # 缺省调用
    >>> main(['player.py', 'player.py'])
    >>> # 路径调用
    >>> main(['../player.py'] * 2, savepath='../match')
    >>> # 函数返回值调用
    >>> import random
    >>> main(['player.py'] * 2,
    ... savepath = lambda : str(random.random()))
    ```

    如果该路径下已经存在同名文件夹，将创建文件夹副本以存放比赛记录。
    例如，`match`文件夹名被两次占用后，产生副本`match_2`，`match_3`。
3. 可选参数 `livequeue`:直播中线程通信用的队列

    模块queue中的Queue对象，缺省值为None，表示直播模式关闭。此队列需要在直播工具中用到，**对抗算法开发者无需手动设置**；赛制工具开发者可以在设定通信队列之后接入即可。

    ```Python
    >>> q = __import__('queue).Queue()
    >>> main(['player.py'] * 2, livequeue = q)
    ```

    为了保证直播观看体验，在比赛中设置了等待时间，所以运行总时间将会很长。

4. 可选参数 `toSave`:是否保存单局详细对局记录文件

    bool类型，缺省值为True。

5. 可选参数 `toReport`:是否生成全部比赛统计报告

    bool类型，缺省值为True。

6. 可选参数 `toGet`:是否返回全部对战平台对象

    bool类型，缺省值为False。

7. 可选参数 `debug`:是否生成报错信息报告

    bool类型，缺省值为False。

8. 可选参数 `REPEAT`:单循环轮数

    int类型，缺省值为默认单循环轮数

9. 可选参数 `MAXTIME`:最大时间限制

    int类型，缺省值为默认最大时间限制

10. 可选参数 `ROUNDS`:总回合数

    int类型，缺省值为默认总回合数。
    
一点提示，如果需要保存某些特定的参数组合，可以使用字典传入参数。

### C.返回值

一般情况下，函数没有返回值。若toGet参数被设置为True，函数将返回全部比赛的平台对象，遵循result的数据协议。

### D. 数据协议

1. result

    `result = {(i, j): [platform1, platform2, ... ], ... }`有序数对 (i, j) 表示 playerList 中下标为 i, j 的模块分别作为先后手。一个数对对应的值为多轮比赛的平台对象列表(长度为REPEAT)。
2. 全部比赛统计报告
    
    在比赛文件夹中保存为_.txt文件，包含全部比赛的统计信息。

    作为例子，某次统计报告(部分)如下。

    ```text
    ========================
    total matches: 20
    name: 5340670467737 -> player0 to player1 -> 114 rounds
    ...
    ...
    ...
    name: 7981237979477 -> player0 to player1 -> 514 rounds
    player0 from path player.py

    offensive cases:
        average time: 0.006
            win rate: 80.00%
            win 8 at
                457295662957825
                ...
                ...
                ...
                835793467976796
            lose 2 at
                427956796709276
                821917974987957
            violate 1 at
                573946794857609
            timeout 0 at

            error 0 at

    defensive cases:
        average time: 0.001
            win rate: 0.00%
            win 0 at

            lost 10 at
                479275973469798
                ...
                ...
                ...
                629145694567296
            violate: 10 at
                579346290609267
                ...
                ...
                ...
                346856926828972
    ========================
    ```

    首先是按每局比赛的统计报告。从上而下分别记录了比赛总局数，每局比赛的名称、比赛队伍与实际回合数。

    之后是按参赛模块的表现统计报告。包括其路径(或类本身)，在先手方的平均耗时、胜率、胜利场次、失败场次、违规场次、超时场次、报错场次、对应比赛名称，以及在后手方的相应信息。

    根据此报告，再在比赛文件夹中找到对应的详细比赛记录，可以分析参赛模块的表现，有利于开发。
3. 报错信息报告
    
    在比赛文件夹中保存为 _Exceptions.txt 文件，包含每局比赛的报错信息。如果没有报错，将输出pass。某次报错信息报告(部分)如下所示。

    ```text
    -> 37890357726976

    offensive:
    pass

    defensive:
    Traceback (most recent call last):
        File "some/file", line 114, in wrappedFunc
            result = func(*args, **kwargs)
        File "some/file", line 514, in __init__
            raise SomeException
    Exception
    ====================================
    -> 34729579347695

    offensive:
    Traceback (most recent call last):
        File "some/file", line 114, in wrappedFunc
            result = func(*args, **kwargs)
        File "some/file", line 514, in __init__
            raise SomeException
    Exception

    defensive:
    pass
    ```

4. 本地直播工具
    
    此工具可以实现比赛的实时本地直播，使比赛更有观赏性，对于开发和调试用处并不很大。

    1. 说明对象

        livetool.py的Live类

    2. 简介

        此类唯一提供的外部调用接口为__init__，所以接下来只介绍__init__的参数表；运行时，只需如示实例化即可观看直播。
    
    ```python
    >>> Live()
    ```

    3. 参数表

    ```Python
        __init__(
            self,
            mode = 0,
            func = __import__('round_match').main,
            playerList = ['player. py' for _ in range(2)]
        )
    ```

    1. 可选参数 mode:可视化版本

        为 0 或 1 分别对应 2048 原版可视化和**柚子社版**可视化，缺省值为 0。

    2. 可选参数 func:赛制工具

        目前开发的只有单循环赛工具可用，缺省值为单循环赛工具。

    3. 可选参数 playerList:参赛队伍的模块列表

        遵循与单循环赛工具相同的约定，缺省值为`['player. py' for _ in range(2)]`，即两个样例随机ai比赛。

    需要提醒的是，由于tkinter对不同系统的兼容性并不好，而编写者使用的是macOS，所以此UI可能在win界面显示异常。
5. 对抗算法开发者工具

为了方便对抗算法开发，我们编制了面向对抗算法开发者的工具。
   1. 逻辑约定
       1. 坐标

            坐标为tuple变量，具有结构(row, column)，row行坐标，从上到下为0到3的int变量；column列，从左到右为0到7的int变量。

       2. 方向

            方向为int变量，0、1、2、3 分别代表上、下、左、右。

       3. 归属

            归属为bool变量，True为先手方，False为后手方。

   2. ai接口规范化
        
        参赛队伍的ai须以以下方式实现。
        
        实现一个Player类，并实现两个方法。
      1. `__init__(self, isFirst, array)` 初始化
         1. 参数:isFirst是否先手，为bool变量。
         2. 参数:array随机序列，为tuple变量。
      2. `output(self, currentRound, board, mode)` 给出己方的决策
         1. 参数:currentRound 当前轮数，与对战平台类变量self.currentRound遵循相同约定。
         2. 参数:board 棋盘对象的拷贝，是Chessboard类的实例。
         3. 参数:mode 模式，mode = ′position′ 对应位置模式，mode = ′direction′ 对应方向模式，如果 mode 为 '_position' 和 '_direction' 表示在对应模式下己方无法给出合法输出。
         4. 返回:位置模式下返回下棋的坐标，方向模式下返回合并的方向，在己方无法给出合法输出时, 对返回值不作要求。
   3. 棋盘对象Chessboard
        
        棋盘对象提供了对棋盘的基本操作接口，参赛ai可以直接调用。接口如下
        1. `__init__(self, array)` 初始化棋盘对象

            参数:array随机序列

        2. `add(self, belong, position, value = 1)` 在指定位置下棋

            参数:belong操作者，position位置坐标，value 下棋的级别，缺省值为1

            注:棋子的数值取以 2 为底的对数即为其级别，为int变量。
            
            根据规则，实际上belong参数会被忽略，不应当对其意义做出假定。

        3. `move(self, belong, direction)` 向指定方向合并，并且返回棋盘是否变化

            参数:belong操作者，direction合并方向

            返回:棋盘是否变化，为bool类型

        4. `getBelong(self, position)` 根据位置得到归属

            参数:position位置坐标

            返回:该位置上的棋子的归属，若为空位，则返回空位的归属

        5. `getValue(self, position)` 根据位置得到级别

            参数:position位置坐标

            返回:该位置上的棋子的级别，若为空位，则返回 0

        6. `getScore(self, belong)` 获取升序排列的某方的全部棋子的级别列表

            参数:belong某方

            返回:由该方全部棋子的级别构成的list类型变量

        7. `getNone(self, belong)` 获取某方的全部空位的位置列表

            参数:belong某方

            返回:由该方全部空位的位置构成的list类型变量

        8. `getNext(self, belong, currentRound)` 获取某方在本方领域允许下棋的位置

            参数:belong某方，currentRound当前轮数

            返回:该方在本方领域允许下棋的位置，若不可下棋，返回空元组

        9. `copy(self)` 返回一个对象拷贝

            返回:深拷贝的棋盘对象

        10. `__repr__(self)`或`__str__(self)` 棋盘的可打印字符串

            打印结果如下所示。

            ```text
            +01 +01 +04 +00 -05 -01 -04 -00\n
            +01 +01 +04 +00 -05 -01 -04 -00\n
            +01 +01 +04 +00 -05 -01 -04 -00\n
            +01 +01 +04 +00 -05 -01 -04 -00\0
            ```
        11. `getTime(self, belong)` 返回用户AI剩余思考时间, 单位为秒.
        
            参数:belong某方

            返回:float类型变量

        12. `updateTime(self, belong, time)` 更新用户AI的剩余思考时间. 用户无需调用.

            参数:belong某方，time剩余时间

        13. `getDecision(self, belong)`获取某方上一次决策时给出的结果
            
            参数:belong某方
            
            返回:若无决策, 返回`tuple()`. 若为决定合并方向, 为`tuple(direction)`. 若为决定下棋位置, 为`(int, int)`.

        14. `updateDecision(self, belong, decision)` 更新用户AI的决策信息. 用户无需调用.

            参数:belong某方，decision决策

        15. `getAnime(self)` 给出上一次棋盘合并时棋子的移动信息. 用户无需调用.
        
            **undocumented** 
        16. `getRaw(self)` 给出二维列表形式的棋盘
        
            返回:一个4*8的二维list类型, 为`[[(value, belong) for column in range(8)] for row in range(4)]`, 这里 value 和 belong 分别为该位置的级别和归属。

   4. 复盘可视化analyser

        <del>你一定很好奇为什么整个技术组都把这个词拼错了</del>

        1. tkinter版复盘程序

            解析对局记录文件并可视化复盘，为调试提供方便。

            采用交互式设计，直接运行即可，根据终端提示依次输入对局文件名和可视化版本，即可进入可视化界面。

            按键盘的 ′[′ 和 ′]′ 分别对应前进、后退操作。

            需要提醒的是，由于tkinter对不同系统的兼容性并不好，而编写者使用的是macOS，所以此UI可能在win界面显示异常。
            
            而从neattool.py可以直接实现单循环赛的自动可视化，此时按键盘的n、p对应观看下一局、上一局操作（next、previous）。

        2. 网页版可视化程序

            考虑到跨平台时UI可能出现异常，因此产生了网页版复盘程序。

            浏览器打开`src/analyser.html`，并按提示上传单场比赛记录即可。操作方式与前者一致。

            此外，`src/analyser_dir.html`是处理一整局循环赛的工具。由于浏览器的跨域限制，使用方法稍微麻烦一些。

            设某个文件夹`dir`既包含`src/analyser_dir.html`和`src/analyser_dir.js`，也包含你的比赛记录文件夹，那么在目录`dir`下执行`python -m http.server`，并用浏览器打开[http://localhost:8000](http://localhost:8000)，你应当可以看到网页(记为标签页a)上显示了`dir`文件夹的内容。

            ```text
            D:\sessdsa.2048\dir> python -m http.server
            ```

            随后在其中选中`src/analyser_dir.html`并新标签(记为标签页b)打开。再在网页a上进入你的比赛记录文件夹，也就是包含`_.txt`的那个文件夹，在地址栏复制其链接，按提示填入标签页b的输入框中。

            此时点击一条记录即可查看，可以按`[]`或左右方向键调整比赛进程。

   5. 网页版人机对战工具

        在单循环赛中将一方设为`src/human.py`，即可自动打开浏览器页面。位置模式下鼠标点击方块可选取下棋的方块，方向模式下按键盘的方向键选取方向。目前错误处理尚不完善，例如没有断线重连功能。

        ```Python
        >>> import round_match
        >>> round_match.main(["player",("human", -30)], MAXTIME=114514)
        ```

        此时浏览器应该会打开一个页面。在方向模式下用方向键给出方向，在位置模式下点击想放置棋子的方块给出位置。

## 编辑历史

2020.5.5 @SophieARG 创立文档

2020.5.6 @HamiltonHuaji 重写为markdown格式并加入网页版可视化程序的介绍

2020.5.6 @HamiltonHuaji 加入网页版人机对战工具的介绍

2020.5.6 @SophieARG 修改analyser.py接口，并关联自动调试工具neattool.py

2020.5.11 @HamiltonHuaji 加入chessboard类四个新接口的介绍

2020.5.14 @SophieARG 修改player的output接口，增加无合法输出的mode

2020.5.25 @SophieARG 增加chessboard类的getRaw接口介绍
