import os
import random
import tkinter

if os.name == "nt":
    from tkinter import Label, Button
else:
    from tkmacosx import Label, Button


######################################
# TODO:
# 1. 将人类输入抽象为Player类
# 2. 优化代码结构
######################################

class Player:
    def __init__(self):
        pass

    def play(self, board_ln, board_col, numbers, ownership, self_place, player, mode):
        if mode == 0:
            if random.randrange(2):
                ln = random.randrange(board_ln)
                col = random.randrange(board_col * 2)
                i = 0
                while [ln, col] == self_place[player ^ 1] or ownership[ln][col] == player or numbers[ln][col] and i < 200:
                    ln = random.randrange(board_ln)
                    col = random.randrange(board_col * 2)
                    i += 1
                return [ln, col]
            else:
                return self_place[player]
        else:
            return random.randrange(4)


def work(board, player):  # 实际处理移动
    dir_xy = [[1, 0], [-1, 0], [0, 1], [0, -1]]

    def inboard(x, y):
        return x in range(board.ln) and y in range(board.col * 2)

    def move(line, column):
        direction = board.dirAB[player]
        while inboard(line, column):
            lst1 = []
            while inboard(line, column) and board.ownership[line][column] == 1 ^ player:
                line += dir_xy[direction][0]
                column += dir_xy[direction][1]
            start = [line, column]
            while inboard(line, column) and board.ownership[line][column] == 0 ^ player:
                if board.numbers[line][column]:
                    lst1.append(board.numbers[line][column])
                line += dir_xy[direction][0]
                column += dir_xy[direction][1]
            stop = [line, column]
            i = 0
            lst2 = []
            while i < len(lst1) - 1:
                if lst1[i] == lst1[i + 1]:
                    lst2.append(lst1[i] * 2)
                    i += 2
                else:
                    lst2.append(lst1[i])
                    i += 1
            if i == len(lst1) - 1:
                lst2.append(lst1[i])
            while len(lst2) < abs(start[0] + start[1] - stop[0] - stop[1]):
                lst2.append(0)
            temp = [start[0], start[1]]
            while temp != stop:
                board.numbers[temp[0]][temp[1]] = lst2[abs(start[0] + start[1] - temp[0] - temp[1])]
                temp[0] += dir_xy[direction][0]
                temp[1] += dir_xy[direction][1]

    if board.dirAB[player] == 0:
        for col in range(board.col * 2):
            move(0, col)
    elif board.dirAB[player] == 1:
        for col in range(board.col * 2):
            move(board.ln - 1, col)
    elif board.dirAB[player] == 2:
        for ln in range(board.ln):
            move(ln, 0)
    elif board.dirAB[player] == 3:
        for ln in range(board.ln):
            move(ln, board.col * 2 - 1)


class pos_click():  # 处理点击 采用这种写法是tkinter特性使然
    def __init__(self, board, ln, col):
        self.board, self.ln, self.col, self.player = board, ln, col, board.phase

    def proc(self):
        board, ln, col = self.board, self.ln, self.col
        player = board.phase
        if [ln, col] != board.self_place[player ^ 1] and ([ln, col] == board.self_place[player] or not board.numbers[ln][col] and board.phase in [0, 1] and board.ownership[ln][col] ^ player):
            board.numbers[ln][col] = 2
            board.button[ln][col]["text"] = 2
            board.handle_phase()


class dir_select():  # 处理选择方向
    def __init__(self, board, mark, direction):
        self.board, self.mark, self.direction = board, mark, direction

    def proc(self):
        board, mark, direction = self.board, self.mark, self.direction
        if board.phase in [2, 3]:
            if (mark == "A") and (board.phase == 2):
                board.dirAB[0] = direction
                board.handle_phase()
            elif (mark == "B") and (board.phase == 3):
                board.dirAB[1] = direction
                board.handle_phase()


class Board():  # 对于棋盘的处理
    def __init__(self, main_window, ln, col):
        def board_init():
            self.ln, self.col = ln, col
            self.phase = 3
            self.sleep = False
            self.dirAB = [0, 0]
            self.self_place = [None, None]
            self.numbers = [[0 for _ in range(self.col * 2)] for _ in range(self.ln)]
            self.ownership = [[i // self.col for i in range(self.col * 2)] for _ in range(self.ln)]
            self.button = [[None for _ in range(self.col * 2)] for _ in range(self.ln)]
            self.label = Label(main_window, width=30, height=2, bg='white', anchor='se', text="请选择模式")
            self.label.grid(row=0, columnspan=8)
            self.player1 = Player()
            self.player2 = Player()
            for i in range(self.ln):
                for j in range(self.col * 2):
                    self.button[i][j] = Button(main_window, width=5, command=pos_click(self, i, j).proc)
                    self.button[i][j].grid(row=i + 1, column=j)
            Label(main_window, text="").grid(row=self.ln + 2, columnspan=8)
            Button(main_window, text="上", width=5, command=dir_select(self, "A", 0).proc).grid(row=self.ln + 3,
                                                                                               column=0)
            Button(main_window, text="下", width=5, command=dir_select(self, "A", 1).proc).grid(row=self.ln + 3,
                                                                                               column=1)
            Button(main_window, text="左", width=5, command=dir_select(self, "A", 2).proc).grid(row=self.ln + 3,
                                                                                               column=2)
            Button(main_window, text="右", width=5, command=dir_select(self, "A", 3).proc).grid(row=self.ln + 3,
                                                                                               column=3)
            Button(main_window, text="上", width=5, command=dir_select(self, "B", 0).proc).grid(row=self.ln + 3,
                                                                                               column=4)
            Button(main_window, text="下", width=5, command=dir_select(self, "B", 1).proc).grid(row=self.ln + 3,
                                                                                               column=5)
            Button(main_window, text="左", width=5, command=dir_select(self, "B", 2).proc).grid(row=self.ln + 3,
                                                                                               column=6)
            Button(main_window, text="右", width=5, command=dir_select(self, "B", 3).proc).grid(row=self.ln + 3,
                                                                                               column=7)
            self.handle_phase()

        def option():
            def option0():
                self.option = 0
                option_window.destroy()
                board_init()

            def option1():
                self.option = 1
                option_window.destroy()
                board_init()

            def option2():
                self.option = 2
                option_window.destroy()
                board_init()

            def option3():
                def next_phase():
                    self.sleep = False
                    self.handle_phase()

                self.option = 3
                option_window.destroy()
                Button(main_window, text="继续", width=5, command=next_phase).grid(row=ln + 4, column=1)
                board_init()

            option_window = tkinter.Tk()
            self.label = Label(option_window, width=30, height=2, bg='white', anchor='se', text="请选择模式")
            self.label.grid(row=0, columnspan=8)
            Button(option_window, text="左右互搏", width=9, command=option0).grid(row=0, column=0, columnspan=2)
            Button(option_window, text="先手随机", width=9, command=option1).grid(row=0, column=2, columnspan=2)
            Button(option_window, text="后手随机", width=9, command=option2).grid(row=0, column=4, columnspan=2)
            Button(option_window, text="全部随机", width=9, command=option3).grid(row=0, column=6, columnspan=2)

        option()

    def random_place(self, player):
        board = self
        ln = random.randrange(board.ln)
        col = random.randrange(board.col * 2)
        i = 0
        while (board.ownership[ln][col] != player or board.numbers[ln][col]) and i < 200:
            ln = random.randrange(board.ln)
            col = random.randrange(board.col * 2)
            i += 1
        board.self_place[player] = [ln, col]

    def handle_phase(self):  # 具体分为5个阶段，最后一阶段为处理移动的阶段
        board = self
        if board.sleep and board.option == 3 and board.phase == 3:
            return
        board.sleep = True
        board.phase = (board.phase + 1) % 5
        if board.phase == 0:
            board.label["text"] = "A摆放阶段"
            if board.option in [1, 3]:
                pos = board.getPlayer1().play(board.ln, board.col, board.numbers, board.ownership, board.self_place, 0, 0)
                pos_click(board, pos[0], pos[1]).proc()
        elif board.phase == 1:
            board.label["text"] = "B摆放阶段"
            if board.option in [2, 3]:
                pos = board.getPlayer2().play(board.ln, board.col, board.numbers, board.ownership, board.self_place, 1, 0)
                pos_click(board, pos[0], pos[1]).proc()
        elif board.phase == 2:
            board.label["text"] = "A指定方向阶段"
            if board.option in [1, 3]:
                direction = board.getPlayer1().play(board.ln, board.col, board.numbers, board.ownership, board.self_place, 0, 1)
                dir_select(board, "A", direction).proc()
        elif board.phase == 3:
            board.label["text"] = "B指定方向阶段"
            if board.option in [2, 3]:
                direction = board.getPlayer2().play(board.ln, board.col, board.numbers, board.ownership, board.self_place, 1, 1)
                dir_select(board, "B", direction).proc()
        else:
            self.proc_move()
            self.handle_phase()

    def getPlayer1(self):
        return self.player1

    def getPlayer2(self):
        return self.player2

    def proc_move(self):  # 处理移动
        board = self

        def inboard(x, y):
            return x in range(board.ln) and y in range(board.col * 2)

        work(board, 0)
        work(board, 1)
        dirxy = [[-1, 0], [1, 0], [0, -1], [0, 1]]
        numbers = [[None for _ in range(board.col * 2)] for _ in range(board.ln)]
        for ln in range(board.ln):
            for col in range(board.col * 2):
                numbers[ln][col] = board.numbers[ln][col]
        for ln in range(board.ln):
            for col in range(board.col * 2):
                if numbers[ln][col]:
                    owner = board.ownership[ln][col]
                    direction = board.dirAB[owner]
                    dln = ln + dirxy[direction][0]
                    dcol = col + dirxy[direction][1]
                    if inboard(dln, dcol) and numbers[dln][dcol] == 0 and owner != board.ownership[dln][dcol]:
                        board.ownership[dln][dcol] = owner
                        dln -= dirxy[direction][0]
                        dcol -= dirxy[direction][1]
                        while inboard(dln, dcol) and board.ownership[dln][dcol] == owner:
                            board.numbers[dln + dirxy[direction][0]][dcol + dirxy[direction][1]], board.numbers[dln][
                                dcol] = \
                                board.numbers[dln][dcol], 0
                            dln -= dirxy[direction][0]
                            dcol -= dirxy[direction][1]
        for ln in range(board.ln):
            for col in range(board.col * 2):
                if not board.numbers[ln][col] and board.ownership[ln][col] ^ (col // board.col):
                    board.ownership[ln][col] ^= 1
        self.random_place(0)
        self.random_place(1)
        board.refresh()

    def refresh(self):
        for i in range(self.ln):
            for j in range(self.col * 2):
                if self.numbers[i][j]:
                    self.button[i][j]["text"] = str(self.numbers[i][j])
                else:
                    self.button[i][j]["text"] = ""
                if self.ownership[i][j]:
                    self.button[i][j]["bg"] = "#9F9FFF"
                else:
                    self.button[i][j]["bg"] = "#FF9F9F"
                if [i, j] == self.self_place[0]:
                    self.button[i][j]["bg"] = "#FF0000"
                if [i, j] == self.self_place[1]:
                    self.button[i][j]["bg"] = "#0000FF"


def init():
    main_window = tkinter.Tk()
    main_window.title("2048平台")
    main_window.resizable(0, 0)
    Board(main_window, 4, 4)
    main_window.mainloop()


if __name__ == "__main__":
    init()
