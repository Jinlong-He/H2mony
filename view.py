class View(object):
    def __init__(self, info):
        self.clickable = info['clickable']
        self.description = info['description']
        self.class_name = info['className']
        self.text = info['text']
        left, right, top, bottom = int(info['left']), int(info['right']), int(info['top']), int(info['bottom'])
        self.bound = [left, top, right - left, bottom - top]
        self.img = None
        self.img_hdash = None