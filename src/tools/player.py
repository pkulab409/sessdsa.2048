# 基于随机算法的模版AI
# 此处采取的算法为优先在己方领域下, 己方满则在对方领域随机下

# 参赛队伍的AI要求:
#
# 须写在Player类里
#
# 须实现两个方法:
#
# __init__(self, isFirst, array):
#   -> 初始化
#   -> 参数: isFirst是否先手, 为bool变量, isFirst = True 表示先手
#   -> 参数: array随机序列, 为一个长度等于总回合数的list
#
# output(self, currentRound, board, mode):
#   -> 给出己方的决策(下棋的位置或合并的方向)
#   -> 参数: currentRound当前轮数, 为从0开始的int
#   -> 参数: board棋盘对象
#   -> 参数: mode模式, mode = 'position' 对应位置模式, mode = 'direction' 对应方向模式, 如果为 '_position' 和 '_direction' 表示在对应模式下己方无法给出合法输出
#   -> 返回: 位置模式返回tuple (row, column), row行, 从上到下为0到3的int; column列, 从左到右为0到7的int
#   -> 返回: 方向模式返回direction = 0, 1, 2, 3 对应 上, 下, 左, 右
#   -> 返回: 在己方无法给出合法输出时, 对返回值不作要求
#
# 其余的属性与方法请自行设计


class Player:
    def __init__(self, isFirst, array):
        # 初始化
        self.isFirst = isFirst
        self.array = array

    def output(self, currentRound, board, mode):
        if mode == 'position':  # 给出己方下棋的位置
            another = board.getNext(self.isFirst, currentRound)  # 己方的允许落子点
            if another != (): return another

            available = board.getNone(not self.isFirst)  # 对方的允许落子点
            if not available:   # 整个棋盘已满
                return None
            else:
                from random import choice
                return choice(available)
        elif mode == 'direction':  # 给出己方合并的方向
            from random import shuffle
            directionList = [0, 1, 2, 3]
            shuffle(directionList)
            for direction in directionList:
                if board.move(self.isFirst, direction): return direction
        else:
            return
