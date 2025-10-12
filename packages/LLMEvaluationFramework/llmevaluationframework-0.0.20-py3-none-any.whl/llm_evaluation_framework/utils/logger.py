"""
Centralized logging utilities for LLM Evaluation Framework.
Provides standardized logging configuration and utilities.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


class LLMEvaluationLogger:
    """
    Centralized logger for the LLM Evaluation Framework.
    
    Provides structured logging with file and console outputs,
    and framework-specific formatting.
    """
    
    _instances: Dict[str, 'LLMEvaluationLogger'] = {}
    
    def __new__(cls, name: str = "LLMEvaluationFramework"):
        """Ensure singleton per logger name."""
        if name not in cls._instances:
            cls._instances[name] = super().__new__(cls)
        return cls._instances[name]
    
    def __init__(self, name: str = "LLMEvaluationFramework"):
        """
        Initialize the logger with given name.
        
        Args:
            name (str): Name of the logger
        """
        # Initialize attributes first
        if not hasattr(self, '_initialized'):
            self._initialized = False
            self._file_handler = None
            
        if self._initialized:
            return
            
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
        
        self._initialized = True
    
    def _setup_handlers(self) -> None:
        """Set up console and file handlers with appropriate formatting."""
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
    
    def enable_file_logging(self, log_dir: str = "logs", log_file: Optional[str] = None) -> None:
        """
        Enable file logging with automatic rotation.
        
        Args:
            log_dir (str): Directory to store log files
            log_file (Optional[str]): Name of the log file
        """
        if self._file_handler:
            return  # Already enabled
        
        # Create log directory
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)
        
        # Generate log filename if not provided
        if log_file is None:
            timestamp = datetime.now().strftime("%Y%m%d")
            log_file = f"llm_eval_{timestamp}.log"
        
        file_path = log_path / log_file
        
        # Create file handler
        from logging.handlers import RotatingFileHandler
        self._file_handler = RotatingFileHandler(
            file_path,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        self._file_handler.setLevel(logging.DEBUG)
        
        # Detailed formatter for file logging
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self._file_handler.setFormatter(file_formatter)
        self.logger.addHandler(self._file_handler)
    
    def set_level(self, level: str) -> None:
        """
        Set the logging level.
        
        Args:
            level (str): Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        """
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        
        if level.upper() in level_map:
            self.logger.setLevel(level_map[level.upper()])
        else:
            self.warning(f"Invalid log level: {level}. Using INFO instead.")
            self.logger.setLevel(logging.INFO)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self.logger.debug(self._format_message(message, **kwargs))
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self.logger.info(self._format_message(message, **kwargs))
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self.logger.warning(self._format_message(message, **kwargs))
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        self.logger.error(self._format_message(message, **kwargs))
    
    def critical(self, message: str, **kwargs) -> None:
        """Log critical message."""
        self.logger.critical(self._format_message(message, **kwargs))
    
    def exception(self, message: str, **kwargs) -> None:
        """Log exception with traceback."""
        self.logger.exception(self._format_message(message, **kwargs))
    
    def log_evaluation_start(self, model_id: str, test_cases_count: int) -> None:
        """Log the start of an evaluation."""
        self.info(f"Starting evaluation for model '{model_id}' with {test_cases_count} test cases")
    
    def log_evaluation_complete(self, model_id: str, results: Dict[str, Any]) -> None:
        """Log the completion of an evaluation."""
        metrics = results.get('aggregate_metrics', {})
        total_cost = metrics.get('total_cost', 0)
        total_time = metrics.get('total_time', 0)
        
        self.info(
            f"Evaluation completed for model '{model_id}' - "
            f"Cost: ${total_cost:.4f}, Time: {total_time:.2f}s"
        )
    
    def log_error_with_context(self, error: Exception, context: Dict[str, Any]) -> None:
        """Log an error with additional context information."""
        context_str = ", ".join(f"{k}={v}" for k, v in context.items())
        self.error(f"Error occurred: {str(error)} | Context: {context_str}")
    
    def _format_message(self, message: str, **kwargs) -> str:
        """
        Format log message with optional context.
        
        Args:
            message (str): The log message
            **kwargs: Additional context to include
            
        Returns:
            str: Formatted message
        """
        if kwargs:
            context = ", ".join(f"{k}={v}" for k, v in kwargs.items())
            return f"{message} | {context}"
        return message
    
    @classmethod
    def get_logger(cls, name: str = "LLMEvaluationFramework") -> 'LLMEvaluationLogger':
        """
        Get or create a logger instance.
        
        Args:
            name (str): Name of the logger
            
        Returns:
            LLMEvaluationLogger: Logger instance
        """
        return cls(name)


# Convenience functions for quick access
def get_logger(name: str = "LLMEvaluationFramework") -> LLMEvaluationLogger:
    """Get a logger instance."""
    return LLMEvaluationLogger.get_logger(name)


def setup_logging(level: str = "INFO", enable_file: bool = False, log_dir: str = "logs") -> LLMEvaluationLogger:
    """
    Setup framework-wide logging configuration.
    
    Args:
        level (str): Logging level
        enable_file (bool): Whether to enable file logging
        log_dir (str): Directory for log files
        
    Returns:
        LLMEvaluationLogger: Configured logger instance
    """
    logger = get_logger()
    logger.set_level(level)
    
    if enable_file:
        logger.enable_file_logging(log_dir)
    
    return logger
