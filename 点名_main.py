import sys
import random
from PyQt5.QtWidgets import QMainWindow, QApplication
from 点名 import Ui_MainWindow


TITLE = '点名助手'


class MainWin(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWin, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(TITLE)

        self.class171 = ['魏梦珂','朱亚宁','王林帅','任自强','贾富洋','郭豫川','袁露  ','畅豫霄','朱坤  ','李丙潮','梁鹏威','胡顺顺','郭国超','陈畅  ','王浩天','林昱廷','张世哲','王宗伟','邵亚崇','刘文超','赵景倩','王天赐','杨瑞琳','张裕鹏','毕晓辉','罗力昌','雷雨旸','严淅峰','王业晨','张朋  ','杨南南','符世长','杜岩森','郭英杰']
        self.class172 = ['高雨晴','崔梦豪','祁帅宾','白高翔','王业浩','刘帅航','囤轲  ','朱玉诚','高远  ','李乾玺','侯亚坤','杨旭升','杨尚衡','孙启智','张扬  ','付东洋','李婧馨','卢梦丽','梁昆  ','张小兵','李玉磊','余金成','韩梦楠','经冠奇','胡一鸣','徐晓霞','赵威庆','刘新宇','仝钰辉','董文娜','张印  ','刘跃峰','杨嘉昊','韩兆龙','滕新  ','张洁  ','杨鑫鑫','李田鑫','程聪帅']
        self.pushButton_171.clicked.connect(self.on_click171)
        self.pushButton_172.clicked.connect(self.on_click172)

    def on_click171(self):
        self.label.setText(self.class171[random.randint(0, len(self.class171)-1)])

    def on_click172(self):
        self.label.setText(self.class172[random.randint(0, len(self.class172)-1)])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = MainWin()
    ui.show()
    sys.exit(app.exec_())