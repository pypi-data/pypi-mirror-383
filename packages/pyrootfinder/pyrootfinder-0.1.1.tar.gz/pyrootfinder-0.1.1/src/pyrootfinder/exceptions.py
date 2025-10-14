class RootFinderError(Exception):
    """Base exception for the pyrootfinder package."""
    pass

class ConvergenceError(RootFinderError):
    """Raised when a root-finding algorithm fails to converge."""
    pass