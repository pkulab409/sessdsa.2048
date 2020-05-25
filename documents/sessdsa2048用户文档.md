# SESSDSA.2048用户文档

理论上, 本文档和规则文档可以作为开发对战AI所需文档的最小集合. 但调试复盘工具链文档待给出/合并.

用户(或用户AI)根据语境, 可能指开发比赛程序的人类或用于对战, 能根据盘面给出决策, 并最大化胜利可能的程序

平台指驱动对战初始化、进行和结束, 给出盘面信息和运行环境, 并调用用户AI的决策方法, 判断胜负的程序.

未定义行为指该行为中平台的行为不受规范, 可能是对战中的任何负面后果. 若未定义行为被其它文档定义, 则遵从该定义文档.

## 用户规范

本章节对用户AI的行为进行规范.

### 引言

Sessdsa.2048 AI 是实现了包含读入本局随机数序列,根据现有的盘面和轮数输出合法的放置位置以及合并方向两个方法的命名为`Player`的类.

需要实现的成员方法具有以下原型

```Python
def __init__(self: Player, isFirst: bool, array: tuple[int]) -> None:
    pass
def output(self: Player, currentRound: int, board: Chessboard, mode: str) -> Union[Tuple[int, int], int]:
    pass
```

平台将会在适当时机调用这些方法.

### 初始化

当平台需要生成一个新的用户AI实例时`__init__`方法被调用. 平台不保证己方初始化与对手初始化的调用顺序, 也不保证新的一场比赛开始时旧的AI实例被销毁.

1. 先后手

    isFirst 是一个布尔参量,其真假表示本局中此 AI 是否是先手

2. 随机列表

    Array 表示本局游戏中标志在己方棋盘中放置棋子时,决定棋子所在位置的参数.

    对于先手, 计算规则为从第 0 行第0列开始,从左往右,从上到下,依次将可用位置排列,将列表中索引值本回合数的数字对可用位置总数取模,得到的结果所对应的可用位置就是本次在己方棋盘中放置棋子的位置.[源码](../src/tools/constants.py#L145)

    对于后手排列顺序相反, 以保证先手和后手棋子的生成位置不在同一列, 避免先手开局就能吃到后手的棋子.

### 输出

1. 基本流程

    游戏开始后,每个回合按照四个阶段顺序执行。

    1. 先手方下一个2棋子
    2. 后手方下一个2棋子
    3. 先手方进行一次合并
    4. 后手方进行一次合并

    重复以上回合直到游戏结束。在每次回合中,先手方和后手方的`output`函数会在该方需要给出其决策时被调用, 参数为三个参量:

    1. `currentRound`: 当前回合数
    2. `board`: 当前盘面
    3. `mode`: 当前决策内容。

    在轮到某方在给定位置下棋时`mode`参数取值`"position"`, 选择合并方向时取值`"direction"`. 用户分别应当返回`Tuple[row, column]`表示下棋位置和`direction`表示合并方向. 而当`mode`参数取`"_position"`与`"_direction"`时表示在对应模式下没有可用操作，此时对返回值没有要求。

    1. `row`: 要下棋位置的棋盘的行号, 从上到下为0到3的`int`
    2. `column`: 要下棋位置的棋盘的列号, 从左到右为0到7的`int`
    3. `direction`: 方向, 取值`0,1,2,3`, 对应`上,下,左,右`

    用户返回值的语义存在规范(见规则文档), 若不符合这些规范(例如, 给出超出棋盘的下棋位置, 或给出棋盘内的位置但该位置已有棋子), 会导致被判违规.

2. 盘面

    盘面为一个类型为`Chessboard`的对象, 其内置方法见平台规范的对应部分.

### 注意事项

1. 结束情况

    不需要考虑游戏结束的情况,假若无法继续游戏会自动结束。

2. 安全要求

    对传入的board参数修改是未定义行为(唯一可以保证的是平台不会因此崩溃), 如果需要使用 board 请自行复制之后使用。己方游戏进行有最大累计时间限制,运行超时会直接判负,请注意分配运算量。关于时间限制以及更多参量可以在`constants.py`中获取。

3. 引用外部模块

    对战平台采用白名单机制. 现允许使用的第三方模块如下
    + math
    + random
    + copy
    + numpy
    + time
    + collections
    + itertools
    + functools
    + heapq
    + operator
    如果有合理需求, 可以向助教或技术组申请引入新的模块.

    此外, 为了阻止绕过代码检查, 以下方法被禁用
    + exec
    + eval
    + compile

## 平台规范

本章节对用户可见的平台行为进行规范(其实本章节没啥说的)

### 棋盘状态

对战中某时刻的棋盘状态由经参数`board`传给用户AI实现的`output`函数的一个`Chessboard`对象给出. 若调用或使用了棋盘除给出接口外的方法或属性, 后果自负.

该对象具有以下方法

   1. `__init__(self: Chessboard, array: tuple[int]) -> None` 初始化棋盘对象

       参数:array随机序列

   2. `add(self: Chessboard, belong: bool, position: Tuple[int, int], value: int = 1) -> None` 在指定位置下棋

       参数:belong操作者，position位置坐标，value 下棋的级别，缺省值为1

       注:棋子的数值取以 2 为底的对数即为其级别，为int变量。若value为0, 为未定义行为.

   3. `move(self: Chessboard, belong: bool, direction: int) -> bool` 向指定方向合并，并且返回棋盘是否变化

       参数:belong操作者，direction合并方向

       返回:棋盘是否变化，为bool类型. direction必须为`0,1,2,3,None`五个值之一, 否则为未定义行为.

   4. `getBelong(self: Chessboard, position: Tuple[int, int]) -> bool` 根据位置得到归属

       参数:position位置坐标

       返回:该位置上的棋子的归属，若为空位，则返回空位的归属

   5. `getValue(self: Chessboard, position: Tuple[int, int]) -> int` 根据位置得到级别

       参数:position位置坐标

       返回:该位置上的棋子的级别，若为空位，则返回 0

   6. `getScore(self: Chessboard, belong: bool) -> List[int]` 获取升序排列的某方的全部棋子的级别列表

       参数:belong某方

       返回:由该方全部棋子的级别构成的list类型变量. 保证升序排列.

   7. `getNone(self: Chessboard, belong: bool) -> List[Tuple[int, int]]` 获取某方的全部空位的位置列表

       参数:belong某方

       返回:由该方全部空位的位置构成的list类型变量

   8. `getNext(self: Chessboard, belong: bool, currentRound) -> Union[Tuple[int, int], Tuple[]]` 获取某方在本方领域允许下棋的位置

       参数:belong某方，currentRound当前轮数

       返回:该方在本方领域允许下棋的位置，若不可下棋，返回空元组. currentRound必须处于`range(0, len(array))`内, 其中`array`是初始化棋盘时传入的随机列表. 超出该范围为未定义行为.

   9. `copy(self: Chessboard) -> Chessboard` 返回一个对象拷贝

       返回:深拷贝的棋盘对象

   10. `__repr__(self: Chessboard) -> str`或`__str__(self: Chessboard) -> str` 棋盘的可打印字符串

       打印结果例子如下.

       ```text
       +01 +01 +04 +00 -05 -01 -04 -00\n
       +01 +01 +04 +00 -05 -01 -04 -00\n
       +01 +01 +04 +00 -05 -01 -04 -00\n
       +01 +01 +04 +00 -05 -01 -04 -00\0
       ```

   11. `getTime(self: Chessboard, belong: bool) -> float`

       返回用户AI剩余思考时间, 单位为秒.

   12. `updateTime(self: Chessboard, belong: bool, time: float) -> None`

       更新用户AI的剩余思考时间. 用户调用为未定义行为.

   13. `getDecision(self: Chessboard, belong: bool) -> Union[Tuple[], Tuple[int, int], Tuple[int]]`

       获取某方上一次决策时给出的结果. 若无决策, 返回`tuple()`. 若为决定合并方向, 为`tuple(direction)`. 若为决定下棋位置, 为`position: Tuple[int, int]`.

   14. `getAnime(self: Chessboard) -> Any`

       给出上一次棋盘合并时棋子的移动信息. 用户调用不会导致异常, 但作为undocumented api, 具体数据形式不给出保证, 天梯平台上现有实现返回`None`, 请勿假定其与本地版本行为一致.

   15. `getRaw(self: Chessboard) -> List[List[Tuple[int, bool]]]`

       返回大小为`4*8`的嵌套列表表示的盘面, 行主序. 其中单个元素为`tuple(value, belong)`, 代表对应位置的棋子的值和归属.

### 杂项

本节列出需要注意的杂项.

+ 比赛服务器的Python版本可能是`3.6`到`3.8`之间任一版本, 请注意不要使用版本限定的语法, 以节约调试时间
+ 所有可能的索引均从`0`开始, 包括但不限于`currentRound`, `position`的两个坐标等变量.
+ 单个AI的内存限制现在为`1GB`

## 有用信息

[天梯网站](http://162.105.17.143:9580/match/dyEWuGIn8N)

## 编辑历史

2020.5.10 @HamiltonHuaji 创建此文档

## 最近更改

+ getScore接口保证返回升序的列表
+ 向add接口传入的value为0为未定义行为
+ 增加了对单个AI的内存限制
+ 传入mode参数的可能值增加了`'_position'`和`'_direction'`, 表示我方AI卡住了不能下棋的两个阶段
+ 新增了允许使用的模块: `heapq`. 可以向助教或技术组申请增加允许使用的模块
+ 增加了对随机位置算法源码的引用, 以方便理解
+ 新增了允许使用的模块: `operator`
+ 明确了部分对棋盘的不合值域操作为未定义行为
+ 增加了API: `getRaw`, 以提供更快的盘面访问方式
