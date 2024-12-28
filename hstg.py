import time

state_num = 0


class State(object):
    def __init__(self, act_name, audio_status):
        self.act_name = act_name
        # audio_status: key=service_name value=status
        self.audio_status = audio_status
        global state_num
        self.id = state_num

    def __eq__(self, other):
        if isinstance(other, State):
            return self.act_name == other.act_name and \
                   self.audio_status == other.audio_status and \
                   self.similarity(other)
        return False

    def similarity(self, other):
        return True


class Edge(object):
    def __init__(self, source_state_id, target_state_id, events):
        self.source_state_id = source_state_id
        self.target_state_id = target_state_id
        self.events = events


class Event(object):
    def __init__(self, info):
        self.x, self.y = self.get_coord(info)

    def get_coord(self, info):
        bounds = info.get('bounds')
        print(f'bounds={bounds}')
        # print(f"className={info.get('className')}")
        top = bounds.get('top')
        bottom = bounds.get('bottom')
        left = bounds.get('left')
        right = bounds.get('right')
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

    # todo 回退至点击前
    """
        events删除最后一项
        状态退回给定state：执行u2.back操作 visit_states更新
        判断当前state与给定state是否相等
        不相等则重启
        相等则返回
    """
    def back_state(self, state_id):
        print(f"++todo: back to state[{state_id}]")
        self.del_event()
        self.device.u2.press('back')
        check_state = self.states[state_id]
        package_name = self.adb.get_current_package()
        act_name = self.adb.get_current_activity()
        audio_status = self.adb.get_audio_status(package_name)
        state = State(act_name, audio_status)
        if self.visit_states[-1] != state_id:
            self.visit_states.pop()
        if state == check_state:
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
        state = State(act_name, audio_status)
        # todo state isequal
        if state in self.states:
            return (state, False)
        self.states.append(state)
        self.visit_states.append(state.id)
        global state_num
        state_num += 1
        print(f"add state[{state.id}] {state.act_name} {state.audio_status}")
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
            time.sleep(1)
        return
