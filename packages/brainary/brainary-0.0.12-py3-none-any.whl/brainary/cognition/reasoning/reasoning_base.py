# brainary/capabilities/reasoning_base.py
from abc import abstractmethod
from typing import List

from brainary.cognition.base import Capability
from brainary.core.ops.action_op import ActionSession

class Reasoning(Capability):
    NAME = "Abstract Reasoning"
    DESC = (
        "Abstract base class for Reasoning capabilities. "
        "Should implement reason(session: ActionSession) method."
    )

    def __init__(self, llm):
        super().__init__(llm)

    @abstractmethod
    def reason(self, session: ActionSession) -> str:
        raise NotImplementedError

    def perform(self, session: ActionSession) -> str:
        return self.reason(session)
