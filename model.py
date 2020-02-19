'''
模型类
'''
import time

class Log():
    '''
    日志信息
    '''
    @staticmethod
    def info(*msg):
        '''
        信息
        :param msg:
        :return:
        '''
        print('【log info】', time.strftime("%Y-%m-%d %H:%M:%S"), msg)

    @staticmethod
    def error(*msg):
        '''
        错误
        :param msg:
        :return:
        '''
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
    '''
    任务模型
    '''
    def __init__(self, name, source=None, sinks=None, fields=None, pager=None, allow_duplica=False):
        self.name = name
        self.source = source
        self.sinks = [] if sinks is None else sinks
        self.fields = [] if fields is None else fields
        self.pager = pager
        self.allow_duplica = allow_duplica
