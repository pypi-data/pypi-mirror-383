from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseRegistry(ABC):
    """
    Abstract base class for registries in the LLM Evaluation Framework.
    Registries store and manage available models, datasets, or other resources.
    """

    def __init__(self):
        self._items: Dict[str, Dict[str, Any]] = {}

    @abstractmethod
    def register(self, item_id: str, item_info: Dict[str, Any]) -> None:
        """Register a new item in the registry."""
        pass

    @abstractmethod
    def get(self, item_id: str) -> Dict[str, Any]:
        """Retrieve an item from the registry by its ID."""
        pass

    @abstractmethod
    def list_items(self) -> List[str]:
        """List all registered item IDs."""
        pass

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
