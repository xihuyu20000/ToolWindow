# #导入模块
# import demjson
# import js2py
# import requests
# import xmltodict
# from pyquery import PyQuery

from bs4 import BeautifulSoup, Tag

info = '''
<div class="download jj0">本书是当代散文家梁衡先生文集名作《觅渡》的修订版。《觅渡》自2004年出版以来深受读者欢迎，至今已重印26次，社会反响长盛不衰...                                </div>
'''
soup = BeautifulSoup(info,'html5lib')

# for item in soup.body.children:
#     if isinstance(item, Tag):
#         print(item)
#         print(item.name, item.attrs)
#         print([item for item in item.children])
# root = [item for item in soup.body.children if item and str(item).strip()][0]
# def parse(tag, style='text'):
#     tags = []
#     def _parseAttrs(tag):
#         if tag.attrs:
#             for key, value in tag.attrs.items():
#                 if key == 'class':
#                     exp = '''//{}[@{}='{}']'''.format(tag.name, key, ' '.join(value))
#                     return exp
#             return '//' + tag.name
#         else:
#             return '//'+tag.name
#     def _parseChild(tags, tag):
#         if tag:
#             flag = True
#             for item in tag.children:
#                 if isinstance(item, Tag):
#                     if flag:
#                         tags.append(_parseAttrs(item))
#                         _parseChild(tags, item)
#                         flag=False
#     _parseChild(tags, tag)
#     tags.append('//')
#     tags.append(style)
#     return ''.join(tags)
# print(parse(soup.body, style='text()'))



js_json = '''{"model":[{"Name":"诺贝尔经济学奖获得者丛书?精品典藏（套...","ID":"72b1e347-9c5b-400d-be29-dddba4aec0fd","Date":"2017-07-05","ISBN":"无"
,"YearMonth":null,"Time":null,"Content":null,"URL":null,"URLTitle":null
,"Digest":"本套装包括《身份与暴力》、《微观动机与宏观行为》、《报酬递增的源泉》、《空间经济学》、《默顿米勒论金融衍生工具》共五册经..."
,"Source":null
,"ClickRate":0,"imgName":null,"imgType":null,"Title":"诺贝尔经济学奖获得者丛书?精品典藏（套装共5册）"
,"About":{},"ImgUrl":"/fzfm/middle/100082.jpg","VirtualPathtag":"1","FORMAT":null
,"Author":"藤田昌久 保罗·R·克鲁格曼等 默顿·米勒 托马斯·C·谢林 阿马蒂亚·森 西奥多·W·舒尔茨"
,"Author_NoSub":"诺贝尔经济学奖获得者丛书?精品典藏（套装共5册）"
,"Course":null,"VideoTime":null,"TotalCharactor":0,"BindingFormat":null
,"BookCode":null,"Parent_Doi":null,"ParentName":null,"Price":"0","Count":0,"tag":""
,"Type":"0","Branch":null,"BookType":0,"Intergration":0,"ISOVERSEASEDITION":null
,"BookOrCourseType":null,"PathExt":null,"BookDoi":null,"RecommendType":0
,"noselected":null,"noselectedname":null,"jd":null
,"Attachment":[]
}]}'''
js_json = '''
'''
# print(demjson.decode(js_json,encoding='utf8' ))








#
# url1 = 'https://www.cnblogs.com/zhai1997/p/12300652.html'
# url2 = 'http://www.crup.com.cn/News/BindList'
# url3 = 'http://www.crup.com.cn/Book/BindCourseList'
# #requests.get(网页地址)   作用是抓取网页内容，抓到的内容保存到response
# params = {
#     'Cookie': 'Hm_lvt_27ad556c2ff2cdcaf4f5255518c49365=1580284918,1580382966,1580838701,1581511176; Hm_lpvt_27ad556c2ff2cdcaf4f5255518c49365=1581511482',
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}
# #resp = requests.get(url1, params=params)
# resp = requests.post(url3, data=params, json={'Keywords': '978-7-300-25432-6'})
#
# if resp.status_code==200:
#     #通过使用response.text拿到的就是我们看到的页面内容
#     print(resp.text)
#     #通过json()获取json格式的内容
#     # for item in resp.json()['model']:
#     #     print(item['Name'])

import asyncio
from pyppeteer import launch
async def main():
    browser = await launch()
    page = await browser.newPage()
    await page.goto('http://www.ruanyifeng.com')
    await page.screenshot({'path':'aaa.png'})
    await browser.close()
asyncio.run(main())