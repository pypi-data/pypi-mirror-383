# brainary/capabilities/critical_thinking_base.py
from abc import abstractmethod
from typing import List

from brainary.cognition.base import Capability
from brainary.core.ops.action_op import ActionSession

class CriticalThinking(Capability):
    NAME = "Abstract Critical Thinking"
    DESC = (
        "Abstract base class for Critical Thinking capabilities. "
        "Should implement think(session: ActionSession) method."
    )

    def __init__(self, llm):
        super().__init__(llm)

    @abstractmethod
    def think(self, session: ActionSession) -> str:
        raise NotImplementedError

    def perform(self, session: ActionSession) -> str:
        return self.think(session)
