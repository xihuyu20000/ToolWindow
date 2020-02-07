import time, re, os
import redis
import requests
from selenium import webdriver
from lxml import etree

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


class Task():
    def __init__(self, name, baseUrl, source=None, sink=None, deduplication=False, method='get', rettype='text', headers=None, params=None, log = Log()):
        '''
        :param name: str
        :param baseUrl: str
        :param source: 表示来源
        :param sink: 表示目的地
        :param deduplication: bool, 是否去重，True还是False，默认不去重
        :param method: str，可能是get或post
        :param rettype: str，可能是text或json
        :param headers: dict
        :param params: dict
        '''
        self.name = name
        self.baseUrl = baseUrl
        self.urls = []
        self.source = source
        self.sink = sink if sink else ConsoleSink()
        self.deduplication = deduplication
        self.method = method
        self.rettype = rettype
        self.headers = headers
        self.params = params
        self.fields = []
        self.pager = None
        self.content = ''
        self.titles = []
        self.rows = []
        self.log = Log()

    def __str__(self):
        return 'name={}  baseUrl={}  method={}  rettype={}  headers={}  params={}'.format(self.name, self.baseUrl, self.method, self.rettype, self.headers, self.params)

class Field():
    def __init__(self, name, style='xpath', express=None, head=None, headinclude=True, tail=None, tailinclude=False, type=None, format=None):
        '''
        需要提取的字段
        :param name: 字段名称
        :param style: str，解析类型，默认是xpath、headtail
        :param express: 提取方式，xpath表达式或者css表达式
        :param head: 提取方式，开头部分
        :param headinclude: bool, 是否包含头部， 默认是True
        :param tail: 提取方式，结尾部分
        :param tailinclude: bool, 是否包含尾部，默认是False
        :param type: str，字段的类型，是str、number、date
        :param format: 处理字段
        '''
        self.name = name
        self.style = style
        self.express = express
        self.head = head
        self.headinclude = headinclude
        self.tail = tail
        self.tailinclude = tailinclude
        self.type = type
        self.format = format
        self.result = []

    def __str__(self):
        return ' name={}  style={}  express={}  type={}  format={}  result={}'.format(self.name, self.style, self.express, self.type, self.format, self.result)

class Pager():
    def __init__(self, style='xpath', express=None, type=None, format=None):
        '''
        需要提取的字段
        :param style: str，解析类型，默认是xpath
        :param express: 提取方式，xpath表达式或者css表达式
        :param type: str，字段的类型，是str、number、date
        :param format: 处理字段
        '''
        self.style = style
        self.express = express
        self.type = type
        self.format = format
        self.result = []

class ConsoleSink():
    def __init__(self, sep='\t\t'):
        self.sep = sep

class FileSink():
    def __init__(self, dirpath, filename, sep):
        self.dirpath = dirpath
        self.filename = filename
        self.sep = sep


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

class Sources():
    def __init__(self, task):
        self.task = task

    def run(self):
        if isinstance(self.task.baseUrl, str):
            self.task.urls.append(self.task.baseUrl)
        elif isinstance(self.task.baseUrl, FileSource):
            filename = os.path.join(self.task.baseUrl.dirpath, self.task.baseUrl.filename)
            with open(filename, encoding='utf-8') as f:
                for line in f.readlines():
                    if line and line.strip():
                        cols = line.strip().split(self.task.baseUrl.sep)
                        self.task.urls.append(cols[self.task.baseUrl.index])


class FileSource():
    def __init__(self, dirpath, filename, sep='\t', index=0):
        self.dirpath = dirpath
        self.filename = filename
        self.sep = sep
        self.index = index


class Crawler():
    def __init__(self, task):
        self.task = task

    def _fromRequests(self, url):
        '''
        使用requests
        :return:
        '''
        self.task.log.info('使用requests', self.task.__str__())
        if self.task.method == 'get':
            resp = requests.get(url, headers=self.task.headers, params=self.task.params)
        elif self.task.method == 'post':
            resp = requests.post(url, headers=self.task.headers, data=self.task.params)

        if resp.status_code != 200:
            self.task.log.error('报错了', resp.status_code)
            return

        if self.task.rettype == 'text':
            return resp.text
        elif self.task.rettype == 'json':
            return resp.json()
        else:
            self.task.log.error('返回类型错误', self.task.resp)

    def _fromWebDriver(self, url):
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.setBinary("C:\\Program Files (x86)\\Google\\Chrome\\chrome.exe");
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
        # driverpath = "/path/to/chromedriver"
        # driver = webdriver.Chrome(executable_path=driverpath, chrome_options=chrome_options)
        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.get(url)
        content = driver.page_source
        driver.quit()
        return content

    def run(self, url):
        # self.task.content =  self._fromRequests(url)
        self.task.content = self._fromWebDriver(url)
        self.task.log.info('抓取内容', self.task.content)


class Extractor():
    def __init__(self, task):
        self.task = task

    def run(self):
        root = etree.HTML(self.task.content)
        if self.task.fields:
            #################提取字段信息
            for field in self.task.fields:
                if field.style=='xpath':
                    field.result = [item.strip() for item in root.xpath(field.express)]
                elif field.style=='headtail':
                    heads = re.findall(field.head, self.task.content)
                    if len(heads)!=1:
                        raise Exception('头部解析不合适', heads)
                    tails = re.findall(field.tail, self.task.content)
                    if len(tails)!=1:
                        raise Exception('尾部解析不合适', heads)

                    head_pos = self.task.content.find(heads[0])
                    head_pos =  head_pos if field.headinclude else head_pos+len(heads[0])
                    tail_pos = self.task.content.find(tails[0])
                    tail_pos = tail_pos + len(tails[0]) if field.tailinclude else tail_pos
                    field.result = [self.task.content[head_pos:tail_pos]]
                else:
                    self.task.log.error('解析类型错误', field.style)
                    raise Exception('解析类型错误')
            ##################处理字段信息
            for field in self.task.fields:
                resu = []
                for value in field.result:
                    value = str(value).strip()
                    if field.type=='date':
                        resu.append(DataUtil.formatDate(value, field.format))
                    else:
                        resu.append(value)
                self.task.log.info('解析字段', field.name, field.result)
                field.result = resu

        if self.task.pager:
            #################提取分页结果
            if self.task.pager.style=='xpath':
                self.task.pager.result = root.xpath(self.task.pager.express)
            else:
                self.task.log.error('解析类型错误', self.task.pager.style)
                raise Exception('解析类型错误')
            ###############处理分页结果
            pagervalues = []
            if self.task.pager:
                for value in self.task.pager.result:
                    pagervalues.append(value.strip())
                self.task.pager.result = pagervalues
            self.task.log.info('解析分页', self.task.pager.result)

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

class Spider():
    def __init__(self, task, period=None, redisUtil=None):
        self.task = task
        self.period = period
        self.redisUtil = redisUtil

    def run(self):
        self.source()
        for url in self.task.urls:
            self.crawle(url)
            self.extract()
            self.toRows()
            self.deduplicate()
            self.sink()

    def source(self):
        sources = Sources(self.task)
        sources.run()

    def crawle(self, url):
        '''
        爬取内容
        :return:
        '''
        crawler = Crawler(self.task)
        crawler.run(url)


    def extract(self):
        '''
        抽取信息
        :return:
        '''
        extractor = Extractor(self.task)
        extractor.run()



    def toRows(self):
        lens = set()
        for field in self.task.fields:
            lens.add(len(field.result))
        if len(lens)!=1:
            raise Exception('每个字段解析的数量不相同')
        self.task.rows = []
        self.task.titles = [field.name for field in self.task.fields]
        self.task.log.info('列转行', self.task.titles)
        for i in range(len(self.task.fields[0].result)):
            self.task.rows.append([field.result[i] for field in self.task.fields])
        self.task.log.info('列转行', self.task.rows)

    def deduplicate(self):
        if self.task.deduplication==False:
            return self.task.rows
        rows2 = []
        for row in self.task.rows:
            if self.redisUtil.isDuplicated(self.task.name, hash(str(row)))==False:
                rows2.append(row)
        self.task.rows = rows2

    def sink(self):
        if self.task.sink:
            sink = Sink(self.task)
            sink.run()
        else:
            pass