from device import Device
from app import App
from hstg import HSTG
import time
import uiautomator2
import xml.etree.ElementTree as ET
import random


class Explorer(object):
    def __init__(self, device, app):
        self.device = device
        self.app = app
        self.adb = device.adb
        self.u2 = device.u2
        self.package_name = self.adb.get_current_package()
        # self.minicap = device.minicap
    
    def explore_dfs(self, depth, hstg, service_list=[]):
        if not service_list:
            return
        if not depth:
            hstg.del_event()
            return
        u2 = self.u2
        elements = u2(clickable='true')
        if not elements:
            hstg.del_event()
            return
        # todo elements order filter
        package_name = self.package_name
        for element in elements:
            element.click()
            time.sleep(1)
            hstg.add_event(element)
            audio_status = self.adb.get_audio_status(package_name)
            if audio_status:
                flag = False
                keys = [key for key, value in audio_status.items() if key in service_list and value in ['START', 'START*', 'DUCK']]
                if keys:
                    flag = True
                    service_list = service_list - keys
                # service start
                if flag and True in hstg.add_state():
                    print(f"add state: {hstg.now_state.act_name}, {hstg.now_state.audio_status}")
                    hstg.add_edge()
            self.explore_dfs(depth-1, hstg, service_list)
            hstg.del_event(element)
            # back to bef state
            hstg.back()
        return

    def explore_bfs(self, hstg, service_list=[]):
        # todo 结点入队列
        if not service_list:
            return
        d = self.u2
        elements = d(clickable='true')
        if not elements:
            return
        for element in elements:
            element.click()
            time.sleep(1)
            for service in service_list:
                if self.adb.get_audio_status(self.package_name, service) in ['START', 'START*', 'DUCK']:
                    service_list.remove(service)
                    hstg.add_state(service)
                    print(hstg.states[0].act_name, hstg.states[0].audio_status)
            # todo 回退上一步
        return

    def explore_for_audio(self, hstg, service_list=[]):
        # strategy qqmusic
        # xml_hierarchy = self.u2.dump_hierarchy()
        # with open(f'xml_hierarchy.xml', 'w', encoding='utf-8') as f:
        #     f.write(xml_hierarchy)
        # elements = self.u2.xpath('//node[@clickable="true"]').all()
        services = service_list[:]
        d = self.u2
        elements = d(clickable='true')
        if not elements:
            return
        for element in elements:
            content_desc = element.info.get('contentDescription', '')
            if '播放' in content_desc:
                element.click()
                time.sleep(1)
                for service in services:
                    print(self.adb.get_audio_status(self.package_name))
                    return
                    # todo check start start* duck
                    # if self.adb.get_audio_status(self.package_name, service) in ['START', 'START*', 'DUCK']:
                        # services.remove(service)
                        # hstg.add_state(service)
                        # # todo hstg.add_edge()
                        # print(hstg.states[0].act_name, hstg.states[0].audio_status)
                        # if not services:
                        #     return
                # todo 回退上一步
        return

    def test_explore_for_audio(self, hstg, service_list=[]):
        # xml_hierarchy = self.u2.dump_hierarchy()
        # with open(f'xml_hierarchy.xml', 'w', encoding='utf-8') as f:
        #     f.write(xml_hierarchy)
        pass