"""
LLM Evaluation Framework
========================
A modular, extensible framework for evaluating and comparing large language models (LLMs)
with support for multiple scoring strategies, dataset generation, persistence, and CLI usage.
"""

__version__ = "0.1.0"

# Expose key components for easy import
from .registry.model_registry import ModelRegistry

# Updated import to reflect correct module path
from .model_inference_engine import ModelInferenceEngine
from .auto_suggestion_engine import AutoSuggestionEngine  # fixed path, file is in root package
from .test_dataset_generator import TestDatasetGenerator

# Persistence components
from .persistence.json_store import JSONStore
from .persistence.db_store import DBStore
from .persistence.persistence_manager import PersistenceManager

# Evaluation components
from .evaluation.scoring_strategies import (
    ScoringStrategy,
    AccuracyScoringStrategy,
    F1ScoringStrategy,
    ScoringContext
)

# Utility components
from .utils.logger import get_logger, setup_logging
from .utils.error_handler import (
    LLMEvaluationError,
    ModelRegistryError,
    ModelInferenceError,
    DatasetGenerationError,
    PersistenceError,
    ScoringError,
    ConfigurationError,
    ErrorHandler,
    handle_exceptions
)

__all__ = [
    # Core components
    'ModelRegistry',
    'ModelInferenceEngine', 
    'AutoSuggestionEngine',
    'TestDatasetGenerator',
    
    # Persistence
    'JSONStore',
    'DBStore', 
    'PersistenceManager',
    
    # Evaluation
    'ScoringStrategy',
    'AccuracyScoringStrategy',
    'F1ScoringStrategy',
    'ScoringContext',
    
    # Utilities
    'get_logger',
    'setup_logging',
    
    # Exceptions
    'LLMEvaluationError',
    'ModelRegistryError',
    'ModelInferenceError',
    'DatasetGenerationError',
    'PersistenceError',
    'ScoringError',
    'ConfigurationError',
    'ErrorHandler',
    'handle_exceptions',
]
