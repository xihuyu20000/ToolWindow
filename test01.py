# #导入模块
import demjson
import js2py
import requests
import xmltodict
from pyquery import PyQuery

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
{"model":[{"Name":"诺贝尔经济学奖获得者丛书?精品典藏（套...","ID":"72b1e347-9c5b-400d-be29-dddba4aec0fd","Date":"2017-07-05","ISBN":"无","YearMonth":null,"Time":null,"Content":null,"URL":null,"URLTitle":null,"Digest":"本套装包括《身份与暴力》、《微观动机与宏观行为》、《报酬递增的源泉》、《空间经济学》、《默顿米勒论金融衍生工具》共五册经...","Source":null,"ClickRate":0,"imgName":null,"imgType":null,"Title":"诺贝尔经济学奖获得者丛书?精品典藏（套装共5册）","About":{},"ImgUrl":"/fzfm/middle/100082.jpg","VirtualPathtag":"1","FORMAT":null,"Author":"藤田昌久 保罗·R·克鲁格曼等 默顿·米勒 托马斯·C·谢林 阿马蒂亚·森 西奥多·W·舒尔茨","Author_NoSub":"诺贝尔经济学奖获得者丛书?精品典藏（套装共5册）","Course":null,"VideoTime":null,"TotalCharactor":0,"BindingFormat":null,"BookCode":null,"Parent_Doi":null,"ParentName":null,"Price":"0","Count":0,"tag":"","Type":"0","Branch":null,"BookType":0,"Intergration":0,"ISOVERSEASEDITION":null,"BookOrCourseType":null,"PathExt":null,"BookDoi":null,"RecommendType":0,"noselected":null,"noselectedname":null,"jd":null,"Attachment":[]},{"Name":"诺贝尔经济学奖获得者丛书?大师经典（套...","ID":"d90ee1d4-2055-4f78-92ba-f1a8688030d2","Date":"2017-07-05","ISBN":"无","YearMonth":null,"Time":null,"Content":null,"URL":null,"URLTitle":null,"Digest":"无","Source":null,"ClickRate":0,"imgName":null,"imgType":null,"Title":"诺贝尔经济学奖获得者丛书?大师经典（套装共10册）","About":{},"ImgUrl":"/fzfm/middle/100081.jpg","VirtualPathtag":"1","FORMAT":null,"Author":"藤田昌久 保罗·R·克鲁格曼等 默顿·米勒 托马斯·C·谢林、阿马蒂亚·森 西奥多·W·舒尔茨 阿马蒂亚·森 迈克尔·斯彭斯等 路易吉·帕加内托等 约瑟夫·E·斯蒂格利茨等、罗伯特·J·希勒","Author_NoSub":"诺贝尔经济学奖获得者丛书?大师经典（套装共10册）","Course":null,"VideoTime":null,"TotalCharactor":0,"BindingFormat":null,"BookCode":null,"Parent_Doi":null,"ParentName":null,"Price":"0","Count":0,"tag":"","Type":"0","Branch":null,"BookType":0,"Intergration":0,"ISOVERSEASEDITION":null,"BookOrCourseType":null,"PathExt":null,"BookDoi":null,"RecommendType":0,"noselected":null,"noselectedname":null,"jd":null,"Attachment":[]},{"Name":"创意写作书系?走进大师（套装18册全）","ID":"d7a752ff-2032-42f2-a83c-fa0842779f19","Date":"2016-07-28","ISBN":"无","YearMonth":null,"Time":null,"Content":null,"URL":null,"URLTitle":null,"Digest":"本套装包括《成为作家》、《小说写作教程虚构文学速成全攻略》、《写作是什么：给爱写作的你》、《小说创作技能拓展》、《从创意...","Source":null,"ClickRate":0,"imgName":null,"imgType":null,"Title":"创意写作书系?走进大师（套装18册全）","About":{},"ImgUrl":"/fzfm/middle/100055.jpg","VirtualPathtag":"1","FORMAT":null,"Author":"克莉·梅杰斯\t陈鸣 詹姆斯·斯科特·贝尔 杰里·克利弗\t詹姆斯·斯科特·贝尔 杰夫·格尔克\t罗伯·托宾 多萝西娅·布兰德等","Author_NoSub":"创意写作书系?走进大师（套装18册全）","Course":null,"VideoTime":null,"TotalCharactor":0,"BindingFormat":null,"BookCode":null,"Parent_Doi":null,"ParentName":null,"Price":"0","Count":0,"tag":"","Type":"0","Branch":null,"BookType":0,"Intergration":0,"ISOVERSEASEDITION":null,"BookOrCourseType":null,"PathExt":null,"BookDoi":null,"RecommendType":0,"noselected":null,"noselectedname":null,"jd":null,"Attachment":[]},{"Name":"诺贝尔经济学奖获得者丛书?经典必读（套...","ID":"05618065-7d03-4a1f-9308-954857a59571","Date":"2016-07-28","ISBN":"无","YearMonth":null,"Time":null,"Content":null,"URL":null,"URLTitle":null,"Digest":"《城镇化与增长:城市是发展中国家繁荣和发展的发动机吗?》是美国增长与发展委员会邀请来自世界各地的知名学者和政策制定者举办的...","Source":null,"ClickRate":0,"imgName":null,"imgType":null,"Title":"诺贝尔经济学奖获得者丛书?经典必读（套装共5册）","About":{},"ImgUrl":"/fzfm/middle/100056.jpg","VirtualPathtag":"1","FORMAT":null,"Author":"迈克尔·斯彭斯; 帕特里夏·克拉克·安妮兹; 阿马蒂亚·森; 路易吉·帕加内托; 埃德蒙·S·费尔普斯; 约瑟夫·E·斯蒂格利茨等; 罗伯特·J·希勒","Author_NoSub":"诺贝尔经济学奖获得者丛书?经典必读（套装共5册）","Course":null,"VideoTime":null,"TotalCharactor":0,"BindingFormat":null,"BookCode":null,"Parent_Doi":null,"ParentName":null,"Price":"0","Count":0,"tag":"","Type":"0","Branch":null,"BookType":0,"Intergration":0,"ISOVERSEASEDITION":null,"BookOrCourseType":null,"PathExt":null,"BookDoi":null,"RecommendType":0,"noselected":null,"noselectedname":null,"jd":null,"Attachment":[]},{"Name":"创意写作书系?写作技巧（套装共4册）","ID":"cc5693d4-cf3c-4d23-9928-6bfe0e8d5ff1","Date":"2015-05-18","ISBN":"无","YearMonth":null,"Time":null,"Content":null,"URL":null,"URLTitle":null,"Digest":"作家可以培养,写作人人可为。什么人能成为作家？写作需要天才吗？作家是可以教会的吗？文学创作需要什么天赋、才能和技艺？作家的...","Source":null,"ClickRate":0,"imgName":null,"imgType":null,"Title":"创意写作书系?写作技巧（套装共4册）","About":{},"ImgUrl":"/fzfm/middle/100044.jpg","VirtualPathtag":"1","FORMAT":null,"Author":"杰夫·格尔克  拉里·布鲁克斯 等","Author_NoSub":"创意写作书系?写作技巧（套装共4册）","Course":null,"VideoTime":null,"TotalCharactor":0,"BindingFormat":null,"BookCode":null,"Parent_Doi":null,"ParentName":null,"Price":"0","Count":0,"tag":"","Type":"0","Branch":null,"BookType":0,"Intergration":0,"ISOVERSEASEDITION":null,"BookOrCourseType":null,"PathExt":null,"BookDoi":null,"RecommendType":0,"noselected":null,"noselectedname":null,"jd":null,"Attachment":[]},{"Name":"创意写作书系?趣味写作（套装共5册）","ID":"42b13c3a-5e75-4c0a-a6c0-7c3887f8a726","Date":"2015-05-18","ISBN":"无","YearMonth":null,"Time":null,"Content":null,"URL":null,"URLTitle":null,"Digest":"音乐家和画家可能需要天赋才能成功，但作家不是。一个好的故事的发生是无法遏制的，在你反应过来之前它就已经触动了你的心灵。 写...","Source":null,"ClickRate":0,"imgName":null,"imgType":null,"Title":"创意写作书系?趣味写作（套装共5册）","About":{},"ImgUrl":"/fzfm/middle/100045.jpg","VirtualPathtag":"1","FORMAT":null,"Author":"塞琪·科恩  多萝西娅·布兰德 等","Author_NoSub":"创意写作书系?趣味写作（套装共5册）","Course":null,"VideoTime":null,"TotalCharactor":0,"BindingFormat":null,"BookCode":null,"Parent_Doi":null,"ParentName":null,"Price":"0","Count":0,"tag":"","Type":"0","Branch":null,"BookType":0,"Intergration":0,"ISOVERSEASEDITION":null,"BookOrCourseType":null,"PathExt":null,"BookDoi":null,"RecommendType":0,"noselected":null,"noselectedname":null,"jd":null,"Attachment":[]},{"Name":"大宋王朝?沉重的黄袍","ID":"5a5f6b6c-aa78-40ad-a18e-ed8b54f92ea8","Date":"2013-12-01","ISBN":"978-7-5117-1816-7","YearMonth":null,"Time":null,"Content":null,"URL":null,"URLTitle":null,"Digest":"《沉重的黄袍》是长篇历史小说《大宋王朝》的第一部。小说在历史研究的基础上展开丰富的想象，拨开历史的疑云，弥补史书的遗缺，深...","Source":null,"ClickRate":0,"imgName":null,"imgType":null,"Title":"大宋王朝?沉重的黄袍","About":{},"ImgUrl":"/fzfm/middle/100003.jpg","VirtualPathtag":"1","FORMAT":null,"Author":"何辉","Author_NoSub":"大宋王朝?沉重的黄袍","Course":null,"VideoTime":null,"TotalCharactor":0,"BindingFormat":null,"BookCode":null,"Parent_Doi":null,"ParentName":null,"Price":"6","Count":0,"tag":"","Type":"0","Branch":null,"BookType":0,"Intergration":0,"ISOVERSEASEDITION":null,"BookOrCourseType":null,"PathExt":null,"BookDoi":null,"RecommendType":0,"noselected":null,"noselectedname":null,"jd":null,"Attachment":[]},{"Name":"我们真的理解金融危机吗?","ID":"7d56ab3f-1f2f-489c-bf8f-7211c9b096bd","Date":"2008-12-02","ISBN":"978-7-300-09977-4","YearMonth":null,"Time":null,"Content":null,"URL":null,"URLTitle":null,"Digest":"本选题围绕当前发生的金融危机，邀请一些经济学者、金融学家，以及工作在金融一线的金融与经济问题的研究人员，从不同的角度来解读...","Source":null,"ClickRate":0,"imgName":null,"imgType":null,"Title":"我们真的理解金融危机吗?","About":{},"ImgUrl":"/fzfm/small/22454-(WBS)-sl.jpg","VirtualPathtag":"1","FORMAT":null,"Author":"黄卫平等","Author_NoSub":"我们真的理解金融危机吗?","Course":null,"VideoTime":null,"TotalCharactor":0,"BindingFormat":null,"BookCode":null,"Parent_Doi":null,"ParentName":null,"Price":"29.8","Count":0,"tag":"","Type":"0","Branch":null,"BookType":0,"Intergration":0,"ISOVERSEASEDITION":null,"BookOrCourseType":null,"PathExt":null,"BookDoi":null,"RecommendType":0,"noselected":null,"noselectedname":null,"jd":null,"Attachment":[]},{"Name":"没有权威和惩罚的教育?（新哲学学院丛书...","ID":"3f5df774-56c6-47c5-a98d-f81c4bfc8cc3","Date":"2005-07-31","ISBN":"7-300-06556-2","YearMonth":null,"Time":null,"Content":null,"URL":null,"URLTitle":null,"Digest":"本书为法国三位哲学家针对当今社会中令人关注的教育问题展开的哲学对话。三位对话人分别从：什么是教育，教育关系中是否需要权威...","Source":null,"ClickRate":0,"imgName":null,"imgType":null,"Title":"没有权威和惩罚的教育?（新哲学学院丛书）","About":{},"ImgUrl":"/fzfm/bookimg/127311-1.gif","VirtualPathtag":"1","FORMAT":null,"Author":"[[法]阿贝尔·雅卡尔 等","Author_NoSub":"没有权威和惩罚的教育?（新哲学学院丛书）","Course":null,"VideoTime":null,"TotalCharactor":0,"BindingFormat":null,"BookCode":null,"Parent_Doi":null,"ParentName":null,"Price":"12.8","Count":0,"tag":"","Type":"0","Branch":null,"BookType":0,"Intergration":0,"ISOVERSEASEDITION":null,"BookOrCourseType":null,"PathExt":null,"BookDoi":null,"RecommendType":0,"noselected":null,"noselectedname":null,"jd":null,"Attachment":[]},{"Name":"初级中学健康教育[?]","ID":"c719c211-7fa3-4af7-8ac2-f8e65975ca4d","Date":"1996-11-25","ISBN":"无","YearMonth":null,"Time":null,"Content":null,"URL":null,"URLTitle":null,"Digest":"无","Source":null,"ClickRate":0,"imgName":null,"imgType":null,"Title":"初级中学健康教育[?]","About":{},"ImgUrl":"/fzfm/middle/5260.jpg","VirtualPathtag":"1","FORMAT":null,"Author":"无","Author_NoSub":"初级中学健康教育[?]","Course":null,"VideoTime":null,"TotalCharactor":0,"BindingFormat":null,"BookCode":null,"Parent_Doi":null,"ParentName":null,"Price":"6.5","Count":0,"tag":"","Type":"0","Branch":null,"BookType":0,"Intergration":0,"ISOVERSEASEDITION":null,"BookOrCourseType":null,"PathExt":null,"BookDoi":null,"RecommendType":0,"noselected":null,"noselectedname":null,"jd":null,"Attachment":[]}],"type":2,"Success":true,"PageCount":3,"Page":1,"Count":26}
'''
print(demjson.decode(js_json,encoding='utf8' ))



















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
