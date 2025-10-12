"""
Comprehensive tests for error handling utilities.
Tests custom exceptions, error handler, decorators, validators, and retry logic.
"""

import pytest
import time
from unittest.mock import Mock, patch
from llm_evaluation_framework.utils.error_handler import (
    LLMEvaluationError,
    ModelRegistryError,
    ModelInferenceError,
    DatasetGenerationError,
    PersistenceError,
    ScoringError,
    ConfigurationError,
    ErrorHandler,
    handle_exceptions,
    validate_not_none,
    validate_not_empty,
    validate_positive_number,
    validate_in_range,
    create_error_context,
    RetryHandler
)


class TestLLMEvaluationError:
    """Tests for the base LLMEvaluationError class."""
    
    def test_basic_error_creation(self):
        """Test basic error creation with message only."""
        error = LLMEvaluationError("Test error message")
        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.error_code is None
        assert error.context == {}
    
    def test_error_with_code(self):
        """Test error creation with error code."""
        error = LLMEvaluationError("Test error", error_code="ERR001")
        assert str(error) == "[ERR001] Test error"
        assert error.error_code == "ERR001"
    
    def test_error_with_context(self):
        """Test error creation with context."""
        context = {"model": "gpt-3.5", "attempt": 2}
        error = LLMEvaluationError("Test error", context=context)
        expected_str = "Test error | Context: model=gpt-3.5, attempt=2"
        assert str(error) == expected_str
        assert error.context == context
    
    def test_error_with_code_and_context(self):
        """Test error creation with both code and context."""
        context = {"model": "gpt-3.5"}
        error = LLMEvaluationError("Test error", error_code="ERR001", context=context)
        expected_str = "[ERR001] Test error | Context: model=gpt-3.5"
        assert str(error) == expected_str
    
    def test_error_inheritance(self):
        """Test that error inherits from Exception properly."""
        error = LLMEvaluationError("Test")
        assert isinstance(error, Exception)
        assert isinstance(error, LLMEvaluationError)
    
    def test_empty_context_handling(self):
        """Test error with empty context."""
        error = LLMEvaluationError("Test error", context={})
        assert str(error) == "Test error"
        assert error.context == {}


class TestSpecificExceptions:
    """Tests for specific exception classes."""
    
    def test_model_registry_error(self):
        """Test ModelRegistryError inherits properly."""
        error = ModelRegistryError("Registry error", error_code="REG001")
        assert isinstance(error, LLMEvaluationError)
        assert isinstance(error, ModelRegistryError)
        assert str(error) == "[REG001] Registry error"
    
    def test_model_inference_error(self):
        """Test ModelInferenceError inherits properly."""
        error = ModelInferenceError("Inference failed")
        assert isinstance(error, LLMEvaluationError)
        assert isinstance(error, ModelInferenceError)
    
    def test_dataset_generation_error(self):
        """Test DatasetGenerationError inherits properly."""
        error = DatasetGenerationError("Generation failed")
        assert isinstance(error, LLMEvaluationError)
        assert isinstance(error, DatasetGenerationError)
    
    def test_persistence_error(self):
        """Test PersistenceError inherits properly."""
        error = PersistenceError("Storage failed")
        assert isinstance(error, LLMEvaluationError)
        assert isinstance(error, PersistenceError)
    
    def test_scoring_error(self):
        """Test ScoringError inherits properly."""
        error = ScoringError("Scoring failed")
        assert isinstance(error, LLMEvaluationError)
        assert isinstance(error, ScoringError)
    
    def test_configuration_error(self):
        """Test ConfigurationError inherits properly."""
        error = ConfigurationError("Config invalid")
        assert isinstance(error, LLMEvaluationError)
        assert isinstance(error, ConfigurationError)


class TestErrorHandler:
    """Tests for ErrorHandler class."""
    
    def test_error_handler_initialization(self):
        """Test basic error handler initialization."""
        handler = ErrorHandler()
        assert handler.logger is None
        assert handler.error_callbacks == {}
    
    def test_error_handler_with_logger(self):
        """Test error handler initialization with logger."""
        mock_logger = Mock()
        handler = ErrorHandler(logger=mock_logger)
        assert handler.logger == mock_logger
    
    def test_register_error_callback(self):
        """Test registering error callbacks."""
        handler = ErrorHandler()
        callback = Mock()
        
        handler.register_error_callback(ValueError, callback)
        assert ValueError in handler.error_callbacks
        assert handler.error_callbacks[ValueError] == callback
    
    def test_handle_error_with_logger(self):
        """Test error handling with logger."""
        mock_logger = Mock()
        handler = ErrorHandler(logger=mock_logger)
        
        error = ValueError("Test error")
        handler.handle_error(error)
        
        mock_logger.error.assert_called_once()
        mock_logger.debug.assert_called_once()
    
    def test_handle_error_with_context_and_logger(self):
        """Test error handling with context and logger."""
        mock_logger = Mock()
        mock_logger.log_error_with_context = Mock()
        handler = ErrorHandler(logger=mock_logger)
        
        error = ValueError("Test error")
        context = {"operation": "test"}
        handler.handle_error(error, context)
        
        mock_logger.log_error_with_context.assert_called_once_with(error, context)
    
    def test_handle_error_with_callback(self):
        """Test error handling with registered callback."""
        handler = ErrorHandler()
        callback = Mock()
        handler.register_error_callback(ValueError, callback)
        
        error = ValueError("Test error")
        context = {"operation": "test"}
        handler.handle_error(error, context)
        
        callback.assert_called_once_with(error, context)
    
    def test_handle_error_callback_exception(self):
        """Test error handling when callback itself raises exception."""
        mock_logger = Mock()
        handler = ErrorHandler(logger=mock_logger)
        
        def failing_callback(error, context):
            raise RuntimeError("Callback failed")
        
        handler.register_error_callback(ValueError, failing_callback)
        
        error = ValueError("Test error")
        handler.handle_error(error)
        
        # Should log the callback error
        assert mock_logger.error.call_count >= 1
    
    def test_safe_execute_success(self):
        """Test safe_execute with successful function."""
        handler = ErrorHandler()
        
        def test_func(x, y):
            return x + y
        
        result = handler.safe_execute(test_func, 2, 3)
        assert result == 5
    
    def test_safe_execute_failure(self):
        """Test safe_execute with failing function."""
        mock_logger = Mock()
        # Mock the log_error_with_context method that is actually called
        mock_logger.log_error_with_context = Mock()
        handler = ErrorHandler(logger=mock_logger)
        
        def failing_func():
            raise ValueError("Function failed")
        
        result = handler.safe_execute(failing_func)
        assert result is None
        # The logger should be called through handle_error
        mock_logger.log_error_with_context.assert_called()
    
    def test_safe_execute_with_args_kwargs(self):
        """Test safe_execute with args and kwargs."""
        handler = ErrorHandler()
        
        def test_func(a, b, c=None):
            return f"{a}-{b}-{c}"
        
        result = handler.safe_execute(test_func, "x", "y", c="z")
        assert result == "x-y-z"


class TestHandleExceptionsDecorator:
    """Tests for handle_exceptions decorator."""
    
    def test_decorator_success(self):
        """Test decorator with successful function execution."""
        @handle_exceptions()
        def test_func():
            return "success"
        
        result = test_func()
        assert result == "success"
    
    def test_decorator_reraise_framework_exception(self):
        """Test decorator reraises framework exceptions."""
        @handle_exceptions()
        def test_func():
            raise LLMEvaluationError("Framework error")
        
        with pytest.raises(LLMEvaluationError):
            test_func()
    
    def test_decorator_wrap_general_exception(self):
        """Test decorator wraps general exceptions."""
        @handle_exceptions(error_type=ModelInferenceError, error_code="INF001")
        def test_func():
            raise ValueError("General error")
        
        with pytest.raises(ModelInferenceError) as exc_info:
            test_func()
        
        assert exc_info.value.error_code == "INF001"
        assert "test_func" in str(exc_info.value)
        assert "General error" in str(exc_info.value)
    
    def test_decorator_no_reraise(self):
        """Test decorator with reraise=False."""
        @handle_exceptions(reraise=False, default_return="default")
        def test_func():
            raise ValueError("Error")
        
        result = test_func()
        assert result == "default"
    
    def test_decorator_no_reraise_framework_exception(self):
        """Test decorator with framework exception and reraise=False."""
        @handle_exceptions(reraise=False, default_return="default")
        def test_func():
            raise LLMEvaluationError("Framework error")
        
        result = test_func()
        assert result == "default"
    
    def test_decorator_context_information(self):
        """Test decorator includes context information."""
        @handle_exceptions(error_type=ConfigurationError)
        def test_func():
            raise RuntimeError("Original error")
        
        with pytest.raises(ConfigurationError) as exc_info:
            test_func()
        
        context = exc_info.value.context
        assert context["function"] == "test_func"
        assert "test_error_handler_comprehensive" in context["module"]
        assert context["original_error"] == "Original error"


class TestValidationFunctions:
    """Tests for validation utility functions."""
    
    def test_validate_not_none_success(self):
        """Test validate_not_none with valid value."""
        result = validate_not_none("test", "value")
        assert result == "test"
        
        result = validate_not_none(0, "number")
        assert result == 0
        
        result = validate_not_none([], "list")
        assert result == []
    
    def test_validate_not_none_failure(self):
        """Test validate_not_none with None value."""
        with pytest.raises(ConfigurationError) as exc_info:
            validate_not_none(None, "test_value")
        
        assert "test_value cannot be None" in str(exc_info.value)
    
    def test_validate_not_empty_success(self):
        """Test validate_not_empty with valid strings."""
        result = validate_not_empty("test", "value")
        assert result == "test"
        
        result = validate_not_empty("  test  ", "value")
        assert result == "  test  "
    
    def test_validate_not_empty_failure(self):
        """Test validate_not_empty with empty strings."""
        with pytest.raises(ConfigurationError) as exc_info:
            validate_not_empty("", "test_value")
        assert "test_value cannot be empty" in str(exc_info.value)
        
        with pytest.raises(ConfigurationError) as exc_info:
            validate_not_empty("   ", "test_value")
        assert "test_value cannot be empty" in str(exc_info.value)
    
    def test_validate_positive_number_success(self):
        """Test validate_positive_number with valid numbers."""
        result = validate_positive_number(5.0, "value")
        assert result == 5.0
        
        result = validate_positive_number(0.1, "value")
        assert result == 0.1
        
        result = validate_positive_number(100, "value")
        assert result == 100
    
    def test_validate_positive_number_failure(self):
        """Test validate_positive_number with invalid numbers."""
        with pytest.raises(ConfigurationError) as exc_info:
            validate_positive_number(0, "test_value")
        assert "test_value must be positive, got 0" in str(exc_info.value)
        
        with pytest.raises(ConfigurationError) as exc_info:
            validate_positive_number(-5, "test_value")
        assert "test_value must be positive, got -5" in str(exc_info.value)
    
    def test_validate_in_range_success(self):
        """Test validate_in_range with valid values."""
        result = validate_in_range(5.0, 0.0, 10.0, "value")
        assert result == 5.0
        
        result = validate_in_range(0.0, 0.0, 10.0, "value")
        assert result == 0.0
        
        result = validate_in_range(10.0, 0.0, 10.0, "value")
        assert result == 10.0
    
    def test_validate_in_range_failure(self):
        """Test validate_in_range with out-of-range values."""
        with pytest.raises(ConfigurationError) as exc_info:
            validate_in_range(-1.0, 0.0, 10.0, "test_value")
        assert "test_value must be between 0.0 and 10.0, got -1.0" in str(exc_info.value)
        
        with pytest.raises(ConfigurationError) as exc_info:
            validate_in_range(11.0, 0.0, 10.0, "test_value")
        assert "test_value must be between 0.0 and 10.0, got 11.0" in str(exc_info.value)


class TestErrorContextFunction:
    """Tests for create_error_context function."""
    
    def test_create_error_context_basic(self):
        """Test basic error context creation."""
        context = create_error_context(model="gpt-3.5", attempt=1)
        expected = {"model": "gpt-3.5", "attempt": 1}
        assert context == expected
    
    def test_create_error_context_with_none_values(self):
        """Test error context creation filters None values."""
        context = create_error_context(model="gpt-3.5", attempt=None, retry=True)
        expected = {"model": "gpt-3.5", "retry": True}
        assert context == expected
    
    def test_create_error_context_empty(self):
        """Test error context creation with no arguments."""
        context = create_error_context()
        assert context == {}
    
    def test_create_error_context_all_none(self):
        """Test error context creation with all None values."""
        context = create_error_context(a=None, b=None, c=None)
        assert context == {}


class TestRetryHandler:
    """Tests for RetryHandler class."""
    
    def test_retry_handler_initialization(self):
        """Test retry handler initialization with defaults."""
        handler = RetryHandler()
        assert handler.max_retries == 3
        assert handler.base_delay == 1.0
        assert handler.max_delay == 60.0
    
    def test_retry_handler_custom_parameters(self):
        """Test retry handler initialization with custom parameters."""
        handler = RetryHandler(max_retries=5, base_delay=0.5, max_delay=30.0)
        assert handler.max_retries == 5
        assert handler.base_delay == 0.5
        assert handler.max_delay == 30.0
    
    def test_retry_success_first_attempt(self):
        """Test retry with function succeeding on first attempt."""
        handler = RetryHandler()
        
        def success_func():
            return "success"
        
        result = handler.retry(success_func)
        assert result == "success"
    
    def test_retry_success_after_failures(self):
        """Test retry with function succeeding after some failures."""
        handler = RetryHandler(max_retries=3, base_delay=0.01)  # Fast for testing
        
        call_count = 0
        def sometimes_fails():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary failure")
            return "success"
        
        result = handler.retry(sometimes_fails)
        assert result == "success"
        assert call_count == 3
    
    def test_retry_max_attempts_exceeded(self):
        """Test retry when max attempts are exceeded."""
        handler = RetryHandler(max_retries=2, base_delay=0.01)  # Fast for testing
        
        call_count = 0
        def always_fails():
            nonlocal call_count
            call_count += 1
            raise ValueError(f"Failure {call_count}")
        
        with pytest.raises(ValueError) as exc_info:
            handler.retry(always_fails)
        
        assert "Failure 3" in str(exc_info.value)  # 2 retries + 1 initial = 3 total
        assert call_count == 3
    
    def test_retry_with_arguments(self):
        """Test retry with function arguments."""
        handler = RetryHandler()
        
        def add_func(a, b):
            return a + b
        
        result = handler.retry(add_func, 2, 3)
        assert result == 5
    
    def test_retry_with_kwargs(self):
        """Test retry with function keyword arguments."""
        handler = RetryHandler()
        
        def multiply_func(a, b=1):
            return a * b
        
        result = handler.retry(multiply_func, 5, b=3)
        assert result == 15
    
    @patch('time.sleep')
    def test_retry_delay_calculation(self, mock_sleep):
        """Test retry delay calculation with exponential backoff."""
        handler = RetryHandler(max_retries=3, base_delay=1.0, max_delay=10.0)
        
        call_count = 0
        def always_fails():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError):
            handler.retry(always_fails)
        
        # Should have called sleep for each retry (3 times)
        assert mock_sleep.call_count == 3
        
        # Check that delays increase (approximately, due to jitter)
        calls = mock_sleep.call_args_list
        delays = [call[0][0] for call in calls]
        
        # First delay should be around base_delay (1.0)
        assert 1.0 <= delays[0] <= 1.1
        # Second delay should be around 2 * base_delay (2.0)
        assert 2.0 <= delays[1] <= 2.2
        # Third delay should be around 4 * base_delay (4.0)
        assert 4.0 <= delays[2] <= 4.4
    
    @patch('time.sleep')
    def test_retry_max_delay_limit(self, mock_sleep):
        """Test that retry respects max_delay limit."""
        handler = RetryHandler(max_retries=5, base_delay=10.0, max_delay=15.0)
        
        def always_fails():
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError):
            handler.retry(always_fails)
        
        # All delays should be limited by max_delay
        calls = mock_sleep.call_args_list
        delays = [call[0][0] for call in calls]
        
        for delay in delays:
            assert delay <= 16.5  # Account for jitter (max_delay + 10% jitter)


class TestErrorHandlerIntegration:
    """Integration tests for error handling components."""
    
    def test_error_handler_with_decorated_function(self):
        """Test error handler working with decorated functions."""
        mock_logger = Mock()
        handler = ErrorHandler(logger=mock_logger)
        callback = Mock()
        handler.register_error_callback(ModelInferenceError, callback)
        
        @handle_exceptions(error_type=ModelInferenceError, error_code="INF001")
        def test_func():
            raise ValueError("Model failed")
        
        # Capture the exception to handle it
        try:
            test_func()
        except ModelInferenceError as e:
            handler.handle_error(e)
        
        # Verify callback was called
        callback.assert_called_once()
        
        # Verify error has proper structure
        error_args = callback.call_args[0]
        error = error_args[0]
        assert isinstance(error, ModelInferenceError)
        assert error.error_code == "INF001"
    
    def test_retry_with_validation(self):
        """Test retry handler with validation functions."""
        handler = RetryHandler(max_retries=2, base_delay=0.01)
        
        def validate_and_process(value):
            validated = validate_positive_number(value, "input_value")
            if validated < 5:
                raise ValueError("Value too small")
            return validated * 2
        
        # Should succeed
        result = handler.retry(validate_and_process, 10)
        assert result == 20
        
        # Should fail validation
        with pytest.raises(ConfigurationError):
            handler.retry(validate_and_process, -1)
    
    def test_comprehensive_error_flow(self):
        """Test comprehensive error handling flow."""
        # Setup error handler with logger and callback
        mock_logger = Mock()
        mock_logger.log_error_with_context = Mock()
        handler = ErrorHandler(logger=mock_logger)
        
        error_log = []
        def error_callback(error, context):
            error_log.append((error, context))
        
        handler.register_error_callback(ModelInferenceError, error_callback)
        
        # Create a function that uses multiple error handling features
        @handle_exceptions(error_type=ModelInferenceError, error_code="INF001")
        def complex_function(model_name, retries=3):
            validate_not_empty(model_name, "model_name")
            validate_positive_number(retries, "retries")
            
            # Simulate a failure
            raise RuntimeError("Model inference failed")
        
        # Execute and handle the error
        try:
            complex_function("gpt-3.5", retries=3)
        except ModelInferenceError as e:
            context = create_error_context(
                operation="model_inference",
                model="gpt-3.5",
                timestamp=time.time()
            )
            handler.handle_error(e, context)
        
        # Verify all components worked
        assert len(error_log) == 1
        error, context = error_log[0]
        assert isinstance(error, ModelInferenceError)
        assert error.error_code == "INF001"
        assert "operation" in context
        
        # Verify logger was called
        mock_logger.log_error_with_context.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])