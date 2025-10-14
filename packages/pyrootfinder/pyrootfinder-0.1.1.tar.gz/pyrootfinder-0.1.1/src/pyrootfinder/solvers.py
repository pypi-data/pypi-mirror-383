from .result import RootResult
from .exceptions import ConvergenceError

# Sentinel object for default parameter values
_sentinel = object()

def bisection(f, a, b, tol=1e-8, max_iter=100):
    """
    Find a root of f(x) = 0 using the Bisection method.
    
    Args:
        f (callable): The function to find the root of.
        a (float): The start of the bracketing interval.
        b (float): The end of the bracketing interval.
        tol (float): The desired tolerance.
        max_iter (int): The maximum number of iterations.
        
    Returns:
        RootResult: An object containing the result.
    """
    method_name = "Bisection"
    fa, fb = f(a), f(b)

    if fa * fb >= 0:
        return RootResult(None, 0, None, method_name, False, "Root not bracketed or multiple roots exist in [a, b].")

    for i in range(1, max_iter + 1):
        c = a + (b - a) / 2  # More stable than (a+b)/2
        fc = f(c)
        
        if abs(b - a) / 2 < tol or fc == 0:
            return RootResult(c, i, fc, method_name, True, "Convergence achieved.")
        
        if fa * fc < 0:
            b, fb = c, fc
        else:
            a, fa = c, fc
            
    return RootResult(None, max_iter, None, method_name, False, "Failed to converge within maximum iterations.")

def secant(f, a, b, tol=1e-8, max_iter=100):
    """
    Find a root of f(x) = 0 using the Secant method.
    
    Args:
        f (callable): The function.
        a, b (float): Two initial guesses. They don't need to bracket the root.
        tol (float): The desired tolerance.
        max_iter (int): Maximum number of iterations.
        
    Returns:
        RootResult: An object containing the result.
    """
    method_name = "Secant"
    fa, fb = f(a), f(b)

    for i in range(1, max_iter + 1):
        if abs(fb - fa) < 1e-15: # Avoid division by zero
            return RootResult(None, i, None, method_name, False, "Derivative approximation is zero; cannot continue.")
        
        c = b - fb * (b - a) / (fb - fa)
        fc = f(c)
        
        if abs(c - b) < tol:
            return RootResult(c, i, fc, method_name, True, "Convergence achieved.")
        
        a, fa = b, fb
        b, fb = c, fc
        
    return RootResult(None, max_iter, None, method_name, False, "Failed to converge within maximum iterations.")

def brentq(f, a, b, tol=1e-8, max_iter=100):
    """
    Find a root of f(x) = 0 using Brent's method.
    
    Combines bisection, secant, and inverse quadratic interpolation. This is
    generally the best choice for bracketing root-finding.
    """
    method_name = "Brent's (Brentq)"
    fa, fb = f(a), f(b)

    if fa * fb >= 0:
        return RootResult(None, 0, None, method_name, False, "Root not bracketed in [a, b].")
    
    if abs(fa) < abs(fb):
        a, b = b, a
        fa, fb = fb, fa
    
    s = b # Contrapoint
    fs = fb
    mflag = True # Bisection flag

    for i in range(1, max_iter + 1):
        # Convergence check
        if abs(b - a) < tol or fb == 0:
            return RootResult(b, i, fb, method_name, True, "Convergence achieved.")

        if abs(fa) > 1e-15 and abs(fb) > 1e-15 and abs(fa) != abs(fs):
            # Inverse Quadratic Interpolation
            s = (a * fb * fs / ((fa - fb) * (fa - fs)) +
                 b * fa * fs / ((fb - fa) * (fb - fs)) +
                 s * fa * fb / ((fs - fa) * (fs - fb)))
        else:
            # Secant method
            s = b - fb * (b - a) / (fb - fa)

        # Check if interpolation step is valid and efficient
        condition1 = (s < (3 * a + b) / 4) or (s > b)
        condition2 = mflag and (abs(s - b) >= abs(b - a) / 2)
        condition3 = not mflag and (abs(s - b) >= abs(a - s) / 2)
        
        if condition1 or condition2 or condition3:
            s = a + (b - a) / 2  # Fallback to Bisection
            mflag = True
        else:
            mflag = False

        fs = f(s)
        a, fa = b, fb
        b, fb = s, fs

        if abs(fa) < abs(fb):
            a, b = b, a
            fa, fb = fb, fa

    return RootResult(None, max_iter, None, method_name, False, "Failed to converge within maximum iterations.")


def newton(f, x0, f_prime, tol=1e-8, max_iter=100):
    """
    Find a root of f(x) = 0 using Newton-Raphson method.
    
    Args:
        f (callable): The function to find the root of.
        x0 (float): Initial guess for the root.
        f_prime (callable): The derivative of the function, f'(x).
        tol (float): The desired tolerance.
        max_iter (int): Maximum number of iterations.
        
    Returns:
        RootResult: An object containing the result.
    """
    method_name = "Newton-Raphson"
    x = x0
    for i in range(1, max_iter + 1):
        fx = f(x)
        fpx = f_prime(x)
        
        if abs(fpx) < 1e-15:
            return RootResult(None, i, fx, method_name, False, "Derivative is zero; cannot continue.")
            
        x_new = x - fx / fpx
        
        if abs(x_new - x) < tol:
            return RootResult(x_new, i, f(x_new), method_name, True, "Convergence achieved.")
        
        x = x_new
        
    return RootResult(None, max_iter, f(x), method_name, False, "Failed to converge within maximum iterations.")

def halley(f, x0, f_prime, f_prime2, tol=1e-8, max_iter=100):
    """
    Find a root of f(x) = 0 using Halley's method.

    Args:
        f (callable): The function.
        x0 (float): Initial guess.
        f_prime (callable): The first derivative, f'(x).
        f_prime2 (callable): The second derivative, f''(x).
        tol (float): The desired tolerance.
        max_iter (int): Maximum number of iterations.

    Returns:
        RootResult: An object containing the result.
    """
    method_name = "Halley's"
    x = x0
    for i in range(1, max_iter + 1):
        fx = f(x)
        fpx = f_prime(x)
        fppx = f_prime2(x)
        
        numerator = 2 * fx * fpx
        denominator = 2 * fpx**2 - fx * fppx
        
        if abs(denominator) < 1e-15:
            return RootResult(None, i, fx, method_name, False, "Denominator is zero; cannot continue.")
            
        x_new = x - numerator / denominator
        
        if abs(x_new - x) < tol:
            return RootResult(x_new, i, f(x_new), method_name, True, "Convergence achieved.")
            
        x = x_new
        
    return RootResult(None, max_iter, f(x), method_name, False, "Failed to converge within maximum iterations.")