import time
import xml.etree.ElementTree as ET
from lxml import etree
import difflib
from view import View
from window import Window
import cv

state_num = 0


class State(object):
    def __init__(self, act_name, audio_status, views, root):
        self.act_name = act_name
        self.audio_status = audio_status
        global state_num
        self.id = state_num
        self.views = views
        self.root = root

    def isequal(self, other):
        if isinstance(other, State):
            return self.act_name == other.act_name and \
                   self.audio_status == other.audio_status and \
                   self.similarity(other)
        return False

    def similarity(self, other):
        if isinstance(other, State):
            # xml str
            # str_self = ET.tostring(self.root, encoding='utf-8').decode('utf-8')
            # str_other = ET.tostring(other.root, encoding='utf-8').decode('utf-8')
            # similarity = difflib.SequenceMatcher(None, str_self, str_other).ratio()

            # node bound
            self_bounds_list = [node.attrib['bound'] for node in self.root.iter('node')]
            self_bounds_list_len = len(self_bounds_list)
            print(f'self_bounds_list_len={self_bounds_list_len}')
            other_bounds_list = [node.attrib['bound'] for node in other.root.iter('node')]
            other_bounds_list_len = len(other_bounds_list)
            print(f'other_bounds_list_len={other_bounds_list_len}')
            same_bounds = 0
            for self_bounds in self_bounds_list:
                if self_bounds in other_bounds_list:
                    same_bounds += 1
            print(f'same_bounds={same_bounds}')
            similarity = same_bounds*2/(self_bounds_list_len+other_bounds_list_len)

            # class
            # self_class_list = [node.attrib['class'] for node in self.root.iter('node')]
            # self_class_list_len = len(self_class_list)
            # print(f'self_class_list_len={self_class_list_len}')
            # other_class_list = [node.attrib['class'] for node in other.root.iter('node')]
            # other_class_list_len = len(other_class_list)
            # print(f'other_class_list_len={other_class_list_len}')
            # self_class_dict = {}
            # other_class_dict = {}
            # for self_class in self_class_list:
            #     self_class_dict[self_class] = self_class_dict.get(self_class, 0) + 1
            # for other_class in other_class_list:
            #     other_class_dict[other_class] = other_class_dict.get(other_class, 0) + 1
            # same_class_count = 0
            # for key, value in self_class_dict.items():
            #     same_class_count += min(other_class_dict.get(key, 0), value)
            # print(f'same_class_count={same_class_count}')
            # similarity = same_class_count*2/(self_class_list_len+other_class_list_len)
            print(f'similarity={round(similarity, 2)} '
                  f'state[{self.id}] <-> state[{other.id}]')
            if similarity > 0.9:
                return True
        return False


class Edge(object):
    def __init__(self, source_state_id, target_state_id, events):
        self.source_state_id = source_state_id
        self.target_state_id = target_state_id
        self.events = events


class Event(object):
    def __init__(self, info):
        self.x, self.y = self.get_coord(info)

    def get_coord(self, info):
        # bounds = info.get('bounds')
        # print(f'bounds={bounds}')
        # # print(f"className={info.get('className')}")
        # top = bounds.get('top')
        # bottom = bounds.get('bottom')
        # left = bounds.get('left')
        # right = bounds.get('right')
        # x = int((left + right) / 2)
        # y = int((top + bottom) / 2)
        # return x, y
        left = info[0]
        top = info[1]
        right = info[2]+left
        bottom = info[3]+top
        x = int((left + right) / 2)
        y = int((top + bottom) / 2)
        return x, y


class ClickEvent(Event):
    def __init__(self, info):
        super().__init__(info)


class HSTG(object):
    def __init__(self, device):
        # self.app = app
        self.device = device
        self.u2 = device.u2
        self.adb = device.adb
        self.states = []
        self.edges = []
        self.events = []
        self.visit_states = []
        self.add_state()

    def back_state(self, state_id):
        print(f"++todo: back to state[{state_id}]")
        self.del_event()
        if self.visit_states[-1] != state_id:
            self.visit_states.pop()

        check_state = self.states[state_id]
        package_name = self.adb.get_current_package()
        act_name = self.adb.get_current_activity()
        audio_status = self.adb.get_audio_status(package_name)
        (views, root) = self.dump_views()
        state = State(act_name, audio_status, views, root)

        if state.isequal(check_state):
            print(f"--done: back to state[{state_id}]")
            return
        else:
            self.device.u2.press('back')
            time.sleep(2)
            check_state = self.states[state_id]
            package_name = self.adb.get_current_package()
            act_name = self.adb.get_current_activity()
            audio_status = self.adb.get_audio_status(package_name)
            (views, root) = self.dump_views()
            state = State(act_name, audio_status, views, root)
            if state.isequal(check_state):
                print(f"--done: back to state[{state_id}]")
                return

        self.goto_state()
        return

    def goto_state(self):
        package_name = self.adb.get_current_package()
        print("--stop app")
        self.u2.app_stop(package_name)
        time.sleep(1)
        print("--restart app")
        self.u2.app_start(package_name)
        # todo 开屏广告
        # while True:
        #     time.sleep(5)
        #     package_name = self.adb.get_current_package()
        #     act_name = self.adb.get_current_activity()
        #     audio_status = self.adb.get_audio_status(package_name)
        #     state = State(act_name, audio_status)
        #     if state == self.states[0]:
        #         break
        time.sleep(10)
        print("--at state[0]")
        if len(self.visit_states) == 1:
            print("--done: back to state[0]")
            return
        state_pairs = zip(self.visit_states[::], self.visit_states[1::])
        for state_pair in state_pairs:
            # print(f'state_pair={state_pair}')
            events = [edge.events for edge in self.edges
                      if edge.source_state_id == state_pair[0]
                      and edge.target_state_id == state_pair[1]]
            if events:
                for event in events[0]:
                    self.handle_event(event)
        print(f"--done: back to state[{self.visit_states[-1]}]")
        return

    def add_state(self):
        package_name = self.device.adb.get_current_package()
        act_name = self.device.adb.get_current_activity()
        audio_status = self.device.adb.get_audio_status(package_name)
        (views, root) = self.dump_views()
        state = State(act_name, audio_status, views, root)
        for s in self.states:
            if state.isequal(s):
                return (state, False)
        self.states.append(state)
        self.visit_states.append(state.id)
        global state_num
        state_num += 1
        print(f"add state[{state.id}] {state.act_name} {state.audio_status}")
        self.u2.screenshot(f'screenshot/state/state_{state.id}.png')
        return (state, True)

    def add_edge(self):
        # source, target, events
        source = self.visit_states[-2]
        target = self.visit_states[-1]
        # todo to check self.events
        edge = Edge(source, target, self.events)
        self.edges.append(edge)
        self.events = []
        print(f"add edge[{source}]->[{target}]")
        return

    def add_event(self, elem_info, event_type=1):
        # event_type:1 ClickEvent
        if event_type == 1:
            event = ClickEvent(elem_info)
            self.events.append(event)
        return

    def del_event(self):
        if len(self.events):
            self.events.pop()
        return

    def handle_event(self, event):
        if isinstance(event, ClickEvent):
            self.device.u2.click(event.x, event.y)
            print(f"click: ({event.x},{event.y})")
        time.sleep(2)
        return

    def dump_views(self):
        window = Window()
        window.img = cv.load_image_from_buf(self.device.minicap.last_sreen)
        window.img_dhash = cv.calculate_dhash(window.img)
        ui_xml = self.u2.dump_hierarchy()
        root = ET.fromstring(ui_xml.encode("utf-8"))
        views = []
        for node in root.iter('node'):
            view = View(node, 'xml')
            views.append(view)
            # node.attrib = {'bounds': node.attrib['bounds'], 'class': node.attrib['class']}
            node.attrib = {'bound': view.bound}
        return (views, root)
