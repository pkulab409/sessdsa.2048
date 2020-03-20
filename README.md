# sessdsa.2048
2020地空数算实习作业选题

## 游戏背景
对战版2048

## 游戏规则
二人博弈。基本规则同2048（待补充）。

其中对战部分，一回合有四个步骤，具体顺序另议：
- 先手方添加一个棋子；
- 后手方添加一个棋子；
- 先手方移动一个方向；
- 后手方移动一个方向。

下棋时可以选择其一：
- 下到对手场地的指定位置（需要为空格）；
- 下到自己场地的随机位置（由特定算法得知，待补充）

## 场地建设：
技术组给出两个4*4的棋盘与全局信息
- 包含回合数、随机种子信息、计分与耗时等
棋盘需提供玩家当前局势信息
棋盘需接受玩家的：
- 添加棋子信息：自己or对方场地，放置位置
- 盘面方向移动信息：上下左右

## 终局条件分类
- 一方无法移动：记为对方胜/对方可继续游戏
- 一方耗时结束：记为对方胜/对方可继续游戏
- 回合数耗尽：进入计分环节
- 双方均无法移动：进入计分环节

## 计分方式：
- 基本计分方式：将双方终盘棋子降序排列，字典序大者胜。例：先手方有一个1024，四个256，其它小棋子；后手方有一个1024，一个512，其它小棋子，则后手方胜利。
- 考虑对先无法移动/耗尽时间者，进行分数惩罚。
