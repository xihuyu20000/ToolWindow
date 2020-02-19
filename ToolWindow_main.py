import sys
import os
import copy
import json
import xlwt

from PyQt5.QtCore import QUrl, pyqtSlot, QSize, QPoint
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWebKitWidgets import QWebPage, QWebView
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtWidgets import QLabel, QButtonGroup, QFileDialog

from qtpy import QtCore
from lxml import etree

from bs4 import BeautifulSoup as soup
import execjs
from ToolWindow import Ui_MainWindow
from model import FileSink, Task, FieldModel

from utils import show_dialog, parse

TITLE = '爬虫助手，非常方便  QQ群692711347'



class WebPage(QWebPage):
    def __init__(self, parent=None):
        super(WebPage, self).__init__(parent)

    def userAgentForUrl(self, url):
        return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'

class WebEngineView(QWebView):
    windowList = []

    def __init__(self, parent=None):
        super(WebEngineView, self).__init__(parent)
        self.SELECT_FLAG = True
        self.covering = QLabel(self)
        self.current_block = None

    def _initCover(self):
        '''
        遮罩层
        :return:
        '''
        rect = self.current_block.geometry()
        scroll_pos = self.page().mainFrame().scrollPosition()
        self.covering.resize(QSize(rect.width(), rect.height()))
        self.covering.move(QPoint(rect.x()-scroll_pos.x(), rect.y()-scroll_pos.y()))
        self.covering.setStyleSheet("border-width: 2px;border-style: dashed;border-color: rgb(255, 170, 0);")
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
        self.setWindowTitle(TITLE)
        self.showMaximized()

        self.current_item = None
        self._url = ''

        self.statusLabel = QLabel()
        self.statusLabel.setMaximumWidth(500)
        self.statusBar().addWidget(self.statusLabel)

        self.browser = WebEngineView()
        self.browser.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
        self.verticalLayout_browser.addWidget(self.browser)

        self.widget_autopagermode.hide()

        self.browser.loadFinished.connect(self.on_browserLoadFinished)
        self.browser.loadProgress.connect(self.on_browserLoadProcess)
        self.pushButton_load.clicked.connect(self.on_browser_loadUrl)
        self.pushButton_browserSelect.clicked.connect(self.on_browserSelect)
        self.pushButton_browserUnselect.clicked.connect(self.on_browserUnselect)

        self.pushButton_extract_link.clicked.connect(self.on_extract_link)
        self.pushButton_extract_text.clicked.connect(self.on_extract_text)
        self.pushButton_extract_preview.clicked.connect(self.on_extract_preview)
        self.pushButton_express_save_field.clicked.connect(self.on_express_save_field)

        self.pushButton_browserContent.clicked.connect(self.on_browserContent)
        self.pushButton_browserSelectParent.clicked.connect(self.on_browserSelectParent)

        self.checkBox_autopager.stateChanged.connect(self.on_checkBox_autopager_stateChanged)
        self.pushButton_pager_test.clicked.connect(self.on_pushButton_pager_test_clicked)
        self.field_group = QButtonGroup()

        self.itemModel = QStandardItemModel()
        self.itemModel.dataChanged.connect(self.on_fields_model_dataChanged)
        self.listView_fields.setModel(self.itemModel)
        self.listView_fields.clicked.connect(self.on_fields_clicked)


        self.pushButton_fieldAdd.clicked.connect(self.on_fieldAdd_clicked)
        self.pushButton_fieldRemove.clicked.connect(self.on_fieldRemove_clicked)
        self.pushButton_fieldCopy.clicked.connect(self.on_fieldCopy_clicked)
        self.pushButton_fieldSave.clicked.connect(self.on_fieldSave_clicked)
        self.pushButton_fieldPreview.clicked.connect(self.on_fieldPreview_clicked)
        self.pushButton_export.clicked.connect(self.on_export_clicked)

        self.groupBox_saveFile.hide()
        self.groupBox_savemysql.hide()
        self.checkBox_savefile_is.stateChanged.connect(self.on_checkBox_savefile_is_stateChanged)
        self.checkBox_savemysql_is.stateChanged.connect(self.on_checkBox_savemysql_is_stateChanged)
        self.pushButton_saveFile_chooseName.clicked.connect(self.on_saveFile_chooseName)
        self.pushButton_exportTask.clicked.connect(self.on_exportTask_clicked)

        self.browser.load(QUrl('http://www.cnblogs.com'))


    @pyqtSlot()
    def on_browser_loadUrl(self):
        '''
        加载页面
        :return:
        '''
        if not self.lineEdit_url.text().strip():
            show_dialog('请输入网址')
            return
        self._buildUrl(self.lineEdit_url.text())
        self.browser.load(QUrl(self._url))

    def _buildUrl(self, url):
        self.lineEdit_url.setText(url)
        if url.startswith("http://") or url.startswith("https://"):
            self._url = url
        else:
            self._url = 'http://'+url
        self.plainTextEdit_urls.setPlainText(self._url)

    ##################################################################################################################
    @pyqtSlot(int)
    def on_browserLoadProcess(self, process):
        self.statusLabel.setText('加载进度{}%'.format(process))

    @pyqtSlot()
    def on_browserLoadFinished(self):
        self.statusLabel.setText('页面加载完成')

        # self._auto_click("//a[starts-with(text(),'Next')]")


    def _auto_click(self, xpath):
        try:
            self.browser.page().mainFrame().evaluateJavaScript('''
                var evaluator = new XPathEvaluator();
                var result = evaluator.evaluate("{}", document.documentElement, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                result.singleNodeValue.click();
            '''.format(xpath))
        except Exception as e:
            show_dialog(e)

    ##################################################################################################################

    @pyqtSlot()
    def on_browserSelect(self):
        self.browser.SELECT_FLAG = True

    @pyqtSlot()
    def on_browserUnselect(self):
        self.browser.SELECT_FLAG = False
        self.browser.covering.hide()

    @pyqtSlot()
    def on_browserSelectParent(self):
        if self.browser.current_block is None:
            show_dialog('请先选中元素')
            return
        self.browser.current_block = self.browser.current_block.parent()
        self.browser.covering.hide()
        self.browser._initCover()

        self.on_browserContent()

    @pyqtSlot(int)
    def on_checkBox_autopager_stateChanged(self, state):
        if state:
            self.widget_autopagermode.show()
        else:
            self.widget_autopagermode.hide()

    @pyqtSlot()
    def on_pushButton_pager_test_clicked(self):
        xpath = self.lineEdit_pager_xpath.text()
        if xpath is None or str(xpath).strip() == '':
            show_dialog('请输入翻页表达式')
            return
        self._auto_click(xpath)

    @pyqtSlot()
    def on_extract_link(self):
        if self.browser.current_block is None:
            show_dialog('请先选中元素')
            return

        data = self.browser.current_block.toOuterXml()
        pretty = soup(data, 'html5lib').body

        self.lineEdit_express.setText(parse(pretty, '@href'))

        values = [item.strip() for item in etree.HTML(self.browser.page().currentFrame().toHtml()).xpath(self.lineEdit_express.text())]
        self.plainTextEdit_field_value.setPlainText('\r\n\r\n'.join(values))
        self.statusLabel.setText('数据{}条'.format(len(values)))

    @pyqtSlot()
    def on_extract_text(self):
        if self.browser.current_block is None:
            show_dialog('请先选中元素')
            return
        data = self.browser.current_block.toOuterXml()
        pretty = soup(data, 'html5lib').body
        self.lineEdit_express.setText(parse(pretty, 'text()'))

        values = [item.strip() for item in etree.HTML(self.browser.page().currentFrame().toHtml()).xpath(self.lineEdit_express.text())]
        self.plainTextEdit_field_value.setPlainText('\r\n\r\n'.join(values))
        self.statusLabel.setText('数据{}条'.format(len(values)))

    @pyqtSlot()
    def on_extract_preview(self):
        '''
        表达式地方，预览数据
        :return:
        '''
        if self.lineEdit_express.text() is None:
            show_dialog('请输入表达式')
            return
        try:
            values = [item.strip() for item in etree.HTML(self.browser.page().currentFrame().toHtml()).xpath(self.lineEdit_express.text())]
            self.plainTextEdit_field_value.setPlainText('\r\n\r\n'.join(values))
            self.statusLabel.setText('数据{}条'.format(len(values)))
        except Exception as e:
            show_dialog(e)

    @pyqtSlot()
    def on_express_save_field(self):
        '''
        表达式地方，保存字段
        :return:
        '''
        fieldModel = FieldModel('字段')
        fieldModel.style = 'xpath'
        fieldModel.express = self.lineEdit_express.text()
        fieldModel.code = ''
        item = QStandardItem('字段')
        item.setData(fieldModel)
        self.itemModel.appendRow(item)

    @pyqtSlot()
    def on_browserContent(self):
        '''
        网页内容
        :return:
        '''
        if self.browser.current_block is None:
            show_dialog('请先选中元素')
            return
        self.plainTextEdit_html.setPlainText(self.browser.current_block.toOuterXml())
        # data = self.browser.current_block.toOuterXml()
        #
        #
        # pretty = soup(data, 'html5lib').body.contents[0]
        # self.plainTextEdit_html.setPlainText(str(pretty))


    def on_fields_model_dataChanged(self):
        '''
        修改名称
        :return:
        '''
        self.current_item.data().name = self.current_item.text()

    def on_fields_clicked(self, modelIndex):
        '''
        选择不同的字段
        :param modelIndex:
        :return:
        '''
        self.current_item = self.itemModel.itemFromIndex(modelIndex)
        fieldModel = self.current_item.data()

        self.lineEdit_field_express.setText(fieldModel.express)
        self.plainTextEdit_code.setPlainText(fieldModel.code)

    def on_fieldAdd_clicked(self):
        item = QStandardItem('字段')
        item.setData(FieldModel('字段'))
        self.current_item = item
        self.itemModel.appendRow(item)

    def on_fieldRemove_clicked(self):
        index = self.listView_fields.currentIndex()
        if index.row() > -1:
            self.itemModel.removeRow(index.row())
            self.current_item = None

    def on_fieldCopy_clicked(self):
        if self.current_item is None:
            show_dialog('请先选择一个字段')
            return

        self.on_fieldSave_clicked()

        item = QStandardItem(self.current_item.text())
        item.setData(copy.deepcopy(self.current_item.data()))
        self.itemModel.appendRow(item)

    def on_fieldSave_clicked(self):
        '''
        保存
        :return:
        '''
        if self.itemModel.rowCount() == 0:
            show_dialog('请先添加一个字段')
            return
        if self.current_item is None:
            self.current_item = self.itemModel.item(0, 0)
        fieldModel = self.current_item.data()
        fieldModel.style = 'xpath'
        fieldModel.express = self.lineEdit_field_express.text()
        fieldModel.code = self.plainTextEdit_code.toPlainText()
        self.current_item.setData(fieldModel)

    def on_fieldPreview_clicked(self):
        '''
        预览数据
        :return:
        '''
        content = self.browser.page().currentFrame().toHtml()
        root = etree.HTML(content)

        self.on_fieldSave_clicked()

        try:
            for i in range(self.itemModel.rowCount()):
                fieldModel = self.itemModel.item(i, 0).data()
                print(fieldModel.name, fieldModel.style)
                fieldModel.values = [item.strip() for item in root.xpath(fieldModel.express)]
                ##################处理字段信息
                resu = []
                for value in fieldModel.values:
                    value = str(value).strip()
                    if fieldModel.code:
                        print(fieldModel.code)
                        resu.append(execjs.compile(fieldModel.code).call('parse', value))
                    else:
                        resu.append(value)
                fieldModel.values = resu
                self.task.log.info('解析字段', fieldModel.name, fieldModel.result)

                self.itemModel.item(i, 0).setData(fieldModel)

            model = QStandardItemModel()
            labels = []
            for column in range(self.itemModel.rowCount()):
                labels.append(self.itemModel.item(column, 0).data().name)
                values = self.itemModel.item(column, 0).data().values
                for row in range(len(values)):
                    model.setItem(row, column, QStandardItem(values[row]))
            model.setHorizontalHeaderLabels(labels)
            self.tableView_alldata.setModel(model)
            self.statusLabel.setText('正确显示数据')
        except Exception as exp:
            show_dialog(str(exp))


    def on_export_clicked(self):
        '''
        导出数据
        :return:
        '''
        self.on_fieldSave_clicked()


        wb = xlwt.Workbook(encoding='utf8')  # 创建实例，并且规定编码
        ws = wb.add_sheet('第一个')  # 设置工作表名称

        labels = []
        for column in range(self.itemModel.rowCount()):
            labels.append(self.itemModel.item(column, 0).data().name)
            values = self.itemModel.item(column, 0).data().values
            for row in range(len(values)):
                ws.write(row+1, column, values[row])

        for i in range(len(labels)):
            ws.write(0, i, labels[i])

        wb.save(os.path.join(os.path.join(os.path.expanduser('~'), "Desktop"), '爬虫数据.xls'))
        show_dialog('数据已经保存到桌面')

    # def on_pager_preview_clicked(self):
    #     if self.checkBox_pager_is.isChecked():
    #         root = etree.HTML(self.browser.page().currentFrame().toHtml())
    #
    #         try:
    #             model = QStandardItemModel()
    #             for index,page in enumerate(root.xpath(self.lineEdit_pager_express.text())):
    #                 model.setItem(index, 0, QStandardItem(page))
    #             model.setHorizontalHeaderLabels([''])
    #             self.tableView_alldata.setModel(model)
    #             self.statusLabel.setText('正确显示数据')
    #         except Exception as e:
    #             showDialog(str(e))

    @pyqtSlot(int)
    def on_checkBox_savefile_is_stateChanged(self, state):
        if state:
            self.groupBox_saveFile.show()
        else:
            self.groupBox_saveFile.hide()

    @pyqtSlot(int)
    def on_checkBox_savemysql_is_stateChanged(self, state):
        '''
        是否保存到mysql中
        :param state:
        :return:
        '''
        if state:
            self.groupBox_savemysql.show()
        else:
            self.groupBox_savemysql.hide()

    def on_saveFile_chooseName(self):
        dir_choose = QFileDialog.getExistingDirectory(self, "选取文件夹", os.path.join(os.path.expanduser('~'), "Desktop"))
        if dir_choose == "":
            show_dialog('请选择一个文件夹')
            return

        self.lineEdit_savefile_filename.setText(dir_choose)

    def on_exportTask_clicked(self):
        if self.lineEdit_taskName.text() is None:
            show_dialog('请输入任务名称')
            return

        try:
            task = Task(self.lineEdit_taskName.text())
            task.source = self.plainTextEdit_urls.toPlainText().split('\n')
            for i in range(self.itemModel.rowCount()):
                task.fields.append(self.itemModel.item(i, 0).data().__dict__)

            if self.checkBox_savefile_is.isChecked():
                task.sinks.append(FileSink(self.lineEdit_savefile_filename.text(), self.lineEdit_savefile_sep.text()).__dict__)

            with open(os.path.join(os.path.join(os.path.expanduser('~'), "Desktop"), '爬虫任务.txt'), 'w', encoding='utf8') as file:
                file.write(json.dumps(task.__dict__, ensure_ascii=False))
            show_dialog('数据已经保存到桌面')
        except Exception as exp:
            show_dialog(str(exp))








if __name__ == '__main__':
    APP = QApplication(sys.argv)
    UI = MainWin()
    UI.show()
    sys.exit(APP.exec_())