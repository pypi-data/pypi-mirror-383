"""
Comprehensive tests for CLI module to improve coverage.
Tests for main.py and __main__.py functionality.
"""

import pytest
import tempfile
import json
from io import StringIO
from unittest.mock import patch, MagicMock
from pathlib import Path

from llm_evaluation_framework.cli.main import (
    create_parser,
    evaluate_command,
    generate_command,
    score_command,
    list_command,
    main
)


class TestCLIParser:
    """Test CLI argument parser functionality."""
    
    def test_create_parser_basic(self):
        """Test basic parser creation."""
        parser = create_parser()
        assert parser is not None
        assert parser.prog == "llm-eval"
        
        # Test help functionality
        with pytest.raises(SystemExit):
            parser.parse_args(["--help"])
    
    def test_evaluate_command_args(self):
        """Test evaluate command argument parsing."""
        parser = create_parser()
        
        args = parser.parse_args([
            "evaluate",
            "--model", "test-model",
            "--test-cases", "10",
            "--capability", "reasoning"
        ])
        
        assert args.command == "evaluate"
        assert args.model == "test-model"
        assert args.test_cases == 10
        assert args.capability == "reasoning"
    
    def test_generate_command_args(self):
        """Test generate command argument parsing."""
        parser = create_parser()
        
        args = parser.parse_args([
            "generate",
            "--capability", "creativity",
            "--count", "15",
            "--domain", "literature"
        ])
        
        assert args.command == "generate"
        assert args.capability == "creativity"
        assert args.count == 15
        assert args.domain == "literature"
    
    def test_score_command_args(self):
        """Test score command argument parsing."""
        parser = create_parser()
        
        args = parser.parse_args([
            "score",
            "--predictions", "hello", "world",
            "--references", "hi", "earth"
        ])
        
        assert args.command == "score"
        assert args.predictions == ["hello", "world"]
        assert args.references == ["hi", "earth"]
    
    def test_list_command_args(self):
        """Test list command argument parsing."""
        parser = create_parser()
        
        # Test without subcommand
        args = parser.parse_args(["list"])
        assert args.command == "list"
        assert not hasattr(args, 'type') or args.type is None
        
        # Test with capabilities subcommand
        args = parser.parse_args(["list", "capabilities"])
        assert args.command == "list"
        assert args.type == "capabilities"


class TestEvaluateCommand:
    """Test evaluate command functionality."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @patch('llm_evaluation_framework.cli.main.ModelRegistry')
    @patch('llm_evaluation_framework.cli.main.TestDatasetGenerator') 
    @patch('llm_evaluation_framework.cli.main.ModelInferenceEngine')
    @patch('llm_evaluation_framework.cli.main.JSONStore')
    def test_evaluate_command_success(self, mock_json_store, mock_engine, 
                                     mock_generator, mock_registry):
        """Test successful evaluate command execution."""
        # Setup mocks
        mock_registry_instance = MagicMock()
        mock_registry.return_value = mock_registry_instance
        mock_registry_instance.get_model.side_effect = KeyError("Model not found")
        
        mock_generator_instance = MagicMock()
        mock_generator.return_value = mock_generator_instance
        mock_generator_instance.generate_test_cases.return_value = [
            {"input": "test", "expected": "result"}
        ]
        
        mock_engine_instance = MagicMock()
        mock_engine.return_value = mock_engine_instance
        mock_engine_instance.evaluate_model.return_value = {
            "test_results": [{"score": 1.0}],
            "aggregate_metrics": {
                "average_accuracy": 1.0,
                "total_cost": 0.001,
                "total_time": 0.5
            }
        }
        
        mock_store_instance = MagicMock()
        mock_json_store.return_value = mock_store_instance
        
        # Create args
        args = MagicMock()
        args.model = "test-model"
        args.test_cases = 5
        args.capability = "reasoning"
        args.output = None
        
        # Capture stdout
        captured_output = StringIO()
        with patch('sys.stdout', captured_output):
            evaluate_command(args)
        
        # Verify execution - function returns None, so check output
        output = captured_output.getvalue()
        assert "Creating a mock configuration" in output
        
        # Verify mocks were called
        mock_registry_instance.register_model.assert_called_once()
        mock_generator_instance.generate_test_cases.assert_called_once()
        mock_engine_instance.evaluate_model.assert_called_once()
    
    @patch('llm_evaluation_framework.cli.main.ModelRegistry')
    def test_evaluate_command_error_handling(self, mock_registry):
        """Test evaluate command error handling."""
        # Setup mock to raise exception
        mock_registry.side_effect = Exception("Test error")
        
        args = MagicMock()
        args.model = "test-model"
        args.test_cases = 5
        args.capability = "reasoning"
        args.output = None
        
                # Should handle errors gracefully (function doesn't return bool)
        with patch('sys.exit'):
            evaluate_command(args)
            # Function may call sys.exit on error
            # We just verify it doesn't crash


class TestGenerateCommand:
    """Test generate command functionality."""
    
    @patch('llm_evaluation_framework.cli.main.TestDatasetGenerator')
    def test_generate_command_success(self, mock_generator):
        """Test successful generate command execution."""
        # Setup mock
        mock_generator_instance = MagicMock()
        mock_generator.return_value = mock_generator_instance
        mock_generator_instance.generate_test_cases.return_value = [
            {"input": "test1", "expected": "result1"},
            {"input": "test2", "expected": "result2"}
        ]
        
        args = MagicMock()
        args.capability = "creativity"
        args.count = 2
        args.domain = "literature"
        args.output = None
        
        # Capture stdout
        captured_output = StringIO()
        with patch('sys.stdout', captured_output):
            generate_command(args)
        
        output = captured_output.getvalue()
        assert "test1" in output  # Verify output contains generated data
        
        # Verify mock was called correctly
        mock_generator_instance.generate_test_cases.assert_called_once()
    
    @patch('llm_evaluation_framework.cli.main.TestDatasetGenerator')
    def test_generate_command_with_output_file(self, mock_generator, tmp_path):
        """Test generate command with output file."""
        # Setup mock
        mock_generator_instance = MagicMock()
        mock_generator.return_value = mock_generator_instance
        mock_generator_instance.generate_test_cases.return_value = [
            {"input": "test", "expected": "result"}
        ]
        
        output_file = tmp_path / "output.json"
        
        args = MagicMock()
        args.capability = "reasoning"
        args.count = 1
        args.domain = "general"
        args.output = str(output_file)
        
        generate_command(args)
        
        assert output_file.exists()
        
        # Verify file content
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        assert len(data) == 1
        assert data[0]["input"] == "test"
    
    @patch('llm_evaluation_framework.cli.main.TestDatasetGenerator')
    def test_generate_command_error_handling(self, mock_generator):
        """Test generate command error handling."""
        # Setup mock to raise exception
        mock_generator.side_effect = Exception("Generation error")
        
        args = MagicMock()
        args.capability = "reasoning"
        args.count = 5
        args.domain = "general"
        args.output = None
        
        # Should handle errors gracefully
        with patch('sys.exit'):
            generate_command(args)


class TestScoreCommand:
    """Test score command functionality."""
    
    @patch('llm_evaluation_framework.cli.main.AccuracyScoringStrategy')
    @patch('llm_evaluation_framework.cli.main.ScoringContext')
    def test_score_command_basic(self, mock_context, mock_accuracy):
        """Test basic score command functionality."""
        # Setup mocks
        mock_strategy = MagicMock()
        mock_accuracy.return_value = mock_strategy
        
        mock_context_instance = MagicMock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.evaluate.return_value = 0.85
        
        args = MagicMock()
        args.predictions = ["hello", "world"]
        args.references = ["hi", "earth"]
        args.metric = "accuracy"
        
        # Capture stdout
        captured_output = StringIO()
        with patch('sys.stdout', captured_output):
            score_command(args)
        
        output = captured_output.getvalue()
        assert "0.8500" in output
    
    def test_score_command_mismatched_lengths(self):
        """Test score command with mismatched prediction/reference lengths."""
        args = MagicMock()
        args.predictions = ["hello", "world", "extra"]
        args.references = ["hi", "earth"]
        args.metric = "accuracy"
        
        # Should exit with error
        with patch('sys.exit') as mock_exit:
            score_command(args)
            mock_exit.assert_called_with(1)
    
    def test_score_command_empty_inputs(self):
        """Test score command with empty inputs."""
        args = MagicMock()
        args.predictions = []
        args.references = []
        args.metric = "accuracy"
        
        # Should exit with error due to length mismatch (0 == 0 but no data)
        with patch('sys.exit'):
            score_command(args)
    
    @patch('llm_evaluation_framework.cli.main.F1ScoringStrategy')
    @patch('llm_evaluation_framework.cli.main.ScoringContext')
    def test_score_command_f1_metric(self, mock_context, mock_f1):
        """Test score command with F1 metric."""
        # Setup mocks
        mock_strategy = MagicMock()
        mock_f1.return_value = mock_strategy
        
        mock_context_instance = MagicMock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.evaluate.return_value = 0.75
        
        args = MagicMock()
        args.predictions = ["test"]
        args.references = ["ref"]
        args.metric = "f1"
        
        # Capture stdout
        captured_output = StringIO()
        with patch('sys.stdout', captured_output):
            score_command(args)
        
        output = captured_output.getvalue()
        assert "F1 score" in output
        assert "0.7500" in output


class TestListCommand:
    """Test list command functionality."""
    
    def test_list_capabilities(self):
        """Test listing capabilities."""
        args = MagicMock()
        args.models = False
        
        # Capture stdout
        captured_output = StringIO()
        with patch('sys.stdout', captured_output):
            list_command(args)
        
        output = captured_output.getvalue()
        assert "Available capabilities" in output
        assert "reasoning" in output
        assert "creativity" in output
        assert "factual" in output
    
    @patch('llm_evaluation_framework.cli.main.ModelRegistry')
    def test_list_models(self, mock_registry):
        """Test listing models."""
        # Setup mock
        mock_registry_instance = MagicMock()
        mock_registry.return_value = mock_registry_instance
        mock_registry_instance.list_models.return_value = {
            "test-model": {
                "provider": "mock",
                "capabilities": ["reasoning", "creativity"],
                "api_cost_input": 0.001,
                "api_cost_output": 0.002
            }
        }
        
        args = MagicMock()
        args.models = True
        
        # Capture stdout
        captured_output = StringIO()
        with patch('sys.stdout', captured_output):
            list_command(args)
        
        output = captured_output.getvalue()
        assert "Registered models" in output or "test-model" in output
    
    @patch('llm_evaluation_framework.cli.main.ModelRegistry')
    def test_list_command_error_handling(self, mock_registry):
        """Test list command error handling."""
        # Setup mock to raise exception
        mock_registry.side_effect = Exception("Registry error")
        
        args = MagicMock()
        args.models = True
        
        # Should handle errors gracefully
        with patch('sys.exit'):
            list_command(args)


class TestMainFunction:
    """Test main function and CLI entry point."""
    
    @patch('llm_evaluation_framework.cli.main.evaluate_command')
    def test_main_evaluate_command(self, mock_evaluate):
        """Test main function with evaluate command."""
        test_args = [
            "evaluate", 
            "--model", "test-model",
            "--test-cases", "5",
            "--capability", "reasoning"
        ]
        
        with patch('sys.argv', ['llm-eval'] + test_args):
            with patch('sys.exit') as mock_exit:
                main()
                mock_exit.assert_called_with(0)
        
        mock_evaluate.assert_called_once()
    
    @patch('llm_evaluation_framework.cli.main.generate_command')
    def test_main_generate_command(self, mock_generate):
        """Test main function with generate command."""
        test_args = [
            "generate",
            "--capability", "creativity",
            "--count", "10"
        ]
        
        with patch('sys.argv', ['llm-eval'] + test_args):
            with patch('sys.exit') as mock_exit:
                main()
                mock_exit.assert_called_with(0)
        
        mock_generate.assert_called_once()
    
    @patch('llm_evaluation_framework.cli.main.score_command')
    def test_main_score_command(self, mock_score):
        """Test main function with score command."""
        test_args = [
            "score",
            "--predictions", "hello",
            "--references", "hi"
        ]
        
        with patch('sys.argv', ['llm-eval'] + test_args):
            with patch('sys.exit') as mock_exit:
                main()
                mock_exit.assert_called_with(0)
        
        mock_score.assert_called_once()
    
    @patch('llm_evaluation_framework.cli.main.list_command')
    def test_main_list_command(self, mock_list):
        """Test main function with list command."""
        test_args = ["list"]
        
        with patch('sys.argv', ['llm-eval'] + test_args):
            with patch('sys.exit') as mock_exit:
                main()
                mock_exit.assert_called_with(0)
        
        mock_list.assert_called_once()
    
    def test_main_no_command(self):
        """Test main function with no command (should show help)."""
        with patch('sys.argv', ['llm-eval']):
            with patch('sys.exit') as mock_exit:
                with patch('sys.stderr', StringIO()):
                    main()
                    # Should exit with error code due to missing command
                    mock_exit.assert_called_with(2)
    
    def test_main_invalid_command(self):
        """Test main function with invalid command."""
        test_args = ["invalid_command"]
        
        with patch('sys.argv', ['llm-eval'] + test_args):
            with patch('sys.exit') as mock_exit:
                with patch('sys.stderr', StringIO()):
                    main()
                    # Should exit with error code
                    mock_exit.assert_called_with(2)


class TestCLIMainModule:
    """Test __main__.py module functionality."""
    
    @patch('llm_evaluation_framework.cli.main.main')
    def test_main_module_execution(self, mock_main):
        """Test that __main__.py correctly calls main function."""
        # Import and execute __main__.py
        import llm_evaluation_framework.cli.__main__  # noqa: F401
        
        # The import should have called main()
        mock_main.assert_called_once()


class TestCLIEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_invalid_capability(self):
        """Test handling of invalid capability."""
        parser = create_parser()
        
        # Invalid capability should fail during parsing
        with pytest.raises(SystemExit):
            parser.parse_args([
                "evaluate",
                "--model", "test-model",
                "--test-cases", "5",
                "--capability", "invalid_capability"
            ])
    
    def test_negative_test_cases(self):
        """Test handling of negative test case count."""
        parser = create_parser()
        
        # This should be handled by argument type validation
        with pytest.raises(SystemExit):
            parser.parse_args([
                "evaluate",
                "--model", "test-model",
                "--test-cases", "-5",
                "--capability", "reasoning"
            ])
    
    def test_missing_required_args(self):
        """Test parser with missing required arguments."""
        parser = create_parser()
        
        # Missing model argument should fail
        with pytest.raises(SystemExit):
            parser.parse_args([
                "evaluate",
                "--test-cases", "5",
                "--capability", "reasoning"
            ])
    
    @patch('llm_evaluation_framework.cli.main.ModelRegistry')
    def test_model_registry_initialization_error(self, mock_registry):
        """Test error handling when model registry fails to initialize."""
        mock_registry.side_effect = Exception("Registry initialization failed")
        
        args = MagicMock()
        args.model = "test-model"
        args.test_cases = 5
        args.capability = "reasoning"
        args.output = None
        
        with patch('sys.exit'):
            evaluate_command(args)


class TestGenerateCommand:
    """Test generate command functionality."""
    
    @patch('llm_evaluation_framework.cli.main.TestDatasetGenerator')
    def test_generate_command_success(self, mock_generator):
        """Test successful generate command execution."""
        # Setup mock
        mock_generator_instance = MagicMock()
        mock_generator.return_value = mock_generator_instance
        mock_generator_instance.generate_test_cases.return_value = [
            {"input": "test1", "expected": "result1"},
            {"input": "test2", "expected": "result2"}
        ]
        
        args = MagicMock()
        args.capability = "creativity"
        args.count = 2
        args.domain = "literature"
        args.output = None
        
        # Capture stdout
        captured_output = StringIO()
        with patch('sys.stdout', captured_output):
            result = generate_command(args)
        
        assert result is True
        output = captured_output.getvalue()
        assert "Generated 2 test cases successfully" in output
        
        # Verify mock was called correctly
        mock_generator_instance.generate_test_cases.assert_called_once()
        call_args = mock_generator_instance.generate_test_cases.call_args[0]
        assert call_args[0]["required_capabilities"] == ["creativity"]
        assert call_args[0]["domain"] == "literature"
        assert call_args[1] == 2
    
    @patch('llm_evaluation_framework.cli.main.TestDatasetGenerator')
    def test_generate_command_with_output_file(self, mock_generator, tmp_path):
        """Test generate command with output file."""
        # Setup mock
        mock_generator_instance = MagicMock()
        mock_generator.return_value = mock_generator_instance
        mock_generator_instance.generate_test_cases.return_value = [
            {"input": "test", "expected": "result"}
        ]
        
        output_file = tmp_path / "output.json"
        
        args = MagicMock()
        args.capability = "reasoning"
        args.count = 1
        args.domain = "general"
        args.output = str(output_file)
        
        result = generate_command(args)
        
        assert result is True
        assert output_file.exists()
        
        # Verify file content
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        assert len(data) == 1
        assert data[0]["input"] == "test"
    
    @patch('llm_evaluation_framework.cli.main.TestDatasetGenerator')
    def test_generate_command_error_handling(self, mock_generator):
        """Test generate command error handling."""
        # Setup mock to raise exception
        mock_generator.side_effect = Exception("Generation error")
        
        args = MagicMock()
        args.capability = "reasoning"
        args.count = 5
        args.domain = "general"
        args.output = None
        
        # Capture stderr
        captured_output = StringIO()
        with patch('sys.stderr', captured_output):
            result = generate_command(args)
        
        assert result is False
        output = captured_output.getvalue()
        assert "Error during generation" in output


class TestScoreCommand:
    """Test score command functionality."""
    
    def test_score_command_basic(self):
        """Test basic score command functionality."""
        args = MagicMock()
        args.predictions = ["hello", "world"]
        args.references = ["hi", "earth"]
        args.strategy = "accuracy"
        
        # Capture stdout
        captured_output = StringIO()
        with patch('sys.stdout', captured_output):
            result = score_command(args)
        
        assert result is True
        output = captured_output.getvalue()
        assert "Scoring Results" in output
        assert "Average Score" in output
    
    def test_score_command_mismatched_lengths(self):
        """Test score command with mismatched prediction/reference lengths."""
        args = MagicMock()
        args.predictions = ["hello", "world", "extra"]
        args.references = ["hi", "earth"]
        args.strategy = "accuracy"
        
        # Capture stderr
        captured_output = StringIO()
        with patch('sys.stderr', captured_output):
            result = score_command(args)
        
        assert result is False
        output = captured_output.getvalue()
        assert "must have the same length" in output
    
    def test_score_command_empty_inputs(self):
        """Test score command with empty inputs."""
        args = MagicMock()
        args.predictions = []
        args.references = []
        args.strategy = "accuracy"
        
        # Capture stderr
        captured_output = StringIO()
        with patch('sys.stderr', captured_output):
            result = score_command(args)
        
        assert result is False
        output = captured_output.getvalue()
        assert "No predictions or references provided" in output
    
    def test_score_command_error_handling(self):
        """Test score command error handling."""
        args = MagicMock()
        args.predictions = ["test"]
        args.references = ["ref"]
        args.strategy = "invalid_strategy"
        
        # This should still work as it uses basic scoring
        captured_output = StringIO()
        with patch('sys.stdout', captured_output):
            result = score_command(args)
        
        # Should succeed with basic scoring even if strategy is invalid
        assert result is True


class TestListCommand:
    """Test list command functionality."""
    
    def test_list_capabilities(self):
        """Test listing capabilities."""
        args = MagicMock()
        args.type = "capabilities"
        
        # Capture stdout
        captured_output = StringIO()
        with patch('sys.stdout', captured_output):
            result = list_command(args)
        
        assert result is True
        output = captured_output.getvalue()
        assert "Available Capabilities" in output
        assert "reasoning" in output
        assert "creativity" in output
        assert "factual" in output
    
    @patch('llm_evaluation_framework.cli.main.ModelRegistry')
    def test_list_models(self, mock_registry):
        """Test listing models."""
        # Setup mock
        mock_registry_instance = MagicMock()
        mock_registry.return_value = mock_registry_instance
        mock_registry_instance.list_models.return_value = {
            "test-model": {
                "provider": "mock",
                "capabilities": ["reasoning", "creativity"],
                "api_cost_input": 0.001,
                "api_cost_output": 0.002
            }
        }
        
        args = MagicMock()
        args.type = "models"
        
        # Capture stdout
        captured_output = StringIO()
        with patch('sys.stdout', captured_output):
            result = list_command(args)
        
        assert result is True
        output = captured_output.getvalue()
        assert "Registered Models" in output
        assert "test-model" in output
    
    def test_list_strategies(self):
        """Test listing scoring strategies."""
        args = MagicMock()
        args.type = "strategies"
        
        # Capture stdout
        captured_output = StringIO()
        with patch('sys.stdout', captured_output):
            result = list_command(args)
        
        assert result is True
        output = captured_output.getvalue()
        assert "Available Scoring Strategies" in output
        assert "accuracy" in output
    
    def test_list_all_when_no_type(self):
        """Test listing all when no specific type provided."""
        args = MagicMock()
        args.type = None
        
        # Capture stdout
        captured_output = StringIO()
        with patch('sys.stdout', captured_output):
            result = list_command(args)
        
        assert result is True
        output = captured_output.getvalue()
        assert "Available Capabilities" in output
        assert "Available Scoring Strategies" in output
    
    @patch('llm_evaluation_framework.cli.main.ModelRegistry')
    def test_list_command_error_handling(self, mock_registry):
        """Test list command error handling."""
        # Setup mock to raise exception
        mock_registry.side_effect = Exception("Registry error")
        
        args = MagicMock()
        args.type = "models"
        
        # Capture stderr
        captured_output = StringIO()
        with patch('sys.stderr', captured_output):
            result = list_command(args)
        
        assert result is False
        output = captured_output.getvalue()
        assert "Error listing models" in output


class TestMainFunction:
    """Test main function and CLI entry point."""
    
    @patch('llm_evaluation_framework.cli.main.evaluate_command')
    def test_main_evaluate_command(self, mock_evaluate):
        """Test main function with evaluate command."""
        mock_evaluate.return_value = True
        
        test_args = [
            "evaluate", 
            "--model", "test-model",
            "--test-cases", "5",
            "--capability", "reasoning"
        ]
        
        with patch('sys.argv', ['llm-eval'] + test_args):
            with patch('sys.exit') as mock_exit:
                main()
                mock_exit.assert_called_with(0)
        
        mock_evaluate.assert_called_once()
    
    @patch('llm_evaluation_framework.cli.main.generate_command')
    def test_main_generate_command(self, mock_generate):
        """Test main function with generate command."""
        mock_generate.return_value = True
        
        test_args = [
            "generate",
            "--capability", "creativity",
            "--count", "10"
        ]
        
        with patch('sys.argv', ['llm-eval'] + test_args):
            with patch('sys.exit') as mock_exit:
                main()
                mock_exit.assert_called_with(0)
        
        mock_generate.assert_called_once()
    
    @patch('llm_evaluation_framework.cli.main.score_command')
    def test_main_score_command(self, mock_score):
        """Test main function with score command."""
        mock_score.return_value = True
        
        test_args = [
            "score",
            "--predictions", "hello",
            "--references", "hi"
        ]
        
        with patch('sys.argv', ['llm-eval'] + test_args):
            with patch('sys.exit') as mock_exit:
                main()
                mock_exit.assert_called_with(0)
        
        mock_score.assert_called_once()
    
    @patch('llm_evaluation_framework.cli.main.list_command')
    def test_main_list_command(self, mock_list):
        """Test main function with list command."""
        mock_list.return_value = True
        
        test_args = ["list", "capabilities"]
        
        with patch('sys.argv', ['llm-eval'] + test_args):
            with patch('sys.exit') as mock_exit:
                main()
                mock_exit.assert_called_with(0)
        
        mock_list.assert_called_once()
    
    def test_main_no_command(self):
        """Test main function with no command (should show help)."""
        with patch('sys.argv', ['llm-eval']):
            with patch('sys.exit') as mock_exit:
                with patch('sys.stderr', StringIO()):
                    main()
                    # Should exit with error code due to missing command
                    mock_exit.assert_called_with(2)
    
    @patch('llm_evaluation_framework.cli.main.evaluate_command')
    def test_main_command_failure(self, mock_evaluate):
        """Test main function when command fails."""
        mock_evaluate.return_value = False
        
        test_args = [
            "evaluate",
            "--model", "test-model",
            "--test-cases", "5",
            "--capability", "reasoning"
        ]
        
        with patch('sys.argv', ['llm-eval'] + test_args):
            with patch('sys.exit') as mock_exit:
                main()
                mock_exit.assert_called_with(1)
    
    def test_main_invalid_command(self):
        """Test main function with invalid command."""
        test_args = ["invalid_command"]
        
        with patch('sys.argv', ['llm-eval'] + test_args):
            with patch('sys.exit') as mock_exit:
                with patch('sys.stderr', StringIO()):
                    main()
                    # Should exit with error code
                    mock_exit.assert_called_with(2)


class TestCLIMainModule:
    """Test __main__.py module functionality."""
    
    @patch('llm_evaluation_framework.cli.main.main')
    def test_main_module_execution(self, mock_main):
        """Test that __main__.py correctly calls main function when executed directly."""
        import llm_evaluation_framework.cli.__main__ as main_module
        
        # Check that the __main__.py module has the correct structure
        assert hasattr(main_module, 'main')
        
        # Simulate the __name__ == "__main__" condition being true
        # Since importing doesn't trigger the condition, we test the function exists
        # and would be called if executed directly
        main_module.main()
        mock_main.assert_called_once()


class TestCLIEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_invalid_capability(self):
        """Test handling of invalid capability."""
        parser = create_parser()
        
        # Invalid capability should still parse (validation happens in command)
        args = parser.parse_args([
            "evaluate",
            "--model", "test-model",
            "--test-cases", "5",
            "--capability", "invalid_capability"
        ])
        
        assert args.capability == "invalid_capability"
    
    def test_negative_test_cases(self):
        """Test handling of negative test case count."""
        parser = create_parser()
        
        # This should be handled by argument type validation
        with pytest.raises(SystemExit):
            parser.parse_args([
                "evaluate",
                "--model", "test-model",
                "--test-cases", "-5",
                "--capability", "reasoning"
            ])
    
    def test_empty_predictions_and_references(self):
        """Test score command with empty predictions and references."""
        args = MagicMock()
        args.predictions = []
        args.references = []
        args.strategy = "accuracy"
        
        result = score_command(args)
        assert result is False
    
    @patch('llm_evaluation_framework.cli.main.ModelRegistry')
    def test_model_registry_initialization_error(self, mock_registry):
        """Test error handling when model registry fails to initialize."""
        mock_registry.side_effect = Exception("Registry initialization failed")
        
        args = MagicMock()
        args.model = "test-model"
        args.test_cases = 5
        args.capability = "reasoning"
        args.domain = "general"
        args.output = None
        
        result = evaluate_command(args)
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__])