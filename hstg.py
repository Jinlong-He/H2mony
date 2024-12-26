class State(object):
    def __init__(self, act_name, service_name, audio_status):
        self.act_name = act_name
        self.service_name = service_name
        self.audio_status = audio_status
        # todo key=service_name value=status


class HSTG(object):
    def __init__(self, device):
        # self.app = app
        self.device = device
        self.states = []
        # todo s0

    # todo def try_back(self, current_state, pre_state):
    # todo fail restart

    def add_state(self, service_name):
        package_name = self.device.adb.get_current_package()
        act_name = self.device.adb.get_current_activity()
        audio_status = self.device.adb.get_audio_status(package_name, service_name)
        state = State(act_name, service_name, audio_status)
        # todo state isequal
        # todo return (state flag)
        self.states.append(state)
        return state

    def add_edge(self, source, target, events):
        pass
