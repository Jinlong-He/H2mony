class State(object):
    def __init__(self, act_name, audio_status):
        self.act_name = act_name
        # audio_status: key=service_name value=status
        self.audio_status = audio_status


class Edge(object):
    def __init__(self, source_state, target_state, events):
        self.source_state = source_state
        self.target_state = target_state
        self.events = events


class Event(object):
    def __init__(self, elem):
        # pos
        self.elem = elem
        info = elem.get('info')
        if not info:
            assert False
        bound = info.get('bound')
        if not bound:
            assert False
        top = bound.get('top')
        bottom = bound.get('bottom')
        left = bound.get('left')
        right = bound.get('right')
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
        self.now_state = None
        self.bef_state = None
        self.add_state()

    # todo def try_back(self, current_state, pre_state):
    def back(self):
        self.device.u2.back()
        # todo
        self.visit_states.pop()
        check_state = self.visit_states[-1]
        package_name = self.device.adb.get_current_package()
        act_name = self.device.adb.get_current_activity()
        audio_status = self.device.adb.get_audio_status(package_name)
        state = State(act_name, audio_status)
        if state == check_state:
            return
        self.go_state()

    def go_state(self):
        pass

    def add_state(self):
        package_name = self.device.adb.get_current_package()
        act_name = self.device.adb.get_current_activity()
        audio_status = self.device.adb.get_audio_status(package_name)
        state = State(act_name, audio_status)
        if state in self.states:
            # todo bef_state now_state change or no change
            return state, False
        if len(self.states):
            self.bef_state = self.states[-1]
        self.states.append(state)
        self.visit_states.append(state)
        self.now_state = self.states[-1]
        return state, True

    def add_edge(self):
        # source, target, events
        edge = Edge(self.bef_state, self.now_state, self.events)
        self.edges.append(edge)
        self.events = []

    def add_event(self, elem):
        event = Event(elem)
        self.events.append(event)

    def del_event(self):
        if len(self.events):
            self.events.pop()
