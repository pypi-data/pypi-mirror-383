from dataclasses import dataclass
from typing import Optional

@dataclass
class RootResult:
    """
    A structured result object for root-finding operations.

    Attributes:
        root (Optional[float]): The found root, or None if not successful.
        iterations (int): The number of iterations performed.
        function_value (Optional[float]): The value of f(root).
        method (str): The name of the algorithm used.
        success (bool): True if the algorithm converged successfully.
        message (str): A human-readable status message.
    """
    root: Optional[float]
    iterations: int
    function_value: Optional[float]
    method: str
    success: bool
    message: str

    def __repr__(self):
        # A clean, appealing representation for printing
        status = "Success" if self.success else "Failed"
        header = f"---- {self.method} Result ({status}) ----"
        
        if self.success:
            body = (
                f"           Root: {self.root:.10f}\n"
                f" Function Value: {self.function_value:e}\n"
                f"     Iterations: {self.iterations}\n"
                f"        Message: {self.message}"
            )
        else:
            body = (
                f"        Message: {self.message}\n"
                f"     Iterations: {self.iterations}"
            )
            
        return f"{header}\n{body}\n" + "-" * len(header)