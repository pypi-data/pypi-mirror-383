"""
Auto Suggestion Engine for LLM Evaluation Framework.
Provides intelligent model recommendations based on evaluation results.
"""

from typing import Dict, List, Any, Set


class AutoSuggestionEngine:
    """
    Engine for providing intelligent model recommendations based on evaluation results.
    
    Uses weighted scoring across performance, efficiency, cost, and suitability
    to rank models and provide actionable suggestions.
    """
    
    def __init__(self, model_registry: Any) -> None:
        """
        Initialize the auto suggestion engine.
        
        Args:
            model_registry: Registry containing model configurations
        """
        self.model_registry = model_registry
        self.weights = {
            "performance": 0.4,
            "efficiency": 0.2,
            "cost": 0.2,
            "suitability": 0.2
        }
    
    def suggest_model(self, evaluation_results: List[Dict[str, Any]], use_case_requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        scored_models = []
        
        for model_result in evaluation_results:
            score = self._calculate_model_score(model_result, use_case_requirements)
            scored_models.append({
                "model_id": model_result["model_id"],
                "model_info": model_result["model_info"],
                "evaluation_results": model_result,
                "score": score,
                "strengths": self._identify_strengths(model_result),
                "weaknesses": self._identify_weaknesses(model_result, use_case_requirements)
            })
        
        scored_models.sort(key=lambda x: x["score"], reverse=True)
        return scored_models
    
    def _calculate_model_score(self, model_result: Dict[str, Any], use_case_requirements: Dict[str, Any]) -> float:
        aggregate_metrics = model_result["aggregate_metrics"]
        performance_score = sum(aggregate_metrics.values()) / len(aggregate_metrics) if aggregate_metrics else 0
        max_acceptable_time = use_case_requirements.get("max_response_time", 10)
        efficiency_score = 1 - min(1, aggregate_metrics["avg_response_time"] / max_acceptable_time)
        budget = use_case_requirements.get("budget", 10)
        cost_score = 1 - min(1, aggregate_metrics["total_cost"] / budget)
        required_capabilities = set(use_case_requirements.get("required_capabilities", []))
        model_capabilities = set(model_result["model_info"].get("capabilities", []))
        suitability_score = len(required_capabilities.intersection(model_capabilities)) / len(required_capabilities) if required_capabilities else 1
        
        total_score = (
            self.weights["performance"] * performance_score +
            self.weights["efficiency"] * efficiency_score +
            self.weights["cost"] * cost_score +
            self.weights["suitability"] * suitability_score
        )
        return total_score
    
    def _identify_strengths(self, model_result: Dict[str, Any]) -> List[str]:
        strengths = []
        aggregate_metrics = model_result["aggregate_metrics"]
        best_criteria = max(aggregate_metrics.items(), key=lambda x: x[1]) if aggregate_metrics else None
        if best_criteria and best_criteria[1] > 0.8:
            strengths.append(f"Excellent {best_criteria[0]}")
        return strengths
    
    def _identify_weaknesses(self, model_result: Dict[str, Any], _use_case_requirements: Dict[str, Any]) -> List[str]:
        weaknesses = []
        aggregate_metrics = model_result["aggregate_metrics"]
        worst_criteria = min(aggregate_metrics.items(), key=lambda x: x[1]) if aggregate_metrics else None
        if worst_criteria and worst_criteria[1] < 0.5:
            weaknesses.append(f"Needs improvement in {worst_criteria[0]}")
        return weaknesses
