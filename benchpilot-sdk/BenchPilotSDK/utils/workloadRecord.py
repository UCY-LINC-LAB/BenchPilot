import datetime


class WorkloadRecord(object):
    """
    This class holds for each workload its start times, end times and configurations.
    The timestamp that its stored is in the same format that Prometheus Pandas receives.
    """
    startTime: []
    endTime: []
    workload_conf: {}

    def __init__(self, workload_conf=None):
        if workload_conf is None:
            workload_conf = {}
        self.workload_conf = workload_conf
        self.startTime = []
        self.endTime = []

    def workload_started(self):
        self.startTime.append(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"))

    def workload_finished(self):
        self.endTime.append(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"))

    def get_starting_ending_timestamps(self):
        starting_ending_timestamps = []
        i = 0
        for trial in range(0, len(self.endTime)):
            trial_record = {
                'trial_id': i,
                'starting_timestamp': self.startTime[i],
                'ending_timestamp': self.endTime[i]
            }
            i += 1
            starting_ending_timestamps.append(trial_record)
        return {'workload_record': starting_ending_timestamps, 'workload_conf': self.workload_conf}

    def print_configs(self):
        print(self.workload_conf)
