from BenchPilotSDK.services.service import Service
from BenchPilotSDK.utils.exceptions import BenchExperimentInvalidException


class Stress(Service):
    """
    This class represents the stress docker service
    Options are the following: cpu, io, vm, vm-bytes, vm-stride, vm-hang, vm-keep, hdd, and hdd-bytes
    """

    def __init__(self, options):
        Service.__init__(self)
        self.hostname = "stress"
        self.assign_image(image_name="benchpilot/stress", same_tag_for_all_arch=True)
        self.command = ""
        self.service_started_log = "Starting"
        self.needs_placement = True
        for i in range(0, len(options)):
            for option_key in options[i]:
                option_value = options[i][option_key]
                suffix = "" if option_value is None or len(option_key) <= 0 else " " + option_value + " "
                self.command += self.__translate_option(option_key) + suffix

    def __translate_option(self, option):
        if "cpu" in option or "-c" == option:
            return "--cpu"
        elif "io" in option or "-i" == option:
            return "--io"
        elif "vm-bytes" in option:
            return "--vm-bytes"
        elif "vm-stride" in option:
            return "--vm-stride"
        elif "vm-hang" in option:
            return "--vm-hang"
        elif "vm-keep" in option:
            return "--vm-keep"
        elif "vm" in option or "-m" == option:
            return "--vm"
        elif "hdd" in option or "-d" == option:
            return "--hdd"
        elif "hdd-bytes" in option:
            return "--hdd-bytes"
        else:
            raise BenchExperimentInvalidException("The command for the service Stress you gave is not supported.")
