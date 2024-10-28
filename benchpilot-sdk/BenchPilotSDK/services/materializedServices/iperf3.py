from BenchPilotSDK.services.service import Service
from BenchPilotSDK.utils.exceptions import BenchExperimentInvalidException


class IPerf3(Service):
    """
    This class represents the iperf3 docker service
    You can always change / add its supporting options
    """

    def __init__(self, options):
        Service.__init__(self)
        self.hostname = "iperf3"
        self.assign_image(image_name="benchpilot/iperf3", same_tag_for_all_arch=True)
        self.needs_placement = True
        self.service_started_log = "Starting"
        for i in range(0, len(options)):
            for option_key in options[i]:
                option_value = options[i][option_key]
                translated_command = self.__translate_option(option_key)
                if translated_command == "--server":
                    self.needs_placement = False
                if i > 0:
                    self.command += " "
                self.command += translated_command + ("" if (option_value is None or len(option_value) <= 0) else " " + option_value)

    def assign_duration(self, duration):
        if not "--server" in self.command:
            if len(self.command) > 0:
                self.command += " "
            self.command += "-t " + duration

    @staticmethod
    def __translate_option(option):
        if "server" in option or "-s" == option:
            return "--server"
        if "client" in option or "-c" == option:
            return "--client"
        elif "port" in option or "-p" == option:
            return "--port"
        elif "format" in option or "-f" == option:
            return "--format"
        elif "interval" in option or "-i" == option:
            return "--interval"
        elif "affinity" in option or "-p" == option:
            return "--affinity"
        elif "file name" in option or "-F" == option:
            return "-F"
        elif "bind" in option or "-B" == option:
            return "--bind"
        elif "json" in option or "-J" == option:
            return "--json"
        elif "daemon" in option or "-D" == option:
            return "--daemon"
        elif "upd" in option or "-u" == option:
            return "--udp"
        elif "connect-timeout" in option:
            return "--connect-timeout"
        elif "fq-rate" in option:
            return "--fq-rate"
        elif "bytes" in option or "-n" == option:
            return "--bytes"
        elif "blockcount" in option or "-k" == option:
            return "--blockcount"
        elif "length" in option or "-l" == option:
            return "--length"
        elif "4" in option:
            return "--version4"
        elif "6" in option:
            return "--version6"
        elif "zerocopy" in option or "-Z" == option:
            return "--zerocopy"
        else:
            raise BenchExperimentInvalidException("The command for the service IPerf3 you gave is not supported.")
