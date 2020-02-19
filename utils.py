'''
工具模块
'''
from bs4 import Tag
from bs4 import BeautifulSoup as soup

class Utils:
    @staticmethod
    def build_xpath_express(html, style='text'):
        '''
        生成xpath表达式
        :param bs4_tag:
        :param style:
        :return:
        '''
        bs4_tag = soup(html, 'html5lib').body
        tags = []
        def _parse_attrs(bs4_tag):
            if bs4_tag.attrs:
                for key, value in bs4_tag.attrs.items():
                    if key in set(['id', 'class', 'style']):
                        exp = '''//{}[@{}='{}']'''.format(bs4_tag.name, key, ' '.join(value))
                        return exp
                return '//' + bs4_tag.name
            return '//'+bs4_tag.name

        def _parse_child(tags, bs4_tag):
            if bs4_tag:
                flag = True
                for item in bs4_tag.children:
                    if isinstance(item, Tag):
                        if flag:
                            tags.append(_parse_attrs(item))
                            _parse_child(tags, item)
                            flag = False
        _parse_child(tags, bs4_tag)
        if style:
            tags.append('//')
            tags.append(style)
        return ''.join(tags)

    @staticmethod
    def build_pager_express(html):
        '''
        生成xpath表达式
        :param bs4_tag:
        :param style:
        :return:
        '''
        bs4_tag = soup(html, 'html5lib').body

        tags = []
        # def _parse_text(bs4_tag):
        #     if bs4_tag.attrs:
        #         for key, value in bs4_tag.attrs.items():
        #             if key in set(['id', 'class', 'style']):
        #                 exp = '''//{}[@{}='{}']'''.format(bs4_tag.name, key, ' '.join(value))
        #                 return exp
        #         return '//' + bs4_tag.name
        #     return '//'+bs4_tag.name
        #
        def _parse_child(tag):
            if tag is None:
                return None
            print(tag.next)
            if Utils.isNextPageTag(tag.string):
                return True
            for item in tag.children:
                if isinstance(item, Tag):
                    print(item.text)
                    return _parse_child(item)
        ret = _parse_child(bs4_tag)
        print(ret)

    @staticmethod
    def isNextPageTag(s):
        '''
        是否翻页字符串
        :param s:
        :return:
        '''
        if s is None or s.strip() == '':
            return False
        s = str(s).strip().lower()
        names = ['next', '下一页']
        for name in names:
            if s.find(name)>-1:
                return True
        return False