from device import Device
from app import App
from hstg import HSTG
import time
import uiautomator2
import xml.etree.ElementTree as ET

class Explorer(object):
    def __init__(self, device, app):
        self.device = device
        self.app = app
        self.adb = device.adb
        self.u2 = device.u2
        # self.minicap = device.minicap
    
    def explore_dfs(self, depth):
        return

    
    def explore_for_audio(self, hstg):
        # hstg.add_state()
        # print(hstg.states[0].act_name, hstg.states[0].audio_status)

        # self.minicap.set_up()

        #strategy 1 网易云
        # view = self.u2(clickable='true', content='播放暂停')
        # if view.exists:
        #check view existence
            # view.click()
            # time.sleep(1)
            # if self.adb.get_audio_status() == 'start' :
            #     return view.info
        return
