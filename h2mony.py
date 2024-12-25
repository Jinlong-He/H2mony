from device import Device
from app import App
from explorer import Explorer
from hstg import HSTG

class H2mony(object):
    def __init__(self):
        self.device_list = []
        from utils import get_available_devices
        for device_serial in get_available_devices():
            self.device_list.append(Device(device_serial))
    
    def explore_for_hopping(self, device, app_path = ''):
        assert isinstance(device, Device)
        app = App(device, app_path)
        print(app.package_name)
        explorer = Explorer(device, app)
        hstg = HSTG(device)
        return explorer.explore_for_audio(hstg)
    
    def hop(self, source_device, target_device, app):
        return

h2mony = H2mony()    
h2mony.explore_for_hopping(h2mony.device_list[0])