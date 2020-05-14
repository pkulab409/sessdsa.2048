# 可视化复盘程序
#
# 按键盘的']', '['键分别对应前进, 回退操作
# 按键盘的n, p对应观看下一局, 上一局操作(next, previous)
#
# 考虑到可扩展性, 内部逻辑采用棋子的级别
#
# 顶端为事件栏, 显示当前轮数和超时, 违规, 终局, 胜利, 比分等信息
# 底端为决策栏, 显示当前玩家的决策信息
# 中间为实时棋盘

from tkinter import Frame, Label, CENTER, PhotoImage  # UI
import constants as c


class GameScreen(Frame):
    def __init__(self, matchList = None, index = 1):
        # matchList = [mode, {'path': path, 'topText': topText, 'bottomText': bottomText}, ...]
        self.matchList = matchList
        self.index = index
        
        if matchList == None:
            while True:  # 加载对局记录
                filename = input('filename: ')
                try:
                    self.log = open('%s.txt' % filename, 'r').read().split('&')  # 读取全部记录并分成单条
                    self.size = len(self.log)
                    break
                except FileNotFoundError:
                    print('%s is not found.' % filename)

            print('=' * 50)
            while True:  # 选择模式
                self.mode = int(input('enter 0 for original mode.\nenter 1 for YuzuSoft mode.\nmode: '))
                if self.mode in range(2):
                    break
                else:
                    print('wrong input.')
        else:
            self.match = self.matchList[index]
            self.log = open(self.match['path'], 'r').read().split('&')  # 读取全部记录并分成单条
            self.size = len(self.log)
            self.mode = self.matchList[0]
            
        topText = self.match['topText'] if matchList and 'topText' in self.match else 'press any key to start'
        bottomText = self.match['bottomText'] if matchList and 'bottomText' in self.match else 'by @SophieARG'

        print('=' * 50)
        declarations = self.log[0].split('\n')
        for declaration in declarations:
            if declaration != '' and declaration[0] != '*':
                print(declaration)  # 打印说明信息

        Frame.__init__(self)
        self.grid()

        self.master.title('UI for reviewing')
        self.master.bind("<Key>", self.press)

        self.gridCells = []  # 所有方格

        background = Frame(self, bg=c.COLOR_BACKGROUND)  # 背景
        background.grid()

        bar = Frame(background, bg=c.COLOR_NONE, width=c.LENGTH * c.COLUMNS, height=c.LENGTH)  # 顶端状态栏
        bar.grid(row=0, column=0, columnspan=c.COLUMNS, padx=c.PADX, pady=c.PADY)
        info = Label(bar, text=topText, bg=c.COLOR_NONE, justify=CENTER, font=c.FONT,
                     width=c.WORD_SIZE[0] * c.COLUMNS, height=c.WORD_SIZE[1])
        info.grid()
        self.topInfo = info

        bar = Frame(background, bg=c.COLOR_NONE, width=c.LENGTH * c.COLUMNS, height=c.LENGTH)  # 底端状态栏
        bar.grid(row=c.ROWS + 1, column=0, columnspan=c.COLUMNS, padx=c.PADX, pady=c.PADY)
        info = Label(bar, text=bottomText, bg=c.COLOR_NONE, font=c.FONT, width=c.WORD_SIZE[0] * c.COLUMNS,
                     height=c.WORD_SIZE[1])
        info.grid()
        self.bottomInfo = info

        if self.mode == 0:  # 2048原版
            for row in range(1, c.ROWS + 1):
                gridRow = []  # 一行方格
                for column in range(c.COLUMNS):
                    cell = Frame(background, bg=c.COLOR_NONE, width=c.LENGTH, height=c.LENGTH)  # 一个方格
                    cell.grid(row=row, column=column, padx=c.PADX, pady=c.PADY)
                    number = Label(cell, text='', bg=c.COLOR_NONE, justify=CENTER, font=c.FONT, width=c.WORD_SIZE[0],
                                   height=c.WORD_SIZE[1])
                    number.grid()
                    gridRow.append(number)
                self.gridCells.append(gridRow)

        if self.mode == 1:  # 柚子社版
            self.photos = {'+': [PhotoImage(file='pic/%s_%d.png' % (c.PICTURES[0], _)) for _ in range(14)],
                           '-': [PhotoImage(file='pic/%s_%d.png' % (c.PICTURES[1], _)) for _ in range(14)]}
            photo = PhotoImage(file='pic/unknown.png')
            for row in range(1, c.ROWS + 1):
                gridRow = []  # 一行方格
                for column in range(c.COLUMNS):
                    cell = Frame(background)  # 一个方格
                    cell.grid(row=row, column=column, padx=c.PADX, pady=c.PADY)
                    number = Label(cell, image=photo)
                    number.grid()
                    gridRow.append(number)
                self.gridCells.append(gridRow)

        self.cur = 0        # 读取单条记录的游标
        self.state = True   # 游标运动的状态, True代表向前

        self.mainloop()

    def analyse(self, log):
        # 分析指令
        if log[0] == 'e':    # 事件在顶端状态栏
            self.topInfo.config(text=log.split(':')[1][:-1])
        elif log[0] == 'd':  # 决策在底端状态栏
            self.topInfo.config(text='round ' + log.split(':')[0][1:])  # 当前轮数
            self.bottomInfo.config(text=log.split(':')[1][:-1])
        elif log[0] == 'p':  # 更新棋盘
            self.topInfo.config(text='round ' + log.split(':')[0][1:])  # 当前轮数
            
            platform = []
            pieces = log.split(':')[1].split()
            for piece in pieces:
                platform.append((piece[0], int(piece[1:])))
            cur = 0

            if self.mode == 0:  # 2048原版
                while cur < c.ROWS * c.COLUMNS:
                    row = cur // c.COLUMNS
                    column = cur % c.COLUMNS
                    belong, number = platform[cur]
                    if number == 0:
                        self.gridCells[row][column].config(text='', bg=c.COLOR_CELL[belong])
                    else:
                        self.gridCells[row][column].config(text=2 ** number, bg=c.COLOR_CELL[belong],
                                                           fg=c.COLOR_WORD[belong])
                    cur += 1

            if self.mode == 1:  # 柚子社版
                while cur < c.ROWS * c.COLUMNS:
                    row = cur // c.COLUMNS
                    column = cur % c.COLUMNS
                    belong, number = platform[cur]
                    self.gridCells[row][column].config(image=self.photos[belong][number])
                    cur += 1

    def press(self, event):
        key = repr(event.char)
        if self.cur == 0:  # 第一条信息
            while True:
                self.cur += 1
                self.analyse(self.log[self.cur])
                if self.cur >= self.size - 1 or self.log[self.cur][0] != 'd':
                    break
        elif key == c.KEY_BACKWARD and self.cur > 1:     # 回退, 更新至决策
            while True:
                while self.log[self.cur - 1][0] == 'e':  # 忽略全部事件
                    self.cur -= 1
                if self.state:
                    if self.log[self.cur - 1][0] == 'd':  
                        self.cur -= 1
                    self.state = False
                self.cur -= 1
                self.analyse(self.log[self.cur])
                if self.cur <= 1 or self.log[self.cur][0] != 'p':
                    break
        elif key == c.KEY_FORWARD and self.cur < self.size - 1:  # 前进, 更新至棋盘
            while True:
                if not self.state:
                    if self.log[self.cur + 1][0] == 'p':
                        self.cur += 1
                    self.state = True
                self.cur += 1
                self.analyse(self.log[self.cur])
                if self.cur >= self.size - 1 or self.log[self.cur][0] != 'd':
                    break
        elif key == "'n'" and self.index != len(self.matchList) - 1:
            self.destroy()
            self.__init__(self.matchList, self.index + 1)
        elif key == "'p'" and self.index != 1:
            self.destroy()
            self.__init__(self.matchList, self.index - 1)


if __name__ == '__main__':
    gamescreen = GameScreen()
