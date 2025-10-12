"""
Legacy CLI module for backward compatibility.
The main CLI implementation has been moved to the cli package.
"""

import argparse
from llm_evaluation_framework.evaluation.scoring_strategies import (
    AccuracyScoringStrategy,
    F1ScoringStrategy,
    ScoringContext,
)
from llm_evaluation_framework.persistence.persistence_manager import PersistenceManager

# Import the new main function
from llm_evaluation_framework.cli.main import main as new_main


def main():
    """
    Legacy main function for backward compatibility.
    This now delegates to the new CLI implementation.
    """
    # Check if this is being called with old-style arguments
    import sys
    if len(sys.argv) > 1 and sys.argv[1] in ['score', 'save', 'load']:
        # Use legacy implementation for backward compatibility
        _legacy_main()
    else:
        # Delegate to new implementation
        new_main()


def _legacy_main():
    """Legacy CLI implementation for backward compatibility."""
    parser = argparse.ArgumentParser(description="LLM Evaluation Framework CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Score command
    score_parser = subparsers.add_parser("score", help="Evaluate predictions against references")
    score_parser.add_argument("--predictions", nargs="+", required=True, help="List of predictions")
    score_parser.add_argument("--references", nargs="+", required=True, help="List of references")
    score_parser.add_argument(
        "--metric", choices=["accuracy", "f1"], default="accuracy", help="Scoring metric"
    )

    # Persistence commands
    save_parser = subparsers.add_parser("save", help="Save evaluation results")
    save_parser.add_argument("filename", help="Filename to save results to")
    save_parser.add_argument("--data", nargs="+", help="Key=Value pairs", required=True)

    load_parser = subparsers.add_parser("load", help="Load evaluation results")
    load_parser.add_argument("filename", help="Filename to load results from")

    args = parser.parse_args()

    if args.command == "score":
        predictions = args.predictions
        references = args.references
        if args.metric == "accuracy":
            strategy = AccuracyScoringStrategy()
        else:
            strategy = F1ScoringStrategy()
        context = ScoringContext(strategy)
        score = context.evaluate(predictions, references)
        print(f"{args.metric.capitalize()} score: {score:.4f}")

    elif args.command == "save":
        data_dict = dict(item.split("=") for item in args.data)
        pm = PersistenceManager()
        pm.save(args.filename, data_dict)
        print(f"Data saved to {args.filename}")

    elif args.command == "load":
        pm = PersistenceManager()
        data = pm.load(args.filename)
        if data is None:
            print("No data found.")
        else:
            print("Loaded data:", data)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
