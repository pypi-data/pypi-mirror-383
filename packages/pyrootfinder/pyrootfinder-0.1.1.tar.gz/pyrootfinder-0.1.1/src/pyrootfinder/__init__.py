__version__ = "0.1.1"

from .solvers import (
    bisection,
    secant,
    brentq,
    newton,
    halley,
)

from .result import RootResult
from .exceptions import RootFinderError, ConvergenceError