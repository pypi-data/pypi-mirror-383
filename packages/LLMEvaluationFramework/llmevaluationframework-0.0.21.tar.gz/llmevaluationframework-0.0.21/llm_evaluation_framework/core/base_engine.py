from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseEngine(ABC):
    """
    Abstract base class for all engines in the LLM Evaluation Framework.
    Engines are responsible for executing a specific type of task, such as
    model inference or generating suggestions.
    """

    def __init__(self, model_registry: Any):
        self.model_registry = model_registry

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute the engine's main function."""
        pass


class BaseAsyncEngine(BaseEngine):
    """
    Abstract base class for engines that support asynchronous execution.
    """

    @abstractmethod
    async def execute_async(self, *args, **kwargs) -> Any:
        """Execute the engine's main function asynchronously."""
        pass
