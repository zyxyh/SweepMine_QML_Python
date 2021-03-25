import sys
import random

from PySide2.QtWidgets import QApplication
from PySide2.QtQuick import QQuickView
from PySide2.QtGui import QStandardItem
from PySide2.QtQml import qmlRegisterType,QQmlComponent,QQmlEngine
from PySide2.QtCore import QUrl, QTimer, QAbstractListModel,QModelIndex
from PySide2.QtCore import QObject, Signal, Slot, Property, Qt


class MinesModel(QAbstractListModel):
    MINEFLAG = Qt.UserRole + 1  # 地雷标志
    OPENEDFLAG = Qt.UserRole + 2  # 揭开标记
    MARK = Qt.UserRole + 3  # 标记
    MINESAROUND = Qt.UserRole + 4  # 周围地雷数

    def __init__(self):
        QAbstractListModel.__init__(self)

        self.__rows = 16  # 行数
        self.__cols = 30  # 列数
        self.__minesCount = 99  # 总地雷数
        self.count_opened = 0  # 揭开的块的总数
        self.markedCount = 0  # 已经标记地雷的总数
        self.gameStatus = 0  # 游戏状态 0：等待，1：正在进行，2：成功，3：引爆了

        self.__table = [] # * (self.__cols * self.__rows)
        for i in range(self.__rows * self.__cols):
            self.__table.append({'mineflag': False, 'openedflag': False, 'mark': "", 'minesaround': 0})
            item = QStandardItem(i,0)
            item.setFlags(item.flags() | Qt.ItemIsEditable)

    def rowCount(self, parent=None):
        return (self.__cols * self.__rows)

    def data(self, index, role):
        """
        QML.ListView 会从这个方法取数据, role 相当于 QML.ListView 请求的 "键",
        我们需要根据 "键" 返回相对应的 "值".

        :param index: 特别注意, 这个是 QModelIndex 类型. 通过 QModelIndex.row()
            可以获得 int 类型的位置. 这个位置是列表元素在列表中的序号, 从 0 开始数.
        :param role:
        :return:
        """

        _row = self.__table[index.row()]  # type: dict
        # e.g. row = {'name': 'Li Ming', 'age': 20}

        if index.isValid() is False or index.row() >= self.rowCount():
            return QVariant()

        # 根据 role 确定想要的 key, 并返回 row[key].
        if role == self.MINEFLAG:
            return _row['mineflag']
        elif role == self.OPENEDFLAG:
            return _row['openedflag']
        elif role == self.MARK:
            return _row['mark']
        elif role == self.MINESAROUND:
            return _row['minesaround']

    def roleNames(self):
        return { # 此处的 b'name' 是指 QML 中的 name. 特别注意的是必须是 bytes 类型, 而不是 str 类型.
        # 此处的'name'返回到qml的view里的delegate中可以直接引用
            self.MINEFLAG: b'mineflag',
            self.OPENEDFLAG: b'openedflag',
            self.MARK: b'mark',
            self.MINESAROUND: b'minesaround'
        }

    def flags(self, index):
        if index.isValid() is False:
            return Qt.ItemIsEnabled
        return Qt.ItemIsEnabled|Qt.ItemIsEditable


    def setData(self, index, value, role):
        """
        设置数据
        """
        #如果当前为编辑角色
        if role == self.MINEFLAG:
            # 保存数据
            self.__table[index.row()]['mineflag'] = value
            # 发射数据更改信号，以便让view更新
            self.dataChanged.emit(index,index)
            # 数据是否成功更新
            return True
        elif role == self.MINESAROUND:
            self.__table[index.row()]['minesaround'] = value
            self.dataChanged.emit(index,index)
            return True
        elif role == self.MARK:
            self.__table[index.row()]['mark'] = value
            self.dataChanged.emit(index, index)
            return True
        elif role == self.OPENEDFLAG:
            self.__table[index.row()]['openedflag'] = value
            self.dataChanged.emit(index, index)
            return True

        return False

    def RC2Index(self, rc):
        return rc[0] * self.__cols + rc[1]

    def Index2RC(self, index):
        return index // self.__cols, index % self.__cols

    @Slot(int)
    def open(self, index):
        if self.gameStatus == 0:
            self.gameStatus = 1
            self.spread_mines(index)
            self.count_opened += 1
            self.setData(self.index(index,0), True, self.OPENEDFLAG)
            self.openAround(index)
            return
        if self.data(self.index(index,0), self.MINEFLAG) and self.data(self.index(index,0), self.MARK) == "":
            self.gameStatus = 3  # 触雷了
            return

        elif self.data(self.index(index,0), self.OPENEDFLAG):
            self.openAround(index)
        else:
            self.count_opened += 1
            self.setData(self.index(index,0), True, self.OPENEDFLAG)
            if self.count_opened == self.__rows * self.__cols - self.__minesCount:
                self.gameStatus = 2  # 成功了
            else:
                self.openAround(index)

    def openAround(self, index):
        if self.count_around_marked(index) == self.data(self.index(index,0),self.MINESAROUND):
            for i in self.around_mine_list(index):
                if not self.data(self.index(i,0), self.OPENEDFLAG) and self.data(self.index(i,0), self.MARK) == "":
                    self.open(i)

    def around_mine_list(self, index):
        """ 返回周围的位置列表 """
        ri, ci = self.Index2RC(index)
        return [self.RC2Index((i, j)) for i in range(max(0, ri - 1), min(self.__rows - 1, ri + 1) + 1)
                for j in range(max(0, ci - 1), min(self.__cols - 1, ci + 1) + 1)
                if i != ri or j != ci]

    def count_around_mine(self, idx):
        """ 返回周围的地雷数 """
        count = 0
        for i in self.around_mine_list(idx):
            if self.data(self.index(i, 0), self.MINEFLAG):
                count += 1
        return count

    def count_around_marked(self, index):
        """返回周围已经标记为地雷的数"""
        marked_mines = 0
        for i in self.around_mine_list(index):
            if self.data(self.index(i,0), self.MARK) == "*":  # 表示地雷标记
                marked_mines += 1
        return marked_mines

    @Slot(result=int)
    def getStatus(self):
        return self.gameStatus

    @Slot(result=int)
    def getmarkedCount(self):
        return self.markedCount

    @Slot()
    def newGame(self):
        self.count_opened = 0
        self.markedCount = 0
        self.gameStatus = 0  # 表示等待状态
        for i in range(self.__cols * self.__rows):
            self.setData(self.index(i,0), False, self.MINEFLAG)
            self.setData(self.index(i,0), False, self.OPENEDFLAG)
            self.setData(self.index(i,0), '', self.MARK)
            self.setData(self.index(i,0), 0, self.MINESAROUND)

    def spread_mines(self, index):  # r,c及周围不安排地雷
        """ 第一次点击，设置其周围没有地雷 """
        around = self.around_mine_list(index)
        mcount = 0
        while mcount < self.__minesCount:
            i = random.randint(0, self.__cols * self.__rows - 1)
            if (i in around) or (i == index):
                continue
            elif (not self.data(self.index(i,0), self.MINEFLAG)):
                mcount += 1
                self.setData(self.index(i,0), True, self.MINEFLAG)

        # 把每格周围的地雷数记录下来
        for i in range(self.__rows * self.__cols):
            if not self.data(self.index(i,0), self.MINEFLAG):
                self.setData(self.index(i,0), self.count_around_mine(i), self.MINESAROUND)

    @Slot(int)
    def mark(self, i):
        if self.data(self.index(i,0), self.OPENEDFLAG):
            return
        m = ""
        currentmark = self.data(self.index(i,0), self.MARK)
        if currentmark == "":
            m = "*"
            self.markedCount += 1
        elif currentmark == "*":
            m = "?"
            self.markedCount -= 1
        elif currentmark == "?":
            m = ""
        self.setData(self.index(i,0), m, self.MARK)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    view = QQuickView()

    minesModel = MinesModel()

    ctx = view.rootContext()
    ctx.setContextProperty("minesModel", minesModel)

    view.engine().quit.connect(app.quit)
    view.setSource(QUrl("view.qml"))
    view.show()

    sys.exit(app.exec_())
