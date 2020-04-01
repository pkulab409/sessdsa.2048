import turtle as t

import tkinter,time,decimal,math,string,os

if os.name == "nt":
    from tkinter import Label, Button
else:
    from tkmacosx import Label, Button

def init():
    root=tkinter.Tk()
    root.title("2048平台")
    root.resizable(0,0)
    board=Board(root,4,4)
    root.mainloop()

def phase(board):#具体分为5个阶段，最后一阶段为处理移动的阶段
    board.phase = (board.phase + 1) % 5
    if (board.phase == 0):
        board.label["text"] = "A摆放阶段"
    elif (board.phase == 1):
        board.label["text"] = "B摆放阶段"
    elif (board.phase == 2):
        board.label["text"] = "A指定方向阶段"
    elif (board.phase == 3):
        board.label["text"] = "B指定方向阶段"
    else:
        proc_move(board)
        phase(board)

def proc_move(board):#处理移动
    def inboard(x, y):
        return x in range(board.ln) and y in range(board.col * 2)
    work(board, 0)
    work(board, 1)
    dirxy=[[-1,0],[1,0],[0,-1],[0,1]]
    numbers=[[None for _ in range(board.col * 2)]for _ in range(board.ln)]
    for ln in range(board.ln):
        for col in range(board.col * 2):
            numbers[ln][col]=board.numbers[ln][col]
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
                        board.numbers[dln + dirxy[direction][0]][dcol + dirxy[direction][1]], board.numbers[dln][dcol] = board.numbers[dln][dcol], 0
                        dln -= dirxy[direction][0]
                        dcol -= dirxy[direction][1]
    board.refresh()

def work(board, player):#实际处理移动
    dirxy=[[1,0],[-1,0],[0,1],[0,-1]]
    def inboard(x, y):
        return x in range(board.ln) and y in range(board.col * 2)
    def move(ln, col):
        direction = board.dirAB[player]
        while inboard(ln,col):
            lst1=[]
            while inboard(ln,col) and board.ownership[ln][col] == 1 ^ player:
                ln += dirxy[direction][0]
                col += dirxy[direction][1]
            start = [ln, col]
            while inboard(ln,col) and board.ownership[ln][col] == 0 ^ player:
                if board.numbers[ln][col]:
                    lst1.append(board.numbers[ln][col])
                ln += dirxy[direction][0]
                col += dirxy[direction][1]
            stop = [ln, col]
            i = 0
            lst2 = []
            while i < len(lst1) - 1:
                if lst1[i] == lst1[i+1]:
                    lst2.append(lst1[i] * 2)
                    i += 2
                else:
                    lst2.append(lst1[i])
                    i += 1
            if i == len(lst1) - 1:
                lst2.append(lst1[i])
            while len(lst2) < abs(start[0] + start[1] - stop[0] - stop[1]):
                lst2.append(0)
            temp = [start[0],start[1]]
            while temp != stop:
                board.numbers[temp[0]][temp[1]] = lst2[abs(start[0] + start[1] - temp[0] - temp[1])]
                temp[0] += dirxy[direction][0]
                temp[1] += dirxy[direction][1]
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

class posclick():#处理点击 采用这种写法是tkinter特性使然
    def __init__(self, board, ln, col):
        self.board, self.ln, self.col = board, ln, col
        
    def proc(self):
        board, ln, col = self.board, self.ln, self.col
        if not board.numbers[ln][col] and board.phase in [0,1] and not (board.ownership[ln][col] ^ board.phase):
            board.numbers[ln][col] = 2
            board.button[ln][col]["text"] = 2
            phase(board)

class dirselect():#处理选择方向
    def __init__(self, board, mark, direction):
        self.board, self.mark, self.direction = board, mark, direction
        
    def proc(self):
        board, mark, direction = self.board, self.mark, self.direction
        if board.phase in [2,3]:
            if (mark == "A") and (board.phase == 2):
                board.dirAB[0] = direction
                phase(board)
            elif (mark == "B") and (board.phase == 3):
                board.dirAB[1] = direction
                phase(board)

class Board():#对于棋盘的处理
    def __init__(self, root, ln, col):
        self.ln, self.col = ln, col
        self.phase = 0
        self.dirAB = [0,0]
        self.numbers = [[0 for i in range(self.col * 2)]for i in range(self.ln)]
        self.ownership = [[i // self.col for i in range(self.col * 2)]for i in range(self.ln)]
        self.button = [[None for i in range(self.col * 2)]for i in range(self.ln)]
        self.label = Label(root, width=30, height=2, bg='white', anchor='se', text="A摆放阶段")
        self.label.grid(row=0, columnspan=8)
        for ln in range(self.ln):
            for col in range(self.col * 2):
                self.button[ln][col] = Button(root,width=5,command=posclick(self,ln,col).proc)
                self.button[ln][col].grid(row=ln+1,column=col)
        Label(root,text="").grid(row=self.ln+2,columnspan=8)
        Button(root,text="上",width=5,command=dirselect(self,"A",0).proc).grid(row=self.ln+3,column=0)
        Button(root,text="下",width=5,command=dirselect(self,"A",1).proc).grid(row=self.ln+3,column=1)
        Button(root,text="左",width=5,command=dirselect(self,"A",2).proc).grid(row=self.ln+3,column=2)
        Button(root,text="右",width=5,command=dirselect(self,"A",3).proc).grid(row=self.ln+3,column=3)
        Button(root,text="上",width=5,command=dirselect(self,"B",0).proc).grid(row=self.ln+3,column=4)
        Button(root,text="下",width=5,command=dirselect(self,"B",1).proc).grid(row=self.ln+3,column=5)
        Button(root,text="左",width=5,command=dirselect(self,"B",2).proc).grid(row=self.ln+3,column=6)
        Button(root,text="右",width=5,command=dirselect(self,"B",3).proc).grid(row=self.ln+3,column=7)
        self.refresh()
    
    def refresh(self):
        for i in range(self.ln):
            for j in range(self.col * 2):
                if (self.numbers[i][j]):
                    self.button[i][j]["text"]=str(self.numbers[i][j])
                else:
                    self.button[i][j]["text"]=""
                if (self.ownership[i][j]):
                    self.button[i][j]["bg"]="#9F9FFF"
                else:
                    self.button[i][j]["bg"]="#FF9F9F"

init()
