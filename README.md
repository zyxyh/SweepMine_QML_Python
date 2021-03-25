# SweepMine_QML_Python
扫雷 Python-QML交互
扫雷游戏
增加了左右键同时点击功能

QML 提供界面， Python处理后台逻辑， 实现界面和逻辑的分离

采用Model/View方式，Python定义了一个模型，继承自QAbstractListModel
模型每个元素代表一个方块，其MINEFLAG表示是否是地雷，OPENEDFLAG表示是否被揭开
MARK是每个方块的标记状态（""、"*"、"?"）
MINESAROUND记录每个方块周围的地雷数

各个状态的变化自动反映在QML中
rowCount、data、setData、rowNames、flags函数要被更新重载才行
注意data、setData函数的参数index为QModelIndex类型，要用其row()函数获取其每一行的内容
每一行是字典类型，根据其role值确定其内容
修改每一项内容需要先确定其flags是否可编辑，因此在__init__()构造函数中用setFlags()设定为
Qt.ItemIsEditable(注意要与其原flag"并"运算)
rowNames函数使QML中可以直接引用role值，注意其类型为byte，不是字符串，因此要用b'name'形式
setData函数根据index和Role修改具体数据，修改好后注意要发射dataChanged信号，来通知QML更新
显示正确内容

open函数揭开指定的方块。注意其参数为整数，要修改对应方块的状态需要用self.index(r, c)返回
QModelIndex类型才可调用data、setData函数。首次调用判断gameStatus，如果为0，表示处于等待状态
此时调用spread_mines函数，随机散布地雷，注意要把第一次点击的地方及周围不分布地雷，防止
第一次就碰上地雷。地雷分布好后，记录每块周围的地雷数

QML 中用一个Repeater展示python里的Model，每个方块儿用minedelegata来delegate
方块根据Model中的index来设置x,y值，根据其openedflag来确定其颜色，用一个Text来显示内容：
如果已经揭开，显示其周围地雷数，如果没有揭开则显示其mark值
minedelegata中定义了两标志：lbtnPressed、rbtnPressed表示左右键被按下，如果都为真表示左右键按下状态
表示要把周围翻开。以解决没有左右键同时按的信号的问题。此处逻辑折腾我很久。

还有不完美的地方，如应定义两个信号来通知python该揭开，还是该mark，此处是直接调用，有些不自然。
还有应该定义几个状态（State），来确定方块的外观，便于后期扩展。
