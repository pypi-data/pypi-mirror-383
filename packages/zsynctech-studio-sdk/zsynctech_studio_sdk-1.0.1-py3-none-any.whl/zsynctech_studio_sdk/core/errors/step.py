class StepError(Exception):
    """Base exception for Step-related errors."""
    pass

class StepFinalizedError(StepError):
    """Exception raised when attempting to modify a finalized step."""
    pass