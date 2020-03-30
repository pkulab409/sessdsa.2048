# 可视化复盘程序
#
# 按键盘的向右, 向左方向键分别对应前进, 回退操作
#
# 考虑到可扩展性, 这里显示的是棋子的级别
#
# 顶端为事件栏, 显示当前轮数和超时, 违规, 终局, 胜利, 比分等信息
# 底端为决策栏, 显示当前玩家的决策信息
# 中间为实时棋盘
#
# 回退的时候轮数显示可能有延迟, 是为了减少空间开销
# 有好的解决方案请随意动手
#
# 柚子社天下第一(什么)

from tkinter import Frame, Label, CENTER, PhotoImage    # UI
import constants as c

class GameScreen(Frame):
    def __init__(self):
        filename = input('filename: ')
        self.log = open('%s.txt' % filename, 'r').read().split('&')  # 读取全部记录并分成单条
        self.size = len(self.log)

        declarations = self.log[0].split('\n')
        for declaration in declarations:
            if declaration != '' and declaration[0] != '<': print(declaration)  # 打印说明信息
        
        Frame.__init__(self)
        self.grid()

        self.master.title('UI for reviewing')
        self.master.bind("<Key>", self.press)
        
        self.gridCells = []  # 所有方格
        
        background = Frame(self, bg = c.COLOR_BACKGROUND)  # 背景
        background.grid()

        self.photos = {'+':[PhotoImage(file = 'pic/%s_%d.png' % (c.PLAYERS[0], _)) for _ in range(14)], \
                       '-':[PhotoImage(file = 'pic/%s_%d.png' % (c.PLAYERS[1], _)) for _ in range(14)]}
        
        bar = Frame(background, bg = c.COLOR_NONE, width = c.LENGTH * c.COLUMNS, height = c.LENGTH) # 顶端状态栏
        bar.grid(row = 0, column = 0, columnspan = c.COLUMNS, padx = c.PADX, pady = c.PADY)
        info = Label(bar, text='press any key to start', bg = c.COLOR_NONE, justify = CENTER, font = c.FONT, width = c.WORD_SIZE[0] * c.COLUMNS, height = c.WORD_SIZE[1])
        info.grid()
        self.topInfo = info

        photo = PhotoImage(file = 'pic/unknown.png')
        for row in range(1, c.ROWS + 1):
            gridRow = []     # 一行方格
            for column in range(c.COLUMNS):
                cell = Frame(background)    # 一个方格
                cell.grid(row = row, column = column, padx = c.PADX, pady = c.PADY)
                number = Label(cell, image = photo)
                number.grid()
                gridRow.append(number)
            self.gridCells.append(gridRow)
            
        bar = Frame(background, bg = c.COLOR_NONE, width = c.LENGTH * c.COLUMNS, height = c.LENGTH) # 底端状态栏
        bar.grid(row = c.ROWS + 1, column = 0, columnspan = c.COLUMNS, padx = c.PADX, pady = c.PADY)
        info = Label(bar, text='by @SophieARG', bg = c.COLOR_NONE, font = c.FONT, width = c.WORD_SIZE[0] * c.COLUMNS, height = c.WORD_SIZE[1])
        info.grid()
        self.bottomInfo = info

        self.cur = 0  # 读取单条记录的游标
        
        self.mainloop()
        
    def analyse(self, log):
        # 分析指令
        if log[0] == 'e':
            self.topInfo.config(text = log[2:-1])
        elif log[0] == 'd':
            if 'direction' in log and 'None' not in log:
                log = log.replace(log[-2], {'0':'up', '1':'down', '2':'left', '3':'right'}[log[-2]])  # 换算方向
            self.bottomInfo.config(text = log[2:-1])
        elif log[0] == 'p':
            platform = []
            pieces = log[2:-1].split()
            for piece in pieces:
                platform.append((piece[0], int(piece[1:])))
            cur = 0
            while cur < c.ROWS * c.COLUMNS:
                row = cur // c.COLUMNS
                column = cur % c.COLUMNS
                belong, number = platform[cur]
                self.gridCells[row][column].config(image = self.photos[belong][number])
                cur += 1
                
    def press(self, event):
        key = repr(event.char)
        if self.cur == 0:  # 第一条信息
            while True:
                self.cur += 1
                self.analyse(self.log[self.cur])
                if self.cur >= self.size - 1 or self.log[self.cur][0] == 'p':
                    break
        elif key == "\'\\uf702\'" and self.cur != 1:
            while True:
                self.cur -= 1
                self.analyse(self.log[self.cur])
                if self.cur <= 1 or self.log[self.cur][0] == 'p':
                    break
        elif key == "\'\\uf703\'":
            if self.cur < self.size - 1:
                while True:
                    self.cur += 1
                    self.analyse(self.log[self.cur])
                    if self.cur >= self.size - 1 or self.log[self.cur][0] == 'p':
                        break

gamescreen = GameScreen()
