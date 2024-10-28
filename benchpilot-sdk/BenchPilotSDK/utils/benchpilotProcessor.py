import subprocess, glob
from re import sub
from BenchPilotSDK.utils.exceptions import MissingBenchExperimentAttributeException, BenchExperimentInvalidException
from BenchPilotSDK.workloads.workload import Workload
from BenchPilotSDK.workloads.materializedWorkloads import *
from BenchPilotSDK.orchestrators.materializedOrchestrators import *

# used to calculate time to sleep for the workload
seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}


def convert_to_seconds(s):
    if (len(s) >= 2) and str.isdigit(s[:-1]) and (
            "s" in (s[-1]) or "m" in (s[-1]) or "d" in (s[-1]) or "h" in (s[-1]) or "w" in (s[-1])):
        return int(s[:-1]) * seconds_per_unit[s[-1]]
    else:
        return -1


def process_check_output(output):
    output = str(output).replace("\\n", "\n").replace("b\'", "").replace("\'", "").split("\n")
    output.remove('')
    return output


def check_required_parameters(main_attribute, required_attributes, definition):
    for att in required_attributes:
        if not att in definition:
            raise MissingBenchExperimentAttributeException(main_attribute + "> " + att)


def kernel_run(command: str, get_output=False, process_output=False):
    if get_output or process_output:
        try:
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            if process_output:
                return process_check_output(output)
            return output
        except subprocess.CalledProcessError as e:
            return ""
    else:
        subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def pipeline_kernel_commands(commands: []):
    return process_commands(prefix="", between_fix=" | ", infix="", suffix="", commands=commands)


def unite_kernel_commands(commands: []):
    return process_commands(prefix="", between_fix=" ", infix="", suffix="", commands=commands)


def get_nth_attribute_kernel_command(n_attributes: [], condition: str = ""):
    if len(condition) > 0:
        condition += " "
    return process_commands(prefix="awk \'" + condition + "{print ", between_fix=",", infix="$", suffix="}\'",
                            commands=n_attributes)


def process_commands(prefix: str, between_fix: str, infix: str, suffix: str, commands: []):
    command = prefix
    for i in range(0, len(commands)):
        if i != 0:
            command += between_fix
        command += infix + commands[i]
    return command + suffix


def define_inner_command_kernel(outer_command: str, inner_command: str):
    return outer_command + " $(" + inner_command + ")"


def process_class_choice(class_name: str, class_type: str, **params):
    if class_type == "orchestrator":
        path = "/BenchPilotSDK/orchestrators/materializedOrchestrators/"
    else:
        path = "/BenchPilotSDK/workloads/materializedWorkloads/"
    _classes = glob.glob(path + "*.py")
    class_list = []
    for _class in range(0, len(_classes)):
        if not '__init__' in _classes[_class]:
            class_item_name = _classes[_class].replace(path, "").replace(".py", "").replace(class_type.capitalize(), "")
            class_item_name = ''.join([class_item_name[0].capitalize(), class_item_name[1:]])
            class_list.append(class_item_name)

    class_name = sub(r"(_|-)+", " ", class_name).title().replace(" ", "")
    class_name = ''.join([class_name[0].capitalize(), class_name[1:]])
    if class_name not in class_list:
        raise BenchExperimentInvalidException("The " + class_type + " you defined is not currently supported")
    return globals()[class_name](**params)
