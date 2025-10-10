# core/ops/base_op.py
from abc import ABC, abstractmethod
from functools import lru_cache  # For memoization if needed

class BaseOp(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def render(self, **kwargs) -> str:
        raise NotImplementedError

    def resolve(self, response: str):
        return response

    def to_json(self) -> dict:
        """Serialize to JSON for persistence."""
        return {"type": self.__class__.__name__, "data": vars(self)}