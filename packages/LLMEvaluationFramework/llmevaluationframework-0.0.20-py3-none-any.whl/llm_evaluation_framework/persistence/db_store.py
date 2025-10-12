"""
Database Store implementation for LLM Evaluation Framework.
Provides SQLite-based persistence for evaluation results and configurations.
"""

import sqlite3
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pathlib import Path


class DBStore:
    """
    SQLite-based storage implementation for evaluation results and configurations.
    
    This class provides methods to save, load, and manage evaluation data
    in a SQLite database with proper schema management and error handling.
    """
    
    def __init__(self, db_name: str = "evaluation_results.db", storage_dir: str = "data"):
        """
        Initialize DBStore with database name and storage directory.
        
        Args:
            db_name (str): Name of the SQLite database file
            storage_dir (str): Directory to store the database file
        """
        self.db_name = db_name
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.db_path = self.storage_dir / db_name
        
        # Initialize database schema
        self._initialize_database()
    
    def _initialize_database(self) -> None:
        """Initialize the database schema with required tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create evaluations table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS evaluations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        evaluation_id TEXT UNIQUE NOT NULL,
                        model_id TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        aggregate_metrics TEXT,  -- JSON string
                        test_results TEXT,       -- JSON string
                        model_info TEXT,         -- JSON string
                        use_case_requirements TEXT,  -- JSON string
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create metadata table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS metadata (
                        key TEXT PRIMARY KEY,
                        value TEXT,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Initialize metadata
                cursor.execute("""
                    INSERT OR IGNORE INTO metadata (key, value) 
                    VALUES ('schema_version', '1.0')
                """)
                cursor.execute("""
                    INSERT OR IGNORE INTO metadata (key, value) 
                    VALUES ('created_at', ?)
                """, (datetime.now().isoformat(),))
                
                conn.commit()
                
        except Exception as e:
            raise RuntimeError(f"Failed to initialize database: {str(e)}") from e
    
    def save_evaluation_result(self, result: Dict[str, Any]) -> str:
        """
        Save an evaluation result to the database.
        
        Args:
            result (Dict[str, Any]): Evaluation result dictionary
            
        Returns:
            str: The evaluation_id of the saved result
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Generate evaluation ID if not present
                evaluation_id = result.get("evaluation_id", f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}")
                
                cursor.execute("""
                    INSERT OR REPLACE INTO evaluations 
                    (evaluation_id, model_id, timestamp, aggregate_metrics, test_results, model_info, use_case_requirements)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    evaluation_id,
                    result.get("model_id", "unknown"),
                    result.get("timestamp", datetime.now().isoformat()),
                    json.dumps(result.get("aggregate_metrics", {})),
                    json.dumps(result.get("test_results", [])),
                    json.dumps(result.get("model_info", {})),
                    json.dumps(result.get("use_case_requirements", {}))
                ))
                
                conn.commit()
                return evaluation_id
                
        except Exception as e:
            raise RuntimeError(f"Failed to save evaluation result: {str(e)}") from e
    
    def load_evaluation_results(self) -> List[Dict[str, Any]]:
        """
        Load all evaluation results from the database.
        
        Returns:
            List[Dict[str, Any]]: List of evaluation results
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT evaluation_id, model_id, timestamp, aggregate_metrics, 
                           test_results, model_info, use_case_requirements, created_at
                    FROM evaluations 
                    ORDER BY created_at DESC
                """)
                
                results = []
                for row in cursor.fetchall():
                    result = {
                        "evaluation_id": row[0],
                        "model_id": row[1],
                        "timestamp": row[2],
                        "aggregate_metrics": json.loads(row[3]) if row[3] else {},
                        "test_results": json.loads(row[4]) if row[4] else [],
                        "model_info": json.loads(row[5]) if row[5] else {},
                        "use_case_requirements": json.loads(row[6]) if row[6] else {},
                        "created_at": row[7]
                    }
                    results.append(result)
                
                return results
                
        except Exception as e:
            raise RuntimeError(f"Failed to load evaluation results: {str(e)}") from e
    
    def get_evaluation_by_id(self, evaluation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific evaluation by its ID.
        
        Args:
            evaluation_id (str): ID of the evaluation to retrieve
            
        Returns:
            Optional[Dict[str, Any]]: Evaluation result if found, None otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT evaluation_id, model_id, timestamp, aggregate_metrics, 
                           test_results, model_info, use_case_requirements, created_at
                    FROM evaluations 
                    WHERE evaluation_id = ?
                """, (evaluation_id,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        "evaluation_id": row[0],
                        "model_id": row[1],
                        "timestamp": row[2],
                        "aggregate_metrics": json.loads(row[3]) if row[3] else {},
                        "test_results": json.loads(row[4]) if row[4] else [],
                        "model_info": json.loads(row[5]) if row[5] else {},
                        "use_case_requirements": json.loads(row[6]) if row[6] else {},
                        "created_at": row[7]
                    }
                return None
                
        except Exception as e:
            raise RuntimeError(f"Failed to get evaluation by ID: {str(e)}") from e
    
    def get_evaluations_by_model(self, model_id: str) -> List[Dict[str, Any]]:
        """
        Get all evaluations for a specific model.
        
        Args:
            model_id (str): ID of the model to filter by
            
        Returns:
            List[Dict[str, Any]]: List of evaluation results for the model
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT evaluation_id, model_id, timestamp, aggregate_metrics, 
                           test_results, model_info, use_case_requirements, created_at
                    FROM evaluations 
                    WHERE model_id = ?
                    ORDER BY created_at DESC
                """, (model_id,))
                
                results = []
                for row in cursor.fetchall():
                    result = {
                        "evaluation_id": row[0],
                        "model_id": row[1],
                        "timestamp": row[2],
                        "aggregate_metrics": json.loads(row[3]) if row[3] else {},
                        "test_results": json.loads(row[4]) if row[4] else [],
                        "model_info": json.loads(row[5]) if row[5] else {},
                        "use_case_requirements": json.loads(row[6]) if row[6] else {},
                        "created_at": row[7]
                    }
                    results.append(result)
                
                return results
                
        except Exception as e:
            raise RuntimeError(f"Failed to get evaluations by model: {str(e)}") from e
    
    def delete_evaluation(self, evaluation_id: str) -> bool:
        """
        Delete an evaluation by its ID.
        
        Args:
            evaluation_id (str): ID of the evaluation to delete
            
        Returns:
            bool: True if deletion was successful, False if evaluation not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM evaluations WHERE evaluation_id = ?", (evaluation_id,))
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            raise RuntimeError(f"Failed to delete evaluation: {str(e)}") from e
    
    def clear_all_evaluations(self) -> None:
        """Clear all evaluation results from the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM evaluations")
                conn.commit()
                
        except Exception as e:
            raise RuntimeError(f"Failed to clear evaluations: {str(e)}") from e
    
    def get_evaluation_count(self) -> int:
        """
        Get the total number of evaluations in the database.
        
        Returns:
            int: Number of evaluations
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM evaluations")
                return cursor.fetchone()[0]
                
        except Exception as e:
            raise RuntimeError(f"Failed to get evaluation count: {str(e)}") from e
    
    def get_model_statistics(self) -> Dict[str, int]:
        """
        Get statistics about evaluations per model.
        
        Returns:
            Dict[str, int]: Dictionary mapping model_id to evaluation count
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT model_id, COUNT(*) 
                    FROM evaluations 
                    GROUP BY model_id
                """)
                
                return dict(cursor.fetchall())
                
        except Exception as e:
            raise RuntimeError(f"Failed to get model statistics: {str(e)}") from e
    
    def search_evaluations(self, 
                          model_id: Optional[str] = None,
                          start_date: Optional[str] = None,
                          end_date: Optional[str] = None,
                          limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search evaluations with optional filters.
        
        Args:
            model_id (Optional[str]): Filter by model ID
            start_date (Optional[str]): Filter evaluations after this date (ISO format)
            end_date (Optional[str]): Filter evaluations before this date (ISO format)
            limit (Optional[int]): Maximum number of results to return
            
        Returns:
            List[Dict[str, Any]]: List of matching evaluation results
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT evaluation_id, model_id, timestamp, aggregate_metrics, 
                           test_results, model_info, use_case_requirements, created_at
                    FROM evaluations 
                    WHERE 1=1
                """
                params = []
                
                if model_id:
                    query += " AND model_id = ?"
                    params.append(model_id)
                
                if start_date:
                    query += " AND created_at >= ?"
                    params.append(start_date)
                
                if end_date:
                    query += " AND created_at <= ?"
                    params.append(end_date)
                
                query += " ORDER BY created_at DESC"
                
                if limit:
                    query += " LIMIT ?"
                    params.append(limit)
                
                cursor.execute(query, params)
                
                results = []
                for row in cursor.fetchall():
                    result = {
                        "evaluation_id": row[0],
                        "model_id": row[1],
                        "timestamp": row[2],
                        "aggregate_metrics": json.loads(row[3]) if row[3] else {},
                        "test_results": json.loads(row[4]) if row[4] else [],
                        "model_info": json.loads(row[5]) if row[5] else {},
                        "use_case_requirements": json.loads(row[6]) if row[6] else {},
                        "created_at": row[7]
                    }
                    results.append(result)
                
                return results
                
        except Exception as e:
            raise RuntimeError(f"Failed to search evaluations: {str(e)}") from e
    
    def backup_database(self, backup_path: Optional[str] = None) -> str:
        """
        Create a backup of the database.
        
        Args:
            backup_path (Optional[str]): Path for the backup file
            
        Returns:
            str: Path to the backup file
        """
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = str(self.storage_dir / f"{self.db_name}.backup_{timestamp}")
        
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            return backup_path
            
        except Exception as e:
            raise RuntimeError(f"Failed to create database backup: {str(e)}") from e
    
    def get_metadata(self, key: Optional[str] = None) -> Union[str, Dict[str, str], None]:
        """
        Get metadata from the database.
        
        Args:
            key (Optional[str]): Specific metadata key to retrieve
            
        Returns:
            Union[str, Dict[str, str], None]: Metadata value(s)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if key:
                    cursor.execute("SELECT value FROM metadata WHERE key = ?", (key,))
                    row = cursor.fetchone()
                    return row[0] if row else None
                else:
                    cursor.execute("SELECT key, value FROM metadata")
                    return dict(cursor.fetchall())
                    
        except Exception as e:
            raise RuntimeError(f"Failed to get metadata: {str(e)}") from e
    
    def set_metadata(self, key: str, value: str) -> None:
        """
        Set metadata in the database.
        
        Args:
            key (str): Metadata key
            value (str): Metadata value
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO metadata (key, value, updated_at) 
                    VALUES (?, ?, ?)
                """, (key, value, datetime.now().isoformat()))
                conn.commit()
                
        except Exception as e:
            raise RuntimeError(f"Failed to set metadata: {str(e)}") from e
    
    def close(self) -> None:
        """Close the database connection (for compatibility)."""
        # SQLite connections are automatically closed when using context managers
    
    def __str__(self) -> str:
        """String representation of the DBStore."""
        count = self.get_evaluation_count()
        return f"DBStore(database={self.db_path}, evaluations={count})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the DBStore."""
        return f"DBStore(db_name='{self.db_name}', storage_dir='{self.storage_dir}')"
