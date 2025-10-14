import pytest
import math
import sys
sys.path.insert(0, 'src')

import pyrootfinder as rf
from pyrootfinder import RootResult


class TestBrentq:
    """Test suite for brentq solver"""
    
    def test_quadratic_function(self):
        """Test brentq with quadratic function: f(x) = x^2 - 4, root x = 2"""
        def f(x):
            return x**2 - 4
        
        result = rf.brentq(f, 0, 3, tol=1e-8)
        
        assert isinstance(result, RootResult)
        assert result.success is True
        assert result.root is not None
        assert abs(result.root - 2.0) < 1e-6
        assert result.iterations > 0
        assert result.iterations < 100  # Should converge quickly
        
    def test_cubic_function(self):
        """Test brentq with cubic function: f(x) = x^3 - x - 2, root x ≈ 1.52138"""
        def f(x):
            return x**3 - x - 2
        
        result = rf.brentq(f, 1, 2, tol=1e-8)
        
        assert isinstance(result, RootResult)
        assert result.success is True
        assert result.root is not None
        assert abs(result.root - 1.52138) < 1e-4
        assert result.iterations > 0
        assert result.iterations < 100
        
    def test_linear_function(self):
        """Test brentq with linear function: f(x) = 5x - 10, root x = 2"""
        def f(x):
            return 5*x - 10
        
        result = rf.brentq(f, 0, 5, tol=1e-8)
        
        assert isinstance(result, RootResult)
        assert result.success is True
        assert result.root is not None
        assert abs(result.root - 2.0) < 1e-6
        assert result.iterations > 0
        
    def test_trigonometric_function(self):
        """Test brentq with trigonometric function: f(x) = sin(x), root x = 0"""
        def f(x):
            return math.sin(x)
        
        result = rf.brentq(f, -0.5, 0.5, tol=1e-8)
        
        assert isinstance(result, RootResult)
        assert result.success is True
        assert result.root is not None
        assert abs(result.root - 0.0) < 1e-6
        assert result.iterations > 0
        
    def test_failure_no_root_bracketed(self):
        """Test brentq failure when no root is bracketed"""
        def f(x):
            return x**2 + 1  # No real roots
        
        result = rf.brentq(f, 0, 1, tol=1e-8)
        
        assert isinstance(result, RootResult)
        assert result.success is False
        assert result.root is None
        assert "not bracketed" in result.message.lower()
        
    def test_failure_same_sign_at_endpoints(self):
        """Test brentq failure when function has same sign at both endpoints"""
        def f(x):
            return x**2 - 4
        
        result = rf.brentq(f, 3, 5, tol=1e-8)  # Both values are positive
        
        assert isinstance(result, RootResult)
        assert result.success is False
        assert result.root is None


class TestBisection:
    """Test suite for bisection solver"""
    
    def test_quadratic_function(self):
        """Test bisection with quadratic function: f(x) = x^2 - 4, root x = 2"""
        def f(x):
            return x**2 - 4
        
        result = rf.bisection(f, 0, 3, tol=1e-8)
        
        assert isinstance(result, RootResult)
        assert result.success is True
        assert result.root is not None
        assert abs(result.root - 2.0) < 1e-6
        assert result.iterations > 0
        assert result.iterations < 100
        
    def test_cubic_function(self):
        """Test bisection with cubic function: f(x) = x^3 - x - 2, root x ≈ 1.52138"""
        def f(x):
            return x**3 - x - 2
        
        result = rf.bisection(f, 1, 2, tol=1e-8)
        
        assert isinstance(result, RootResult)
        assert result.success is True
        assert result.root is not None
        assert abs(result.root - 1.52138) < 1e-4
        assert result.iterations > 0
        assert result.iterations < 100
        
    def test_linear_function(self):
        """Test bisection with linear function: f(x) = 5x - 10, root x = 2"""
        def f(x):
            return 5*x - 10
        
        result = rf.bisection(f, 0, 5, tol=1e-8)
        
        assert isinstance(result, RootResult)
        assert result.success is True
        assert result.root is not None
        assert abs(result.root - 2.0) < 1e-6
        assert result.iterations > 0
        
    def test_trigonometric_function(self):
        """Test bisection with trigonometric function: f(x) = sin(x), root x = 0"""
        def f(x):
            return math.sin(x)
        
        result = rf.bisection(f, -0.5, 0.5, tol=1e-8)
        
        assert isinstance(result, RootResult)
        assert result.success is True
        assert result.root is not None
        assert abs(result.root - 0.0) < 1e-6
        assert result.iterations > 0
        
    def test_failure_no_root_bracketed(self):
        """Test bisection failure when no root is bracketed"""
        def f(x):
            return x**2 + 1  # No real roots
        
        result = rf.bisection(f, 0, 1, tol=1e-8)
        
        assert isinstance(result, RootResult)
        assert result.success is False
        assert result.root is None
        assert "not bracketed" in result.message.lower() or "multiple roots" in result.message.lower()
        
    def test_failure_same_sign_at_endpoints(self):
        """Test bisection failure when function has same sign at both endpoints"""
        def f(x):
            return x**2 - 4
        
        result = rf.bisection(f, 3, 5, tol=1e-8)  # Both values are positive
        
        assert isinstance(result, RootResult)
        assert result.success is False
        assert result.root is None
