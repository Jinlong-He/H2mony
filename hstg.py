import time
import xml.etree.ElementTree as ET
from view import View
from window import Window
import cv

state_num = 0


class State(object):
    def __init__(self, act_name, audio_status, views, window):
        self.act_name = act_name
        self.audio_status = audio_status
        global state_num
        self.id = state_num
        self.views = views
        self.window = window

    def isequal(self, other):
        if isinstance(other, State):
            return self.act_name == other.act_name and \
                   self.audio_status == other.audio_status and \
                   self.similarity(other)
        return False

    def similarity(self, other):
        if isinstance(other, State):
            bounds_sim = self.window.bounds_similarity(other.window)
            img_sim = self.window.img_similarity(other.window)
            print(f'state[{self.id}]<->state[{other.id}] '
                  f'bounds_sim={round(bounds_sim,2)} img_sim={round(img_sim,2)}')
            if img_sim > 0.99 or bounds_sim > 0.99:
                return True
            if img_sim > 0.9 and bounds_sim > 0.7:
                return True
            if bounds_sim > 0.9 and img_sim > 0.7:
                return True
            return False
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
        (views, window) = self.dump_views()
        state = State(act_name, audio_status, views, window)

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
            (views, window) = self.dump_views()
            state = State(act_name, audio_status, views, window)
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
        (views, window) = self.dump_views()
        state = State(act_name, audio_status, views, window)
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
        elements = self.u2(clickable='true')
        elements_info = [element.info for element in elements]

        bounds_set = set()
        views = []
        for element_info in elements_info:
            view = View(element_info, 'info')
            views.append(view)
            bounds = tuple(view.bound)
            bounds_set.add(bounds)

        window = Window(bounds_set)
        window.img = cv.load_image_from_buf(self.device.minicap.last_screen)
        window.img_dhash = cv.calculate_dhash(window.img)
        return views, window
