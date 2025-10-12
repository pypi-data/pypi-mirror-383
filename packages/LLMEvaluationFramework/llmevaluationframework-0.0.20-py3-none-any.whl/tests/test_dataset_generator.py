import pytest
import llm_evaluation_framework.test_dataset_generator as tdg

def test_generate_test_cases():
    gen = tdg.TestDatasetGenerator()
    # Ensure templates are initialized
    assert hasattr(gen, "templates")
    assert "reasoning" in gen.templates

    cases = gen.generate_test_cases({"required_capabilities": ["reasoning"], "domain": "math"}, num_cases=2)
    assert len(cases) == 2
    for case in cases:
        assert case['type'] == 'reasoning'
        assert 'prompt' in case
        assert 'evaluation_criteria' in case

def test_fill_template_problem():
    gen = tdg.TestDatasetGenerator()
    template = "Solve {problem}"
    result = gen._fill_template(template, {"domain": "science"})
    assert "science problem" in result

def test_fill_template_topic():
    gen = tdg.TestDatasetGenerator()
    template = "Discuss {topic}"
    result = gen._fill_template(template, {"domain": "history"})
    assert "history topic" in result

def test_fill_template_task():
    gen = tdg.TestDatasetGenerator()
    template = "Perform {task}"
    result = gen._fill_template(template, {"domain": "engineering"})
    assert "engineering task" in result

def test_get_evaluation_criteria():
    gen = tdg.TestDatasetGenerator()
    criteria = gen._get_evaluation_criteria("reasoning")
    assert "logical_consistency" in criteria
    assert isinstance(criteria, list)

def test_get_evaluation_criteria_default():
    gen = tdg.TestDatasetGenerator()
    criteria = gen._get_evaluation_criteria("nonexistent")
    assert criteria == []

def test_fill_template_no_placeholder():
    gen = tdg.TestDatasetGenerator()
    template = "No placeholders here"
    result = gen._fill_template(template, {"domain": "irrelevant"})
    assert result == template

def test_generate_test_cases_empty_capabilities():
    gen = tdg.TestDatasetGenerator()
    cases = gen.generate_test_cases({"required_capabilities": []}, num_cases=2)
    assert cases == []
