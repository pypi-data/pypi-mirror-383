import os
import pytest
from llm_evaluation_framework.evaluation.scoring_strategies import (
    AccuracyScoringStrategy,
    F1ScoringStrategy,
    ScoringContext,
)
from llm_evaluation_framework.persistence.persistence_manager import PersistenceManager
from llm_evaluation_framework.logging.logger import ObservableLogger, LoggerObserver


def test_accuracy_scoring_strategy():
    strategy = AccuracyScoringStrategy()
    score = strategy.score(["a", "b", "c"], ["a", "x", "c"])
    assert score == pytest.approx(2 / 3)


def test_f1_scoring_strategy():
    strategy = F1ScoringStrategy()
    score = strategy.score([1, 0, 1], [1, 0, 0])
    assert 0.0 <= score <= 1.0


def test_scoring_context_switch():
    context = ScoringContext(AccuracyScoringStrategy())
    acc_score = context.evaluate(["a"], ["a"])
    assert acc_score == 1.0
    context.set_strategy(F1ScoringStrategy())
    f1_score = context.evaluate([1], [1])
    assert f1_score == 1.0


def test_persistence_manager(tmp_path):
    pm = PersistenceManager(storage_dir=tmp_path)
    data = {"key": "value"}
    pm.save("test.json", data)
    loaded = pm.load("test.json")
    assert loaded == data
    pm.delete("test.json")
    assert pm.load("test.json") is None


def test_observable_logger(capsys):
    messages = []

    def observer_callback(level, message):
        messages.append((level, message))

    logger = ObservableLogger("TestLogger")
    observer = LoggerObserver(observer_callback)
    logger.add_observer(observer)

    logger.info("Test message")
    captured = capsys.readouterr()
    assert "Test message" in captured.out or "Test message" in captured.err
    assert ("INFO", "Test message") in messages
