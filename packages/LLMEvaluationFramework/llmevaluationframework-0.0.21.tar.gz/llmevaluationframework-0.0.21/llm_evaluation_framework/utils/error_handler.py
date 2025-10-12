"""
Error handling utilities for LLM Evaluation Framework.
Provides structured error handling and custom exceptions.
"""

import traceback
from typing import Any, Dict, Optional, Type, Callable
from functools import wraps


class LLMEvaluationError(Exception):
    """Base exception for LLM Evaluation Framework."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        
    def __str__(self) -> str:
        base_msg = self.message
        if self.error_code:
            base_msg = f"[{self.error_code}] {base_msg}"
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            base_msg = f"{base_msg} | Context: {context_str}"
        return base_msg


class ModelRegistryError(LLMEvaluationError):
    """Exception raised for model registry operations."""


class ModelInferenceError(LLMEvaluationError):
    """Exception raised during model inference."""


class DatasetGenerationError(LLMEvaluationError):
    """Exception raised during dataset generation."""


class PersistenceError(LLMEvaluationError):
    """Exception raised for persistence operations."""


class ScoringError(LLMEvaluationError):
    """Exception raised during scoring operations."""


class ConfigurationError(LLMEvaluationError):
    """Exception raised for configuration issues."""


class ErrorHandler:
    """
    Centralized error handling for the LLM Evaluation Framework.
    
    Provides structured error handling, logging, and recovery mechanisms.
    """
    
    def __init__(self, logger=None):
        """
        Initialize the error handler.
        
        Args:
            logger: Logger instance for error reporting
        """
        self.logger = logger
        self.error_callbacks: Dict[Type[Exception], Callable] = {}
    
    def register_error_callback(self, error_type: Type[Exception], callback: Callable) -> None:
        """
        Register a callback for specific error types.
        
        Args:
            error_type (Type[Exception]): Type of exception to handle
            callback (Callable): Function to call when error occurs
        """
        self.error_callbacks[error_type] = callback
    
    def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Handle an error with logging and optional callbacks.
        
        Args:
            error (Exception): The exception to handle
            context (Optional[Dict[str, Any]]): Additional context information
        """
        # Log the error
        if self.logger:
            if context:
                self.logger.log_error_with_context(error, context)
            else:
                self.logger.error(f"Error occurred: {str(error)}")
                self.logger.debug(f"Traceback: {traceback.format_exc()}")
        
        # Execute registered callback if available
        error_type = type(error)
        if error_type in self.error_callbacks:
            try:
                self.error_callbacks[error_type](error, context)
            except Exception as callback_error:
                if self.logger:
                    self.logger.error(f"Error in error callback: {str(callback_error)}")
    
    def safe_execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a function with error handling.
        
        Args:
            func (Callable): Function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Any: Function result or None if error occurred
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.handle_error(e, {"function": func.__name__, "args": str(args), "kwargs": str(kwargs)})
            return None


def handle_exceptions(
    error_type: Type[LLMEvaluationError] = LLMEvaluationError,
    error_code: Optional[str] = None,
    default_return: Any = None,
    reraise: bool = True
):
    """
    Decorator for handling exceptions in functions.
    
    Args:
        error_type (Type[LLMEvaluationError]): Type of error to raise
        error_code (Optional[str]): Error code to include
        default_return (Any): Default value to return on error
        reraise (bool): Whether to reraise the exception
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except LLMEvaluationError:
                # Re-raise framework exceptions as-is
                if reraise:
                    raise
                return default_return
            except Exception as e:
                # Wrap other exceptions in framework exception
                context = {
                    "function": func.__name__,
                    "module": func.__module__,
                    "original_error": str(e)
                }
                
                framework_error = error_type(
                    f"Error in {func.__name__}: {str(e)}",
                    error_code=error_code,
                    context=context
                )
                
                if reraise:
                    raise framework_error from e
                return default_return
        
        return wrapper
    return decorator


def validate_not_none(value: Any, name: str) -> Any:
    """
    Validate that a value is not None.
    
    Args:
        value (Any): Value to validate
        name (str): Name of the value for error message
        
    Returns:
        Any: The validated value
        
    Raises:
        ConfigurationError: If value is None
    """
    if value is None:
        raise ConfigurationError(f"{name} cannot be None")
    return value


def validate_not_empty(value: str, name: str) -> str:
    """
    Validate that a string is not empty.
    
    Args:
        value (str): String to validate
        name (str): Name of the value for error message
        
    Returns:
        str: The validated string
        
    Raises:
        ConfigurationError: If string is empty
    """
    if not value or not value.strip():
        raise ConfigurationError(f"{name} cannot be empty")
    return value


def validate_positive_number(value: float, name: str) -> float:
    """
    Validate that a number is positive.
    
    Args:
        value (float): Number to validate
        name (str): Name of the value for error message
        
    Returns:
        float: The validated number
        
    Raises:
        ConfigurationError: If number is not positive
    """
    if value <= 0:
        raise ConfigurationError(f"{name} must be positive, got {value}")
    return value


def validate_in_range(value: float, min_val: float, max_val: float, name: str) -> float:
    """
    Validate that a number is within a specific range.
    
    Args:
        value (float): Number to validate
        min_val (float): Minimum allowed value
        max_val (float): Maximum allowed value
        name (str): Name of the value for error message
        
    Returns:
        float: The validated number
        
    Raises:
        ConfigurationError: If number is outside the range
    """
    if not min_val <= value <= max_val:
        raise ConfigurationError(f"{name} must be between {min_val} and {max_val}, got {value}")
    return value


def create_error_context(**kwargs) -> Dict[str, Any]:
    """
    Create an error context dictionary from keyword arguments.
    
    Args:
        **kwargs: Context key-value pairs
        
    Returns:
        Dict[str, Any]: Context dictionary
    """
    return {k: v for k, v in kwargs.items() if v is not None}


class RetryHandler:
    """Handler for retry logic with exponential backoff."""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
        """
        Initialize retry handler.
        
        Args:
            max_retries (int): Maximum number of retry attempts
            base_delay (float): Base delay between retries in seconds
            max_delay (float): Maximum delay between retries in seconds
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
    
    def retry(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with retry logic.
        
        Args:
            func (Callable): Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Any: Function result
            
        Raises:
            Exception: Last exception if all retries failed
        """
        import time
        import random
        
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt == self.max_retries:
                    break
                
                # Calculate delay with exponential backoff and jitter
                delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                jitter = random.uniform(0, delay * 0.1)
                time.sleep(delay + jitter)
        
        raise last_exception
