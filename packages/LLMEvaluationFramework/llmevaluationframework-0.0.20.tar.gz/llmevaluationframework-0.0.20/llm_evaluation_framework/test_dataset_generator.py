"""
Test Dataset Generator for LLM Evaluation Framework.
Generates synthetic test cases for various evaluation capabilities.
"""

import random
from typing import Dict, List, Any


class TestDatasetGenerator:
    """
    Generator for synthetic test datasets across various evaluation capabilities.
    
    Provides template-based generation for reasoning, creativity, factual,
    instruction, and coding test cases.
    """
    
    def __init__(self) -> None:
        """Initialize templates for test case generation"""
        self.templates = {
            "reasoning": [
                "Explain step by step how to solve the following problem: {problem}",
                "What are the logical steps to address this issue: {problem}",
                "Break down this complex question into simpler parts: {problem}"
            ],
            "creativity": [
                "Write a creative story about {topic}",
                "Generate an imaginative description of {topic}",
                "Create an original poem about {topic}"
            ],
            "factual": [
                "What are the key facts about {topic}?",
                "Provide accurate information about {topic}",
                "Summarize the most important details about {topic}"
            ],
            "instruction": [
                "How do I accomplish this task: {task}",
                "Provide instructions for {task}",
                "What are the steps to complete {task}"
            ],
            "coding": [
                "Write code to solve this problem: {problem}",
                "How would you implement a solution for {problem} in Python?",
                "Create a function that handles {task}"
            ]
        }
    
    def generate_test_cases(self, use_case_requirements: Dict[str, Any], num_cases: int = 10) -> List[Dict[str, Any]]:
        test_cases = []
        required_capabilities = use_case_requirements.get("required_capabilities", [])
        
        for capability in required_capabilities:
            if capability in self.templates:
                for i in range(num_cases):
                    template = random.choice(self.templates[capability])
                    filled_template = self._fill_template(template, use_case_requirements)
                    test_cases.append({
                        "id": f"{capability}_{i}",
                        "type": capability,
                        "prompt": filled_template,
                        "evaluation_criteria": self._get_evaluation_criteria(capability)
                    })
        
        return test_cases
    
    def _fill_template(self, template: str, use_case_requirements: Dict[str, Any]) -> str:
        domain = use_case_requirements.get("domain", "general")
        if "{problem}" in template:
            return template.replace("{problem}", f"a {domain} problem")
        elif "{topic}" in template:
            return template.replace("{topic}", f"a {domain} topic")
        elif "{task}" in template:
            return template.replace("{task}", f"a {domain} task")
        return template
    
    def _get_evaluation_criteria(self, capability: str) -> List[str]:
        criteria = {
            "reasoning": ["logical_consistency", "step_completeness", "correctness"],
            "creativity": ["originality", "engagement", "coherence"],
            "factual": ["accuracy", "completeness", "relevance"],
            "instruction": ["clarity", "actionability", "completeness"],
            "coding": ["correctness", "efficiency", "readability"]
        }
        return criteria.get(capability, [])
