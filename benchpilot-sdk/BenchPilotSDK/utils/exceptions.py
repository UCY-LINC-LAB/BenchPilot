class BenchExperimentInvalidException(Exception):
    """
    Raised when bench-experiments.yaml does not have valid format
    """
    pass


class MissingBenchExperimentAttributeException(Exception):
    """
    Raised when an attribute is missing in the benchpilot configuration yaml files
    """

    def __init__(self, attribute):
        self.attribute = attribute


class InvalidSshKeyPath(Exception):
    """
    Raised when an invalid ssh key path was given in BenchPilot-cluster.yaml
    """

    def __init__(self, node):
        self.node = node


class BenchClusterInvalidException(Exception):
    """
    Raised when bench-cluster-setup.yaml does not have valid format
    """
    pass


class UnsupportedOrchestratorException(Exception):
    """
    Raised when the user chose an unsupported orchestrator for their workload
    """
    pass


class UnsupportedWorkloadException(Exception):
    """
    Raised when the user chose an unsupported workload for their experiment
    """
    pass

class UnsupportedImageArchitectureException(Exception):
    """
    Raised when the user chose to place a service on a node that its architecture is not supported for that docker image.
    """
    pass

class WorkloadDeployTimeOut(Exception):
    """
    Raised when something went wrong with the workload deployment
    """
    pass

class InvalidWorkloadName(Exception):
    """
    Raised when an invalid workload name has been given
    """
    pass

class UnloadedBenchmarkMetrics(Exception):
    """
    Raised when the user did not execute the "loacBenchmarkMetrics" method first
    """
    pass

class DockerNotInstalled(Exception):
    """
    Raised when docker was not installed successfully
    """
    pass

class PostExperimentMetricNotDefined(Exception):
    """
    Raised when trying to retrieve a metric from post experiment analysis which is not yet defined
    """
    pass