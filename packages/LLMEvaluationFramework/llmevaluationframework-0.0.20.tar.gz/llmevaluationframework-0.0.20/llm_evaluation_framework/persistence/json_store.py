"""
JSON Store implementation for LLM Evaluation Framework.
Provides JSON-based persistence for evaluation results and configurations.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path


class JSONStore:
    """
    JSON-based storage implementation for evaluation results and configurations.
    
    This class provides methods to save, load, and manage evaluation data
    in JSON format with proper error handling and data validation.
    """
    
    def __init__(self, filename: str = "evaluation_results.json", storage_dir: str = "data"):
        """
        Initialize JSONStore with filename and storage directory.
        
        Args:
            filename (str): Name of the JSON file to use for storage
            storage_dir (str): Directory to store the JSON files
        """
        self.filename = filename
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.filepath = self.storage_dir / filename
        
        # Initialize empty file if it doesn't exist
        if not self.filepath.exists():
            self._initialize_file()
    
    def _initialize_file(self) -> None:
        """Initialize an empty JSON file with basic structure."""
        initial_data = {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "version": "1.0",
                "total_evaluations": 0
            },
            "evaluations": []
        }
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(initial_data, f, indent=2, ensure_ascii=False)
    
    def save_evaluation_result(self, result: Dict[str, Any]) -> None:
        """
        Save an evaluation result to the JSON store.
        
        Args:
            result (Dict[str, Any]): Evaluation result dictionary
        """
        try:
            data = self._load_all_data()
            
            # Add timestamp to result
            result["timestamp"] = datetime.now().isoformat()
            result["evaluation_id"] = len(data["evaluations"]) + 1
            
            # Add to evaluations
            data["evaluations"].append(result)
            data["metadata"]["total_evaluations"] = len(data["evaluations"])
            data["metadata"]["last_updated"] = datetime.now().isoformat()
            
            # Save back to file
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            raise RuntimeError(f"Failed to save evaluation result: {str(e)}") from e
    
    def load_evaluation_results(self) -> List[Dict[str, Any]]:
        """
        Load all evaluation results from the JSON store.
        
        Returns:
            List[Dict[str, Any]]: List of evaluation results
        """
        try:
            data = self._load_all_data()
            return data.get("evaluations", [])
        except Exception as e:
            raise RuntimeError(f"Failed to load evaluation results: {str(e)}") from e
    
    def get_evaluation_by_id(self, evaluation_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific evaluation by its ID.
        
        Args:
            evaluation_id (int): ID of the evaluation to retrieve
            
        Returns:
            Optional[Dict[str, Any]]: Evaluation result if found, None otherwise
        """
        results = self.load_evaluation_results()
        for result in results:
            if result.get("evaluation_id") == evaluation_id:
                return result
        return None
    
    def get_evaluations_by_model(self, model_id: str) -> List[Dict[str, Any]]:
        """
        Get all evaluations for a specific model.
        
        Args:
            model_id (str): ID of the model to filter by
            
        Returns:
            List[Dict[str, Any]]: List of evaluation results for the model
        """
        results = self.load_evaluation_results()
        return [result for result in results if result.get("model_id") == model_id]
    
    def delete_evaluation(self, evaluation_id: int) -> bool:
        """
        Delete an evaluation by its ID.
        
        Args:
            evaluation_id (int): ID of the evaluation to delete
            
        Returns:
            bool: True if deletion was successful, False if evaluation not found
        """
        try:
            data = self._load_all_data()
            evaluations = data.get("evaluations", [])
            
            # Find and remove the evaluation
            for i, evaluation in enumerate(evaluations):
                if evaluation.get("evaluation_id") == evaluation_id:
                    evaluations.pop(i)
                    data["metadata"]["total_evaluations"] = len(evaluations)
                    data["metadata"]["last_updated"] = datetime.now().isoformat()
                    
                    # Save back to file
                    with open(self.filepath, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    return True
            
            return False  # Evaluation not found
            
        except Exception as e:
            raise RuntimeError(f"Failed to delete evaluation: {str(e)}") from e
    
    def clear_all_evaluations(self) -> None:
        """Clear all evaluation results from the store."""
        try:
            data = self._load_all_data()
            data["evaluations"] = []
            data["metadata"]["total_evaluations"] = 0
            data["metadata"]["last_updated"] = datetime.now().isoformat()
            
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            raise RuntimeError(f"Failed to clear evaluations: {str(e)}") from e
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the stored evaluations.
        
        Returns:
            Dict[str, Any]: Metadata dictionary
        """
        data = self._load_all_data()
        return data.get("metadata", {})
    
    def export_to_file(self, export_path: str) -> None:
        """
        Export all data to a different file.
        
        Args:
            export_path (str): Path to export the data to
        """
        try:
            data = self._load_all_data()
            export_file = Path(export_path)
            export_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            raise RuntimeError(f"Failed to export data: {str(e)}") from e
    
    def _load_all_data(self) -> Dict[str, Any]:
        """
        Load all data from the JSON file.
        
        Returns:
            Dict[str, Any]: Complete data structure
        """
        try:
            if not self.filepath.exists():
                self._initialize_file()
            
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON file format: {str(e)}") from e
        except Exception as e:
            raise RuntimeError(f"Failed to load data: {str(e)}") from e
    
    def backup(self, backup_suffix: str = None) -> str:
        """
        Create a backup of the current JSON file.
        
        Args:
            backup_suffix (str): Optional suffix for backup filename
            
        Returns:
            str: Path to the backup file
        """
        if backup_suffix is None:
            backup_suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        backup_filename = f"{self.filename}.backup_{backup_suffix}"
        backup_path = self.storage_dir / backup_filename
        
        try:
            if self.filepath.exists():
                import shutil
                shutil.copy2(self.filepath, backup_path)
            return str(backup_path)
        except Exception as e:
            raise RuntimeError(f"Failed to create backup: {str(e)}") from e
    
    def __str__(self) -> str:
        """String representation of the JSONStore."""
        metadata = self.get_metadata()
        total_evaluations = metadata.get("total_evaluations", 0)
        return f"JSONStore(file={self.filepath}, evaluations={total_evaluations})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the JSONStore."""
        return f"JSONStore(filename='{self.filename}', storage_dir='{self.storage_dir}')"
