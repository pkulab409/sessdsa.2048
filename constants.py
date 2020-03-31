ROWS = 4                        # 行总数
COLUMNS = 8                     # 列总数
ROUNDS = 100                    # 总回合数
MAXTIME = 0.02                  # 总时间限制
ARRAY = list(range(ROUNDS))     # 随机(?)列表
MAXLEVEL = 14                   # 总级别数

NAMES = {_:str(2**_).zfill(4) for _ in range(MAXLEVEL)}  # 将内在级别转换为显示对象的字典
NAMES[0] = '0000'

INIT_BELONG = [[0 if _ < COLUMNS // 2 else 1 for _ in range(COLUMNS)] for _ in range(ROWS)]  # 初始化领域
INIT_PLATFORM = [[0 for _ in range(COLUMNS)] for _ in range(ROWS)]  # 初始化棋盘

PLAYERS = ['nanami', 'ayase']   # 游戏图片名称
LENGTH = 100                    # 格子的边长
PADX = PADY = 10                # 边界填充的距离
WORD_SIZE = (5, 2)              # 标签大小
FONT = ('Verdana', 40, 'bold')  # 文字字体

COLOR_BACKGROUND = '#92877d'    # 全局背景色
COLOR_NONE = '#9e948a'          # 初始界面方格色

COLOR_CELL = {'+':'#eee4da', '-':'#f2b179'}  # 双方的方格色
COLOR_WORD = {'+':'#776e65', '-':'#f9f6f2'}  # 双方的文字色

KEY_BACKWARD = "\'[\'"    # 回退
KEY_FORWARD = "\']\'"     # 前进
