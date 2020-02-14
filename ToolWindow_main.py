import sys
import os
import copy
import time
import json
import tempfile,uuid

import demjson
import requests

import execjs
from PyQt5.QtCore import QUrl, pyqtSlot, QSize, QPoint
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWebKit import QWebSettings
from PyQt5.QtWebKitWidgets import QWebPage, QWebView
from PyQt5.QtWidgets import QLabel, QMainWindow, QMessageBox, QApplication, QButtonGroup
from json2html import json2html
from qtpy import QtCore
from lxml import etree
from bs4 import BeautifulSoup as soup, Tag
from ToolWindow import Ui_MainWindow


TITLE = '爬虫助手，非常方便  QQ群692711347'

def parse(tag, style='text'):
    tags = []
    def _parseAttrs(tag):
        if tag.attrs:
            for key, value in tag.attrs.items():
                if key == 'class':
                    exp = '''//{}[@{}='{}']'''.format(tag.name, key, ' '.join(value))
                    return exp
            return '//' + tag.name
        else:
            return '//'+tag.name
    def _parseChild(tags, tag):
        if tag:
            flag = True
            for item in tag.children:
                if isinstance(item, Tag):
                    if flag:
                        tags.append(_parseAttrs(item))
                        _parseChild(tags, item)
                        flag=False
    _parseChild(tags, tag)
    tags.append('//')
    tags.append(style)
    return ''.join(tags)

class Log():
    def info(self, *msg):
        print('【log info】', time.strftime("%Y-%m-%d %H:%M:%S"), msg)
    def error(self, *msg):
        print('【log error】', time.strftime("%Y-%m-%d %H:%M:%S"), msg)

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
        self.current_block = None

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
        self.setWindowTitle(TITLE)
        self.showMaximized()

        self.statusLabel = QLabel()
        self.statusLabel.setMaximumWidth(500)
        self.statusBar().addWidget(self.statusLabel)

        self.browser = WebEngineView()
        self.verticalLayout_browser.addWidget(self.browser)

        self.widget_quickmode.hide()

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

        self.checkBox_quickmode.stateChanged.connect(self.on_quickmode_stateChanged)

        self.field_group =QButtonGroup()

        self.current_item = []

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

        self.pushButton_exportTask.clicked.connect(self.on_exportTask_clicked)



    @pyqtSlot()
    def on_browser_loadUrl(self):
        '''
        加载页面
        :return:
        '''
        if not self.lineEdit_url.text().strip():
            QMessageBox.about(self, self.tr('提示'), self.tr('请输入网址'))
            return
        self._buildUrl(self.lineEdit_url.text())
        if self.checkBox_quickmode.isChecked()==False:
            self._buildUrl(self.lineEdit_url.text())
            self.browser.load(QUrl(self._url))
        else:
            headers = {}
            params = {}
            if self.plainTextEdit_request_useragent.toPlainText():
                headers['User-Agent']=self.plainTextEdit_request_useragent.toPlainText()
            if self.plainTextEdit_request_cookie.toPlainText():
                headers['Cookie'] = self.plainTextEdit_request_cookie.toPlainText()
            if self.plainTextEdit_request_params.toPlainText():
                for item in self.plainTextEdit_request_params.toPlainText().split('\n'):
                    if item and item.strip():
                        arr = item.split(':')
                        params[arr[0]] = arr[1].strip()
            response = requests.request(str(self.comboBox_request_method.currentText()).upper(), self._url, headers=headers, params=params)
            content = ''
            if self.comboBox_request_content.currentText()=='text':
                content = response.text

            cnt_dict = demjson.decode(content, encoding='utf8')
            tempfilename = os.path.join(os.path.abspath(tempfile.gettempdir()), str(uuid.uuid4())+'.html')
            with open(tempfilename, 'w', encoding='utf-8') as f:
                f.write(json2html.convert(cnt_dict))
            self.browser.settings().setAttribute(QWebSettings.LocalContentCanAccessRemoteUrls, True)
            self.browser.settings().setDefaultTextEncoding('utf-8')
            self.browser.load(QUrl.fromLocalFile(tempfilename))


    def _buildUrl(self, url):
        self.lineEdit_url.setText(url)
        if url.startswith("http://") or url.startswith("https://"):
            self._url = url
        else:
            self._url = 'http://'+url

    ##################################################################################################################
    @pyqtSlot(int)
    def on_browserLoadProcess(self, process):
        self.statusLabel.setText('加载进度{}%'.format(process))

    @pyqtSlot()
    def on_browserLoadFinished(self):
        self.statusLabel.setText('页面加载完成')

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
        if self.browser.current_block==None:
            QMessageBox.about(self, self.tr('提示'), self.tr('请先选中元素'))
            return
        self.browser.current_block = self.browser.current_block.parent()
        self.browser.covering.hide()
        self.browser._initCover()

    @pyqtSlot(int)
    def on_quickmode_stateChanged(self, state):
        if state:
            self.widget_quickmode.show()
        else:
            self.widget_quickmode.hide()

    @pyqtSlot()
    def on_extract_link(self):
        if self.browser.current_block==None:
            QMessageBox.about(self, self.tr('提示'), self.tr('请先选中元素'))
            return

        data = self.browser.current_block.toOuterXml()
        pretty = soup(data, 'html5lib').body
        self.lineEdit_express.setText(parse(pretty, '@href'))

        values = [item.strip() for item in etree.HTML(self.browser.page().currentFrame().toHtml()).xpath(self.lineEdit_express.text())]
        self.plainTextEdit_field_value.setPlainText('\r\n\r\n'.join(values))
        self.statusLabel.setText('数据{}条'.format(len(values)))

    @pyqtSlot()
    def on_extract_text(self):
        if self.browser.current_block==None:
            QMessageBox.about(self, self.tr('提示'), self.tr('请先选中元素'))
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
        if self.lineEdit_express.text()==None:
            QMessageBox.about(self, self.tr('提示'), self.tr('请输入表达式'))
            return
        try:
            values = [item.strip() for item in etree.HTML(self.browser.page().currentFrame().toHtml()).xpath(self.lineEdit_express.text())]
            self.plainTextEdit_field_value.setPlainText('\r\n\r\n'.join(values))
            self.statusLabel.setText('数据{}条'.format(len(values)))
        except Exception as e:
            QMessageBox.about(self, self.tr('提示'), str(e))

    @pyqtSlot()
    def on_express_save_field(self):
        '''
        表达式地方，保存字段
        :return:
        '''
        fieldModel = FieldModel('字段')
        fieldModel.style = 'xpath'
        fieldModel.express = self.lineEdit_express.text()
        fieldModel.head = ''
        fieldModel.tail = ''
        fieldModel.headinclude = True
        fieldModel.tailinclude = False
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
        if self.browser.current_block==None:
            QMessageBox.about(self, self.tr('提示'), self.tr('请先选中元素'))
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
        self.current_item.data().name =self.current_item.text()

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
        self.itemModel.appendRow(item)

    def on_fieldRemove_clicked(self):
        index = self.listView_fields.currentIndex()
        if index.row()>-1:
            self.itemModel.removeRow(index.row())
            self.current_item = None

    def on_fieldCopy_clicked(self):
        if self.current_item==None:
            QMessageBox.about(self, self.tr('提示'), self.tr('请先选择一个字段'))
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
        if self.itemModel.rowCount()==0:
            QMessageBox.about(self, self.tr('提示'), self.tr('请先添加一个字段'))
            return
        if self.current_item==None:
            self.current_item = self.itemModel.item(0,0)
        fieldModel = self.current_item.data()
        fieldModel.style = 'xpath'
        fieldModel.express = self.lineEdit_field_express.text()
        fieldModel.code = self.plainTextEdit_code.toPlainText()
        self.current_item.setData(fieldModel)

    def on_fieldPreview_clicked(self):
        '''
        显示数据
        :return:
        '''
        content = self.browser.page().currentFrame().toHtml()
        root = etree.HTML(content)

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
                # self.task.log.info('解析字段', fieldModel.name, fieldModel.result)

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
        except Exception as e:
            QMessageBox.about(self, self.tr('提示'), self.tr(str(e)))


    def on_export_clicked(self):
        '''
        导出数据
        :return:
        '''
        import xlwt
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
        QMessageBox.about(self, self.tr('提示'), self.tr('数据已经保存到桌面'))

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
    #             QMessageBox.about(self, self.tr('提示'), self.tr(str(e)))

    def on_exportTask_clicked(self):
        if self.lineEdit_taskName.text()==None:
            QMessageBox.about(self, self.tr('提示'), self.tr('请输入任务名称'))
            return

        try:
            task = Task(self.lineEdit_taskName.text())
            task.source = self.plainTextEdit_urls.toPlainText().split('\n')
            for i in range(self.itemModel.rowCount()):
                task.fields.append(self.itemModel.item(i, 0).data().__dict__)

            task.deduplication = self.checkBox_pager_is.isChecked()

            if self.checkBox_savefile_is.isChecked():
                task.sinks.append(FileSink(self.lineEdit_savefile_filename.text(), self.lineEdit_savefile_sep.text()).__dict__)

            with open(os.path.join(os.path.join(os.path.expanduser('~'), "Desktop"), '爬虫任务.txt'), 'w', encoding='utf8') as f:
                f.write(json.dumps(task.__dict__ , ensure_ascii=False))
            QMessageBox.about(self, self.tr('提示'), self.tr('数据已经保存到桌面'))
        except Exception as e:
            QMessageBox.about(self, self.tr('提示'), self.tr(str(e)))



class Task():
    def __init__(self, name, source=None, sinks=[], fields=[], pager=None, deduplication=False):
        self.name = name
        self.source = source
        self.sinks = sinks
        self.fields = fields
        self.pager = pager
        self.deduplication = deduplication



class FieldModel(object):
    def __init__(self, name, style='xpath', express='', code=''):
        self.name = name
        self.style = style
        self.express = express
        self.code = code
        self.values = []

class FileSink():
    def __init__(self, filename, sep):
        self.filename = filename
        self.sep = sep


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = MainWin()
    ui.show()
    sys.exit(app.exec_())