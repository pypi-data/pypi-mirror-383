"""
Main CLI module for LLM Evaluation Framework.
Provides command-line interface for common framework operations.
"""

import argparse
import sys

from llm_evaluation_framework.registry.model_registry import ModelRegistry
from llm_evaluation_framework.model_inference_engine import ModelInferenceEngine
from llm_evaluation_framework.test_dataset_generator import TestDatasetGenerator
from llm_evaluation_framework.persistence.json_store import JSONStore
from llm_evaluation_framework.evaluation.scoring_strategies import (
    AccuracyScoringStrategy,
    F1ScoringStrategy,
    ScoringContext,
)
from llm_evaluation_framework.utils.logger import setup_logging


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="llm-eval",
        description="LLM Evaluation Framework CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Score predictions against references
  llm-eval score --predictions "pred1" "pred2" --references "ref1" "ref2"
  
  # Run a quick evaluation
  llm-eval evaluate --model gpt-3.5-turbo --test-cases 5
  
  # Generate test dataset
  llm-eval generate --capability reasoning --count 10
        """
    )
    
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true", 
        help="Enable verbose logging"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    # Do not require subparser here to allow help display when no command is given
    
    # Score command
    score_parser = subparsers.add_parser(
        "score", 
        help="Evaluate predictions against references"
    )
    score_parser.add_argument(
        "--predictions", 
        nargs="+", 
        required=True, 
        help="List of predictions"
    )
    score_parser.add_argument(
        "--references", 
        nargs="+", 
        required=True, 
        help="List of references"
    )
    score_parser.add_argument(
        "--metric", 
        choices=["accuracy", "f1"], 
        default="accuracy", 
        help="Scoring metric to use"
    )
    
    # Evaluate command
    eval_parser = subparsers.add_parser(
        "evaluate",
        help="Run model evaluation"
    )
    eval_parser.add_argument(
        "--model",
        required=True,
        help="Model identifier"
    )
    def positive_int(value):
        ivalue = int(value)
        if ivalue <= 0:
            raise argparse.ArgumentTypeError("Number of test cases must be positive")
        return ivalue

    eval_parser.add_argument(
        "--test-cases",
        type=positive_int,
        default=5,
        help="Number of test cases to generate"
    )
    eval_parser.add_argument(
        "--capability",
        default="reasoning",
        help="Capability to test"
    )
    eval_parser.add_argument(
        "--output",
        help="Output file for results (JSON)"
    )
    
    # Generate command
    gen_parser = subparsers.add_parser(
        "generate",
        help="Generate test dataset"
    )
    gen_parser.add_argument(
        "--capability",
        choices=["reasoning", "creativity", "factual", "instruction", "coding"],
        required=True,
        help="Capability to generate tests for"
    )
    gen_parser.add_argument(
        "--count",
        type=positive_int,
        default=10,
        help="Number of test cases to generate"
    )
    gen_parser.add_argument(
        "--domain",
        default="general",
        help="Domain for test cases"
    )
    gen_parser.add_argument(
        "--output",
        help="Output file for generated tests (JSON)"
    )
    
    # List command
    list_parser = subparsers.add_parser(
        "list",
        help="List available models and configurations"
    )
    list_parser.add_argument(
        "--models",
        action="store_true",
        help="List registered models"
    )
    list_parser.add_argument(
        "type",
        nargs="?",
        choices=["capabilities", "models", "strategies"],
        help="Type of items to list"
    )
    
    return parser


def score_command(args) -> None:
    """Handle the score command."""
    predictions = args.predictions
    references = args.references
    
    if not predictions or not references:
        print("No predictions or references provided", file=sys.stderr)
        return False
    
    if len(predictions) != len(references):
        print("Predictions and references must have the same length", file=sys.stderr)
        return False
    
    if args.metric == "accuracy":
        strategy = AccuracyScoringStrategy()
    else:
        strategy = F1ScoringStrategy()
    
    context = ScoringContext(strategy)
    try:
        score = context.evaluate(predictions, references)
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    print("Scoring Results")
    print("Average Score")
    print(f"{args.metric.capitalize()} score: {float(score):.4f}")
    return True


def evaluate_command(args) -> bool:
    """Handle the evaluate command."""
    # Setup logging based on verbosity
    log_level = "DEBUG" if getattr(args, "verbose", False) else "INFO"
    setup_logging(level=log_level)
    try:
        # Create a mock registry with a default model
        registry = ModelRegistry()
        
        # Register a mock model if it doesn't exist
        try:
            registry.get_model(args.model)
        except KeyError:
            print(f"Model '{args.model}' not found. Creating a mock configuration...")
            model_config = {
                "provider": "mock",
                "parameters": {"temperature": 0.7, "max_tokens": 100},
                "api_cost_input": 0.001,
                "api_cost_output": 0.002,
                "capabilities": [args.capability]
            }
            registry.register_model(args.model, model_config)
        
        # Generate test cases
        generator = TestDatasetGenerator()
        use_case_requirements = {
            "domain": "general",
            "required_capabilities": [args.capability]
        }
        
        test_cases = generator.generate_test_cases(
            use_case_requirements,
            args.test_cases
        )
        
        # Run evaluation
        engine = ModelInferenceEngine(registry)
        results = engine.evaluate_model(args.model, test_cases, use_case_requirements)
        
        # Display results
        print(f"\nEvaluation Results for {args.model}:")
        total_cost = results['aggregate_metrics'].get('total_cost', 0.0)
        total_time = results['aggregate_metrics'].get('total_time', 0.0)
        test_count = len(results.get('test_results', []))
        print(f"Total Cost: ${float(total_cost):.4f}")
        print(f"Total Time: {float(total_time):.2f}s")
        print(f"Test Cases: {test_count}")
        
        # Save results if output specified
        if args.output:
            store = JSONStore(args.output)
            store.save_evaluation_result(results)
            print(f"Results saved to: {args.output}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def generate_command(args) -> bool:
    """Handle the generate command."""
    # Setup logging based on verbosity
    log_level = "DEBUG" if getattr(args, "verbose", False) else "INFO"
    setup_logging(level=log_level)
    
    try:
        generator = TestDatasetGenerator()
        use_case_requirements = {
            "domain": args.domain,
            "required_capabilities": [args.capability]
        }
        
        test_cases = generator.generate_test_cases(
            use_case_requirements,
            args.count
        )
    except Exception as e:
        print(f"Error during generation: {e}", file=sys.stderr)
        return False
    
    print(f"Generated {len(test_cases)} test cases successfully")
    for i, test_case in enumerate(test_cases, 1):
        prompt = test_case.get('prompt', '<no prompt>')
        criteria = test_case.get('evaluation_criteria', '<no criteria>')
        print(f"\n{i}. {prompt}")
        print(f"   Criteria: {criteria}")
    
    # Save if output specified
    if args.output:
        import json
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(test_cases, f, indent=2)
        print(f"\nTest cases saved to: {args.output}")
    return True


def list_command(args) -> bool:
    """Handle the list command."""
    try:
        if args.models or args.type == "models":
            registry = ModelRegistry()
            models = registry.list_models()
            if models:
                print("Registered Models")
                for model in models:
                    print(f"  - {model}")
            else:
                print("No models registered")
                print("Available Capabilities")
                capabilities = ["reasoning", "creativity", "factual", "instruction", "coding"]
                for cap in capabilities:
                    print(f"  - {cap}")
                print("Available Scoring Strategies")
                strategies = ["accuracy", "f1"]
                for strat in strategies:
                    print(f"  - {strat}")
                return True
        elif args.type == "capabilities":
            print("Available Capabilities")
            capabilities = ["reasoning", "creativity", "factual", "instruction", "coding"]
            for cap in capabilities:
                print(f"  - {cap}")
            return True
        elif args.type == "strategies":
            print("Available Scoring Strategies")
            strategies = ["accuracy", "f1"]
            for strat in strategies:
                print(f"  - {strat}")
            return True
        else:
            print("Available Capabilities")
            capabilities = ["reasoning", "creativity", "factual", "instruction", "coding"]
            for cap in capabilities:
                print(f"  - {cap}")
            return True
        return True
    except Exception as e:
        if args.type == "models" or args.models:
            print("Error listing models", file=sys.stderr)
        else:
            print(f"Error: {e}", file=sys.stderr)
        return False
    return True


def main() -> None:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(level=log_level)
    
    if not args.command:
        parser.print_help()
        sys.exit(2)
    
    try:
        if args.command == "score":
            if score_command(args):
                sys.exit(0)
            else:
                sys.exit(1)
        elif args.command == "evaluate":
            if evaluate_command(args):
                sys.exit(0)
            else:
                sys.exit(1)
        elif args.command == "generate":
            if generate_command(args):
                sys.exit(0)
            else:
                sys.exit(1)
        elif args.command == "list":
            if list_command(args):
                sys.exit(0)
            else:
                sys.exit(1)
        else:
            print(f"Unknown command: {args.command}")
            parser.print_help()
            return False
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
