from abc import ABC, abstractmethod
from typing import Any, Dict, List


class ScoringStrategy(ABC):
    """Abstract base class for scoring strategies."""

    @abstractmethod
    def score(self, predictions: List[Any], references: List[Any]) -> float:
        """Compute a score given predictions and references."""
        pass


class AccuracyScoringStrategy(ScoringStrategy):
    """Scores predictions based on exact match accuracy and is callable."""

    def score(self, predictions: List[Any], references: List[Any]) -> float:
        correct = sum(1 for p, r in zip(predictions, references) if p == r)
        return correct / len(references) if references else 0.0

    def __call__(self, predictions: List[Any] = None, references: List[Any] = None) -> float:
        """Allow the strategy to be called like a function."""
        if predictions is None or references is None:
            return 0.0
        return self.score(predictions, references)


class F1ScoringStrategy(ScoringStrategy):
    """Scores predictions using F1 score for binary classification."""

    def score(self, predictions: List[int], references: List[int]) -> float:
        tp = sum(1 for p, r in zip(predictions, references) if p == r == 1)
        fp = sum(1 for p, r in zip(predictions, references) if p == 1 and r == 0)
        fn = sum(1 for p, r in zip(predictions, references) if p == 0 and r == 1)
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        return (2 * precision * recall) / (precision + recall) if (precision + recall) else 0.0


class ScoringContext:
    """Context for applying a scoring strategy."""

    def __init__(self, strategy: ScoringStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: ScoringStrategy):
        self._strategy = strategy

    def evaluate(self, predictions: List[Any], references: List[Any]) -> float:
        return self._strategy.score(predictions, references)
