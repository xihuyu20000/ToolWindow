import time,os,redis


class RedisConfig():
    def __init__(self, password=None, host='127.0.0.1', port=6379):
        self.password = password
        self.host = host
        self.port = port
class ConsoleSink():
    def __init__(self, sep='\t\t'):
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
