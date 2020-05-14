# 直播工具

# 顶端为事件栏, 显示当前轮数和超时, 违规, 终局, 胜利, 比分等信息
# 底端为决策栏, 显示当前玩家的决策信息
# 中间为实时棋盘

from tkinter import Frame, Label, CENTER, PhotoImage  # UI

import constants as c
import time


class Live(Frame):
    def __init__(self, mode = 0, func = __import__('round_match').main, playerList = ['player.py' for _ in range(2)]):
        self.mode = mode
        self.func = func
        self.playerList = playerList
        
        
        Frame.__init__(self)
        self.grid()

        self.master.title('UI for reviewing')
        
        self.gridCells = []  # 所有方格

        background = Frame(self, bg=c.COLOR_BACKGROUND)  # 背景
        background.grid()

        bar = Frame(background, bg=c.COLOR_NONE, width=c.LENGTH * c.COLUMNS, height=c.LENGTH)  # 顶端状态栏
        bar.grid(row=0, column=0, columnspan=c.COLUMNS, padx=c.PADX, pady=c.PADY)
        info = Label(bar, text='', bg=c.COLOR_NONE, justify=CENTER, font=c.FONT,
                     width=c.WORD_SIZE[0] * c.COLUMNS, height=c.WORD_SIZE[1])
        info.grid()
        self.topInfo = info

        bar = Frame(background, bg=c.COLOR_NONE, width=c.LENGTH * c.COLUMNS, height=c.LENGTH)  # 底端状态栏
        bar.grid(row=c.ROWS + 1, column=0, columnspan=c.COLUMNS, padx=c.PADX, pady=c.PADY)
        info = Label(bar, text='', bg=c.COLOR_NONE, font=c.FONT, width=c.WORD_SIZE[0] * c.COLUMNS,
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
            self.photos = {'+': [PhotoImage(file='../analyser/pic/%s_%d.png' % (c.PICTURES[0], _)) for _ in range(14)],
                           '-': [PhotoImage(file='../analyser/pic/%s_%d.png' % (c.PICTURES[1], _)) for _ in range(14)]}
            photo = PhotoImage(file='../analyser/pic/unknown.png')
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

        self.start()
        self.process()
        self.mainloop()

    def process(self):
        self.after(100, self.process)
        while not self.queue.empty():
            self.analyse(self.queue.get().log[-1])

    def start(self):
        import queue
        self.queue = queue.Queue()
        import round_match
                
        import threading
        thread = threading.Thread(target = self.func, args = (self.playerList,), kwargs = {'livequeue':self.queue, 'REPEAT': 1})
        thread.setDaemon(True)
        thread.start()
        
    def analyse(self, log):
        # 分析指令
        if log[:2] == '&e':    # 事件在顶端状态栏
            self.topInfo.config(text=log.split(':')[1])
        elif log[:2] == '&d':  # 决策在底端状态栏
            self.topInfo.config(text='round ' + log.split(':')[0][2:])  # 当前轮数
            self.bottomInfo.config(text=log.split(':')[1])
        elif log[:2] == '&p':  # 更新棋盘
            self.topInfo.config(text='round ' + log.split(':')[0][2:])  # 当前轮数
            
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
