class ExecutionError(Exception):
    """Base exception for execution-related errors."""
    pass

class ExecutionFinishedError(ExecutionError):
    """Exception raised when attempting to modify a finalized execution."""
    pass