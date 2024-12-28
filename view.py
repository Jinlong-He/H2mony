import re
class View(object):
    def __init__(self, node, type = 'xml'):
        if type == 'xml':
            bound_re = re.compile("\[(\d*),(\d*)\]\[(\d*),(\d*)\]")
            self.clickable = node.attrib['clickable']
            self.description = node.attrib['content-desc']
            self.class_name = node.attrib['class']
            self.text = node.attrib['text']
            bound = node.attrib['bounds']
            m = bound_re.match(bound)
            left, top, right, bottom = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
        if type == 'info':
            self.clickable = node['clickable']
            self.description = node['description']
            self.class_name = node['className']
            self.text = node['text']
            left, right, top, bottom = int(node['left']), int(node['right']), int(node['top']), int(node['bottom'])
        else:
            pass
        self.bound = [left, top, right - left, bottom - top]
        self.img = None
        self.img_hdash = None