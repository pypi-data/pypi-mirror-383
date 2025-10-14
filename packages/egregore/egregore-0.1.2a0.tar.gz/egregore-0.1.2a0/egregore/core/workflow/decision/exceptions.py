"""
Decision Pattern Matching Exceptions

Custom exceptions for the enhanced decision pattern matching system.
"""

from typing import Any, Optional


class PatternMatchingError(Exception):
    """Base exception for pattern matching errors"""
    
    def __init__(self, message: str, pattern: Any = None, input_value: Any = None):
        super().__init__(message)
        self.pattern = pattern
        self.input_value = input_value
        self.message = message
    
    def __str__(self) -> str:
        if self.pattern is not None and self.input_value is not None:
            return f"{self.message} (pattern: {self.pattern}, input: {self.input_value})"
        return self.message


class MaxIterationsExceededError(PatternMatchingError):
    """Raised when decision exceeds max_iter without finding a default pattern"""
    
    def __init__(self, max_iter: int, iterations: int, decision_name: str = "Decision"):
        message = f"{decision_name} exceeded max_iter={max_iter} after {iterations} iterations with no default pattern"
        super().__init__(message)
        self.max_iter = max_iter
        self.iterations = iterations
        self.decision_name = decision_name


class InvalidPatternError(PatternMatchingError):
    """Raised when a pattern is malformed or invalid"""
    
    def __init__(self, pattern: Any, reason: str):
        message = f"Invalid pattern: {reason}"
        super().__init__(message, pattern=pattern)
        self.reason = reason


class AttributeMatchingError(PatternMatchingError):
    """Raised when attribute matching fails unexpectedly"""
    
    def __init__(self, attribute_name: str, pattern_value: Any, actual_value: Any, obj: Any):
        message = f"Attribute '{attribute_name}' mismatch: expected {pattern_value}, got {actual_value}"
        super().__init__(message, pattern=pattern_value, input_value=actual_value)
        self.attribute_name = attribute_name
        self.pattern_value = pattern_value
        self.actual_value = actual_value
        self.obj = obj


class PredicateEvaluationError(PatternMatchingError):
    """Raised when predicate evaluation fails"""
    
    def __init__(self, predicate: callable, input_value: Any, original_error: Exception):
        message = f"Predicate evaluation failed: {original_error}"
        super().__init__(message, pattern=predicate, input_value=input_value)
        self.predicate = predicate
        self.original_error = original_error