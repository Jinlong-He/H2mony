from h2mony import H2mony
from app import App
from explorer import Explorer
from hstg import HSTG
import sys
from view import View
import time
import cv

class Window(object):
    def __init__(self, bounds=set(), img=None):
        self.bounds = bounds
        self.img = img
        self.img_dhash = ''

    def boudns_similarity(self, other):
        l = self.bounds
        r = other.bounds
        print(f'self_bounds_len: {len(l)}')
        print(f'other_bounds_len: {len(r)}')
        return len(l.intersection(r))/len(l.union(r))

    def img_distance(self, other):
        if self.img_dhash == '':
            self.img_dhash = cv.calculate_dhash(self.img)
        if other.img_dhash == '':
            other.img_dhash = cv.calculate_dhash(self.img)
        return cv.dhash_hamming_distance(self.img_dhash, other.img_dhash)


h2mony = H2mony()
if len(h2mony.device_list) > 0:
    device = h2mony.device_list[0]
    app = App(device, '')
    u2 = device.u2
    adb = device.adb
    minicap = device.minicap
    elements = u2(clickable='true')
    elements_info = [element.info for element in elements]
    bounds_set = set()
    for element_info in elements_info:
        # print(element_info)
        view = View(element_info, 'info')
        # print(view.bound)
        bounds = tuple(view.bound)
        # print(bounds)
        bounds_set.add(bounds)
    # print(bounds_set)
    window_bef = Window(bounds_set)
    window_bef.img = cv.load_image_from_buf(minicap.last_screen)
    print('bef ok')
    print('sleep begin')
    time.sleep(10)
    print('sleep end')

    elements = u2(clickable='true')
    elements_info = [element.info for element in elements]
    bounds_set = set()
    for element_info in elements_info:
        # print(element_info)
        view = View(element_info, 'info')
        # print(view.bound)
        bounds = tuple(view.bound)
        # print(bounds)
        bounds_set.add(bounds)
    # print(bounds_set)
    window_aft = Window(bounds_set)
    window_aft.img = cv.load_image_from_buf(minicap.last_screen)
    print('aft ok')
    print(f'similarity={window_bef.boudns_similarity(window_aft)}')
    print(f'distance={window_bef.img_distance(window_aft)}')

