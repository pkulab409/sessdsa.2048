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
