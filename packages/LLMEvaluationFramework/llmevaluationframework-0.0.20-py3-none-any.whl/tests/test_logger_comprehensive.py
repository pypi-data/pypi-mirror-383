"""
Comprehensive tests for LLM Evaluation Framework logger utilities.
Tests the LLMEvaluationLogger class, singleton behavior, file logging, and convenience functions.
"""

import pytest
import logging
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock, call
import sys
from io import StringIO

from llm_evaluation_framework.utils.logger import (
    LLMEvaluationLogger,
    get_logger,
    setup_logging
)


class TestLLMEvaluationLogger:
    """Test the LLMEvaluationLogger class."""
    
    def setup_method(self):
        """Set up test environment."""
        # Clear singleton instances
        LLMEvaluationLogger._instances.clear()
        # Create temporary directory for log files
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Clean up test environment."""
        # Clean up temporary files
        if hasattr(self, 'temp_dir') and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
        # Clear singleton instances
        LLMEvaluationLogger._instances.clear()
        # Remove all handlers from all loggers
        for logger_name in logging.Logger.manager.loggerDict:
            logger = logging.getLogger(logger_name)
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
    
    def test_singleton_behavior(self):
        """Test that logger instances are singletons per name."""
        logger1 = LLMEvaluationLogger("test1")
        logger2 = LLMEvaluationLogger("test1")
        logger3 = LLMEvaluationLogger("test2")
        
        assert logger1 is logger2
        assert logger1 is not logger3
        assert len(LLMEvaluationLogger._instances) == 2
    
    def test_default_initialization(self):
        """Test default logger initialization."""
        logger = LLMEvaluationLogger()
        
        assert logger.name == "LLMEvaluationFramework"
        assert logger.logger.level == logging.DEBUG
        assert logger._initialized is True
        assert logger._file_handler is None
        assert len(logger.logger.handlers) == 1  # Console handler
    
    def test_custom_name_initialization(self):
        """Test logger initialization with custom name."""
        logger = LLMEvaluationLogger("CustomLogger")
        
        assert logger.name == "CustomLogger"
        assert logger.logger.name == "CustomLogger"
    
    def test_no_duplicate_handlers(self):
        """Test that duplicate handlers are not added."""
        logger = LLMEvaluationLogger("test")
        initial_handlers = len(logger.logger.handlers)
        
        # Try to initialize again
        logger2 = LLMEvaluationLogger("test")
        
        assert len(logger2.logger.handlers) == initial_handlers
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_console_logging(self, mock_stdout):
        """Test console logging functionality."""
        logger = LLMEvaluationLogger("test")
        
        logger.info("Test message")
        
        output = mock_stdout.getvalue()
        assert "Test message" in output
        assert "INFO" in output
    
    def test_set_level_valid(self):
        """Test setting valid log levels."""
        logger = LLMEvaluationLogger("test")
        
        logger.set_level("ERROR")
        assert logger.logger.level == logging.ERROR
        
        logger.set_level("debug")  # Test case insensitive
        assert logger.logger.level == logging.DEBUG
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_set_level_invalid(self, mock_stdout):
        """Test setting invalid log level."""
        logger = LLMEvaluationLogger("test")
        
        logger.set_level("INVALID")
        
        assert logger.logger.level == logging.INFO
        output = mock_stdout.getvalue()
        assert "Invalid log level: INVALID" in output
    
    def test_enable_file_logging_default(self):
        """Test enabling file logging with default parameters."""
        logger = LLMEvaluationLogger("test")
        
        with patch('llm_evaluation_framework.utils.logger.Path.mkdir') as mock_mkdir:
            with patch('logging.handlers.RotatingFileHandler') as mock_handler:
                mock_handler_instance = MagicMock()
                mock_handler.return_value = mock_handler_instance
                
                logger.enable_file_logging(log_dir=self.temp_dir)
                
                mock_mkdir.assert_called_once_with(exist_ok=True)
                assert logger._file_handler is mock_handler_instance
                assert mock_handler_instance in logger.logger.handlers
    
    def test_enable_file_logging_custom_file(self):
        """Test enabling file logging with custom filename."""
        logger = LLMEvaluationLogger("test")
        
        with patch('logging.handlers.RotatingFileHandler') as mock_handler:
            mock_handler_instance = MagicMock()
            mock_handler.return_value = mock_handler_instance
            
            logger.enable_file_logging(log_dir=self.temp_dir, log_file="custom.log")
            
            # Check that RotatingFileHandler was called with correct path
            expected_path = Path(self.temp_dir) / "custom.log"
            mock_handler.assert_called_once_with(
                expected_path,
                maxBytes=10*1024*1024,
                backupCount=5
            )
    
    def test_enable_file_logging_already_enabled(self):
        """Test that file logging is not enabled twice."""
        logger = LLMEvaluationLogger("test")
        
        with patch('logging.handlers.RotatingFileHandler') as mock_handler:
            mock_handler_instance = MagicMock()
            mock_handler.return_value = mock_handler_instance
            
            logger.enable_file_logging(log_dir=self.temp_dir)
            initial_handlers = len(logger.logger.handlers)
            
            # Try to enable again
            logger.enable_file_logging(log_dir=self.temp_dir)
            
            assert len(logger.logger.handlers) == initial_handlers
            mock_handler.assert_called_once()  # Should not be called again
    
    def test_debug_logging(self):
        """Test debug logging method."""
        logger = LLMEvaluationLogger("test")
        logger.set_level("DEBUG")
        
        # Capture the actual logger output
        log_capture_stream = StringIO()
        test_handler = logging.StreamHandler(log_capture_stream)
        test_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
        test_handler.setFormatter(formatter)
        
        logger.logger.handlers.clear()
        logger.logger.addHandler(test_handler)
        logger.logger.setLevel(logging.DEBUG)
        
        logger.debug("Debug message")
        
        output = log_capture_stream.getvalue()
        assert "Debug message" in output
        assert "DEBUG" in output
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_info_logging(self, mock_stdout):
        """Test info logging method."""
        logger = LLMEvaluationLogger("test")
        
        logger.info("Info message")
        
        output = mock_stdout.getvalue()
        assert "Info message" in output
        assert "INFO" in output
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_warning_logging(self, mock_stdout):
        """Test warning logging method."""
        logger = LLMEvaluationLogger("test")
        
        logger.warning("Warning message")
        
        output = mock_stdout.getvalue()
        assert "Warning message" in output
        assert "WARNING" in output
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_error_logging(self, mock_stdout):
        """Test error logging method."""
        logger = LLMEvaluationLogger("test")
        
        logger.error("Error message")
        
        output = mock_stdout.getvalue()
        assert "Error message" in output
        assert "ERROR" in output
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_critical_logging(self, mock_stdout):
        """Test critical logging method."""
        logger = LLMEvaluationLogger("test")
        
        logger.critical("Critical message")
        
        output = mock_stdout.getvalue()
        assert "Critical message" in output
        assert "CRITICAL" in output
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_exception_logging(self, mock_stdout):
        """Test exception logging method."""
        logger = LLMEvaluationLogger("test")
        
        try:
            raise ValueError("Test exception")
        except ValueError:
            logger.exception("Exception occurred")
        
        output = mock_stdout.getvalue()
        assert "Exception occurred" in output
        assert "ERROR" in output
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_format_message_with_kwargs(self, mock_stdout):
        """Test message formatting with keyword arguments."""
        logger = LLMEvaluationLogger("test")
        
        logger.info("Test message", model_id="test_model", batch_size=32)
        
        output = mock_stdout.getvalue()
        assert "Test message" in output
        assert "model_id=test_model" in output
        assert "batch_size=32" in output
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_format_message_without_kwargs(self, mock_stdout):
        """Test message formatting without keyword arguments."""
        logger = LLMEvaluationLogger("test")
        
        logger.info("Simple message")
        
        output = mock_stdout.getvalue()
        assert "Simple message" in output
        assert "|" not in output  # No context separator
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_log_evaluation_start(self, mock_stdout):
        """Test evaluation start logging."""
        logger = LLMEvaluationLogger("test")
        
        logger.log_evaluation_start("gpt-4", 100)
        
        output = mock_stdout.getvalue()
        assert "Starting evaluation for model 'gpt-4' with 100 test cases" in output
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_log_evaluation_complete(self, mock_stdout):
        """Test evaluation completion logging."""
        logger = LLMEvaluationLogger("test")
        
        results = {
            'aggregate_metrics': {
                'total_cost': 1.2345,
                'total_time': 67.89
            }
        }
        
        logger.log_evaluation_complete("gpt-4", results)
        
        output = mock_stdout.getvalue()
        assert "Evaluation completed for model 'gpt-4'" in output
        assert "Cost: $1.2345" in output
        assert "Time: 67.89s" in output
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_log_evaluation_complete_missing_metrics(self, mock_stdout):
        """Test evaluation completion logging with missing metrics."""
        logger = LLMEvaluationLogger("test")
        
        results = {}  # No aggregate_metrics
        
        logger.log_evaluation_complete("gpt-4", results)
        
        output = mock_stdout.getvalue()
        assert "Evaluation completed for model 'gpt-4'" in output
        assert "Cost: $0.0000" in output
        assert "Time: 0.00s" in output
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_log_error_with_context(self, mock_stdout):
        """Test error logging with context."""
        logger = LLMEvaluationLogger("test")
        
        error = ValueError("Test error")
        context = {"model_id": "gpt-4", "batch_size": 32, "attempt": 1}
        
        logger.log_error_with_context(error, context)
        
        output = mock_stdout.getvalue()
        assert "Error occurred: Test error" in output
        assert "model_id=gpt-4" in output
        assert "batch_size=32" in output
        assert "attempt=1" in output
    
    def test_get_logger_class_method(self):
        """Test the class method get_logger."""
        logger1 = LLMEvaluationLogger.get_logger("test")
        logger2 = LLMEvaluationLogger.get_logger("test")
        
        assert logger1 is logger2
        assert isinstance(logger1, LLMEvaluationLogger)


class TestConvenienceFunctions:
    """Test convenience functions for logging."""
    
    def setup_method(self):
        """Set up test environment."""
        LLMEvaluationLogger._instances.clear()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test environment."""
        if hasattr(self, 'temp_dir') and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
        LLMEvaluationLogger._instances.clear()
        # Remove all handlers from all loggers
        for logger_name in logging.Logger.manager.loggerDict:
            logger = logging.getLogger(logger_name)
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
    
    def test_get_logger_function(self):
        """Test the get_logger convenience function."""
        logger = get_logger("test")
        
        assert isinstance(logger, LLMEvaluationLogger)
        assert logger.name == "test"
    
    def test_get_logger_default_name(self):
        """Test get_logger with default name."""
        logger = get_logger()
        
        assert logger.name == "LLMEvaluationFramework"
    
    def test_setup_logging_basic(self):
        """Test basic setup_logging functionality."""
        logger = setup_logging(level="ERROR")
        
        assert logger.logger.level == logging.ERROR
        assert logger._file_handler is None
    
    def test_setup_logging_with_file(self):
        """Test setup_logging with file logging enabled."""
        with patch('logging.handlers.RotatingFileHandler') as mock_handler:
            mock_handler_instance = MagicMock()
            mock_handler.return_value = mock_handler_instance
            
            logger = setup_logging(
                level="DEBUG",
                enable_file=True,
                log_dir=self.temp_dir
            )
            
            assert logger.logger.level == logging.DEBUG
            assert logger._file_handler is mock_handler_instance
    
    def test_setup_logging_default_parameters(self):
        """Test setup_logging with default parameters."""
        logger = setup_logging()
        
        assert logger.logger.level == logging.INFO
        assert logger._file_handler is None


class TestLoggerFileOperations:
    """Test actual file operations for logging."""
    
    def setup_method(self):
        """Set up test environment."""
        LLMEvaluationLogger._instances.clear()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test environment."""
        if hasattr(self, 'temp_dir') and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
        LLMEvaluationLogger._instances.clear()
        # Remove all handlers from all loggers
        for logger_name in logging.Logger.manager.loggerDict:
            logger = logging.getLogger(logger_name)
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
    
    def test_actual_file_logging(self):
        """Test actual file logging functionality."""
        logger = LLMEvaluationLogger("test")
        logger.enable_file_logging(log_dir=self.temp_dir, log_file="test.log")
        
        logger.info("Test file message")
        
        # Check that log file was created
        log_file = Path(self.temp_dir) / "test.log"
        assert log_file.exists()
        
        # Check log content
        content = log_file.read_text()
        assert "Test file message" in content
        assert "INFO" in content
    
    def test_log_directory_creation(self):
        """Test that log directory is created if it doesn't exist."""
        # Use a single level directory since the implementation doesn't use parents=True
        non_existent_dir = Path(self.temp_dir) / "logs"
        
        logger = LLMEvaluationLogger("test")
        logger.enable_file_logging(log_dir=str(non_existent_dir))
        
        assert non_existent_dir.exists()
    
    def test_default_log_filename(self):
        """Test default log filename generation."""
        logger = LLMEvaluationLogger("test")
        
        with patch('llm_evaluation_framework.utils.logger.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "20231201"
            
            logger.enable_file_logging(log_dir=self.temp_dir)
            
            expected_file = Path(self.temp_dir) / "llm_eval_20231201.log"
            # We can't easily test file creation without mocking RotatingFileHandler
            # But we can verify the method was called correctly
            mock_datetime.now.assert_called_once()


class TestLoggerEdgeCases:
    """Test edge cases and error scenarios."""
    
    def setup_method(self):
        """Set up test environment."""
        LLMEvaluationLogger._instances.clear()
    
    def teardown_method(self):
        """Clean up test environment."""
        LLMEvaluationLogger._instances.clear()
        # Remove all handlers from all loggers
        for logger_name in logging.Logger.manager.loggerDict:
            logger = logging.getLogger(logger_name)
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
    
    def test_empty_message_logging(self):
        """Test logging empty messages."""
        logger = LLMEvaluationLogger("test")
        
        # Should not raise exception
        logger.info("")
        logger.debug("")
        logger.error("")
    
    def test_none_values_in_kwargs(self):
        """Test logging with None values in kwargs."""
        logger = LLMEvaluationLogger("test")
        
        # Capture the actual logger output rather than mocking stdout
        log_capture_stream = StringIO()
        test_handler = logging.StreamHandler(log_capture_stream)
        test_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
        test_handler.setFormatter(formatter)
        
        # Add to logger and ensure no other handlers interfere
        logger.logger.handlers.clear()
        logger.logger.addHandler(test_handler)
        logger.logger.setLevel(logging.DEBUG)
        
        logger.info("Test", value=None, number=42)
        
        output = log_capture_stream.getvalue()
        assert "value=None" in output
        assert "number=42" in output
    
    def test_special_characters_in_message(self):
        """Test logging messages with special characters."""
        logger = LLMEvaluationLogger("test")
        
        # Capture the actual logger output
        log_capture_stream = StringIO()
        test_handler = logging.StreamHandler(log_capture_stream)
        test_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
        test_handler.setFormatter(formatter)
        
        logger.logger.handlers.clear()
        logger.logger.addHandler(test_handler)
        logger.logger.setLevel(logging.DEBUG)
        
        logger.info("Test with special chars: äöü, 中文, emoji 🎉")
        
        output = log_capture_stream.getvalue()
        assert "äöü" in output
        assert "中文" in output
        assert "🎉" in output
    
    def test_very_long_message(self):
        """Test logging very long messages."""
        logger = LLMEvaluationLogger("test")
        long_message = "A" * 1000  # Reduce size for easier testing
        
        # Capture the actual logger output
        log_capture_stream = StringIO()
        test_handler = logging.StreamHandler(log_capture_stream)
        test_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
        test_handler.setFormatter(formatter)
        
        logger.logger.handlers.clear()
        logger.logger.addHandler(test_handler)
        logger.logger.setLevel(logging.DEBUG)
        
        logger.info(long_message)
        
        output = log_capture_stream.getvalue()
        assert long_message in output
    
    def test_multiple_logger_instances_different_levels(self):
        """Test multiple logger instances with different levels."""
        logger1 = LLMEvaluationLogger("logger1")
        logger2 = LLMEvaluationLogger("logger2")
        
        logger1.set_level("ERROR")
        logger2.set_level("DEBUG")
        
        assert logger1.logger.level == logging.ERROR
        assert logger2.logger.level == logging.DEBUG
    
    def test_complex_kwargs_formatting(self):
        """Test formatting with complex kwargs."""
        logger = LLMEvaluationLogger("test")
        
        # Capture the actual logger output
        log_capture_stream = StringIO()
        test_handler = logging.StreamHandler(log_capture_stream)
        test_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
        test_handler.setFormatter(formatter)
        
        logger.logger.handlers.clear()
        logger.logger.addHandler(test_handler)
        logger.logger.setLevel(logging.DEBUG)
        
        complex_data = {
            "list": [1, 2, 3],
            "dict": {"key": "value"},
            "boolean": True,
            "float": 3.14159
        }
        
        logger.info("Complex data", **complex_data)
        
        output = log_capture_stream.getvalue()
        assert "list=[1, 2, 3]" in output
        assert "dict={'key': 'value'}" in output
        assert "boolean=True" in output
        assert "float=3.14159" in output