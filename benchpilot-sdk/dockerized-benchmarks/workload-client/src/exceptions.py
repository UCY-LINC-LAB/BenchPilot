class UiHostnameAndPortMissingException(Exception):
    """
    Raised when no ui service name and port was declared
    """
    pass

class UiNotFoundException(Exception):
    """
    Raised when no ui service was found
    """
    pass

class EngineMissingException(Exception):
    """
    Raised when the engine wasn't declared in the container's env variables
    """
    pass

class WorkloadMissingException(Exception):
    """
    Raised when the workload wasn't declared in the container's env variables
    """
    pass
