class State(object):
    def __init__(self, act_name, audio_status):
        self.act_name = act_name
        self.audio_status = audio_status

class HSTG(object):
    def __init__(self, device):
        # self.app = app
        self.device = device
        self.states = []
    
    def add_state(self):
        package_name = self.device.adb.get_current_package()
        act_name = self.device.adb.get_current_activity()
        audio_status = self.device.adb.get_audio_status(package_name)
        state = State(act_name, audio_status)
        self.states.append(state)
        return state
