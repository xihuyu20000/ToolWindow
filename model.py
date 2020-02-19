import time

class Log():
    def info(self, *msg):
        print('【log info】', time.strftime("%Y-%m-%d %H:%M:%S"), msg)
    def error(self, *msg):
        print('【log error】', time.strftime("%Y-%m-%d %H:%M:%S"), msg)

class FieldModel():
    '''
    字段模型
    '''
    def __init__(self, name, style='xpath', express='', code=''):
        self.name = name
        self.style = style
        self.express = express
        self.code = code
        self.values = []

class FileSink():
    '''
    文件输出
    '''
    def __init__(self, filename, sep):
        self.filename = filename
        self.sep = sep

class Task():
    def __init__(self, name, source=None, sinks=[], fields=[], pager=None, deduplication=False):
        self.name = name
        self.source = source
        self.sinks = sinks
        self.fields = fields
        self.pager = pager
        self.deduplication = deduplication
