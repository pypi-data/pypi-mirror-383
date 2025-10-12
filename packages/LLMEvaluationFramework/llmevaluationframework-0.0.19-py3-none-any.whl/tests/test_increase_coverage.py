import pytest
from llm_evaluation_framework.model_inference_engine import ModelInferenceEngine
from llm_evaluation_framework.model_registry import ModelRegistry

def test_empty_test_cases_branch():
    registry = ModelRegistry()
    # Manually insert a dummy model into registry's internal storage
    if hasattr(registry, "models"):
        registry.models["dummy-model"] = {"api_cost_input": 0.001, "api_cost_output": 0.002}
    elif hasattr(registry, "_models"):
        registry._models["dummy-model"] = {"api_cost_input": 0.001, "api_cost_output": 0.002}
    if hasattr(registry, "models"):
        registry.models["dummy-model"] = {"api_cost_input": 0.001, "api_cost_output": 0.002}
    elif hasattr(registry, "_models"):
        registry._models["dummy-model"] = {"api_cost_input": 0.001, "api_cost_output": 0.002}
    engine = ModelInferenceEngine(registry)
    # Trigger the empty test_cases branch
    result = engine.evaluate_model("dummy-model", [], {})
    assert result["aggregate_metrics"]["total_cost"] == 0
    assert result["aggregate_metrics"]["total_time"] == 0
    assert result["aggregate_metrics"]["avg_response_time"] == 0

def test_invalid_model_info_type():
    class BadRegistry:
        def get_model(self, model_id):
            return "not-a-dict"
    engine = ModelInferenceEngine(BadRegistry())
    with pytest.raises(TypeError):
        engine.evaluate_model("any-model", [{"id": 1, "type": "unit", "prompt": "test", "evaluation_criteria": []}], {})

def test_nonexistent_model_returns_none():
    registry = ModelRegistry()
    engine = ModelInferenceEngine(registry)
    result = engine.evaluate_model("nonexistent", [{"id": 1, "type": "unit", "prompt": "test", "evaluation_criteria": []}], {})
    assert result is None

def test_evaluate_response_with_unknown_criterion():
    registry = ModelRegistry()
    if hasattr(registry, "models"):
        registry.models["dummy-model"] = {"api_cost_input": 0.001, "api_cost_output": 0.002}
    elif hasattr(registry, "_models"):
        registry._models["dummy-model"] = {"api_cost_input": 0.001, "api_cost_output": 0.002}
    engine = ModelInferenceEngine(registry)
    test_case = {
        "id": 1,
        "type": "unit",
        "prompt": "test",
        "evaluation_criteria": ["unknown_criterion"]
    }
    result = engine.evaluate_model("dummy-model", [test_case], {})
    assert "unknown_criterion" in result["test_results"][0]["evaluation_scores"]
    assert result["test_results"][0]["evaluation_scores"]["unknown_criterion"] is None
