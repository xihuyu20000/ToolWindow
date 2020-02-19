from PyQt5.QtWidgets import QMessageBox
from bs4 import Tag


def show_dialog(msg):
    QMessageBox.about('提示', msg)

def parse(tag, style='text'):
    '''
    解析xpath表达式
    :param tag:
    :param style:
    :return:
    '''
    if not isinstance(tag, Tag):
        show_dialog('类型不正确')
        return

    tags = []
    def _parse_attrs(tag):
        if tag.attrs:
            for key, value in tag.attrs.items():
                if key in set(['id', 'class', 'style']):
                    exp = '''//{}[@{}='{}']'''.format(tag.name, key, ' '.join(value))
                    return exp
            return '//' + tag.name
        return '//'+tag.name

    def _parse_child(tags, tag):
        if tag:
            flag = True
            for item in tag.children:
                if isinstance(item, Tag):
                    if flag:
                        tags.append(_parse_attrs(item))
                        _parse_child(tags, item)
                        flag = False
    _parse_child(tags, tag)
    if style:
        tags.append('//')
        tags.append(style)
    return ''.join(tags)
