import pytest
from llm_evaluation_framework import cli
from llm_evaluation_framework.core import base_engine, base_registry
from llm_evaluation_framework.engines import async_inference_engine
from llm_evaluation_framework.evaluation import scoring_strategies
from llm_evaluation_framework.logging import logger as custom_logger
from llm_evaluation_framework.registry import model_registry

def test_cli_main_runs():
    # Test that CLI doesn't crash when called with no arguments
    import sys
    from unittest.mock import patch
    
    # Mock sys.argv to provide help command
    with patch.object(sys, 'argv', ['test-cli', '--help']):
        # Capture SystemExit which argparse raises for --help
        with pytest.raises(SystemExit) as exc_info:
            if hasattr(cli, "main"):
                cli.main()
            else:
                # If cli is a package, try importing from cli.main
                import importlib
                try:
                    cli_main = importlib.import_module("llm_evaluation_framework.cli.main")
                    if hasattr(cli_main, "main"):
                        cli_main.main()
                except ModuleNotFoundError:
                    pass
        
        # SystemExit with code 0 means --help was successfully displayed
        assert exc_info.value.code == 0

def test_base_engine_and_registry_full_coverage():
    class DummyEngine(base_engine.BaseEngine):
        def execute(self):
            return "executed"

    class DummyRegistry(base_registry.BaseRegistry):
        def register(self, item_id, item_info):
            self._items[item_id] = item_info

        def get(self, item_id):
            return self._items.get(item_id)

        def list_items(self):
            return list(self._items.keys())

    dummy_registry = DummyRegistry()
    e = DummyEngine(model_registry=dummy_registry)
    assert e.execute() == "executed"

    dummy_registry.register("x", {"data": 1})
    assert dummy_registry.get("x") == {"data": 1}
    assert "x" in dummy_registry.list_items()
    # Simulate unregister by directly manipulating _items for coverage
    dummy_registry._items.pop("x")
    assert "x" not in dummy_registry.list_items()

def test_async_inference_engine_full():
    import asyncio
    class DummyAsync(async_inference_engine.AsyncInferenceEngine):
        async def ainfer(self):
            return "async result"
    d = DummyAsync(model_callable=lambda: None)
    res = asyncio.run(d.ainfer())
    assert res == "async result"

def test_scoring_strategies_callable_and_line_11():
    strat = scoring_strategies.AccuracyScoringStrategy()
    # Ensure __call__ exists
    assert hasattr(strat, "__call__")
    data = {"predictions": [1, 0], "labels": [1, 1]}
    score = strat(data)
    assert isinstance(score, float)

def test_logger_all_methods_and_registry_model_full():
    # Try to get ObservableLogger class from logger module
    LoggerClass = getattr(custom_logger, "ObservableLogger", None)
    if LoggerClass:
        log = LoggerClass("test")
        log.info("info msg")
        log.error("error msg")
        log.debug("debug msg")
        if hasattr(log, "warning"):
            log.warning("warn msg")
        if hasattr(log, "critical"):
            log.critical("critical msg")

    reg = model_registry.ModelRegistry()
    reg.register_model("m1", object())
    assert "m1" in reg.list_models()
    reg.unregister_model("m1")
    assert "m1" not in reg.list_models()
