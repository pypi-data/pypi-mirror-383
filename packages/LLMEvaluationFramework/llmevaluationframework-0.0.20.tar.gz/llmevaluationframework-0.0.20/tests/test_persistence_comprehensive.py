"""
Comprehensive tests for persistence layer to achieve 85% coverage.
Tests for JSONStore, DBStore, and PersistenceManager.
"""

import pytest
import os
import json
import sqlite3
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from llm_evaluation_framework.persistence.json_store import JSONStore
from llm_evaluation_framework.persistence.db_store import DBStore
from llm_evaluation_framework.persistence.persistence_manager import PersistenceManager


class TestJSONStore:
    """Comprehensive tests for JSONStore class."""
    
    @pytest.fixture
    def sample_results(self):
        """Sample evaluation results for testing."""
        return {
            "model_id": "test-model",
            "timestamp": "2024-01-15T10:30:00",
            "test_results": [
                {"input": "What is 2+2?", "expected": "4", "actual": "4", "score": 1.0},
                {"input": "What is 3+3?", "expected": "6", "actual": "6", "score": 1.0}
            ],
            "aggregate_metrics": {
                "average_accuracy": 1.0,
                "total_cost": 0.004,
                "total_time": 1.2
            },
            "use_case_requirements": {
                "domain": "math",
                "required_capabilities": ["reasoning"]
            }
        }
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    def test_json_store_initialization(self, temp_dir):
        """Test JSONStore initialization with various parameters."""
        # Basic initialization
        store = JSONStore("test_results.json", temp_dir)
        assert store.filename == "test_results.json"
        assert store.storage_dir == Path(temp_dir)
        assert store.filepath.exists()
    
    def test_save_and_load_evaluation_result(self, temp_dir, sample_results):
        """Test saving and loading evaluation results."""
        store = JSONStore("test_results.json", temp_dir)
        
        # Save results
        store.save_evaluation_result(sample_results)
        
        # Load results
        loaded_results = store.load_evaluation_results()
        assert len(loaded_results) == 1
        assert loaded_results[0]["model_id"] == "test-model"
        assert loaded_results[0]["aggregate_metrics"]["average_accuracy"] == 1.0
    
    def test_save_multiple_results(self, temp_dir, sample_results):
        """Test saving multiple evaluation results."""
        store = JSONStore("test_results.json", temp_dir)
        
        # Save first result
        store.save_evaluation_result(sample_results)
        
        # Save second result
        sample_results2 = sample_results.copy()
        sample_results2["model_id"] = "test-model-2"
        store.save_evaluation_result(sample_results2)
        
        # Load and verify
        loaded_results = store.load_evaluation_results()
        assert len(loaded_results) == 2
        assert loaded_results[0]["model_id"] == "test-model"
        assert loaded_results[1]["model_id"] == "test-model-2"
    
    def test_get_evaluation_by_id(self, temp_dir, sample_results):
        """Test getting evaluation by ID."""
        store = JSONStore("test_results.json", temp_dir)
        store.save_evaluation_result(sample_results)
        
        # Get by ID
        result = store.get_evaluation_by_id(1)
        assert result is not None
        assert result["model_id"] == "test-model"
        
        # Test non-existent ID
        result = store.get_evaluation_by_id(999)
        assert result is None
    
    def test_get_evaluations_by_model(self, temp_dir, sample_results):
        """Test filtering results by model ID."""
        store = JSONStore("test_results.json", temp_dir)
        
        # Save multiple results with different models
        store.save_evaluation_result(sample_results)
        
        sample_results2 = sample_results.copy()
        sample_results2["model_id"] = "different-model"
        store.save_evaluation_result(sample_results2)
        
        # Filter by model_id
        filtered = store.get_evaluations_by_model("test-model")
        assert len(filtered) == 1
        assert filtered[0]["model_id"] == "test-model"
    
    def test_delete_evaluation(self, temp_dir, sample_results):
        """Test deleting evaluations."""
        store = JSONStore("test_results.json", temp_dir)
        store.save_evaluation_result(sample_results)
        
        # Verify evaluation exists
        results = store.load_evaluation_results()
        assert len(results) == 1
        
        # Delete evaluation
        success = store.delete_evaluation(1)
        assert success is True
        
        # Verify deletion
        results = store.load_evaluation_results()
        assert len(results) == 0
        
        # Test deleting non-existent evaluation
        success = store.delete_evaluation(999)
        assert success is False
    
    def test_clear_all_evaluations(self, temp_dir, sample_results):
        """Test clearing all evaluations."""
        store = JSONStore("test_results.json", temp_dir)
        
        # Save multiple results
        store.save_evaluation_result(sample_results)
        store.save_evaluation_result(sample_results)
        
        # Verify results exist
        results = store.load_evaluation_results()
        assert len(results) == 2
        
        # Clear all
        store.clear_all_evaluations()
        
        # Verify cleared
        results = store.load_evaluation_results()
        assert len(results) == 0
    
    def test_get_metadata(self, temp_dir, sample_results):
        """Test metadata functionality."""
        store = JSONStore("test_results.json", temp_dir)
        
        # Save some results
        store.save_evaluation_result(sample_results)
        
        # Get metadata
        metadata = store.get_metadata()
        assert "created_at" in metadata
        assert "version" in metadata
        assert metadata["total_evaluations"] == 1
    
    def test_export_to_file(self, temp_dir, sample_results):
        """Test exporting to file."""
        store = JSONStore("test_results.json", temp_dir)
        store.save_evaluation_result(sample_results)
        
        # Export to file
        export_path = os.path.join(temp_dir, "export.json")
        store.export_to_file(export_path)
        
        # Verify export
        assert os.path.exists(export_path)
        with open(export_path, 'r', encoding='utf-8') as f:
            exported_data = json.load(f)
        assert "evaluations" in exported_data
        assert len(exported_data["evaluations"]) == 1
    
    def test_backup(self, temp_dir, sample_results):
        """Test backup functionality."""
        store = JSONStore("test_results.json", temp_dir)
        store.save_evaluation_result(sample_results)
        
        # Create backup
        backup_path = store.backup()
        
        # Verify backup exists and has correct content
        assert os.path.exists(backup_path)
        with open(backup_path, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        assert "evaluations" in backup_data
        assert len(backup_data["evaluations"]) == 1
    
    def test_error_handling(self, temp_dir):
        """Test error handling for various edge cases."""
        store = JSONStore("test_results.json", temp_dir)
        
        # Test loading from empty file (should return empty list)
        results = store.load_evaluation_results()
        assert results == []
        
        # Test getting non-existent evaluation
        result = store.get_evaluation_by_id(999)
        assert result is None
        
        # Test getting evaluations for non-existent model
        model_results = store.get_evaluations_by_model("non-existent")
        assert model_results == []


class TestDBStore:
    """Comprehensive tests for DBStore class."""
    
    @pytest.fixture
    def sample_results(self):
        """Sample evaluation results for testing."""
        return {
            "model_id": "test-model",
            "timestamp": "2024-01-15T10:30:00",
            "test_results": [
                {"input": "What is 2+2?", "expected": "4", "actual": "4", "score": 1.0},
                {"input": "What is 3+3?", "expected": "6", "actual": "6", "score": 1.0}
            ],
            "aggregate_metrics": {
                "average_accuracy": 1.0,
                "total_cost": 0.004,
                "total_time": 1.2
            },
            "use_case_requirements": {
                "domain": "math",
                "required_capabilities": ["reasoning"]
            }
        }
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    def test_db_store_initialization(self, temp_dir):
        """Test DBStore initialization and table creation."""
        store = DBStore("test.db", temp_dir)
        
        # Verify database file was created
        db_path = Path(temp_dir) / "test.db"
        assert db_path.exists()
        
        # Verify table was created
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='evaluations'")
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
        assert result[0] == "evaluations"
    
    def test_save_and_load_evaluation_result(self, temp_dir, sample_results):
        """Test saving and loading evaluation results."""
        store = DBStore("test.db", temp_dir)
        
        # Save results
        eval_id = store.save_evaluation_result(sample_results)
        assert eval_id is not None
        
        # Load results
        loaded_results = store.load_evaluation_results()
        assert len(loaded_results) == 1
        assert loaded_results[0]["model_id"] == "test-model"
        assert loaded_results[0]["aggregate_metrics"]["average_accuracy"] == 1.0
    
    def test_get_evaluation_by_id(self, temp_dir, sample_results):
        """Test getting evaluation by ID."""
        store = DBStore("test.db", temp_dir)
        eval_id = store.save_evaluation_result(sample_results)
        
        # Get by ID
        result = store.get_evaluation_by_id(eval_id)
        assert result is not None
        assert result["model_id"] == "test-model"
        
        # Test non-existent ID
        result = store.get_evaluation_by_id("non-existent")
        assert result is None
    
    def test_get_evaluations_by_model(self, temp_dir, sample_results):
        """Test querying evaluations by model."""
        store = DBStore("test.db", temp_dir)
        
        # Save results for different models
        store.save_evaluation_result(sample_results)
        
        sample_results2 = sample_results.copy()
        sample_results2["model_id"] = "different-model"
        store.save_evaluation_result(sample_results2)
        
        # Query by model
        model_results = store.get_evaluations_by_model("test-model")
        assert len(model_results) == 1
        assert model_results[0]["model_id"] == "test-model"
    
    def test_delete_evaluation(self, temp_dir, sample_results):
        """Test deleting evaluations."""
        store = DBStore("test.db", temp_dir)
        eval_id = store.save_evaluation_result(sample_results)
        
        # Verify evaluation exists
        result = store.get_evaluation_by_id(eval_id)
        assert result is not None
        
        # Delete evaluation
        success = store.delete_evaluation(eval_id)
        assert success is True
        
        # Verify deletion
        result = store.get_evaluation_by_id(eval_id)
        assert result is None
        
        # Test deleting non-existent evaluation
        success = store.delete_evaluation("non-existent")
        assert success is False
    
    def test_clear_all_evaluations(self, temp_dir, sample_results):
        """Test clearing all evaluations."""
        store = DBStore("test.db", temp_dir)
        
        # Save multiple results
        store.save_evaluation_result(sample_results)
        store.save_evaluation_result(sample_results)
        
        # Verify results exist
        count = store.get_evaluation_count()
        assert count == 2
        
        # Clear all
        store.clear_all_evaluations()
        
        # Verify cleared
        count = store.get_evaluation_count()
        assert count == 0
    
    def test_get_evaluation_count(self, temp_dir, sample_results):
        """Test getting evaluation count."""
        store = DBStore("test.db", temp_dir)
        
        # Initially should be 0
        count = store.get_evaluation_count()
        assert count == 0
        
        # Add some evaluations
        store.save_evaluation_result(sample_results)
        store.save_evaluation_result(sample_results)
        
        # Check count
        count = store.get_evaluation_count()
        assert count == 2
    
    def test_get_model_statistics(self, temp_dir, sample_results):
        """Test getting model statistics."""
        store = DBStore("test.db", temp_dir)
        
        # Save results for different models
        store.save_evaluation_result(sample_results)
        
        sample_results2 = sample_results.copy()
        sample_results2["model_id"] = "different-model"
        store.save_evaluation_result(sample_results2)
        
        # Get statistics
        stats = store.get_model_statistics()
        assert "test-model" in stats
        assert "different-model" in stats
        assert stats["test-model"] == 1
        assert stats["different-model"] == 1
    
    def test_search_evaluations(self, temp_dir, sample_results):
        """Test advanced search functionality."""
        store = DBStore("test.db", temp_dir)
        
        # Save multiple results
        store.save_evaluation_result(sample_results)
        
        sample_results2 = sample_results.copy()
        sample_results2["model_id"] = "model-2"
        store.save_evaluation_result(sample_results2)
        
        # Search with no filters (should return all)
        all_results = store.search_evaluations()
        assert len(all_results) == 2
        
        # Search with model filter
        model_results = store.search_evaluations(model_id="test-model")
        assert len(model_results) == 1
        assert model_results[0]["model_id"] == "test-model"
    
    def test_backup_database(self, temp_dir, sample_results):
        """Test database backup functionality."""
        store = DBStore("test.db", temp_dir)
        store.save_evaluation_result(sample_results)
        
        # Create backup
        backup_path = store.backup_database()
        
        # Verify backup exists and has correct content
        assert os.path.exists(backup_path)
        
        backup_store = DBStore(os.path.basename(backup_path), os.path.dirname(backup_path))
        backup_results = backup_store.load_evaluation_results()
        assert len(backup_results) == 1
        assert backup_results[0]["model_id"] == "test-model"
    
    def test_metadata_operations(self, temp_dir):
        """Test metadata get and set operations."""
        store = DBStore("test.db", temp_dir)
        
        # Set metadata
        store.set_metadata("test_key", "test_value")
        
        # Get specific metadata
        value = store.get_metadata("test_key")
        assert value == "test_value"
        
        # Get all metadata
        all_metadata = store.get_metadata()
        assert isinstance(all_metadata, dict)
        assert "test_key" in all_metadata
        assert all_metadata["test_key"] == "test_value"
        
        # Get non-existent metadata
        non_existent = store.get_metadata("non_existent")
        assert non_existent is None
    
    def test_close_connection(self, temp_dir):
        """Test closing database connection."""
        store = DBStore("test.db", temp_dir)
        
        # Close connection
        store.close()
        
        # Should still work (creates new connection)
        count = store.get_evaluation_count()
        assert count == 0
    
    def test_connection_error_handling(self):
        """Test database connection error handling."""
        # Test that invalid storage path raises an error during initialization
        with pytest.raises((FileNotFoundError, RuntimeError)):
            DBStore("test.db", "/invalid/path")


class TestPersistenceManager:
    """Tests for PersistenceManager orchestration."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    def test_persistence_manager_initialization(self, temp_dir):
        """Test PersistenceManager initialization."""
        manager = PersistenceManager(storage_dir=temp_dir)
        assert manager.storage_dir == temp_dir
    
    def test_save_and_load_operations(self, temp_dir):
        """Test basic save and load operations."""
        manager = PersistenceManager(storage_dir=temp_dir)
        
        test_data = {"key": "value", "number": 42}
        
        # Save data
        manager.save("test.json", test_data)
        
        # Load data
        loaded_data = manager.load("test.json")
        assert loaded_data == test_data
    
    def test_delete_operation(self, temp_dir):
        """Test delete operation."""
        manager = PersistenceManager(storage_dir=temp_dir)
        
        test_data = {"key": "value"}
        manager.save("test.json", test_data)
        
        # Verify file exists
        assert manager.load("test.json") == test_data
        
        # Delete file
        manager.delete("test.json")
        
        # Verify file is deleted
        assert manager.load("test.json") is None
    
    def test_file_operations_with_subdirectories(self, temp_dir):
        """Test operations with subdirectories."""
        manager = PersistenceManager(storage_dir=temp_dir)
        
        test_data = {"key": "value"}
        
        # Create subdirectory first
        os.makedirs(os.path.join(temp_dir, "subdir"), exist_ok=True)
        
        # Save in subdirectory
        manager.save("subdir/test.json", test_data)
        
        # Load from subdirectory
        loaded_data = manager.load("subdir/test.json")
        assert loaded_data == test_data
    
    def test_error_handling(self, temp_dir):
        """Test error handling for various edge cases."""
        manager = PersistenceManager(storage_dir=temp_dir)
        
        # Test loading non-existent file
        result = manager.load("non_existent.json")
        assert result is None
        
        # Test deleting non-existent file
        manager.delete("non_existent.json")  # Should not raise error


if __name__ == "__main__":
    pytest.main([__file__])