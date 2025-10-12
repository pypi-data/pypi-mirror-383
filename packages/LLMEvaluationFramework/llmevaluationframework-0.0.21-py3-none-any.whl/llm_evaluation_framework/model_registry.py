import random

class ModelRegistry:
    def __init__(self):
        self.models = {
            "gpt-4": {
                "name": "GPT-4",
                "provider": "OpenAI",
                "capabilities": ["text", "reasoning", "creativity"],
                "context_window": 128000,
                "modalities": ["text"],
                "api_cost_input": 0.03,
                "api_cost_output": 0.06,
                "max_tokens": 4096,
                "rate_limits": {"rpm": 10000, "tpm": 1000000}
            },
            "claude-3-opus": {
                "name": "Claude 3 Opus",
                "provider": "Anthropic",
                "capabilities": ["text", "reasoning", "long_context"],
                "context_window": 200000,
                "modalities": ["text"],
                "api_cost_input": 0.015,
                "api_cost_output": 0.075,
                "max_tokens": 4096,
                "rate_limits": {"rpm": 5000, "tpm": 500000}
            },
            "llama-3-70b": {
                "name": "Llama 3 70B",
                "provider": "Meta",
                "capabilities": ["text", "reasoning"],
                "context_window": 8192,
                "modalities": ["text"],
                "api_cost_input": 0.0025,
                "api_cost_output": 0.0025,
                "max_tokens": 4096,
                "rate_limits": {"rpm": 10000, "tpm": 1000000}
            },
            "gemini-ultra": {
                "name": "Gemini Ultra",
                "provider": "Google",
                "capabilities": ["text", "multimodal", "reasoning"],
                "context_window": 32768,
                "modalities": ["text", "image"],
                "api_cost_input": 0.02,
                "api_cost_output": 0.04,
                "max_tokens": 4096,
                "rate_limits": {"rpm": 15000, "tpm": 1000000}
            }
        }
    
    def get_model(self, model_id):
        return self.models.get(model_id, {})
    
    def list_models(self):
        return list(self.models.keys())
