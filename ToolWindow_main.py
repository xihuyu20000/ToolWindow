import re
import sys,os,copy
import time
import json
from PyQt5.QtCore import QUrl, pyqtSlot, QSize, QPoint
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWebKitWidgets import QWebPage, QWebView
from PyQt5.QtWidgets import QLabel, QMainWindow, QHeaderView, QMessageBox, QTableWidgetItem, QApplication, QButtonGroup
from apscheduler.jobstores import redis
from qtpy import QtCore
from pyquery import PyQuery as pq
from lxml import etree


from ToolWindow import Ui_MainWindow
####使用webkit

class Log():
    def info(self, *msg):
        print('【log info】', time.strftime("%Y-%m-%d %H:%M:%S"), msg)
    def error(self, *msg):
        print('【log error】', time.strftime("%Y-%m-%d %H:%M:%S"), msg)

class RedisConfig():
    def __init__(self, password=None, host='127.0.0.1', port=6379):
        self.password = password
        self.host = host
        self.port = port
class ConsoleSink():
    def __init__(self, sep='\t\t'):
        self.sep = sep

class FileSink():
    def __init__(self, filename, sep):
        self.filename = filename
        self.sep = sep

class RedisUtil():
    def __init__(self, config):
        self.config = config
        self.pool = redis.ConnectionPool(host=self.config.host, port=self.config.port, password=self.config.password)
        self.r = redis.Redis(connection_pool=self.pool)

    def isDuplicated(self, name, value):
        '''
        判断是否重复
        :param name:
        :param value:
        :return:
        '''
        ret = self.r.sismember(name, value)
        if ret==False:
            self.r.sadd(name, value)
        return ret
class Sink():
    def __init__(self, task):
        self.task = task

    def run(self):
        if isinstance(self.task.sink, ConsoleSink):
            print('***************************************************************************************')
            print(self.task.sink.sep.join(self.task.titles))
            for row in self.task.rows:
                print(self.task.sink.sep.join(row))
        elif isinstance(self.task.sink, FileSink):
            filepath = os.path.join(self.task.sink.dirpath, self.task.sink.filename)
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(self.task.sink.sep.join(self.task.titles))
                f.write('\r\n')
                for row in self.task.rows:
                    f.write(self.task.sink.sep.join(row))
                    f.write('\r\n')
class FileSource():
    def __init__(self, dirpath, filename, sep='\t', index=0):
        self.dirpath = dirpath
        self.filename = filename
        self.sep = sep
        self.index = index

class DataUtil():
    @staticmethod
    def formatDate(t, format):
        '''
        格式化日期时间
        :param t:
        :param format:
        :return:
        '''
        format = format.replace('年', '%Y')
        format = format.replace('月', '%m')
        format = format.replace('日', '%d')
        format = format.replace('时', '%H')
        format = format.replace('分', '%M')
        format = format.replace('秒', '%S')
        timeStruct = time.strptime(t, format)
        strTime = time.strftime("%Y-%m-%d %H:%M:%S", timeStruct)
        return strTime

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
        self.setWindowTitle('爬虫助手，非常方便  QQ群692711347')
        self.showMaximized()

        self.statusLabel = QLabel()
        self.statusLabel.setMaximumWidth(500)
        self.statusBar().addWidget(self.statusLabel)

        self.browser = WebEngineView()
        self._loadBrowser("https://stackoverflow.com/search?q=python++class+copy")
        self.verticalLayout_browser.addWidget(self.browser)

        self.browser.loadFinished.connect(self.on_browserLoadFinished)
        self.browser.loadProgress.connect(self.on_browserLoadProcess)

        self.pushButton_browserSelect.clicked.connect(self.on_browserSelect)
        self.pushButton_browserUnselect.clicked.connect(self.on_browserUnselect)
        self.pushButton_browserSelectParent.clicked.connect(self.on_browserSelectParent)
        self.pushButton_browserExtractText.clicked.connect(self.on_browserExtractText)

        self.field_group =QButtonGroup()
        self.field_group.addButton(self.radioButton_field_xpath)
        self.field_group.addButton(self.radioButton_field_headtail)
        self.current_item = None
        self.pagermodel = PagerModel()
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
        self.pushButton_pager_preview.clicked.connect(self.on_pager_preview_clicked)

        self.pushButton_exportTask.clicked.connect(self.on_exportTask_clicked)



    @pyqtSlot()
    def loadUrl(self):
        '''
        加载新页面
        :return:
        '''
        self._loadBrowser(self.lineEdit_url.text())

    def _loadBrowser(self, url):
        self.lineEdit_url.setText(url)
        if url.startswith("http://") or url.startswith("https://"):
            self._url = url
        else:
            self._url = 'http://'+url
        self.browser.load(QUrl(self._url))

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
        if fieldModel.style=='xpath':
            self.radioButton_field_xpath.setChecked(True)
        if fieldModel.style=='headtail':
            self.radioButton_field_headtail.setChecked(True)
        self.lineEdit_field_express.setText(fieldModel.express)
        self.checkBox_field_headinclude.setChecked(fieldModel.headinclude)
        self.checkBox_field_tailinclude.setChecked(fieldModel.tailinclude)
        self.textEdit_field_head.setText(fieldModel.head)
        self.textEdit_field_tail.setText(fieldModel.tail)
        self.lineEdit_field_datepattern.setText(fieldModel.datepattern)

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
        if self.current_item==None:
            self.current_item = self.itemModel.item(0,0)
        fieldModel = self.current_item.data()
        if self.radioButton_field_xpath.isChecked():
            fieldModel.style = 'xpath'
        if self.radioButton_field_headtail.isChecked():
            fieldModel.style = 'headtail'
        fieldModel.express = self.lineEdit_field_express.text()
        fieldModel.head = self.textEdit_field_head.toPlainText()
        fieldModel.tail = self.textEdit_field_tail.toPlainText()
        fieldModel.headinclude = self.checkBox_field_headinclude.isChecked()
        fieldModel.tailinclude = self.checkBox_field_tailinclude.isChecked()
        fieldModel.datepattern = self.lineEdit_field_datepattern.text()
        self.current_item.setData(fieldModel)

        if self.checkBox_pager_is.isChecked():
            self.pagermodel.express = self.lineEdit_pager_express.text()

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
                if fieldModel.style=='xpath':
                    fieldModel.values = [item.strip() for item in root.xpath(fieldModel.express)]
                elif fieldModel.style=='headtail':
                    heads = re.findall(fieldModel.head, content)
                    if len(heads)!=1:
                        raise Exception('头部解析不合适', heads)
                    tails = re.findall(fieldModel.tail, content)
                    if len(tails)!=1:
                        raise Exception('尾部解析不合适', heads)

                    head_pos = content.find(heads[0])
                    head_pos =  head_pos if fieldModel.headinclude else head_pos+len(heads[0])
                    tail_pos = content.find(tails[0])
                    tail_pos = tail_pos + len(tails[0]) if fieldModel.tailinclude else tail_pos
                    fieldModel.values = [content[head_pos:tail_pos]]
                else:
                    # self.task.log.error('解析类型错误', fieldModel.style)
                    raise Exception('解析类型错误')

                ##################处理字段信息
                resu = []
                for value in fieldModel.values:
                    value = str(value).strip()
                    if fieldModel.datepattern:
                        resu.append(DataUtil.formatDate(value, fieldModel.datepattern))
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

    def on_pager_preview_clicked(self):
        if self.checkBox_pager_is.isChecked():
            root = etree.HTML(self.browser.page().currentFrame().toHtml())

            try:
                model = QStandardItemModel()
                for index,page in enumerate(root.xpath(self.lineEdit_pager_express.text())):
                    model.setItem(index, 0, QStandardItem(page))
                model.setHorizontalHeaderLabels([''])
                self.tableView_alldata.setModel(model)
                self.statusLabel.setText('正确显示数据')
            except Exception as e:
                QMessageBox.about(self, self.tr('提示'), self.tr(str(e)))

    def on_exportTask_clicked(self):
        if self.lineEdit_taskName.text()==None:
            QMessageBox.about(self, self.tr('提示'), self.tr('请输入任务名称'))
            return

        try:
            task = Task(self.lineEdit_taskName.text())
            task.source = self.plainTextEdit_urls.toPlainText().split('\n')
            for i in range(self.itemModel.rowCount()):
                task.fields.append(self.itemModel.item(i, 0).data().__dict__)
            task.pager = self.pagermodel.__dict__
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
    def __init__(self, name, style='xpath', express='', headinclude=True, head='', tailinclude=False, tail='', datepattern=''):
        self.name = name
        self.style = style
        self.express = express
        self.headinclude = headinclude
        self.head = head
        self.tailinclude = tailinclude
        self.tail = tail
        self.datepattern = datepattern
        self.values = []


class PagerModel():
    def __init__(self, express=None):
        self.express = express



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = MainWin()
    ui.show()
    sys.exit(app.exec_())