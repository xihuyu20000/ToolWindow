import sys,os

from PyQt5.QtCore import QUrl, pyqtSlot, QSize, QPoint
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWebKitWidgets import QWebPage, QWebView
from PyQt5.QtWidgets import QLabel, QMainWindow, QHeaderView, QMessageBox, QTableWidgetItem, QApplication
from qtpy import QtCore
from pyquery import PyQuery as pq
from lxml import etree
from ToolWindow import Ui_MainWindow
####使用webkit


class WebPage(QWebPage):
    def __init__(self, parent=None):
        super(WebPage, self).__init__(parent)

    def userAgentForUrl(self, QUrl):
        return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'

class WebEngineView(QWebView):
    windowList = []

    def __init__(self, parent=None):
        super(WebEngineView, self).__init__(parent)
        self.SELECT_FLAG = True
        self.covering = QLabel(self)

    def _initCover(self):
        '''
        遮罩层
        :return:
        '''
        rect = self.current_block.geometry()
        scrollPos = self.page().mainFrame().scrollPosition()
        self.covering.resize(QSize(rect.width(), rect.height()))
        self.covering.move(QPoint(rect.x()-scrollPos.x(), rect.y()-scrollPos.y()))
        self.covering.setStyleSheet("border-width: 4px;border-style: solid;border-color: rgb(255, 170, 0);")
        self.covering.show()

    # 重写createwindow()
    def createWindow(self, QWebEnginePage_WebWindowType):
        new_webview = QWebView()
        page = WebPage()
        new_webview.setPage(page)
        win = MainWin()
        win.setCentralWidget(new_webview)
        self.windowList.append(win)  # 注：没有这句会崩溃！！！
        return new_webview

    def mousePressEvent(self, event):
        if self.SELECT_FLAG and event.buttons() == QtCore.Qt.LeftButton:
            self.covering.hide()
            self.current_block = self.page().currentFrame().hitTestContent(event.pos()).element()
            self._initCover()

class MainWin(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWin, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('爬虫助手，非常方便  QQ群692711347')
        self.showMaximized()
        self.statusLabel = QLabel()
        self.statusBar().addWidget(self.statusLabel)
        self.browser = WebEngineView()
        self._loadBrowser("https://www.defense.gov/Explore/News/Listing/")
        self.browserLayout.addWidget(self.browser)

        self.tableWidget_defineField.setColumnCount(2)
        self.tableWidget_defineField.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tableWidget_defineField.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tableWidget_defineField.setHorizontalHeaderLabels(['字段名', '提取方式'])
        self._initBrowserLoadSignalSlot()
        self._initBrowserToolsSignalSlot()

        self.fields = []


    def _loadBrowser(self, url):
        self.lineEdit_url.setText(url)
        if url.startswith("http://") or url.startswith("https://"):
            self._url = url
        else:
            self._url = 'http://'+url
        self.browser.load(QUrl(self._url))

    @pyqtSlot()
    def loadUrl(self):
        '''
        加载新页面
        :return:
        '''
        self._loadBrowser(self.lineEdit_url.text())

    ##################################################################################################################
    def _initBrowserLoadSignalSlot(self):
        self.browser.loadFinished.connect(self.on_browserLoadFinished)
        self.browser.loadProgress.connect(self.on_browserLoadProcess)

    @pyqtSlot(int)
    def on_browserLoadProcess(self, process):
        self.statusLabel.setText('加载进度{}%'.format(process))

    @pyqtSlot()
    def on_browserLoadFinished(self):
        self.statusLabel.setText('页面加载完成')

    ##################################################################################################################
    def _initBrowserToolsSignalSlot(self):
        '''
        初始化操作信号和槽
        :return:
        '''
        self.pushButton_browserSelect.clicked.connect(self.on_browserSelect)
        self.pushButton_browserUnselect.clicked.connect(self.on_browserUnselect)
        self.pushButton_browserSelectParent.clicked.connect(self.on_browserSelectParent)
        self.pushButton_browserExtractText.clicked.connect(self.on_browserExtractText)
        self.pushButton_defineField_addRow.clicked.connect(self.on_defineField_addRow)
        self.pushButton_defineField_removeRow.clicked.connect(self.on_defineField_removeRow)
        self.pushButton_alldata_showData.clicked.connect(self.on_alldata_showData)
        self.pushButton_alldata_export.clicked.connect(self.on_pushButton_alldata_export)

    @pyqtSlot()
    def on_browserSelect(self):
        self.browser.SELECT_FLAG = True

    @pyqtSlot()
    def on_browserUnselect(self):
        self.browser.SELECT_FLAG = False
        self.browser.covering.hide()

    @pyqtSlot()
    def on_browserSelectParent(self):
        self.browser.current_block = self.browser.current_block.parent()
        self.browser.covering.hide()
        self.browser._initCover()

    @pyqtSlot()
    def on_browserExtractText(self):
        '''
        提取文本
        :return:
        '''
        if self.browser.current_block==None:
            QMessageBox.about(self, self.tr('提示'), self.tr('请先选中元素'))
            return
        self.plainTextEdit_html.setPlainText(self.browser.current_block.toOuterXml())
        data = self.browser.current_block.toOuterXml()
        from bs4 import BeautifulSoup as soup

        pretty = soup(data, 'html5lib').prettify()
        pretty = pretty.replace('''<html>
 <head>
 </head>
 <body>''', '')
        pretty = pretty.replace(''' </body>
</html>''','')
        self.plainTextEdit_html.setPlainText(pretty)


    @pyqtSlot()
    def on_defineField_addRow(self):
        '''
        添加行
        :return:
        '''
        self.tableWidget_defineField.setRowCount(self.tableWidget_defineField.rowCount()+1)
        self.tableWidget_defineField.setItem(self.tableWidget_defineField.rowCount(), 0, QTableWidgetItem('字段名称'))
        self.tableWidget_defineField.setItem(self.tableWidget_defineField.rowCount(), 1, QTableWidgetItem('提取方式'))

    @pyqtSlot()
    def on_defineField_removeRow(self):
        '''
        删除行
        :return:
        '''
        self.tableWidget_defineField.removeRow(self.tableWidget_defineField.currentRow())

    @pyqtSlot()
    def on_alldata_showData(self):
        '''
        显示数据
        :return:
        '''
        root = etree.HTML(self.browser.page().currentFrame().toHtml())

        try:
            self.fields = []
            for i in range(self.tableWidget_defineField.rowCount()):
                if self.tableWidget_defineField.item(i, 0) == None \
                        or self.tableWidget_defineField.item(i, 1) == None \
                        or self.tableWidget_defineField.item(i, 0).text() == '' \
                        or self.tableWidget_defineField.item(i, 1).text() == '':
                    QMessageBox.about(self, self.tr('提示'), self.tr('第{}行的数据，不允许空'.format(i)))
                    return
                name = self.tableWidget_defineField.item(i, 0).text()
                express = self.tableWidget_defineField.item(i, 1).text()
                self.fields.append(Field(name, express, [item.strip() for item in root.xpath(express)]))

            if len(self.fields) == 0:
                QMessageBox.about(self, self.tr('提示'), self.tr('没有数据'))
                return
        except Exception as e:
            self.textBrowser_info.setText(str(e))
            return

        model = QStandardItemModel()
        model.setHorizontalHeaderLabels([f.name for f in self.fields])

        for row in range(len(self.fields[0].values)):
            for column in range(len(self.fields)):
                item = QStandardItem(self.fields[column].values[row])
                # 设置每个位置的文本值
                model.setItem(row, column, item)

        self.tableView_alldata.setModel(model)
        self.statusLabel.setText('正确显示数据')

    @pyqtSlot()
    def on_pushButton_alldata_export(self):
        '''
        导出数据
        :return:
        '''
        if len(self.fields) == 0:
            QMessageBox.about(self, self.tr('提示'), self.tr('没有数据'))
            return False
        import xlwt
        wb = xlwt.Workbook(encoding='utf8')  # 创建实例，并且规定编码
        ws = wb.add_sheet('第一个')  # 设置工作表名称

        for column in range(len(self.fields)):
            ws.write(0, column, self.fields[column].name)

        for row in range(len(self.fields[0].values)):
            for column in range(len(self.fields)):
                ws.write(row+1, column, self.fields[column].values[row])
        xlspath = os.path.join(os.path.join(os.path.expanduser('~'), "Desktop"), '爬虫数据.xls')
        wb.save(xlspath)
        QMessageBox.about(self, self.tr('提示'), self.tr('数据已经保存到桌面'))


class Field():
    def __init__(self, name, express, value, width=100):
        self.name = name
        self.express = express
        self.values = value
        self.width = width





if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = MainWin()
    ui.show()
    sys.exit(app.exec_())