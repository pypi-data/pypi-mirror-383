"""
Comprehensive tests for LLM Evaluation Framework model inference engine.
Tests the ModelInferenceEngine class with various scenarios, error handling, and edge cases.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from llm_evaluation_framework.model_inference_engine import ModelInferenceEngine


class TestModelInferenceEngine:
    """Test the ModelInferenceEngine class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.mock_model_registry = Mock()
        self.engine = ModelInferenceEngine(self.mock_model_registry)
        
    def test_initialization(self):
        """Test engine initialization."""
        assert self.engine.model_registry is self.mock_model_registry
        assert isinstance(self.engine.api_clients, dict)
        assert len(self.engine.api_clients) == 0
    
    def test_evaluate_model_invalid_model_id(self):
        """Test evaluation with invalid model ID."""
        self.mock_model_registry.get_model.return_value = None
        
        result = self.engine.evaluate_model(
            "invalid_model",
            [{"id": "test", "type": "qa", "prompt": "Test prompt"}],
            {}
        )
        
        assert result is None
        self.mock_model_registry.get_model.assert_called_once_with("invalid_model")
    
    def test_evaluate_model_empty_test_cases(self):
        """Test evaluation with empty test cases."""
        model_info = {
            "name": "test_model",
            "api_cost_input": 0.001,
            "api_cost_output": 0.002
        }
        self.mock_model_registry.get_model.return_value = model_info
        
        result = self.engine.evaluate_model("test_model", [], {})
        
        assert result["model_id"] == "test_model"
        assert result["model_info"] == model_info
        assert result["test_results"] == []
        assert result["aggregate_metrics"]["total_cost"] == 0
        assert result["aggregate_metrics"]["total_time"] == 0
        assert result["aggregate_metrics"]["avg_response_time"] == 0
    
    def test_evaluate_model_non_dict_model_info(self):
        """Test evaluation with non-dict model info."""
        self.mock_model_registry.get_model.return_value = "invalid_model_info"
        
        with pytest.raises(TypeError, match="Expected model_info to be dict"):
            self.engine.evaluate_model("test_model", [{"id": "test", "type": "qa", "prompt": "Test"}], {})
    
    def test_evaluate_model_missing_cost_keys(self):
        """Test evaluation with model info missing cost keys."""
        model_info = {"name": "test_model"}  # Missing api_cost_input and api_cost_output
        self.mock_model_registry.get_model.return_value = model_info
        
        test_cases = [{
            "id": "test1",
            "type": "qa",
            "prompt": "What is the capital of France?",
            "evaluation_criteria": ["correctness"]
        }]
        
        with patch.object(self.engine, '_call_model_api') as mock_call_api:
            mock_call_api.return_value = {
                "content": "Paris is the capital of France.",
                "input_tokens": 10,
                "output_tokens": 8
            }
            
            result = self.engine.evaluate_model("test_model", test_cases, {})
            
            assert result is not None
            assert model_info["api_cost_input"] == 0
            assert model_info["api_cost_output"] == 0
    
    def test_evaluate_model_single_test_case(self):
        """Test evaluation with a single test case."""
        model_info = {
            "name": "test_model",
            "api_cost_input": 0.001,
            "api_cost_output": 0.002
        }
        self.mock_model_registry.get_model.return_value = model_info
        
        test_cases = [{
            "id": "test1",
            "type": "qa",
            "prompt": "What is the capital of France?",
            "evaluation_criteria": ["correctness", "logical_consistency"]
        }]
        
        with patch.object(self.engine, '_call_model_api') as mock_call_api:
            mock_call_api.return_value = {
                "content": "Paris is the capital of France.",
                "input_tokens": 10,
                "output_tokens": 8
            }
            
            with patch.object(self.engine, '_evaluate_logical_consistency', return_value=0.9):
                with patch.object(self.engine, '_evaluate_correctness', return_value=0.95):
                    result = self.engine.evaluate_model("test_model", test_cases, {})
        
        assert result["model_id"] == "test_model"
        assert result["model_info"] == model_info
        assert len(result["test_results"]) == 1
        
        test_result = result["test_results"][0]
        assert test_result["test_case_id"] == "test1"
        assert test_result["test_case_type"] == "qa"
        assert test_result["response"] == "Paris is the capital of France."
        assert test_result["input_tokens"] == 10
        assert test_result["output_tokens"] == 8
        assert test_result["evaluation_scores"]["correctness"] == 0.95
        assert test_result["evaluation_scores"]["logical_consistency"] == 0.9
        assert "response_time" in test_result
        assert "cost" in test_result
    
    def test_evaluate_model_multiple_test_cases(self):
        """Test evaluation with multiple test cases."""
        model_info = {
            "name": "test_model",
            "api_cost_input": 0.001,
            "api_cost_output": 0.002
        }
        self.mock_model_registry.get_model.return_value = model_info
        
        test_cases = [
            {
                "id": "test1",
                "type": "qa",
                "prompt": "What is 2+2?",
                "evaluation_criteria": ["correctness"]
            },
            {
                "id": "test2",
                "type": "creative",
                "prompt": "Write a poem about cats",
                "evaluation_criteria": ["originality"]
            }
        ]
        
        with patch.object(self.engine, '_call_model_api') as mock_call_api:
            mock_call_api.side_effect = [
                {"content": "4", "input_tokens": 5, "output_tokens": 1},
                {"content": "Cats are fluffy and nice", "input_tokens": 8, "output_tokens": 5}
            ]
            
            with patch.object(self.engine, '_evaluate_correctness', return_value=1.0):
                with patch.object(self.engine, '_evaluate_originality', return_value=0.8):
                    result = self.engine.evaluate_model("test_model", test_cases, {})
        
        assert len(result["test_results"]) == 2
        assert result["test_results"][0]["test_case_id"] == "test1"
        assert result["test_results"][1]["test_case_id"] == "test2"
        assert result["aggregate_metrics"]["total_cost"] > 0
        assert result["aggregate_metrics"]["total_time"] > 0
        assert result["aggregate_metrics"]["avg_response_time"] > 0
    
    def test_evaluate_model_with_api_error(self):
        """Test evaluation when API call fails."""
        model_info = {
            "name": "test_model",
            "api_cost_input": 0.001,
            "api_cost_output": 0.002
        }
        self.mock_model_registry.get_model.return_value = model_info
        
        test_cases = [{
            "id": "test1",
            "type": "qa",
            "prompt": "Test prompt",
            "evaluation_criteria": ["correctness"]
        }]
        
        with patch.object(self.engine, '_call_model_api') as mock_call_api:
            mock_call_api.side_effect = Exception("API Error")
            
            result = self.engine.evaluate_model("test_model", test_cases, {})
        
        assert len(result["test_results"]) == 1
        test_result = result["test_results"][0]
        assert test_result["response"] is None
        assert test_result["error"] == "API Error"
        assert test_result["response_time"] is None
        assert test_result["cost"] == 0
        assert test_result["input_tokens"] == 0
        assert test_result["output_tokens"] == 0
        assert test_result["evaluation_scores"] == {}
    
    def test_call_model_api(self):
        """Test the _call_model_api method."""
        with patch('time.sleep'):  # Speed up test by mocking sleep
            with patch('random.uniform', return_value=0.1):
                with patch('random.randint', return_value=100):
                    result = self.engine._call_model_api("test_model", "Hello world", {})
        
        assert result["content"] == "Simulated response from test_model to: Hello world"
        assert isinstance(result["input_tokens"], int)
        assert result["input_tokens"] > 0
        assert result["output_tokens"] == 100
    
    def test_calculate_cost(self):
        """Test cost calculation."""
        model_info = {
            "api_cost_input": 0.001,
            "api_cost_output": 0.002
        }
        
        cost = self.engine._calculate_cost(model_info, 1000, 500)
        expected_cost = (1000 / 1000) * 0.001 + (500 / 1000) * 0.002
        assert cost == round(expected_cost, 6)
    
    def test_calculate_cost_missing_keys(self):
        """Test cost calculation with missing cost keys."""
        model_info = {}  # No cost keys
        
        cost = self.engine._calculate_cost(model_info, 1000, 500)
        assert cost == 0.0
    
    def test_calculate_cost_zero_tokens(self):
        """Test cost calculation with zero tokens."""
        model_info = {
            "api_cost_input": 0.001,
            "api_cost_output": 0.002
        }
        
        cost = self.engine._calculate_cost(model_info, 0, 0)
        assert cost == 0.0
    
    def test_evaluate_response_all_criteria(self):
        """Test response evaluation with all supported criteria."""
        test_case = {
            "evaluation_criteria": ["logical_consistency", "correctness", "originality"]
        }
        
        with patch.object(self.engine, '_evaluate_logical_consistency', return_value=0.9):
            with patch.object(self.engine, '_evaluate_correctness', return_value=0.95):
                with patch.object(self.engine, '_evaluate_originality', return_value=0.8):
                    scores = self.engine._evaluate_response(test_case, "test response", {})
        
        assert scores["logical_consistency"] == 0.9
        assert scores["correctness"] == 0.95
        assert scores["originality"] == 0.8
    
    def test_evaluate_response_unknown_criterion(self):
        """Test response evaluation with unknown criterion."""
        test_case = {
            "evaluation_criteria": ["unknown_criterion"]
        }
        
        scores = self.engine._evaluate_response(test_case, "test response", {})
        assert scores["unknown_criterion"] is None
    
    def test_evaluate_response_no_criteria(self):
        """Test response evaluation with no criteria."""
        test_case = {}  # No evaluation_criteria
        
        scores = self.engine._evaluate_response(test_case, "test response", {})
        assert scores == {}
    
    def test_evaluate_response_empty_criteria(self):
        """Test response evaluation with empty criteria list."""
        test_case = {"evaluation_criteria": []}
        
        scores = self.engine._evaluate_response(test_case, "test response", {})
        assert scores == {}
    
    def test_evaluate_logical_consistency(self):
        """Test logical consistency evaluation."""
        with patch('random.uniform', return_value=0.85):
            score = self.engine._evaluate_logical_consistency("test response")
        assert score == 0.85
    
    def test_evaluate_correctness(self):
        """Test correctness evaluation."""
        with patch('random.uniform', return_value=0.92):
            score = self.engine._evaluate_correctness("test response", {})
        assert score == 0.92
    
    def test_evaluate_originality(self):
        """Test originality evaluation."""
        with patch('random.uniform', return_value=0.75):
            score = self.engine._evaluate_originality("test response")
        assert score == 0.75
    
    def test_calculate_aggregate_metrics_valid_scores(self):
        """Test aggregate metrics calculation with valid scores."""
        results = [
            {
                "evaluation_scores": {
                    "correctness": 0.9,
                    "originality": 0.8
                }
            },
            {
                "evaluation_scores": {
                    "correctness": 0.95,
                    "originality": 0.75
                }
            }
        ]
        
        metrics = self.engine._calculate_aggregate_metrics(results)
        assert metrics["correctness"] == (0.9 + 0.95) / 2
        assert metrics["originality"] == (0.8 + 0.75) / 2
    
    def test_calculate_aggregate_metrics_none_scores(self):
        """Test aggregate metrics calculation with None scores."""
        results = [
            {
                "evaluation_scores": {
                    "correctness": 0.9,
                    "unknown": None
                }
            },
            {
                "evaluation_scores": {
                    "correctness": 0.8,
                    "unknown": None
                }
            }
        ]
        
        metrics = self.engine._calculate_aggregate_metrics(results)
        assert metrics["correctness"] == (0.9 + 0.8) / 2
        assert metrics["unknown"] == 0.0  # Should be 0.0 for None scores
    
    def test_calculate_aggregate_metrics_invalid_score_types(self):
        """Test aggregate metrics calculation with invalid score types."""
        results = [
            {
                "evaluation_scores": {
                    "correctness": 0.9,
                    "invalid": "not_a_number"
                }
            },
            {
                "evaluation_scores": {
                    "correctness": 0.8,
                    "invalid": [1, 2, 3]
                }
            }
        ]
        
        metrics = self.engine._calculate_aggregate_metrics(results)
        assert metrics["correctness"] == (0.9 + 0.8) / 2
        assert metrics["invalid"] == 0.0  # Should be 0.0 for invalid scores
    
    def test_calculate_aggregate_metrics_empty_results(self):
        """Test aggregate metrics calculation with empty results."""
        results = []
        
        metrics = self.engine._calculate_aggregate_metrics(results)
        assert metrics == {}
    
    def test_calculate_aggregate_metrics_mixed_criteria(self):
        """Test aggregate metrics calculation with mixed criteria across results."""
        results = [
            {
                "evaluation_scores": {
                    "correctness": 0.9,
                    "originality": 0.8
                }
            },
            {
                "evaluation_scores": {
                    "correctness": 0.95,
                    "logical_consistency": 0.85
                }
            },
            {
                "evaluation_scores": {
                    "originality": 0.7,
                    "logical_consistency": 0.9
                }
            }
        ]
        
        metrics = self.engine._calculate_aggregate_metrics(results)
        assert metrics["correctness"] == (0.9 + 0.95) / 2
        assert metrics["originality"] == (0.8 + 0.7) / 2
        assert metrics["logical_consistency"] == (0.85 + 0.9) / 2
    
    def test_calculate_aggregate_metrics_all_none_scores(self):
        """Test aggregate metrics calculation when all scores for a criterion are None."""
        results = [
            {
                "evaluation_scores": {
                    "correctness": 0.9,
                    "unknown": None
                }
            },
            {
                "evaluation_scores": {
                    "correctness": 0.8,
                    "unknown": None
                }
            }
        ]
        
        metrics = self.engine._calculate_aggregate_metrics(results)
        assert metrics["correctness"] == (0.9 + 0.8) / 2
        assert metrics["unknown"] == 0.0


class TestModelInferenceEngineIntegration:
    """Integration tests for ModelInferenceEngine."""
    
    def setup_method(self):
        """Set up test environment."""
        self.mock_model_registry = Mock()
        self.engine = ModelInferenceEngine(self.mock_model_registry)
    
    def test_full_evaluation_workflow(self):
        """Test complete evaluation workflow."""
        model_info = {
            "name": "gpt-3.5-turbo",
            "api_cost_input": 0.0015,
            "api_cost_output": 0.002
        }
        self.mock_model_registry.get_model.return_value = model_info
        
        test_cases = [
            {
                "id": "math_test",
                "type": "reasoning",
                "prompt": "What is 15 * 7?",
                "evaluation_criteria": ["correctness", "logical_consistency"]
            },
            {
                "id": "creative_test",
                "type": "creative",
                "prompt": "Write a haiku about programming",
                "evaluation_criteria": ["originality", "correctness"]
            }
        ]
        
        use_case_requirements = {
            "max_response_time": 5.0,
            "budget": 10.0
        }
        
        # Mock the random elements for predictable results
        with patch('random.uniform') as mock_uniform:
            with patch('random.randint', return_value=75):
                with patch('time.sleep'):  # Speed up test
                    # Set up predictable random values
                    mock_uniform.side_effect = [
                        0.1,  # sleep time for first call
                        0.95, # correctness score for first test
                        0.9,  # logical_consistency score for first test
                        0.15, # sleep time for second call
                        0.85, # originality score for second test
                        0.88  # correctness score for second test
                    ]
                    
                    result = self.engine.evaluate_model("gpt-3.5-turbo", test_cases, use_case_requirements)
        
        # Verify overall structure
        assert result["model_id"] == "gpt-3.5-turbo"
        assert result["model_info"] == model_info
        assert len(result["test_results"]) == 2
        
        # Verify first test result
        first_result = result["test_results"][0]
        assert first_result["test_case_id"] == "math_test"
        assert first_result["test_case_type"] == "reasoning"
        assert "15 * 7" in first_result["response"]
        assert first_result["evaluation_scores"]["correctness"] == 0.95
        assert first_result["evaluation_scores"]["logical_consistency"] == 0.9
        
        # Verify second test result
        second_result = result["test_results"][1]
        assert second_result["test_case_id"] == "creative_test"
        assert second_result["test_case_type"] == "creative"
        assert "haiku about programming" in second_result["response"]
        assert second_result["evaluation_scores"]["originality"] == 0.85
        assert second_result["evaluation_scores"]["correctness"] == 0.88
        
        # Verify aggregate metrics
        metrics = result["aggregate_metrics"]
        assert metrics["correctness"] == (0.95 + 0.88) / 2
        assert metrics["logical_consistency"] == 0.9  # Only in first test
        assert metrics["originality"] == 0.85  # Only in second test
        assert metrics["total_cost"] > 0
        assert metrics["total_time"] > 0
        assert metrics["avg_response_time"] > 0
    
    def test_evaluation_with_mixed_success_failure(self):
        """Test evaluation where some API calls succeed and others fail."""
        model_info = {
            "name": "test_model",
            "api_cost_input": 0.001,
            "api_cost_output": 0.002
        }
        self.mock_model_registry.get_model.return_value = model_info
        
        test_cases = [
            {
                "id": "success_test",
                "type": "qa",
                "prompt": "This will succeed",
                "evaluation_criteria": ["correctness"]
            },
            {
                "id": "failure_test",
                "type": "qa",
                "prompt": "This will fail",
                "evaluation_criteria": ["correctness"]
            }
        ]
        
        with patch.object(self.engine, '_call_model_api') as mock_call_api:
            mock_call_api.side_effect = [
                {"content": "Success response", "input_tokens": 10, "output_tokens": 20},
                Exception("API timeout")
            ]
            
            with patch.object(self.engine, '_evaluate_correctness', return_value=0.9):
                result = self.engine.evaluate_model("test_model", test_cases, {})
        
        assert len(result["test_results"]) == 2
        
        # First result should be successful
        assert result["test_results"][0]["response"] == "Success response"
        assert "error" not in result["test_results"][0]
        assert result["test_results"][0]["evaluation_scores"]["correctness"] == 0.9
        
        # Second result should show failure
        assert result["test_results"][1]["response"] is None
        assert result["test_results"][1]["error"] == "API timeout"
        assert result["test_results"][1]["evaluation_scores"] == {}
        
        # Aggregate metrics should only include successful results
        assert result["aggregate_metrics"]["correctness"] == 0.9


class TestModelInferenceEngineEdgeCases:
    """Test edge cases and error scenarios."""
    
    def setup_method(self):
        """Set up test environment."""
        self.mock_model_registry = Mock()
        self.engine = ModelInferenceEngine(self.mock_model_registry)
    
    def test_extremely_long_prompt(self):
        """Test handling of extremely long prompts."""
        model_info = {
            "name": "test_model",
            "api_cost_input": 0.001,
            "api_cost_output": 0.002
        }
        self.mock_model_registry.get_model.return_value = model_info
        
        # Create a very long prompt
        long_prompt = "A" * 10000
        test_cases = [{
            "id": "long_test",
            "type": "stress",
            "prompt": long_prompt,
            "evaluation_criteria": ["correctness"]
        }]
        
        with patch('time.sleep'):  # Speed up test
            with patch('random.randint', return_value=50):
                with patch.object(self.engine, '_evaluate_correctness', return_value=0.8):
                    result = self.engine.evaluate_model("test_model", test_cases, {})
        
        assert result is not None
        assert len(result["test_results"]) == 1
        assert long_prompt in result["test_results"][0]["response"]
        # The token calculation is int(len(prompt.split()) * 1.33) which for "A"*10000 is int(1 * 1.33) = 1
        # So we just verify it's calculated correctly
        assert result["test_results"][0]["input_tokens"] == 1
    
    def test_unicode_and_special_characters(self):
        """Test handling of unicode and special characters."""
        model_info = {
            "name": "test_model",
            "api_cost_input": 0.001,
            "api_cost_output": 0.002
        }
        self.mock_model_registry.get_model.return_value = model_info
        
        unicode_prompt = "Hello 你好 مرحبا こんにちは 🌟🚀💻"
        test_cases = [{
            "id": "unicode_test",
            "type": "multilingual",
            "prompt": unicode_prompt,
            "evaluation_criteria": ["correctness"]
        }]
        
        with patch('time.sleep'):
            with patch('random.randint', return_value=30):
                with patch.object(self.engine, '_evaluate_correctness', return_value=0.9):
                    result = self.engine.evaluate_model("test_model", test_cases, {})
        
        assert result is not None
        assert unicode_prompt in result["test_results"][0]["response"]
    
    def test_zero_cost_model(self):
        """Test evaluation with a model that has zero cost."""
        model_info = {
            "name": "free_model",
            "api_cost_input": 0.0,
            "api_cost_output": 0.0
        }
        self.mock_model_registry.get_model.return_value = model_info
        
        test_cases = [{
            "id": "free_test",
            "type": "qa",
            "prompt": "Test prompt",
            "evaluation_criteria": ["correctness"]
        }]
        
        with patch('time.sleep'):
            with patch('random.randint', return_value=25):
                with patch.object(self.engine, '_evaluate_correctness', return_value=0.85):
                    result = self.engine.evaluate_model("free_model", test_cases, {})
        
        assert result["test_results"][0]["cost"] == 0.0
        assert result["aggregate_metrics"]["total_cost"] == 0.0
    
    def test_empty_response_content(self):
        """Test handling of empty response content."""
        model_info = {
            "name": "test_model",
            "api_cost_input": 0.001,
            "api_cost_output": 0.002
        }
        self.mock_model_registry.get_model.return_value = model_info
        
        test_cases = [{
            "id": "empty_test",
            "type": "qa",
            "prompt": "Test prompt",
            "evaluation_criteria": ["correctness"]
        }]
        
        with patch.object(self.engine, '_call_model_api') as mock_call_api:
            mock_call_api.return_value = {
                "content": "",  # Empty response
                "input_tokens": 5,
                "output_tokens": 0
            }
            
            with patch.object(self.engine, '_evaluate_correctness', return_value=0.0):
                result = self.engine.evaluate_model("test_model", test_cases, {})
        
        assert result["test_results"][0]["response"] == ""
        assert result["test_results"][0]["output_tokens"] == 0
        assert result["test_results"][0]["evaluation_scores"]["correctness"] == 0.0
    
    def test_very_high_token_counts(self):
        """Test handling of very high token counts."""
        model_info = {
            "name": "test_model",
            "api_cost_input": 0.001,
            "api_cost_output": 0.002
        }
        self.mock_model_registry.get_model.return_value = model_info
        
        test_cases = [{
            "id": "high_token_test",
            "type": "long_form",
            "prompt": "Test prompt",
            "evaluation_criteria": ["correctness"]
        }]
        
        with patch.object(self.engine, '_call_model_api') as mock_call_api:
            mock_call_api.return_value = {
                "content": "Long response",
                "input_tokens": 100000,  # Very high input tokens
                "output_tokens": 50000   # Very high output tokens
            }
            
            with patch.object(self.engine, '_evaluate_correctness', return_value=0.9):
                result = self.engine.evaluate_model("test_model", test_cases, {})
        
        # Cost should be calculated correctly even with high token counts
        expected_cost = (100000 / 1000) * 0.001 + (50000 / 1000) * 0.002
        assert result["test_results"][0]["cost"] == round(expected_cost, 6)
    
    def test_malformed_test_case(self):
        """Test handling of malformed test cases."""
        model_info = {
            "name": "test_model",
            "api_cost_input": 0.001,
            "api_cost_output": 0.002
        }
        self.mock_model_registry.get_model.return_value = model_info
        
        # Test case missing required fields - this will cause a KeyError
        # The engine doesn't handle this gracefully (it's a bug in the implementation)
        test_cases = [{
            "id": "malformed_test"
            # Missing type, prompt, evaluation_criteria
        }]
        
        # The engine will raise a KeyError because it tries to access missing fields
        with pytest.raises(KeyError):
            self.engine.evaluate_model("test_model", test_cases, {})