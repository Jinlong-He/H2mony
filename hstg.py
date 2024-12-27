state_num = 0


class State(object):
    def __init__(self, act_name, audio_status):
        self.act_name = act_name
        # audio_status: key=service_name value=status
        self.audio_status = audio_status
        global state_num
        self.num = state_num

    def __eq__(self, other):
        if isinstance(other, State):
            return self.act_name == other.act_name and \
                   self.audio_status == other.audio_status and \
                   self.similarity(other)
        return False

    def similarity(self, other):
        return True


class Edge(object):
    def __init__(self, source_state_num, target_state_num, events):
        self.source_state_num = source_state_num
        self.target_state_num = target_state_num
        self.events = events


# todo click event
class Event(object):
    def __init__(self, elem):
        # pos
        # self.elem = elem
        info = elem.info
        if not info:
            assert False
        bounds = info.get('bounds')
        if not bounds:
            assert False
        print(f'bounds={bounds}')
        print(f"className={elem.info.get('className')}")
        top = bounds.get('top')
        bottom = bounds.get('bottom')
        left = bounds.get('left')
        right = bounds.get('right')
        self.posx = int((left+right)/2)
        self.posy = int((top+bottom)/2)


class HSTG(object):
    def __init__(self, device):
        # self.app = app
        self.device = device
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
    def back_state(self, state_num):
        print(f"back to state[{state_num}]")
        self.del_event()
        self.device.u2.press('back')
        check_state = self.states[state_num]
        package_name = self.device.adb.get_current_package()
        act_name = self.device.adb.get_current_activity()
        audio_status = self.device.adb.get_audio_status(package_name)
        state = State(act_name, audio_status)
        if self.visit_states[-1] != state_num:
            self.visit_states.pop()
        if state == check_state:
            return
        self.goto_state()
        return

    # todo
    # 思路 重启应用 visit_states+edges 点击
    def goto_state(self):
        print("restart app")
        print(f"go to state[{self.visit_states[-1]}]")
        pass

    def add_state(self):
        package_name = self.device.adb.get_current_package()
        act_name = self.device.adb.get_current_activity()
        audio_status = self.device.adb.get_audio_status(package_name)
        state = State(act_name, audio_status)
        # todo state isequal
        if state in self.states:
            return (state, False)
        self.states.append(state)
        self.visit_states.append(state.num)
        global state_num
        state_num += 1
        print(f"add state[{state.num}] {state.act_name} {state.audio_status}")
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

    def add_event(self, elem):
        event = Event(elem)
        self.events.append(event)
        print(f"click: ({self.events[-1].posx},{self.events[-1].posy})")
        return

    def del_event(self):
        if len(self.events):
            self.events.pop()
        return
