# brainary/capabilities/abstraction_base.py
from abc import abstractmethod
from typing import List

from brainary.cognition.base import Capability

class Abstraction(Capability):
    NAME = "Abstract Abstraction"
    DESC = (
        "Abstract base class for Abstraction capabilities. "
        "Should implement abstract(task: str) method."
    )

    def __init__(self, llm):
        super().__init__(llm)

    @abstractmethod
    def abstract(self, task: str):
        raise NotImplementedError

    def perform(self, task: str):
        return self.abstract(task)
