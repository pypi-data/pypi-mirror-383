# brainary/capabilities/evaluation_base.py
from abc import abstractmethod
from typing import List

from brainary.cognition.base import Capability
from brainary.core.ops.action_op import ActionSession

class Evaluation(Capability):
    NAME = "Abstract Evaluation"
    DESC = (
        "Abstract base class for Evaluation capabilities. "
        "Should implement evaluate(session: ActionSession) method."
    )

    def __init__(self, llm):
        super().__init__(llm)

    @abstractmethod
    def evaluate(self, session: ActionSession) -> str:
        raise NotImplementedError

    def perform(self, session: ActionSession) -> str:
        return self.evaluate(session)
