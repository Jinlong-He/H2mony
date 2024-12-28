from h2mony import H2mony
from app import App
from explorer import Explorer
from hstg import HSTG
import sys
from view import View
import time

class Window(object):
    def __init__(self, bounds=set(), img=None):
        self.bounds = bounds
        self.img = img

    def similarity(self, other):
        l = self.bounds
        r = other.bounds
        print(f'self_bounds_len: {len(l)}')
        print(f'other_bounds_len: {len(r)}')
        return len(l.intersection(r))/len(l.union(r))


h2mony = H2mony()
if len(h2mony.device_list) > 0:
    device = h2mony.device_list[0]
    app = App(device, '')
    u2 = device.u2
    adb = device.adb
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
    print('aft ok')
    print(f'similarity={window_bef.similarity(window_aft)}')

