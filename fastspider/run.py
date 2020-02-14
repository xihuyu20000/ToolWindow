from pyecharts.charts import Bar

from fastspider.spider import *

def a():
    # 网站配置信息
    task = Task('美国国防部最新新闻', baseUrl='https://www.defense.gov/Newsroom/Latest/')
    # 需要抓取的字段信息
    title = Field('标题', style='xpath', express='//div[@class="section section-1"]//a[@class="title"]/text()')
    url = Field('链接', style='xpath', express='//div[@class="section section-1"]//a[@class="title"]/@href')
    pubtime = Field('发布时间', style='xpath', express='//div[@class="section section-1"]//time/@data-dateago', type='date',
                    format='年-月-日T时:分:秒')
    task.fields = [title, url, pubtime]
    task.pager = Pager(style='xpath', express='//div[@class="apager"]//div[position()>1 and position()<last()]/a/@href')
    spider = Spider(task, redisUtil=RedisUtil(RedisConfig()))
    spider.run()


def b():
    # 网站配置信息
    task = Task('美国国防部新闻列表', baseUrl='https://www.defense.gov/Explore/News/Listing/')
    # 需要抓取的字段信息
    title = Field('标题', style='xpath', express='//div[@class="title-wrapper"]//a[@class="title"]//text()')
    url = Field('链接', style='xpath', express='//div[@class="title-wrapper"]//a[@class="title"]/@href')
    pubtime = Field('发布时间', style='xpath', express='//div[@class="bar"]//time/@data-dateago', type='date',
                    format='年-月-日T时:分:秒')
    task.fields = [title, url, pubtime]
    task.pager = Pager(style='xpath', express='//div[@class="apager"]//div[position()>1 and position()<last()]/a/@href')

    spider = Spider(task, redisUtil=RedisUtil(RedisConfig()))
    spider.run()


def c():
    # 网站配置信息
    task = Task('美国国防部一篇新闻', baseUrl=FileSource(dirpath='.', filename='urls.txt'),
                sink=FileSink('.', 'a.txt','\t\t'))
    # 需要抓取的字段信息
    title = Field('标题', style='xpath', express='//h1[@class="maintitle"]//text()')
    author = Field('作者', style='xpath', express='//span[@class="author-block"]//a[@class="article-link"]/text()')
    url = Field('作者主页', style='xpath', express='//span[@class="author-block"]//a[@class="article-link"]/@href')
    content = Field('内容', style='headtail', head='<div class="body">',tail='<div class="social-bottom">')
    task.fields = [title, author, url, content]

    spider = Spider(task, redisUtil=RedisUtil(RedisConfig()))
    spider.run()


def d():
    import execjs
    ret = execjs.compile().call('parse', 'aaaaaa')
    print(ret)


def e():

    bar = Bar()
    bar.add_xaxis(["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"])
    bar.add_yaxis('服务站',  [5, 20, 36, 10, 75, 90])
    bar.render()

e()