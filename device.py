import subprocess
import sys
import os
import time
import uiautomator2
from app import App
from adb import ADB
# from minicap import Minicap
from loguru import logger

DEFAULT_NUM = '1234567890'
DEFAULT_CONTENT = 'Hello world!'


class Device(object):
    """
    this class describes a connected device
    """

    def __init__(self, 
                 device_serial=None, 
                 is_emulator=False):
        """
        initialize a device connection
        :param device_serial: serial number of target device
        :param is_emulator: boolean, type of device, True for emulator, False for real device
        :return:
        """
        if device_serial is None:
            from utils import get_available_devices
            all_devices = get_available_devices()
            if len(all_devices) == 0:
                logger.warning("ERROR: No device connected.")
                sys.exit(-1)
            device_serial = all_devices[0]
        if "emulator" in device_serial and not is_emulator:
            logger.warning("Seems like you are using an emulator. If so, please add is_emulator option.")
        self.serial = device_serial
        self.is_emulator = is_emulator

        self.adb = ADB(device=self)
        self.u2 = uiautomator2.connect(self.serial)
        # self.minicap = Minicap(device=self)
    
    def check_connectivity(self):
        return self.adb.check_connectivity()
    
    def install_app(self, app_path = ''):
        """
        install an app to device
        @param app: instance of App
        @return:
        """
        assert isinstance(app_path, str)
        if not os.path.isfile(app_path) or not app_path.endswith('.apk'):
            logger.error("%s is not a apk file"%(app_path))
            return None
        app = App(self, app_path)
        assert isinstance(app, App)

        package_name = app.get_package_name()
        if package_name not in self.connector.get_installed_apps():
            install_cmd = ["adb", "-s", self.serial, "install", "-r"]
            # if self.grant_perm and self.get_sdk_version() >= 23:
            #     install_cmd.append("-g")
            install_cmd.append(app.app_path)
            install_p = subprocess.Popen(install_cmd, stdout=subprocess.PIPE)
            while self.check_connectivity() and package_name not in self.connector.get_installed_apps():
                print("Please wait while installing the app...")
                time.sleep(2)
            if not self.check_connectivity():
                install_p.terminate()
                return

        dumpsys_p = subprocess.Popen(["adb", "-s", self.serial, "shell",
                                      "dumpsys", "package", package_name], stdout=subprocess.PIPE)
        dumpsys_lines = []
        while True:
            line = dumpsys_p.stdout.readline()
            if not line:
                break
            if not isinstance(line, str):
                line = line.decode()
            dumpsys_lines.append(line)
        if self.output_dir is not None:
            package_info_file_name = "%s/dumpsys_package_%s.txt" % (self.output_dir, app.get_package_name())
            package_info_file = open(package_info_file_name, "w")
            package_info_file.writelines(dumpsys_lines)
            package_info_file.close()
        # app.dumpsys_main_activity = self.__parse_main_activity_from_dumpsys_lines(dumpsys_lines)

        logger.info("App installed: %s" % package_name)
        logger.info("Main activity: %s" % app.get_main_activity())
        return app
    
    def start_app(self, app):
        if isinstance(app, str):
            package_name = app
        elif isinstance(app, App):
            package_name = app.get_package_name()
        else:
            logger.warning("unsupported param " + app + " with type: ", type(app))
            return
        self.u2.app_start(package_name)

    def stop_app(self, app):
        if isinstance(app, str):
            package_name = app
        elif isinstance(app, App):
            package_name = app.get_package_name()
        else:
            logger.warning("unsupported param " + app + " with type: ", type(app))
            return
        self.u2.app_stop(package_name)
    
    def push_file(self, local_file, remote_dir="/sdcard/"):
        """
        push file/directory to target_dir
        :param local_file: path to file/directory in host machine
        :param remote_dir: path to target directory in device
        :return:
        """
        if not os.path.exists(local_file):
            logger.warning("push_file file does not exist: %s" % local_file)
        self.adb.run_cmd(["push", local_file, remote_dir])

    def pull_file(self, remote_file, local_file):
        self.adb.run_cmd(["pull", remote_file, local_file])
