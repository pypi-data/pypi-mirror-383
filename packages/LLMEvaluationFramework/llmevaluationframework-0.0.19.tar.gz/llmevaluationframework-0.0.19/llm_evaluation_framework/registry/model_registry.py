from typing import Any, Dict, List
from llm_evaluation_framework.core.base_registry import BaseRegistry


class ModelRegistry(BaseRegistry):
    """
    Concrete implementation of BaseRegistry for managing model instances.
    """

    def __init__(self):
        self._models: Dict[str, Any] = {}

    def register(self, name: str, item: Any) -> None:
        if name in self._models:
            raise ValueError(f"Model '{name}' is already registered.")
        self._models[name] = item

    def get(self, name: str) -> Any:
        if name not in self._models:
            raise KeyError(f"Model '{name}' not found in registry.")
        return self._models[name]

    def list_items(self) -> List[str]:
        return list(self._models.keys())

    # Alias methods to match test expectations
    def register_model(self, name: str, model: Any) -> None:
        """Alias for register to match test naming."""
        return self.register(name, model)

    def get_model(self, name: str) -> Any:
        """Alias for get to match test naming."""
        return self.get(name)

    def list_models(self) -> List[str]:
        """Alias for list_items to match test naming."""
        return self.list_items()

    def unregister_model(self, name: str) -> None:
        """Remove a model from the registry."""
        if name in self._models:
            del self._models[name]
        else:
            raise KeyError(f"Model '{name}' not found in registry.")
