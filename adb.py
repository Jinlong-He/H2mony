import subprocess
import re
from loguru import logger
try:
    from shlex import quote  # Python 3
except ImportError:
    from pipes import quote  # Python 2

class ADBException(Exception):
    """
    Exception in ADB connection
    """
    pass

class ADB(object):
    """
    this class describes a connector (ADB or HDC)
    """
    def __init__(self, device=None):
        self.device = device
        self.cmd_prefix = ['adb', "-s", device.serial]
        self.sdk = self.get_sdk()

    def run_cmd(self, extra_args):
        """
        run a command and return the output
        :return: output of command
        @param extra_args: arguments to run in adb or hdc
        """
        if isinstance(extra_args, str):
            extra_args = extra_args.split()
        if not isinstance(extra_args, list):
            msg = "invalid arguments: %s\nshould be str, %s given" % (extra_args, type(extra_args))
            logger.warning(msg)
            raise ADBException(msg)

        args = [] + self.cmd_prefix
        args += extra_args

        logger.debug('command:')
        logger.debug(args)
        r = subprocess.check_output(args).strip()
        if not isinstance(r, str):
            r = r.decode()
        logger.debug('return:')
        logger.debug(r)
        return r

    def shell(self, extra_args):
        """
        run an `adb shell` command
        @param extra_args:
        @return: output of adb shell command
        """
        if isinstance(extra_args, str):
            extra_args = extra_args.split()
        if not isinstance(extra_args, list):
            msg = "invalid arguments: %s\nshould be str, %s given" % (extra_args, type(extra_args))
            logger.warning(msg)
            raise ADBException(msg)

        shell_extra_args = ['shell'] + [ quote(arg) for arg in extra_args ]
        return self.run_cmd(shell_extra_args)

    def shell_grep(self, extra_args, grep_args):
        """
        run an `adb shell` command with `grep` command
        @param extra_args:
        @param grep_args:
        @return: output of adb shell command
        """
        if isinstance(extra_args, str):
            extra_args = extra_args.split()
        if isinstance(grep_args, str):
            grep_args = grep_args.split()
        if not isinstance(extra_args, list) or not isinstance(grep_args, list):
            msg = "invalid arguments: %s\nshould be str, %s given" % (extra_args, type(extra_args))
            logger.warning(msg)
            raise ADBException(msg)

        args = self.cmd_prefix +['shell'] + [ quote(arg) for arg in extra_args ]
        grep_args = ['grep'] + [ quote(arg) for arg in grep_args ]
        
        proc1 = subprocess.Popen(args, stdout=subprocess.PIPE)
        proc2 = subprocess.Popen(grep_args, stdin=proc1.stdout,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        proc1.stdout.close() # Allow proc1 to receive a SIGPIPE if proc2 exits.
        out, err = proc2.communicate()
        if not isinstance(out, str):
            out = out.decode()
        return out

    def check_connectivity(self):
        """
        check if adb is connected
        :return: True for connected
        """
        r = self.run_cmd("get-state")
        return r.startswith("device")
    
    def get_installed_apps(self):
        """
        Get the package names and apk paths of installed apps on the device
        :return: a dict, each key is a package name of an app and each value is the file path to the apk
        """
        app_lines = self.shell("pm list packages -f").splitlines()
        app_line_re = re.compile("package:(?P<apk_path>.+)=(?P<package>[^=]+)")
        package_to_path = {}
        for app_line in app_lines:
            m = app_line_re.match(app_line)
            if m:
                package_to_path[m.group('package')] = m.group('apk_path')
        return package_to_path
    
    def get_uid(self, package_name):
        process_lines = self.shell_grep("ps", package_name).splitlines()
        if len(process_lines) > 0 :
            usr_name = process_lines[0].split()[0]
            uid = str(int(usr_name.split('_a')[1]) + 10000)
            return uid
        else :
            return -1

    def get_pid(self, package_name, service_name):
        process_lines = self.shell_grep("ps", "%s:%s" % (package_name, service_name)).splitlines()
        if len(process_lines) > 0:
            pid = str(process_lines[0].split()[1])
            return pid
        else:
            return -1
    
    def get_audio_status(self, package_name):
        """
        Get the audio status of given app on the device
        :return: a dict, each key is a package name of an app and each value is the file path to the apk
        """
        audio_lines = self.shell_grep("dumpsys audio", "AudioPlaybackConfiguration").splitlines()
        # uid pid
        audio_line_re = re.compile(".*u/pid:(.*)/(.*) .*state:(.*) attr.*")
        audio_status_dict = {}
        started_count = 0
        for audio_line in audio_lines:
            m = audio_line_re.match(audio_line)
            if m:
                uid = m.group(1)
                pid = m.group(2)
                status = m.group(3)
                audio_status_dict[(uid, pid)] = status
                if status == 'started':
                    started_count += 1
        # todo change focus_lines
        # focus_lines = self.shell_grep("dumpsys audio", "source").splitlines()
        # focus_line_re = re.compile(".* pack: (.*) -- client.* gain: (.*) -- flags.* loss: (.*) -- notified.*")
        # focus_dict = {}
        # for focus_line in focus_lines:
        #     m = focus_line_re.match(focus_line)
        #     if m:
        #         focus_dict[m.group(1)] = (m.group(2), m.group(3))
        uid = self.get_uid(package_name)
        pid = self.get_pid(package_name, service_name)
        if (uid, pid) not in audio_status_dict:
            return ''
        if audio_status_dict[(uid, pid)] == 'paused':
            if package_name not in focus_dict:
                return 'PAUSE'
            if focus_dict[package_name][1] == 'LOSS_TRANSIENT':
                return 'PAUSE*'
            else:
                return 'PAUSE'
        if audio_status_dict[(uid, pid)] == 'stopped' or audio_status_dict[(uid, pid)] == 'idle':
            return 'STOP'
        if audio_status_dict[(uid, pid)] == 'started':
            if package_name not in focus_dict:
                if started_count > 1:
                    return 'START*'
                else:
                    return 'START'
            if focus_dict[package_name][1] == 'LOSS_TRANSIENT_CAN_DUCK':
                return 'DUCK'
            else:
                return 'START'
        # audio_line_re = re.compile(".*u/pid:(.*)/.*state:(.*) attr.*")
        # if audio_status_dict[self.get_uid(package_name)] == 'started':
        # return status

    def get_current_package(self):
        focus_lines = self.shell_grep("dumpsys window", "mCurrentFocus").splitlines()
        package_re = re.compile(".*u0 (.*)/.*")
        if len(focus_lines) > 0:
            for focus_line in focus_lines:
                m = package_re.match(focus_line)
                if m:
                    return m.group(1)
        return

    def get_current_activity(self):
        focus_lines = self.shell_grep("dumpsys window", "mCurrentFocus").splitlines()
        package_re = re.compile(".*u0 .*/(.*)}")
        if len(focus_lines) > 0 :
            for focus_line in focus_lines:
                m = package_re.match(focus_line)
                if m:
                    return m.group(1)
        return

    def get_property(self, property_name):
        """
        get the value of property
        @param property_name:
        @return:
        """
        return self.shell(["getprop", property_name])

    def get_sdk(self):
        return self.get_property("ro.build.version.sdk")