# src文档草案

## 基本介绍
此文件夹包含了[对战平台内核](plat.py)，[样例随机ai](player.py)，[复盘可视化](analyser.py)，[可供引用的帮助库](constants.py)，[隔离代码装置](secureclass.py)，[样例初级ai](less_stupid_player.py)(目前还需要修改接口)。

## 使用方法介绍
### 对战平台内核
```
from player import Player as Player0  # 先手
from player import Player as Player1  # 后手
```
从```player.py```中引用Player对象参与对战，直接运行即可开始比赛。

运行界面出现
```
for complete record...(y/n): 
```
输入y可以查看完整对战记录。
运行界面出现
```
save record...(y/n): 
```
输入y可以保存对战记录为txt文件，后者可以由```analyser.py```解析并可视化。

一次实际记录
```
for complete record...(y/n): y
Squeezed text(4261 lines)[可以双击展开]
==================================================
total rounds are 255
score of player 0 is {1: 2, 2: 4, 3: 1, 4: 2, 5: 2, 6: 1, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0}
score of player 1 is {1: 6, 2: 4, 3: 2, 4: 2, 5: 0, 6: 1, 7: 1, 8: 1, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0}
time of player 0 is 0.022074460983276367
time of player 1 is 0.02318406105041504
player 0 violate
player 1 win
==================================================
save record...(y/n): y
filename: match
```
最后生成match.txt对局记录文件。
