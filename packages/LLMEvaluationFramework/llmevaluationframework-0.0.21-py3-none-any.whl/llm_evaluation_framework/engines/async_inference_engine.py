import asyncio
from typing import Any, Dict, List, Callable


class AsyncInferenceEngine:
    """
    Asynchronous inference engine to run multiple model inferences concurrently.
    """

    def __init__(self, model_callable: Callable[[Any], Any]):
        """
        :param model_callable: A callable that takes input data and returns inference result.
        """
        self.model_callable = model_callable

    async def _run_single(self, input_data: Any) -> Any:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.model_callable, input_data)

    async def run_batch(self, batch_data: List[Any]) -> List[Any]:
        """
        Run inference on a batch of inputs concurrently.
        """
        tasks = [self._run_single(data) for data in batch_data]
        return await asyncio.gather(*tasks)

    def run(self, batch_data: List[Any]) -> List[Any]:
        """
        Synchronous wrapper for async batch inference.
        """
        return asyncio.run(self.run_batch(batch_data))
