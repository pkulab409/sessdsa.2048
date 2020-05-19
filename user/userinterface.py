import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

#请注意，本程序仅为本地可视化调试工具，为不会使用或无法使用平台的用户提供帮助，未经过优化，内容非常丑陋，若想详细了解平台原理，请观看平台源代码
#pyqt is totally disastrous

class c1:
    def __init__(self):
        self.MAXTIME = 5     # 最大时间限制
        self.ROUNDS = 500    # 总回合数
        self.REPEAT = 10     # 单循环轮数

        self.ROWS = 4        # 行总数
        self.COLUMNS = 8     # 列总数
        self.MAXLEVEL = 14   # 总级别数

        self.SLEEP = 0.3       # 直播等待时间

        self.ARRAY = list(range(self.ROUNDS))  # 随机(?)列表

        self.NAMES = {_: str(2 ** _).zfill(4) for _ in range(self.MAXLEVEL)}  # 将内在级别转换为显示对象的字典
        self.NAMES[0] = '0000'

        class _DIRECTIONS(list):
            def __init__(self):
                super().__init__(['up', 'down', 'left', 'right'])
            def __getitem__(self, key):
                return super().__getitem__(key) if key in range(4) else 'unknown'
        self.DIRECTIONS = _DIRECTIONS()      # 换算方向的字典
        self.PLAYERS = {True: 'player 0', False: 'player 1'}  # 换算先后手名称的字典

        self.PICTURES = ['nanami', 'ayase']  # 游戏图片名称
        self.LENGTH = 100                    # 格子的边长
        self.PADX = PADY = 10                # 边界填充的距离
        self.WORD_SIZE = (5, 2)              # 标签大小
        self.FONT = ('Verdana', 40, 'bold')  # 文字字体

        self.COLOR_BACKGROUND = '#92877d'    # 全局背景色
        self.COLOR_NONE = '#9e948a'          # 初始界面方格色

        self.COLOR_CELL = {'+': '#eee4da', '-': '#f2b179'}  # 双方的方格色
        self.COLOR_WORD = {'+': '#776e65', '-': '#f9f6f2'}  # 双方的文字色

        self.KEY_BACKWARD = "\'[\'"  # 回退
        self.KEY_FORWARD = "\']\'"   # 前进


c = c1()
# 棋子

from collections import namedtuple

'''
-> 初始化棋子
-> 参数: belong   归属, 为bool, True代表先手
-> 参数: position 位置, 为tuple
-> 参数: value    数值, 为int
'''

Chessman = namedtuple('Chessman', 'belong position value', defaults=(1,))

# 棋盘

class Chessboard:
    def __init__(self, array):
        '''
        -> 初始化棋盘
        '''
        self.array = array  # 随机序列
        self.board = {}  # 棋盘所有棋子
        self.belongs = {True: [], False: []}  # 双方的棋子位置
        self.decision = {True: (), False: ()}  # 双方上一步的决策
        self.time = {True: 0, False: 0}  # 双方剩余的时长
        self.anime = []  # 动画效果
        

    def add(self, belong, position, value = 1, force_change = False):
        '''
        -> 在指定位置下棋
        '''
        if not force_change:
            belong = position[1] < c.COLUMNS // 2  # 重定义棋子的归属
        self.belongs[belong].append(position)
        self.board[position] = Chessman(belong, position, value)

    def move(self, belong, direction):
        '''
        -> 向指定方向合并, 返回是否变化
        '''
        self.anime = []
        def inBoard(position):  # 判断是否在棋盘内
            return position[0] in range(c.ROWS) and position[1] in range(c.COLUMNS)
        def isMine(position):   # 判断是否在领域中
            return belong if position[1] < c.COLUMNS // 2 else not belong
        def theNext(position):  # 返回下一个位置
            delta = [(-1,0), (1,0), (0,-1), (0,1)][direction]
            return (position[0] + delta[0], position[1] + delta[1])
        def conditionalSorted(chessmanList):  # 返回根据不同的条件排序结果
            if direction == 0: return sorted(chessmanList, key = lambda x:x[0], reverse = False)
            if direction == 1: return sorted(chessmanList, key = lambda x:x[0], reverse = True )
            if direction == 2: return sorted(chessmanList, key = lambda x:x[1], reverse = False)
            if direction == 3: return sorted(chessmanList, key = lambda x:x[1], reverse = True )
            return []
        def move_one(chessman, eaten):  # 移动一个棋子并返回是否移动, eaten是已经被吃过的棋子位置
            nowPosition = chessman.position
            nextPosition = theNext(nowPosition)
            while inBoard(nextPosition) and isMine(nextPosition) and nextPosition not in self.board:  # 跳过己方空格
                nowPosition = nextPosition
                nextPosition = theNext(nextPosition)
            if inBoard(nextPosition) and nextPosition in self.board and nextPosition not in eaten \
                    and chessman.value == self.board[nextPosition].value:  # 满足吃棋条件
                self.anime.append(chessman.position + nextPosition)
                self.belongs[belong].remove(chessman.position)
                self.belongs[belong if nextPosition in self.belongs[belong] else not belong].remove(nextPosition)
                self.belongs[belong].append(nextPosition)
                self.board[nextPosition] = Chessman(belong, nextPosition, chessman.value + 1)
                del self.board[chessman.position]
                eaten.append(nextPosition)
                return True
            elif nowPosition != chessman.position:  # 不吃棋但移动了
                self.anime.append(chessman.position + nowPosition)
                self.belongs[belong].remove(chessman.position)
                self.belongs[belong].append(nowPosition)
                self.board[nowPosition] = Chessman(belong, nowPosition, chessman.value)
                del self.board[chessman.position]
                return True
            else:  # 未发生移动
                return False
        eaten = []
        change = False
        for _ in conditionalSorted(self.belongs[belong]):
            if move_one(self.board[_], eaten): change = True
        return change

    def getBelong(self, position):
        '''
        -> 返回归属
        '''
        return self.board[position].belong if position in self.board else position[1] < c.COLUMNS // 2

    def getValue(self, position):
        '''
        -> 返回数值
        '''
        return self.board[position].value if position in self.board else 0

    def getScore(self, belong):
        '''
        -> 返回某方的全部棋子数值列表
        '''
        return sorted(map(lambda x: self.board[x].value, self.belongs[belong]))

    def getNone(self, belong):
        '''
        -> 返回某方的全部空位列表
        '''
        return [(row, column) for row in range(c.ROWS) for column in range(c.COLUMNS) \
                if ((column < c.COLUMNS // 2) == belong) and (row, column) not in self.board]
    
    def getNext(self, belong, currentRound):
        '''
        -> 根据随机序列得到在本方领域允许下棋的位置
        '''
        available = self.getNone(belong)
        if not belong: available.reverse()  # 后手序列翻转
        return available[self.array[currentRound] % len(available)] if available != [] else ()

    def updateDecision(self, belong, decision):
        '''
        -> 更新决策
        '''
        self.decision[belong] = decision

    def getDecision(self, belong):
        '''
        -> 返回上一步的决策信息
        -> 无决策为(), 位置决策为position, 方向决策为(direction,)
        -> 采用同类型返回值是为了和优化库统一接口
        '''
        return self.decision[belong]

    def updateTime(self, belong, time):
        '''
        -> 更新剩余时间
        '''
        self.time[belong] = time

    def getTime(self, belong):
        '''
        -> 返回剩余时间
        '''
        return self.time[belong]

    def getAnime(self):
        '''
        -> 返回动画效果辅助信息
        '''
        return self.anime

    def copy(self):
        '''
        -> 返回一个对象拷贝
        '''
        new = Chessboard(self.array)
        new.board = self.board.copy()
        new.belongs[True] = self.belongs[True].copy()
        new.belongs[False] = self.belongs[False].copy()
        new.decision = self.decision.copy()
        new.time = self.time.copy()
        new.anime = self.anime.copy()
        return new

    def __repr__(self):
        '''
        -> 打印棋盘, + 代表先手, - 代表后手
        '''       
        return '\n'.join([' '.join([('+' if self.getBelong((row, column)) else '-') + str(self.getValue((row, column))).zfill(2) \
                                   for column in range(c.COLUMNS)]) \
                         for row in range(c.ROWS)])
    __str__ = __repr__


class defaultplayer:
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
        else:  # 给出己方合并的方向
            from random import shuffle
            directionList = [0, 1, 2, 3]
            shuffle(directionList)
            for direction in directionList:
                if board.move(self.isFirst, direction): return direction


class gui:
    class Ui_MainWindow(object):
        def setupUi(self, MainWindow):
            MainWindow.setObjectName("MainWindow")
            MainWindow.resize(740, 655)
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
            MainWindow.setSizePolicy(sizePolicy)
            MainWindow.setMinimumSize(QtCore.QSize(600, 450))
            MainWindow.setMaximumSize(QtCore.QSize(1200, 900))
            self.centralwidget = QtWidgets.QWidget(MainWindow)
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
            self.centralwidget.setSizePolicy(sizePolicy)
            self.centralwidget.setMinimumSize(QtCore.QSize(600, 450))
            self.centralwidget.setObjectName("centralwidget")
            self.gridLayoutWidget = QtWidgets.QWidget(self.centralwidget)
            self.gridLayoutWidget.setGeometry(QtCore.QRect(0, 50, 741, 361))
            self.gridLayoutWidget.setObjectName("gridLayoutWidget")
            self.chessboard = QtWidgets.QGridLayout(self.gridLayoutWidget)
            self.chessboard.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
            self.chessboard.setContentsMargins(0, 0, 0, 0)
            self.chessboard.setSpacing(0)
            self.chessboard.setObjectName("chessboard")
            self.roundnumber = QtWidgets.QLabel(self.centralwidget)
            self.roundnumber.setGeometry(QtCore.QRect(50, 20, 51, 20))
            self.roundnumber.setObjectName("roundnumber")
            self.rounddisplay = QtWidgets.QLabel(self.centralwidget)
            self.rounddisplay.setGeometry(QtCore.QRect(100, 20, 41, 20))
            self.rounddisplay.setText("")
            self.rounddisplay.setObjectName("rounddisplay")
            self.up = QtWidgets.QPushButton(self.centralwidget)
            self.up.setEnabled(False)
            self.up.setGeometry(QtCore.QRect(130, 410, 61, 61))
            self.up.setObjectName("up")
            self.left = QtWidgets.QPushButton(self.centralwidget)
            self.left.setEnabled(False)
            self.left.setGeometry(QtCore.QRect(70, 470, 61, 61))
            self.left.setObjectName("left")
            self.right = QtWidgets.QPushButton(self.centralwidget)
            self.right.setEnabled(False)
            self.right.setGeometry(QtCore.QRect(190, 470, 61, 61))
            self.right.setObjectName("right")
            self.down = QtWidgets.QPushButton(self.centralwidget)
            self.down.setEnabled(False)
            self.down.setGeometry(QtCore.QRect(130, 530, 61, 61))
            self.down.setObjectName("down")
            self.statelabel = QtWidgets.QLabel(self.centralwidget)
            self.statelabel.setGeometry(QtCore.QRect(210, 10, 371, 41))
            self.statelabel.setText("")
            self.statelabel.setObjectName("statelabel")
            self.selectlabel = QtWidgets.QLabel(self.centralwidget)
            self.selectlabel.setGeometry(QtCore.QRect(280, 470, 411, 61))
            self.selectlabel.setText("")
            self.selectlabel.setObjectName("selectlabel")
            MainWindow.setCentralWidget(self.centralwidget)
            self.menubar = QtWidgets.QMenuBar(MainWindow)
            self.menubar.setGeometry(QtCore.QRect(0, 0, 740, 18))
            self.menubar.setObjectName("menubar")
            self.menu = QtWidgets.QMenu(self.menubar)
            self.menu.setObjectName("menu")
            self.mode = QtWidgets.QMenu(self.menu)
            self.mode.setObjectName("mode")
            self.menu_2 = QtWidgets.QMenu(self.menubar)
            self.menu_2.setObjectName("menu_2")
            self.menu_3 = QtWidgets.QMenu(self.menubar)
            self.menu_3.setObjectName("menu_3")
            MainWindow.setMenuBar(self.menubar)
            self.statusbar = QtWidgets.QStatusBar(MainWindow)
            self.statusbar.setObjectName("statusbar")
            MainWindow.setStatusBar(self.statusbar)
            self.restart = QtWidgets.QAction(MainWindow)
            self.restart.setObjectName("restart")
            self.action_2 = QtWidgets.QAction(MainWindow)
            self.action_2.setObjectName("action_2")
            self.about = QtWidgets.QAction(MainWindow)
            self.about.setObjectName("about")
            self.mode1 = QtWidgets.QAction(MainWindow)
            self.mode1.setObjectName("mode1")
            self.mode2 = QtWidgets.QAction(MainWindow)
            self.mode2.setEnabled(True)
            self.mode2.setObjectName("mode2")
            self.mode3 = QtWidgets.QAction(MainWindow)
            self.mode3.setEnabled(True)
            self.mode3.setObjectName("mode3")
            self.mode4 = QtWidgets.QAction(MainWindow)
            self.mode4.setEnabled(True)
            self.mode4.setObjectName("mode4")
            self.ai_set = QtWidgets.QAction(MainWindow)
            self.ai_set.setObjectName("ai_set")
            self.undo = QtWidgets.QAction(MainWindow)
            self.undo.setEnabled(False)
            self.undo.setObjectName("undo")
            self.save_current = QtWidgets.QAction(MainWindow)
            self.save_current.setEnabled(False)
            self.save_current.setObjectName("save_current")
            self.start = QtWidgets.QAction(MainWindow)
            self.start.setObjectName("start")
            self.action88 = QtWidgets.QAction(MainWindow)
            self.action88.setObjectName("action88")
            self.settings_2 = QtWidgets.QAction(MainWindow)
            self.settings_2.setObjectName("settings_2")
            self.settings = QtWidgets.QAction(MainWindow)
            self.settings.setObjectName("settings")
            self.match_settings = QtWidgets.QAction(MainWindow)
            self.match_settings.setObjectName("match_settings")
            self.loadfile = QtWidgets.QAction(MainWindow)
            self.loadfile.setEnabled(True)
            self.loadfile.setObjectName("loadfile")
            self.load_from_net = QtWidgets.QAction(MainWindow)
            self.load_from_net.setEnabled(True)
            self.load_from_net.setObjectName("load_from_net")
            self.download_from_net = QtWidgets.QAction(MainWindow)
            self.download_from_net.setEnabled(True)
            self.download_from_net.setObjectName("download_from_net")
            self.continue_match = QtWidgets.QAction(MainWindow)
            self.continue_match.setEnabled(False)
            self.continue_match.setObjectName("continue_match")
            self.mode.addAction(self.mode1)
            self.mode.addAction(self.mode2)
            self.mode.addAction(self.mode3)
            self.mode.addAction(self.mode4)
            self.menu.addAction(self.mode.menuAction())
            self.menu.addAction(self.ai_set)
            self.menu.addSeparator()
            self.menu.addAction(self.match_settings)
            self.menu_2.addAction(self.start)
            self.menu_2.addAction(self.undo)
            self.menu_2.addSeparator()
            self.menu_2.addAction(self.save_current)
            self.menu_2.addAction(self.loadfile)
            self.menu_2.addAction(self.load_from_net)
            self.menu_2.addAction(self.download_from_net)
            self.menu_2.addAction(self.continue_match)
            self.menu_3.addAction(self.about)
            self.menubar.addAction(self.menu.menuAction())
            self.menubar.addAction(self.menu_2.menuAction())
            self.menubar.addAction(self.menu_3.menuAction())

            self.retranslateUi(MainWindow)
            QtCore.QMetaObject.connectSlotsByName(MainWindow)

        def retranslateUi(self, MainWindow):
            _translate = QtCore.QCoreApplication.translate
            MainWindow.setWindowTitle(_translate("MainWindow", "调试工具"))
            self.roundnumber.setText(_translate("MainWindow", "轮数"))
            self.up.setText(_translate("MainWindow", "上"))
            self.left.setText(_translate("MainWindow", "左"))
            self.right.setText(_translate("MainWindow", "右"))
            self.down.setText(_translate("MainWindow", "下"))
            self.menu.setTitle(_translate("MainWindow", "菜单"))
            self.mode.setTitle(_translate("MainWindow", "模式"))
            self.menu_2.setTitle(_translate("MainWindow", "操作"))
            self.menu_3.setTitle(_translate("MainWindow", "帮助"))
            self.restart.setText(_translate("MainWindow", "重新开始"))
            self.action_2.setText(_translate("MainWindow", "重新开始"))
            self.about.setText(_translate("MainWindow", "说明"))
            self.about.setShortcut(_translate("MainWindow", "Ctrl+H"))
            self.mode1.setText(_translate("MainWindow", "电脑-电脑"))
            self.mode1.setShortcut(_translate("MainWindow", "Ctrl+1"))
            self.mode2.setText(_translate("MainWindow", "电脑-玩家"))
            self.mode2.setShortcut(_translate("MainWindow", "Ctrl+2"))
            self.mode3.setText(_translate("MainWindow", "玩家-电脑"))
            self.mode3.setShortcut(_translate("MainWindow", "Ctrl+3"))
            self.mode4.setText(_translate("MainWindow", "玩家-玩家"))
            self.mode4.setShortcut(_translate("MainWindow", "Ctrl+4"))
            self.ai_set.setText(_translate("MainWindow", "管理ai"))
            self.ai_set.setShortcut(_translate("MainWindow", "Ctrl+O"))
            self.undo.setText(_translate("MainWindow", "撤销上一步移动"))
            self.undo.setShortcut(_translate("MainWindow", "Ctrl+Z"))
            self.save_current.setText(_translate("MainWindow", "保存当前对局记录"))
            self.save_current.setShortcut(_translate("MainWindow", "Ctrl+S"))
            self.start.setText(_translate("MainWindow", "开始"))
            self.start.setShortcut(_translate("MainWindow", "Ctrl+R"))
            self.action88.setText(_translate("MainWindow", "88"))
            self.settings_2.setText(_translate("MainWindow", "2"))
            self.settings.setText(_translate("MainWindow", "设置"))
            self.match_settings.setText(_translate("MainWindow", "设置"))
            self.match_settings.setIconText(_translate("MainWindow", "设置"))
            self.loadfile.setText(_translate("MainWindow", "读取记录"))
            self.loadfile.setShortcut(_translate("MainWindow", "Ctrl+L"))
            self.load_from_net.setText(_translate("MainWindow", "从天梯读取记录"))
            self.download_from_net.setText(_translate("MainWindow", "从天梯下载记录"))
            self.continue_match.setText(_translate("MainWindow", "在此继续游戏"))

class dialog:
    class Ui_settings(object):
        def setupUi(self, settings):
            settings.setObjectName("settings")
            settings.resize(289, 373)
            self.layoutWidget = QtWidgets.QWidget(settings)
            self.layoutWidget.setGeometry(QtCore.QRect(30, 20, 221, 271))
            self.layoutWidget.setObjectName("layoutWidget")
            self.gridLayout = QtWidgets.QGridLayout(self.layoutWidget)
            self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
            self.gridLayout.setContentsMargins(0, 0, 0, 0)
            self.gridLayout.setObjectName("gridLayout")
            self.label_4 = QtWidgets.QLabel(self.layoutWidget)
            self.label_4.setObjectName("label_4")
            self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)
            self.label_3 = QtWidgets.QLabel(self.layoutWidget)
            self.label_3.setObjectName("label_3")
            self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
            self.checkBox_3 = QtWidgets.QCheckBox(self.layoutWidget)
            self.checkBox_3.setMaximumSize(QtCore.QSize(20, 20))
            self.checkBox_3.setText("")
            self.checkBox_3.setObjectName("checkBox_3")
            self.gridLayout.addWidget(self.checkBox_3, 2, 1, 1, 1, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
            self.checkBox_2 = QtWidgets.QCheckBox(self.layoutWidget)
            self.checkBox_2.setMaximumSize(QtCore.QSize(20, 20))
            self.checkBox_2.setText("")
            self.checkBox_2.setObjectName("checkBox_2")
            self.gridLayout.addWidget(self.checkBox_2, 1, 1, 1, 1, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
            self.checkBox = QtWidgets.QCheckBox(self.layoutWidget)
            self.checkBox.setMaximumSize(QtCore.QSize(20, 20))
            self.checkBox.setText("")
            self.checkBox.setObjectName("checkBox")
            self.gridLayout.addWidget(self.checkBox, 0, 1, 1, 1, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
            self.label_2 = QtWidgets.QLabel(self.layoutWidget)
            self.label_2.setObjectName("label_2")
            self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
            self.label_5 = QtWidgets.QLabel(self.layoutWidget)
            self.label_5.setObjectName("label_5")
            self.gridLayout.addWidget(self.label_5, 4, 0, 1, 1)
            self.textEdit_2 = QtWidgets.QTextEdit(self.layoutWidget)
            self.textEdit_2.setMinimumSize(QtCore.QSize(80, 36))
            self.textEdit_2.setMaximumSize(QtCore.QSize(16777215, 36))
            self.textEdit_2.setObjectName("textEdit_2")
            self.gridLayout.addWidget(self.textEdit_2, 4, 1, 1, 1)
            self.textEdit_3 = QtWidgets.QTextEdit(self.layoutWidget)
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Ignored)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.textEdit_3.sizePolicy().hasHeightForWidth())
            self.textEdit_3.setSizePolicy(sizePolicy)
            self.textEdit_3.setMinimumSize(QtCore.QSize(80, 36))
            self.textEdit_3.setMaximumSize(QtCore.QSize(16777215, 36))
            self.textEdit_3.setObjectName("textEdit_3")
            self.gridLayout.addWidget(self.textEdit_3, 5, 1, 1, 1)
            self.textEdit = QtWidgets.QTextEdit(self.layoutWidget)
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Ignored)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.textEdit.sizePolicy().hasHeightForWidth())
            self.textEdit.setSizePolicy(sizePolicy)
            self.textEdit.setMinimumSize(QtCore.QSize(80, 36))
            self.textEdit.setMaximumSize(QtCore.QSize(16777215, 36))
            self.textEdit.setObjectName("textEdit")
            self.gridLayout.addWidget(self.textEdit, 3, 1, 1, 1)
            self.label_6 = QtWidgets.QLabel(self.layoutWidget)
            self.label_6.setObjectName("label_6")
            self.gridLayout.addWidget(self.label_6, 5, 0, 1, 1)
            self.label = QtWidgets.QLabel(self.layoutWidget)
            self.label.setObjectName("label")
            self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
            self.label_7 = QtWidgets.QLabel(self.layoutWidget)
            self.label_7.setObjectName("label_7")
            self.gridLayout.addWidget(self.label_7, 6, 0, 1, 1)
            self.checkBox_5 = QtWidgets.QCheckBox(self.layoutWidget)
            self.checkBox_5.setMaximumSize(QtCore.QSize(20, 20))
            self.checkBox_5.setText("")
            self.checkBox_5.setObjectName("checkBox_5")
            self.gridLayout.addWidget(self.checkBox_5, 6, 1, 1, 1, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
            self.pushButton = QtWidgets.QPushButton(settings)
            self.pushButton.setGeometry(QtCore.QRect(110, 320, 131, 31))
            self.pushButton.setObjectName("pushButton")

            self.retranslateUi(settings)
            QtCore.QMetaObject.connectSlotsByName(settings)

        def retranslateUi(self, settings):
            _translate = QtCore.QCoreApplication.translate
            settings.setWindowTitle(_translate("settings", "设置"))
            self.label_4.setText(_translate("settings", "总用时限制"))
            self.label_3.setText(_translate("settings", "打印报错信息"))
            self.label_2.setText(_translate("settings", "生成统计报告"))
            self.label_5.setText(_translate("settings", "最大回合数"))
            self.label_6.setText(_translate("settings", "重复次数"))
            self.label.setText(_translate("settings", "保存对局记录"))
            self.label_7.setText(_translate("settings", "非法操作反馈"))
            self.pushButton.setText(_translate("settings", "保存并退出"))

#以下基于plat.py,analyser.py和round_match.py

import time


# 平台


pos, dirt, phase, plat_cur, statelabel, MainWindow = None, None, None, None, None, None


class Platform:
    def __init__(self, states, match, livequeue, toSave, MAXTIME, ROUNDS, BOARDXXX = None):
        '''
        初始化
        -> 参数: states 保存先后手方模块元信息的字典
        -> 参数: match 比赛名称
        -> 参数: livequeue 直播通信队列
        -> 参数: toSave 是否保存为记录文件
        -> 参数: MAXTIME 最大时间限制
        -> 参数: ROUNDS 总回合数
        '''
        
        # 生成覆盖随机序列
        from random import randrange
        c.ARRAY = tuple(randrange(720720) for _ in range(ROUNDS))
        
        # 超时异常
        class Timeout(Exception):
            pass

        # 返回值
        class Result:
            def __init__(self, func):
                self.func = func
                self.result = Timeout()
            def call(self, *args, **kwargs):
                self.result = self.func(*args, **kwargs)
                
        # 超时退出的装饰器
        import threading
        def timeoutManager(maxtime, isFirst):
            def decorator(func):
                def wrappedFunc(*args, **kwargs):
                    result = Result(func)
                    thread = threading.Thread(target = result.call, args = (*args, ), kwargs = {**kwargs})
                    thread.setDaemon(True)
                    thread.start()
                    thread.join(maxtime - self.states[isFirst]['time'])
                    if isinstance(result.result, Timeout): self.states[isFirst]['time'] = maxtime
                    return result.result
                return wrappedFunc
            return decorator
        
        # 监测运行状态的装饰器
        import traceback
        def stateManager(isFirst):
            def decorator(func):
                @timeoutManager(MAXTIME * 1.1, isFirst)
                def wrappedFunc(*args, **kwargs):
                    try:
                        begin = time.perf_counter()
                        result = func(*args, **kwargs)
                        end = time.perf_counter()
                        self.states[isFirst]['time'] += end - begin
                    except:
                        result = None
                        self.states[isFirst]['error'] = True
                        self.states[isFirst]['exception'] = traceback.format_exc()
                    return result
                return wrappedFunc
            return decorator

        # 重载对象方法
        for isFirst in [True, False]:
            if states[isFirst]['player'] == 'human':
                continue
            states[isFirst]['player'].__init__ = stateManager(isFirst)(states[isFirst]['player'].__init__)
            states[isFirst]['player'].output = stateManager(isFirst)(states[isFirst]['player'].output)


        # 构建一个日志类, 可以实现直播功能
        class Log(list):
            def __init__(self, parent):
                list.__init__(self, [])
                self.parent = parent
                Log.add = Log._add if parent.livequeue != None else list.append

            def _add(self, log):
                self.append(log)
                self.parent.livequeue.put(self.parent)
                time.sleep(c.SLEEP)
                
        self.states = states                # 参赛AI运行状态
        self.match = match                  # 比赛名称
        self.livequeue = livequeue          # 直播工具
        self.toSave = toSave                # 保存记录文件
        self.maxtime = MAXTIME              # 最大时间限制
        self.rounds = ROUNDS                # 总回合数
        self.winner = None                  # 胜利者
        self.violator = None                # 违规者
        self.timeout = None                 # 超时者
        self.error = None                   # 报错者
        self.currentRound = 0               # 当前轮数
        self.change = False                 # 监控棋盘是否改变
        self.next = (None, None)            # 按照随机序列得到的下一个位置
        self.board = Chessboard(c.ARRAY)  # 棋盘
        self.log = Log(self)                # 日志, &d 决策 decision, &p 棋盘 platform, &e 事件 event
        
        if BOARDXXX != None:
            for row in range(c.ROWS):
                for column in range(c.COLUMNS):
                    if BOARDXXX[row][column][1]:
                        self.board.add(BOARDXXX[row][column][0] == '+', (row, column), BOARDXXX[row][column][1], True)
                        

    def play(self):
        '''
        一局比赛, 返回player表现报告
        '''
        
        for isFirst in [True, False]:
            if self.states[isFirst]['player'] == 'human':
                continue
            self.states[isFirst]['player'].__init__(isFirst, c.ARRAY)
            
        # 检查双方是否合法加载
        if mode == 1:
            fail = [self.checkState(True), self.checkState(False)]
            if sum(fail) == 0:  # 双方合法加载
                self.start()
            elif sum(fail) == 1:  # 一方合法加载
                self.winner = not fail[0]
            else:  # 双方非法加载
                if self.timeout == None:
                    self.error = 'both'
                if self.error == None:
                    self.timeout = 'both'

            self.save()  # 计分并保存
                
            return {True:  {'index': self.states[True]['index'],
                            'win': self.winner == True,
                            'lose': self.winner == False,
                            'violate': self.violator == True,
                            'timeout': self.timeout in [True, 'both'],
                            'error': self.error in [True, 'both'],
                            'time': self.states[True]['time'] - self.states[True]['time0'],
                            'exception': self.states[True]['exception']},
                    False: {'index': self.states[False]['index'],
                            'win': self.winner == False,
                            'lose': self.winner == True,
                            'violate': self.violator == False,
                            'timeout': self.timeout in [False, 'both'],
                            'error': self.error in [False, 'both'],
                            'time': self.states[False]['time'] - self.states[False]['time0'],
                            'exception': self.states[False]['exception']},
                    'name': self.name,
                    'rounds': self.currentRound}
        else:
            self.phase = 0
            self.involved_play(0)
        
              
    def start(self):
        '''
        进行比赛
        '''
        def if_position(isFirst, currentRound):
            if not (self.board.getNone(True) == [] and self.board.getNone(False) == []): return True
            self.board.updateTime(isFirst, self.maxtime - self.states[isFirst]['time'])  # 更新剩余时间
            self.states[isFirst]['player'].output(currentRound, self.board.copy(), '_position')  # 获取输出
            self.board.updateDecision(isFirst, ())  # 更新决策
            return False

        def if_direction(isFirst, currentRound):
            for _ in range(4):
                if self.board.copy().move(isFirst, _): return True
            self.board.updateTime(isFirst, self.maxtime - self.states[isFirst]['time'])  # 更新剩余时间
            self.states[isFirst]['player'].output(currentRound, self.board.copy(), '_direction')  # 获取输出
            self.board.updateDecision(isFirst, ())  # 更新决策
            return False
            
        def get_position(isFirst, currentRound):
            self.next = self.board.getNext(isFirst, currentRound)  # 按照随机序列得到下一个位置
            self.board.updateTime(isFirst, self.maxtime - self.states[isFirst]['time'])  # 更新剩余时间
            position = self.states[isFirst]['player'].output(currentRound, self.board.copy(), 'position')  # 获取输出
            if self.checkState(isFirst): return True  # 判断运行状态
            self.log.add('&d%d:%s set position %s' % (currentRound, c.PLAYERS[isFirst], str(position)))  # 记录
            if self.checkViolate(isFirst, 'position', position): return True  # 判断是否违规
            self.board.add(isFirst, position)  # 更新棋盘
            self.board.updateDecision(isFirst, position)  # 更新决策
            self.log.add('&p%d:\n' % currentRound + self.board.__repr__())  # 记录
            return False

        def get_direction(isFirst, currentRound):
            self.board.updateTime(isFirst, self.maxtime - self.states[isFirst]['time'])  # 更新剩余时间
            direction = self.states[isFirst]['player'].output(currentRound, self.board.copy(), 'direction')  # 获取输出
            if self.checkState(isFirst): return True  # 判断运行状态
            self.log.add('&d%d:%s set direction %s' % (currentRound, c.PLAYERS[isFirst], c.DIRECTIONS[direction]))  # 记录
            self.change = self.board.move(isFirst, direction)  # 更新棋盘
            self.board.updateDecision(isFirst, (direction,))  # 更新决策
            if self.checkViolate(isFirst, 'direction', direction): return True  # 判断是否违规
            self.log.add('&p%d:\n' % currentRound + self.board.__repr__())  # 记录
            return False
                
        # 进行比赛
        for _ in range(self.rounds):
            if if_position(True, _) and get_position(True, _): break
            if if_position(False, _) and get_position(False, _): break
            if if_direction(True, _) and get_direction(True, _): break
            if if_direction(False, _) and get_direction(False, _): break

        # 记录总轮数
        self.currentRound = _ + 1
        
        # 得到winner
        for _ in (self.timeout, self.violator, self.error):
            if _ != None:
                self.winner = not _
                self.log.add('&e:%s win' % (c.PLAYERS[self.winner]))
    def human_get_position(self, isFirst):
        global pos
        currentRound = self.currentRound
        position = pos
        pos = None
        statelabel.setText(("player1" if isFirst else "player2") + " choose position " + str(position))
        if self.checkViolate(isFirst, 'position', position):
            self.violator = None
            return False
        else:
            self.board.add(isFirst, position)
            self.board.updateDecision(isFirst, position)
            self.log.add('&d%d:%s set position %s' % (currentRound, c.PLAYERS[isFirst], str(position)))
            self.log.add('&p%d:\n' % currentRound + self.board.__repr__())
            return True
    def human_get_direction(self, isFirst):
        global dirt
        currentRound = self.currentRound
        direction = dirt
        dirt = None
        statelabel.setText(("player1" if isFirst else "player2") + " choose direction " + str(direction))
        self.change = self.board.move(isFirst, direction)
        if self.checkViolate(isFirst, 'direction', direction):
            self.violator = None
            return False
        else:
            self.board.updateDecision(isFirst, (direction,))  # 更新决策
            self.log.add('&d%d:%s set direction %s' % (currentRound, c.PLAYERS[isFirst], c.DIRECTIONS[direction]))
            self.log.add('&p%d:\n' % currentRound + self.board.__repr__())
            return True
    def involved_play(self, currentRound):
        def if_position(isFirst):
            if not (self.board.getNone(True) == [] and self.board.getNone(False) == []): return True
            if self.states[isFirst]['player'] != 'human':
                self.board.updateTime(isFirst, self.maxtime - self.states[isFirst]['time'])  # 更新剩余时间
                self.states[isFirst]['player'].output(currentRound, self.board.copy(), '_position')  # 获取输出
            self.board.updateDecision(isFirst, ())  # 更新决策
            return False

        def if_direction(isFirst):
            for _ in range(4):
                if self.board.copy().move(isFirst, _): return True
            if self.states[isFirst]['player'] != 'human':
                self.board.updateTime(isFirst, self.maxtime - self.states[isFirst]['time'])  # 更新剩余时间
                self.states[isFirst]['player'].output(currentRound, self.board.copy(), '_direction')  # 获取输出
            self.board.updateDecision(isFirst, ())  # 更新决策
            return False
            
        def get_position(isFirst):
            self.next = self.board.getNext(isFirst, currentRound)  # 按照随机序列得到下一个位置
            self.board.updateTime(isFirst, self.maxtime - self.states[isFirst]['time'])  # 更新剩余时间
            position = self.states[isFirst]['player'].output(currentRound, self.board.copy(), 'position')  # 获取输出
            if self.checkState(isFirst): return True  # 判断运行状态
            self.log.add('&d%d:%s set position %s' % (currentRound, c.PLAYERS[isFirst], str(position)))  # 记录
            if self.checkViolate(isFirst, 'position', position): return True  # 判断是否违规
            self.board.add(isFirst, position)  # 更新棋盘
            self.board.updateDecision(isFirst, position)  # 更新决策
            self.log.add('&p%d:\n' % currentRound + self.board.__repr__())  # 记录
            return False
        
        def get_direction(isFirst):
            self.board.updateTime(isFirst, self.maxtime - self.states[isFirst]['time'])  # 更新剩余时间
            direction = self.states[isFirst]['player'].output(currentRound, self.board.copy(), 'direction')  # 获取输出
            statelabel.setText(("player1" if isFirst else "player2") + " choose direction " + str(direction))
            if self.checkState(isFirst): return True  # 判断运行状态
            self.log.add('&d%d:%s set direction %s' % (currentRound, c.PLAYERS[isFirst], c.DIRECTIONS[direction]))  # 记录
            self.change = self.board.move(isFirst, direction)  # 更新棋盘
            self.board.updateDecision(isFirst, (direction,))  # 更新决策
            if self.checkViolate(isFirst, 'direction', direction): return True  # 判断是否违规
            self.log.add('&p%d:\n' % currentRound + self.board.__repr__())  # 记录
            return False
        
        def endstage():
            self.currentRound = currentRound + 1
            
            # 得到winner
            for _ in (self.timeout, self.violator, self.error):
                if _ != None:
                    self.winner = not _
                    self.log.add('&e:%s win' % (c.PLAYERS[self.winner]))
                
        # 进行比赛
        if currentRound < self.rounds:
            self.currentRound = currentRound
            if self.phase == 0:
                if not if_position(True):
                    self.phase = 1
                    self.involved_play(currentRound)
                    return
                if self.states[True]['player'] == 'human':
                    self.next = self.board.getNext(True, currentRound)
                    MainWindow.drawboard(currentRound, self.log[-2] if len(self.log) else "", self.board)
                    return
                else:
                    if get_position(True):
                        endstage()
                        return
                    self.phase = 1
                    self.involved_play(currentRound)
            if self.phase == 1:
                if not if_position(False):
                    self.phase = 2
                    self.involved_play(currentRound)
                    return
                if self.states[False]['player'] == 'human':
                    self.next = self.board.getNext(False, currentRound)
                    MainWindow.drawboard(currentRound, self.log[-2], self.board)
                    return
                else:
                    if if_position(False) and get_position(False):
                        endstage()
                        return
                    self.phase = 2
                    self.involved_play(currentRound)
            if self.phase == 2:
                if not if_direction(True):
                    self.phase = 3
                    self.involved_play(currentRound)
                    return
                if self.states[True]['player'] == 'human':
                    MainWindow.drawboard(currentRound, self.log[-2], self.board)
                    return
                else:
                    if get_direction(True):
                        endstage()
                        return
                    self.phase = 3
                    self.involved_play(currentRound)
            if self.phase == 3:
                if not if_direction(False):
                    self.phase = 4
                    self.involved_play(currentRound)
                    return
                if self.states[False]['player'] == 'human':
                    MainWindow.drawboard(currentRound, self.log[-2], self.board)
                    return
                else:
                    if get_direction(False):
                        endstage()
                        return
                    self.phase = 4
                    self.involved_play(currentRound)
            if self.phase == 4:
                self.phase = 0
                self.involved_play(currentRound + 1)
        else:
            endstage()
    
    def undo(self):
        if self.currentRound > 1:
            x = len(self.log) - 2
            while int(self.log[x].split(':')[0][2:]) >= self.currentRound - 1:
                x -= 2
                self.log.pop()
                self.log.pop()
            platform = []
            pieces = self.log[x + 1].split(':')[1].split()
            for piece in pieces:
                platform.append((piece[0], int(piece[1:])))
            cur = 0
            BOARDXXX = [[None for _ in range(c.COLUMNS)] for _ in range(c.ROWS)]
            while cur < c.ROWS * c.COLUMNS:
                row = cur // c.COLUMNS
                column = cur % c.COLUMNS
                belong, number = platform[cur]
                BOARDXXX[row][column] = (belong, number)
                cur += 1
            self.board = Chessboard(c.ARRAY)
            for row in range(c.ROWS):
                for column in range(c.COLUMNS):
                    if BOARDXXX[row][column][1]:
                        self.board.add(BOARDXXX[row][column][0] == '+', (row, column), BOARDXXX[row][column][1], True)
            MainWindow.drawboard(self.currentRound - 1, "撤销", self.board)
            self.phase = 0
            self.involved_play(self.currentRound - 1)
        else:
            self.board = Chessboard(c.ARRAY)
            MainWindow.drawboard(0, "撤销", self.board)
            self.phase = 0
            self.involved_play(0)
            
        
    def checkState(self, isFirst):
        '''
        检查是否超时和报错
        '''
        
        if self.states[isFirst]['time'] >= self.maxtime:  # 超时
            self.log.add('&e:%s time out' % (c.PLAYERS[isFirst]))
            self.timeout = isFirst
            return True
        if self.states[isFirst]['error']:  # 抛出异常
            self.log.add('&e:%s run time error' % (c.PLAYERS[isFirst]))
            self.error = isFirst
            return True
        return False

    def checkViolate(self, isFirst, mode, value):
        '''
        检查是否非法输出
        -> 违规有三种情形:
        -> 输出格式错误
        -> 选择的方格在可选范围之外
        -> 选择的方向使得合并前后棋盘没有变化
        '''
        
        if mode == 'position':
            if not (isinstance(value, tuple) and len(value) == 2 and value[0] in range(c.ROWS) and value[1] in range(c.COLUMNS)):
                self.log.add('&e:%s violate by illegal output of position' % (c.PLAYERS[isFirst]))
                self.violator = isFirst
                return True
            if self.board.getValue(value) == 0 and (self.board.getBelong(value) != isFirst or value == self.next):
                return False
            else:
                self.log.add('&e:%s violate by not achievable position' % (c.PLAYERS[isFirst]))
                self.violator = isFirst
                return True
        else:
            if value not in range(4):
                self.log.add('&e:%s violate by illegal output of direction' % (c.PLAYERS[isFirst]))
                self.violator = isFirst
                return True
            elif self.change:
                return False
            else:
                self.log.add('&e:%s violate by not achievable direction' % (c.PLAYERS[isFirst]))
                self.violator = isFirst
                return True
            self.change = False

    def save(self):
        '''
        计分并保存比赛记录
        '''
        
        # 获取所有棋子并计数
        results = {True: self.board.getScore(True), False: self.board.getScore(False)}
        scores = {True: {}, False: {}}
        for level in range(1, c.MAXLEVEL):
            scores[True][level] = results[True].count(level)
            scores[False][level] = results[False].count(level)

        # 比较比分
        if self.winner == None:
            for _ in reversed(range(1, c.MAXLEVEL)):
                self.log.add('&e:check level %d' % _)
                if scores[True][_] == scores[False][_]:
                    self.log.add('&e:level %d tied by %d' % (_, scores[True][_]))
                else:
                    self.winner = scores[True][_] > scores[False][_]
                    self.log.add('&e:%s win by level %d (%d to %d)' % (c.PLAYERS[self.winner], _, scores[True][_], scores[False][_]))
                    break
            else:
                self.log.add('&e:tied')

        # 保存对局信息, 可以用analyser.py解析
        self.name = repr(hash(time.perf_counter()))  # 对局名称
        if self.toSave:
            file = open('%s/%s.txt' % (self.match, self.name),'w')
            myDict = {True:'player 0', False:'player 1', None:'None', 'both':'both'}  # 协助转换为字符串
            title = 'player0: %d from path %s\n' % (self.states[True]['index'][0], self.states[True]['path']) + \
                    'player1: %d from path %s\n' % (self.states[False]['index'][0], self.states[False]['path']) + \
                    'time: %s\n' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + \
                    '{:*^45s}\n'.format('basic record')
            file.write(title)
            file.write('=' * 45 + '\n|{:^10s}|{:^10s}|{:^10s}|{:^10s}|\n'.format('timeout', 'violator', 'error', 'winner') + \
                       '-' * 45 + '\n|{:^10s}|{:^10s}|{:^10s}|{:^10s}|\n'.format(myDict[self.timeout], myDict[self.violator], myDict[self.error], myDict[self.winner]) + \
                       '=' * 45 + '\n')
            file.write('=' * 60 + '\n|%6s|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|\n' % ('player', *range(1, c.MAXLEVEL)) + \
                       '-' * 60 + '\n|%6d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|\n' % (0, *[scores[True][_] for _ in range(1, c.MAXLEVEL)]) + \
                       '-' * 60 + '\n|%6d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|\n' % (1, *[scores[False][_] for _ in range(1, c.MAXLEVEL)]) + \
                       '=' * 60 + '\n')
            file.flush()
            file.write('{:*^45s}\n'.format('complete record'))
            for log in self.log:
                file.write(log + '\n')  # '&'表示一条log的开始
                file.flush()
            file.close()
    
    def human_save(self):
        '''
        计分并保存比赛记录
        '''
        x = QWidget()
        self.name = QFileDialog.getSaveFileName(x,"保存记录","" ,"Text files (*.txt);;all files(*.*)")
        if len(self.name) == 0:
            return
        # 获取所有棋子并计数
        results = {True: self.board.getScore(True), False: self.board.getScore(False)}
        scores = {True: {}, False: {}}
        for level in range(1, c.MAXLEVEL):
            scores[True][level] = results[True].count(level)
            scores[False][level] = results[False].count(level)

        # 比较比分

        # 保存对局信息, 可以用analyser.py解析
        file = open(self.name[0],'w')
        myDict = {True:'player 0', False:'player 1', None:'None', 'both':'both'}  # 协助转换为字符串
        title = 'player0: %d from path %s\n' % (self.states[True]['index'][0], self.states[True]['path']) + \
                'player1: %d from path %s\n' % (self.states[False]['index'][0], self.states[False]['path']) + \
                'time: %s\n' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + \
                '{:*^45s}\n'.format('basic record')
        file.write(title)
        file.write('=' * 45 + '\n|{:^10s}|{:^10s}|{:^10s}|{:^10s}|\n'.format('timeout', 'violator', 'error', 'winner') + \
                   '-' * 45 + '\n|{:^10s}|{:^10s}|{:^10s}|{:^10s}|\n'.format(myDict[self.timeout], myDict[self.violator], myDict[self.error], myDict[self.winner]) + \
                   '=' * 45 + '\n')
        file.write('=' * 60 + '\n|%6s|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|\n' % ('player', *range(1, c.MAXLEVEL)) + \
                   '-' * 60 + '\n|%6d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|\n' % (0, *[scores[True][_] for _ in range(1, c.MAXLEVEL)]) + \
                   '-' * 60 + '\n|%6d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|%3d|\n' % (1, *[scores[False][_] for _ in range(1, c.MAXLEVEL)]) + \
                   '=' * 60 + '\n')
        file.flush()
        file.write('{:*^45s}\n'.format('complete record'))
        for log in self.log:
            file.write(log + '\n')  # '&'表示一条log的开始
            file.flush()
        file.close()
def main(playerList,
         savepath = None,
         livequeue = None,
         toSave = True,
         toReport = True,
         toGet = False,
         debug = False,
         REPEAT = c.REPEAT + 1,
         MAXTIME = c.MAXTIME,
         ROUNDS = c.ROUNDS,
         BOARDXXX = None):
    '''
    主函数
    -> 参数: playerList 参赛队伍的模块列表, 支持绝对路径, 相对路径, 和已读取的类. 例如 playerList = ['player.py', 'player.py']
    -> 参数: savepath 比赛文件夹的保存路径, 支持相对路径, 支持函数返回值, 默认为在当前目录创建
    -> 参数: livequeue 直播进程通讯用的队列
    -> 参数: toSave 是否保存对局记录
    -> 参数: toReport 是否生成统计报告
    -> 参数: toGet 是否返回平台对象
    -> 参数: debug 是否打印报错信息
    -> 参数: REPEAT 单循环轮数
    -> 参数: MAXTIME 总时间限制
    -> 参数: ROUNDS 总回合数
    '''
    
    import time
    
    '''
    第一部分, 构建存放log文件的文件夹
    '''
    
    import os
    if callable(savepath): match = savepath()
    elif isinstance(savepath, str): match = savepath
    else: match = time.strftime('%Y-%m-%d %H-%M-%S', time.localtime())
    
    count = 0
    while True:  # 文件夹存在则创立副本
        count += 1
        try:
            _match = '_%d' % count if count != 1 else ''
            os.mkdir(match + _match)
            match += _match
            break
        except FileExistsError:
            continue

    '''
    第二部分, 导入模块并准备成绩记录
    '''
    
    # 导入全部ai模块
    global mode
    import sys
    Players = []
    time0 = [0 for count in range(len(playerList))]
    for count in range(len(playerList)):
        if playerList[count] == 'human':
            Players.append('human')
            continue
        if playerList[count] == 'defaultplayer':
            Players.append(defaultplayer)
            continue
        if isinstance(playerList[count], tuple):  # 指定初始时间
            time0[count] = playerList[count][1]
            playerList[count] = playerList[count][0]
        if isinstance(playerList[count], str):  # 路径
            path = playerList[count]
            sys.path.insert(0, os.path.dirname(os.path.abspath(path)))
            module = os.path.splitext(os.path.basename(path))[0]
            Players.append(__import__(module).Player)
            sys.path.pop(0)
            del sys.modules[module]
        else:  # 已读取的类
            Players.append(playerList[count])
    
    # 进行成绩记录的准备    
    matchResults = {'basic': [], 'exception': []}
    playerResults = [{True: {'win': [],
                             'lose': [],
                             'violate': [],
                             'timeout': [],
                             'error': [],
                             'time': []},
                      False: {'win': [],
                              'lose': [],
                              'violate': [],
                              'timeout': [],
                              'error': [],
                              'time': []},
                      'path': playerList[count]} for count in range(len(playerList))]
            
    def update(matchResults, playerResults, result):  # 更新成绩记录
        matchResults['basic'].append('name: %s -> player%d to player%d -> %d rounds'
                                    % (result['name'],
                                       result[True]['index'][0],
                                       result[False]['index'][0],
                                       result['rounds']))
        matchResults['exception'].append((result['name'], result[True]['exception'], result[False]['exception']))
        for isFirst in [True, False]:
            for _ in result[isFirst]:
                if _ not in  ['index', 'exception'] and result[isFirst][_]:
                    playerResults[result[isFirst]['index'][0]][isFirst][_].append(result['name'] if _ != 'time' else result[isFirst]['time'])
                    
    '''
    第三部分, 比赛
    '''
    
    # 开始游戏, 单循环先后手多次比赛
    kwargs = {'match': match,
              'livequeue': livequeue,
              'toSave': toSave,
              'MAXTIME': MAXTIME,
              'ROUNDS': ROUNDS,
              'BOARDXXX': BOARDXXX}
    platforms = {}
    global plat_cur
    if mode == 1:
        for count1 in range(len(playerList)):
            for count2 in range(count1 + 1, len(playerList)):
                platforms[(count1, count2)] = []
                platforms[(count2, count1)] = []
                for _ in range(REPEAT):
                    for isFirst in [True, False]:
                        counts = (count1, count2) if isFirst else (count2, count1)
                        trueCount, falseCount = counts
                        platforms[counts].append(Platform({True: {'player': object.__new__(Players[trueCount]),
                                                                  'path': playerList[trueCount],
                                                                  'time': time0[trueCount],
                                                                  'time0': time0[trueCount],
                                                                  'error': False,
                                                                  'exception': None,
                                                                  'index': (trueCount, True)},
                                                           False: {'player': object.__new__(Players[falseCount]),
                                                                   'path': playerList[falseCount],
                                                                   'time': time0[falseCount],
                                                                   'time0': time0[falseCount],
                                                                   'error': False,
                                                                   'exception': None,
                                                                   'index': (falseCount, False)}}, **kwargs))
                        update(matchResults, playerResults, platforms[counts][-1].play())
    elif mode == 2:
        plat_cur = Platform({True: {'player': object.__new__(Players[0]),
                                                  'path': playerList[0],
                                                  'time': time0[0],
                                                  'time0': time0[0],
                                                  'error': False,
                                                  'exception': None,
                                                  'index': (0, True)},
                                           False: {'player': 'human',
                                                   'path': None,
                                                   'time': None,
                                                   'time0': None,
                                                   'error': False,
                                                   'exception': None,
                                                   'index': (1, False)}}, **kwargs)
        plat_cur.play()
    elif mode == 3:
        plat_cur = Platform({True: {'player': 'human',
                                                   'path': None,
                                                   'time': None,
                                                   'time0': None,
                                                   'error': False,
                                                   'exception': None,
                                                   'index': (1, False)},
                                           False: {'player': object.__new__(Players[0]),
                                                  'path': playerList[0],
                                                  'time': time0[0],
                                                  'time0': time0[0],
                                                  'error': False,
                                                  'exception': None,
                                                  'index': (0, True)}}, **kwargs)
        plat_cur.play()
    elif mode == 4:
        plat_cur = Platform({True: {'player': 'human',
                                                   'path': None,
                                                   'time': None,
                                                   'time0': None,
                                                   'error': False,
                                                   'exception': None,
                                                   'index': (0, False)},
                                           False: {'player': 'human',
                                                   'path': None,
                                                   'time': None,
                                                   'time0': None,
                                                   'error': False,
                                                   'exception': None,
                                                   'index': (1, False)}}, **kwargs)
        plat_cur.play()
                
    '''
    第四部分, 统计比赛结果
    '''
    
    # 统计全部比赛并归档到一个总文件中
    if toReport:
        f = open('%s/_.txt' % match, 'w')
        f.write('=' * 50 + '\n')
        f.write('total matches: %d\n' % len(matchResults['basic']))
        f.write('\n'.join(matchResults['basic']))
        f.write('\n' + '=' * 50 + '\n')
        f.flush()
        for count in range(len(playerList)):
            f.write('player%s from path %s\n\n' % (count, playerResults[count]['path']))
            player = playerResults[count][True]
            f.write('''offensive cases:
    average time: %.3f
        win rate: %.2f%%
        win: %d at
            %s
        lose: %d at
            %s
        violate: %d at
            %s
        timeout: %d at
            %s
        error: %d at
            %s
'''            %(sum(player['time']) / len(player['time']) if player['time'] != [] else 0,
                 100 * len(player['win']) / REPEAT / (len(playerResults) - 1),
                 len(player['win']),
                 '\n            '.join(player['win']),
                 len(player['lose']),
                 '\n            '.join(player['lose']),
                 len(player['violate']),
                 '\n            '.join(player['violate']),
                 len(player['timeout']),
                 '\n            '.join(player['timeout']),
                 len(player['error']),
                 '\n            '.join(player['error'])))
            player = playerResults[count][False]
            f.write('''defensive cases:
    average time: %.3f
        win rate: %.2f%%
        win: %d at
            %s
        lose: %d at
            %s
        violate: %d at
            %s
        timeout: %d at
            %s
        error: %d at
            %s
'''            %(sum(player['time']) / len(player['time']) if player['time'] != [] else 0,
                 100 * len(player['win']) / REPEAT / (len(playerResults) - 1),
                 len(player['win']),
                 '\n            '.join(player['win']),
                 len(player['lose']),
                 '\n            '.join(player['lose']),
                 len(player['violate']),
                 '\n            '.join(player['violate']),
                 len(player['timeout']),
                 '\n            '.join(player['timeout']),
                 len(player['error']),
                 '\n            '.join(player['error'])))
            f.write('=' * 50 + '\n')
            f.flush()
        f.close()

    # 打印报错信息
    if debug:
        f = open('%s/_Exceptions.txt' % match, 'w')
        for metamatch in matchResults['exception']:
            f.write('-> %s\n\n' % metamatch[0])
            f.write('offensive:\n')
            f.write(metamatch[1] if metamatch[1] else 'pass\n')
            f.write('\ndefensive:\n')
            f.write(metamatch[2] if metamatch[2] else 'pass\n')
            f.write('=' * 50 + '\n')
            f.flush()
        f.close()

    # 返回全部平台
    if toGet: return platforms

class mywindow(QMainWindow):
    def __init__(self):
        super(mywindow, self).__init__(None)
        self.load = 0
    
    
    def loadmode(self, matchList = None, index = 1, log = None):
        # matchList = [mode, {'path': path, 'topText': topText, 'bottomText': bottomText}, ...]
        if matchList == None:
            if log != None:
                self.log = log  
                self.size = len(self.log)
            else:
                while True:  # 加载对局记录
                    try:
                        x = QWidget()
                        y = QFileDialog.getOpenFileName(x,'选择文件','','Text files(*.txt)')[0]
                        if len(y) == 0:
                            return
                        self.log = open(y, 'r').read().split('&')  # 读取全部记录并分成单条    
                        self.size = len(self.log)
                        break
                    except FileNotFoundError:
                        print('%s is not found.' % filename)

            print('=' * 50)
            x = QWidget()
            self.mode = QInputDialog.getInt(x,'选择模式','enter 0 for original mode.\nenter 1 for YuzuSoft mode.\nmode: ', 0, 0, 1)[0]
        else:
            self.match = self.matchList[index]
            self.log = open(self.match['path'], 'r').read().split('&')  # 读取全部记录并分成单条
            self.size = len(self.log)
            self.mode = self.matchList[0]
        
        self.ui.continue_match.setEnabled(True)
        self.ui.continue_match.triggered.connect(self.continue_match)
        self.matchList = matchList
        self.index = index
        self.load = 1
        self.ui.left.setEnabled(True)
        self.ui.right.setEnabled(True)
        self.ui.left.clicked.disconnect()
        self.ui.left.clicked.connect(self.previous)
        self.ui.right.clicked.disconnect()
        self.ui.right.clicked.connect(self.succ)
        self.ui.left.setText("后退\n(A)")
        self.ui.right.setText("前进\n(D)")
            
        self.statelabel.setText('press any key to start\nA previous step D next step')

        print('=' * 50)
        declarations = self.log[0].split('\n')
        for declaration in declarations:
            if declaration != '' and declaration[0] != '*':
                print(declaration)  # 打印说明信息

        self.cur = 0        # 读取单条记录的游标
        self.state = True   # 游标运动的状态, True代表向前

    def analyse(self, log):
        # 分析指令
        if log[0] == 'e':    # 事件在顶端状态栏
            self.statelabel.setText(log.split(':')[1][:-1])
        elif log[0] == 'd':  # 决策在底端状态栏
            self.rounddisplay.setText(log.split(':')[0][1:])  # 当前轮数
            self.statelabel.setText(log.split(':')[1][:-1])
        elif log[0] == 'p':  # 更新棋盘
            self.rounddisplay.setText(log.split(':')[0][1:])  # 当前轮数
            
            platform = []
            pieces = log.split(':')[1].split()
            for piece in pieces:
                platform.append((piece[0], int(piece[1:])))
            cur = 0

            while cur < c.ROWS * c.COLUMNS:
                row = cur // c.COLUMNS
                column = cur % c.COLUMNS
                belong, number = platform[cur]
                if self.mode == 0:
                    self.button[row][column].setStyleSheet("background-color:" + c.COLOR_CELL[belong])
                    if number == 0:
                        self.button[row][column].setText("")
                    else:
                        self.button[row][column].setText(str(2 ** number))
                else:
                    self.button[row][column].setStyleSheet("border-image: url(../src/analyser/pic/%s_%d.png)" % (c.PICTURES[0 if belong == '+' else 1], number))
                cur += 1
    
    def previous(self):
        self.keyPressEvent(None, Qt.Key_A)
    
    def succ(self):
        self.keyPressEvent(None, Qt.Key_D)
    
    def continue_match(self):
        platform = []
        pieces = self.log[self.cur].split(':')[1].split()
        for piece in pieces:
            platform.append((piece[0], int(piece[1:])))
        cur = 0
        BOARDXXX = [[None for _ in range(c.COLUMNS)] for _ in range(c.ROWS)]
        while cur < c.ROWS * c.COLUMNS:
            row = cur // c.COLUMNS
            column = cur % c.COLUMNS
            belong, number = platform[cur]
            BOARDXXX[row][column] = (belong, number)
            cur += 1
        plst = []
        self.ui.left.setText("左")
        self.ui.right.setText("右")
        dirtlst = [click1(_) for _ in range(4)]
        self.ui.left.clicked.disconnect()
        self.ui.left.clicked.connect(dirtlst[2].proc)
        self.ui.right.clicked.disconnect()
        self.ui.right.clicked.connect(dirtlst[3].proc)
        for _ in range(len(player_list)):
            if player_state[_]:
                plst.append(player_list[_])
        self.load = 2
        if mode == 0:
            x = QWidget()
            QMessageBox.information(x, "提示", "尚未选择模式", QMessageBox.Yes)
            return
        elif mode == 1:
            if len(plst) < 2:
                x = QWidget()
                QMessageBox.information(x, "提示", "ai数量小于两个", QMessageBox.Yes)
            else:
                main(plst, toSave = toSave, toReport = toReport, debug = debug, MAXTIME = MAXTIME, ROUNDS = ROUNDS, REPEAT = REPEAT, BOARDXXX = BOARDXXX)
                x = QWidget()
            QMessageBox.information(x, "提示", "已完成", QMessageBox.Yes)
        elif mode == 2:
            if len(plst) != 1:
                x = QWidget()
                QMessageBox.information(x, "提示", "请只启用一个ai", QMessageBox.Yes)
            else:
                main(plst, toSave = False, toReport = False, debug = False, MAXTIME = MAXTIME, ROUNDS = ROUNDS, REPEAT = REPEAT, BOARDXXX = BOARDXXX)
        elif mode == 3:
            if len(plst) != 1:
                x = QWidget()
                QMessageBox.information(x, "提示", "请只启用一个ai", QMessageBox.Yes)
            else:
                main(plst, toSave = False, toReport = False, debug = False, MAXTIME = MAXTIME, ROUNDS = ROUNDS, REPEAT = REPEAT, BOARDXXX = BOARDXXX)
        else:
            main(plst, toSave = False, toReport = False, debug = False, MAXTIME = MAXTIME, ROUNDS = ROUNDS, REPEAT = REPEAT, BOARDXXX = BOARDXXX)
    
    def keyPressEvent(self, event, key = None):
        if self.load == 0:
            return
        elif self.load == 1:
            if key == None:
                key = event.key()
            if self.cur == 0:  # 第一条信息
                while True:
                    self.cur += 1
                    self.analyse(self.log[self.cur])
                    if self.cur >= self.size - 1 or self.log[self.cur][0] != 'd':
                        break
            elif key == Qt.Key_A and self.cur > 1:     # 回退, 更新至决策
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
            elif key == Qt.Key_D and self.cur < self.size - 1:  # 前进, 更新至棋盘
                while True:
                    if not self.state:
                        if self.log[self.cur + 1][0] == 'p':
                            self.cur += 1
                        self.state = True
                    self.cur += 1
                    self.analyse(self.log[self.cur])
                    if self.cur >= self.size - 1 or self.log[self.cur][0] != 'd':
                        break
            elif key == Qt.Key_N and self.index != len(self.matchList) - 1:
                self.destroy()
                self.loadmode(self.matchList, self.index + 1)
            elif key == Qt.Key_P and self.index != 1:
                self.destroy()
                self.loadmode(self.matchList, self.index - 1)
        elif self.load == 2:
            key = event.key()
            if key == Qt.Key_W:
                dirtlst[0].proc()
            if key == Qt.Key_S:
                dirtlst[1].proc()
            if key == Qt.Key_A:
                dirtlst[2].proc()
            if key == Qt.Key_D:
                dirtlst[3].proc()

    def drawboard(self, currentRound, log, board):
        ui.save_current.setEnabled(True)
        ui.undo.setEnabled(True)
        try:
            ui.save_current.triggered.disconnect()
            ui.save_current.triggered.connect(plat_cur.human_save)
        except:
            pass
        try:
            ui.undo.triggered.disconnect()
            ui.undo.triggered.connect(plat_cur.undo)
        except:
            pass
        ui.up.setEnabled(True)
        ui.down.setEnabled(True)
        ui.left.setEnabled(True)
        ui.right.setEnabled(True)
        for i in range(c.ROWS):
            for j in range(c.COLUMNS):
                if board.getValue((i, j)) == 0:
                    self.button[i][j].setStyleSheet("background-color:" + c.COLOR_CELL['+' if board.getBelong((i, j)) else '-'])
                    self.button[i][j].setText("")
                else:
                    self.button[i][j].setStyleSheet("background-color:" + c.COLOR_CELL['+' if board.getBelong((i, j)) else '-'])
                    self.button[i][j].setText(str(2 ** board.getValue((i, j))))
        if plat_cur.phase == 0:
            if board.getNext(True, currentRound) != ():
                i, j = board.getNext(True, currentRound)
                self.button[i][j].setStyleSheet("background-color:white")
        if plat_cur.phase == 1:
            if board.getNext(False, currentRound) != ():
                i, j = board.getNext(False, currentRound)
                self.button[i][j].setStyleSheet("background-color:white")
        self.rounddisplay.setText(str(currentRound))
        self.statelabel.setText(log)

class click:
    def __init__(self, x, y):
        self.pos = (x, y)
    def proc(self):
        if plat_cur.phase == 2 or plat_cur.phase == 3:
            if warning:
                x = QWidget()
                QMessageBox.information(x, "提示", "请选择方向！", QMessageBox.Yes)
            return
        global pos
        pos = self.pos
        ui.selectlabel.setText("you selected " + str(pos))
        work()

class click1:
    def __init__(self, d):
        self.d = d
    def proc(self):
        if plat_cur.phase == 0 or plat_cur.phase == 1:
            if warning:
                x = QWidget()
                QMessageBox.information(x, "提示", "请选择位置！", QMessageBox.Yes)
            return
        global dirt
        dirt = self.d
        if dirt == 0:
            ui.selectlabel.setText("you selected up")
        if dirt == 1:
            ui.selectlabel.setText("you selected down")
        if dirt == 2:
            ui.selectlabel.setText("you selected left")
        if dirt == 3:
            ui.selectlabel.setText("you selected right")
        work()

class loadai_content(QItemDelegate):
    def __init__(self, parent = None):
        super(loadai_content, self).__init__(parent)

    def paint(self, painter, option, index):
        if not self.parent().indexWidget(index):
            if index.column() == 2:
                if index.row() < len(player_list):
                    button_read = QPushButton(
                        self.tr('删除ai'),
                        self.parent(),
                        clicked=self.parent().delai
                    )
                    button_read.index = [index.row(), index.column()]
                    h_box_layout = QHBoxLayout()
                    h_box_layout.addWidget(button_read)
                    h_box_layout.setContentsMargins(0, 0, 0, 0)
                    h_box_layout.setAlignment(Qt.AlignCenter)
                    widget = QWidget()
                    widget.setLayout(h_box_layout)
                    self.parent().setIndexWidget(
                        index,
                        widget
                    )
                else:
                    button_read = QPushButton(
                        self.tr('关闭窗口'),
                        self.parent(),
                        clicked=self.parent().destroyself
                    )
                    button_read.index = [index.row(), index.column()]
                    h_box_layout = QHBoxLayout()
                    h_box_layout.addWidget(button_read)
                    h_box_layout.setContentsMargins(0, 0, 0, 0)
                    h_box_layout.setAlignment(Qt.AlignCenter)
                    widget = QWidget()
                    widget.setLayout(h_box_layout)
                    self.parent().setIndexWidget(
                        index,
                        widget
                    )
            elif index.column() == 1:
                if index.row() < len(player_list):
                    button_read = QCheckBox(
                        self.parent()
                    )
                    button_write = QPushButton(
                        self.tr('禁用') if player_state[index.row()] else self.tr('启用'),
                        self.parent(),
                        clicked=self.parent().cellButtonClicked
                    )
                    if player_state[index.row()]:
                        button_write.tr('禁用')
                    else:
                        button_write.tr('启用')
                    button_read.setChecked(player_state[index.row()])
                    button_read.stateChanged.connect(self.parent().cellButtonClicked)
                    button_read.index = [index.row(), index.column()]
                    button_write.index = [index.row(), index.column()]
                    h_box_layout = QHBoxLayout()
                    h_box_layout.addWidget(button_read)
                    h_box_layout.addWidget(button_write)
                    h_box_layout.setContentsMargins(0, 0, 0, 0)
                    h_box_layout.setAlignment(Qt.AlignCenter)
                    widget = QWidget()
                    widget.setLayout(h_box_layout)
                    self.parent().setIndexWidget(
                        index,
                        widget
                    )
            else:
                if index.row() < len(player_list):
                    button_read = QLabel(
                        self.tr(player_list[index.row()]),
                        self.parent()
                    )
                    button_read.index = [index.row(), index.column()]
                    h_box_layout = QHBoxLayout()
                    h_box_layout.addWidget(button_read)
                    h_box_layout.setContentsMargins(0, 0, 0, 0)
                    h_box_layout.setAlignment(Qt.AlignCenter)
                    widget = QWidget()
                    widget.setLayout(h_box_layout)
                    self.parent().setIndexWidget(
                        index,
                        widget
                    )
                else:
                    button_read = QPushButton(
                        self.tr('添加ai'),
                        self.parent(),
                        clicked=self.parent().openfile
                    )
                    button_write = QPushButton(
                        self.tr('添加默认ai'),
                        self.parent(),
                        clicked=self.parent().openfile1
                    )
                    button_read.index = [index.row(), index.column()]
                    button_write.index = [index.row(), index.column()]
                    h_box_layout = QHBoxLayout()
                    h_box_layout.addWidget(button_read)
                    h_box_layout.addWidget(button_write)
                    h_box_layout.setContentsMargins(0, 0, 0, 0)
                    h_box_layout.setAlignment(Qt.AlignCenter)
                    widget = QWidget()
                    widget.setLayout(h_box_layout)
                    self.parent().setIndexWidget(
                        index,
                        widget
                    )


class MyModel(QAbstractTableModel):
    global playerlist
    def __init__(self, parent=None):
        super(MyModel, self).__init__(parent)

    def rowCount(self, QModelIndex):
        return len(player_list) + 1

    def columnCount(self, QModelIndex):
        return 3

    def data(self, index, role):
        row = index.row()
        col = index.column()
        return QVariant()
    
    def headerData(self,section,orientation,role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()
        elif orientation == Qt.Horizontal:
            return ['路径','状态','操作'][section]
        else:
            return "%d" % (section + 1)


class ai_load(QTableView):
    global ui, load
    def __init__(self, parent = None):
        super(ai_load, self).__init__(parent)
        self.setItemDelegate(loadai_content(self))

    def cellButtonClicked(self):
        player_state[self.sender().index[0]] = not player_state[self.sender().index[0]]
        loadai()

    def delai(self):
        player_list.pop(self.sender().index[0])
        player_state.pop(self.sender().index[0])
        loadai()

    def destroyself(self):
        load.destroy()
    
    def openfile(self):
        global cnt
        x = QWidget()
        c=QFileDialog.getOpenFileName(x,'选择文件','','Python files(*.py)')[0]
        if len(c):
            player_list.append(c)
            player_state.append(True)
            loadai()
    
    def openfile1(self):
        global cnt
        x = QWidget()
        player_list.append("defaultplayer")
        player_state.append(True)
        loadai()


def settings():
    global dialog1, toSave, toReport, debug, MAXTIME, ROUNDS, REPEAT, warning
    ui_settings = dialog.Ui_settings()
    dialog1 = QDialog()
    ui_settings.setupUi(dialog1)
    def savechange():
        global toSave, toReport, debug, MAXTIME, ROUNDS, REPEAT, warning
        toSave = ui_settings.checkBox.isChecked()
        toReport = ui_settings.checkBox_2.isChecked()
        debug = ui_settings.checkBox_3.isChecked()
        MAXTIME = int(ui_settings.textEdit.toPlainText())
        ROUNDS = int(ui_settings.textEdit_2.toPlainText())
        REPEAT = int(ui_settings.textEdit_3.toPlainText())
        warning = ui_settings.checkBox_5.isChecked()
        dialog1.destroy()
    ui_settings.checkBox.setChecked(toSave)
    ui_settings.checkBox_2.setChecked(toReport)
    ui_settings.checkBox_3.setChecked(debug)
    ui_settings.textEdit.setText(str(MAXTIME))
    ui_settings.textEdit_2.setText(str(ROUNDS))
    ui_settings.textEdit_3.setText(str(REPEAT))
    ui_settings.checkBox_5.setChecked(warning)
    ui_settings.pushButton.clicked.connect(savechange)
    dialog1.show()

class setmode:
    def __init__(self, set_mode):
        self.mode = set_mode
    def proc(self):
        global mode
        mode = self.mode
        if mode == 1:
            statelabel.setText("当前模式为电脑-电脑")
        elif mode == 2:
            statelabel.setText("当前模式为电脑-人类")
        elif mode == 3:
            statelabel.setText("当前模式为人类-电脑")
        else:
            statelabel.setText("当前模式为人类-人类")

def work():
    if plat_cur.phase == 0:
        if pos != None and plat_cur != None:
            if plat_cur.human_get_position(True):
                plat_cur.phase = 1
                plat_cur.involved_play(plat_cur.currentRound)
            else:
                if warning:
                    x = QWidget()
                    QMessageBox.information(x, "提示", "位置非法", QMessageBox.Yes)
    elif plat_cur.phase == 1:
        if pos != None and plat_cur != None:
            if plat_cur.human_get_position(False):
                plat_cur.phase = 2
                plat_cur.involved_play(plat_cur.currentRound)
            else:
                if warning:
                    x = QWidget()
                    QMessageBox.information(x, "提示", "位置非法", QMessageBox.Yes)
    elif plat_cur.phase == 2:
        if dirt != None and plat_cur != None:
            if plat_cur.human_get_direction(True):
                plat_cur.phase = 3
                plat_cur.involved_play(plat_cur.currentRound)
            else:
                if warning:
                    x = QWidget()
                    QMessageBox.information(x, "提示", "方向非法", QMessageBox.Yes)
    elif plat_cur.phase == 3:
        if dirt != None and plat_cur != None:
            if plat_cur.human_get_direction(False):
                plat_cur.phase = 4
                plat_cur.involved_play(plat_cur.currentRound)
            else:
                if warning:
                    x = QWidget()
                    QMessageBox.information(x, "提示", "方向非法", QMessageBox.Yes)

def match_init():
    global dirtlst, ui, MainWindow, toSave, toReport, debug, MAXTIME, ROUNDS, REPEAT
    plst = []
    for _ in range(len(player_list)):
        if player_state[_]:
            plst.append(player_list[_])
    if mode == 0:
        x = QWidget()
        QMessageBox.information(x, "提示", "尚未选择模式", QMessageBox.Yes)
        return
    if mode == 1:
        if len(plst) < 2:
            x = QWidget()
            QMessageBox.information(x, "提示", "ai数量小于两个", QMessageBox.Yes)
        else:
            main(plst, toSave = toSave, toReport = toReport, debug = debug, MAXTIME = MAXTIME, ROUNDS = ROUNDS, REPEAT = REPEAT)
            x = QWidget()
            QMessageBox.information(x, "提示", "已完成", QMessageBox.Yes)
        return
    MainWindow.load = 2
    ui.left.setText("左")
    ui.right.setText("右")
    ui.left.clicked.disconnect()
    ui.left.clicked.connect(dirtlst[2].proc)
    ui.right.clicked.disconnect()
    ui.right.clicked.connect(dirtlst[3].proc)
    if mode == 2:
        if len(plst) != 1:
            x = QWidget()
            QMessageBox.information(x, "提示", "请只启用一个ai", QMessageBox.Yes)
        else:
            main(plst, toSave = False, toReport = False, debug = False, MAXTIME = MAXTIME, ROUNDS = ROUNDS, REPEAT = REPEAT)
    elif mode == 3:
        if len(plst) != 1:
            x = QWidget()
            QMessageBox.information(x, "提示", "请只启用一个ai", QMessageBox.Yes)
        else:
            main(plst, toSave = False, toReport = False, debug = False, MAXTIME = MAXTIME, ROUNDS = ROUNDS, REPEAT = REPEAT)
    else:
        main(plst, toSave = False, toReport = False, debug = False, MAXTIME = MAXTIME, ROUNDS = ROUNDS, REPEAT = REPEAT)

def get_log_from_net(download = False):
    import requests
    import json

    token = "MQ6KWY9RRyL6ldFHd0E3hsVF5YFgZdOJOvrf5YBEwLz9V4R34O27lSGrofXy1Mxg"
    sessionid = "ngschzmuskjgos3fcjapznm6ihnqza5t"

    headers = {
        "Accept": "text/html, application/xhtml+xml, application/xml; q=0.9, */*; q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-Hans-CN, zh-Hans; q=0.5",
        "Cache-Control": "max-age=0",
        "Connection": "Keep-Alive",
        "Cookie": f"csrftoken={token}; sessionid={sessionid}",
        "Host": "gis4g.pku.edu.cn",
        "Pragma": "no-cache",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763",
    }
    
    x = QWidget()
    url = QInputDialog.getText(x,'加载记录','请输入查看比赛页面的地址: ')[0]
    if url == '':
        return
    #url = "http://" + url
    r = requests.get(url, headers=headers)
    items = json.loads(r.text.split('使用比赛参数')[1].split("<div>")[1].split("</div>")[0].replace("&quot;", "\""))
    if download:
        import os
        dirname = time.strftime('%Y-%m-%d %H-%M-%S', time.localtime())
        os.mkdir(dirname)
        for i in range(int(items["rounds"])):
            r = requests.get(url + str(i) + "/", headers=headers)
            items = json.loads(r.text.split('<div id="record_receiver" style="display:none">')[1].split("</div>")[0].replace("&quot;", "\""))
            f = open(dirname + "/" + str(i) + ".txt", "w")
            f.write(items["time"])
            for i in items["logs"]:
                f.write("&d" + str(i['D']['r']) + ":player " + str(i['D']['p']) + " set " + i['D']['d'][0] + " " + str(i['D']['d'][1]))
                f.write("&p" + str(i['D']['r']) + ":\n" + '\n'.join([' '.join([('+' if i['P'][row][column] > 0 or (i['P'][row][column] == 0 and column < c.COLUMNS / 2) else '-')\
                                     + str(abs(i['P'][row][column])).zfill(2) \
                                     for column in range(c.COLUMNS)]) for row in range(c.ROWS)]))
            for i in items["logs"][-1]["E"]:
                f.write("&e:" + i)
            f.write("&e:cause" + items["cause"])
            f.write("&e:winner" + str(items["winner"]))
            try:
                f.write("&e:error" + items["error"])
            except:
                pass
            f.close()
        QMessageBox.information(x, '', '已完成', QMessageBox.Yes)
        return
    num = QInputDialog.getInt(x,'加载记录','您想查看哪一场比赛: ', 0, 0, int(items["rounds"]) - 1, 1)[0]
    r = requests.get(url + str(num) + "/", headers=headers)
    items = json.loads(r.text.split('<div id="record_receiver" style="display:none">')[1].split("</div>")[0].replace("&quot;", "\""))
    log = [items["time"]]
    for i in items["logs"]:
        log.append("d" + str(i['D']['r']) + ":player " + str(i['D']['p']) + " set " + i['D']['d'][0] + " " + str(i['D']['d'][1]))
        log.append("p" + str(i['D']['r']) + ":\n" + '\n'.join([' '.join([('+' if i['P'][row][column] > 0 or (i['P'][row][column] == 0 and column < c.COLUMNS / 2) else '-')\
                             + str(abs(i['P'][row][column])).zfill(2) \
                             for column in range(c.COLUMNS)]) for row in range(c.ROWS)]))
    for i in items["logs"][-1]["E"]:
        log.append("e:" + i)
    log.append("e:cause" + items["cause"])
    log.append("e:winner" + items["winner"])
    try:
        log.append("e:error" + items["error"])
    except:
        pass
    return log


player_list = []
player_state = []
mode = 0
cnt = 0
toSave, toReport, debug, MAXTIME, ROUNDS, REPEAT, warning = True, True, False, c.MAXTIME, c.ROUNDS, c.REPEAT, True

if __name__ == '__main__':
    global ui, dirtlst
    app = QApplication(sys.argv)
    MainWindow = mywindow()
    ui = gui.Ui_MainWindow()
    ui.setupUi(MainWindow)
    button = [[QtWidgets.QPushButton() for _ in range(0, c.COLUMNS)] for _ in range(0, c.ROWS)]
    table = [[None for _ in range(0, c.COLUMNS)] for _ in range(0, c.ROWS)]
    for i in range(c.ROWS):
        for j in range(c.COLUMNS):
            ui.chessboard.addWidget(button[i][j], i, j)
            button[i][j].setFixedSize(QtCore.QSize(80, 80))
            table[i][j] = click(i, j)
            button[i][j].clicked.connect(table[i][j].proc)
            #button[i][j].setEnabled(False)
    MainWindow.button = button
    MainWindow.rounddisplay = ui.rounddisplay
    MainWindow.statelabel = ui.statelabel
    MainWindow.ui = ui
    def loadai():
        global load
        load = ai_load()
        myModel = MyModel()
        load.setModel(myModel)
        load.resize(1000,600)
        load.setColumnWidth(0, 600)
        load.show()
    ui.ai_set.triggered.connect(loadai)
    ui.match_settings.triggered.connect(settings)
    dirtlst = [click1(_) for _ in range(4)]
    ui.up.clicked.connect(dirtlst[0].proc)
    ui.down.clicked.connect(dirtlst[1].proc)
    ui.left.clicked.connect(dirtlst[2].proc)
    ui.right.clicked.connect(dirtlst[3].proc)
    modelst = [setmode(_) for _ in range(1,5)]
    ui.mode1.triggered.connect(modelst[0].proc)
    ui.mode2.triggered.connect(modelst[1].proc)
    ui.mode3.triggered.connect(modelst[2].proc)
    ui.mode4.triggered.connect(modelst[3].proc)
    ui.start.triggered.connect(match_init)
    ui.menubar.setNativeMenuBar(False)
    def loadmode():
        MainWindow.loadmode()
    ui.loadfile.triggered.connect(loadmode)
    def load_from_net():
        MainWindow.loadmode(log = get_log_from_net())
    ui.load_from_net.triggered.connect(load_from_net)
    def download_from_net():
        get_log_from_net(True)
    ui.download_from_net.triggered.connect(download_from_net)
    def about():
        x = QWidget()
        QMessageBox.information(x, "", "本程序对之前的调试工具做了整合，并制作了可视化界面\n其中有一些功能未经测试，可能会有bug\n不建议在运行中更换模式，可能会导致未知错误", QMessageBox.Yes)
    ui.about.triggered.connect(about)
    statelabel = ui.statelabel
    MainWindow.show()
    sys.exit(app.exec_())
