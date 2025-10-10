# brainary/capabilities/planning_base.py
from abc import abstractmethod
from typing import List

from brainary.cognition.base import Capability
from brainary.core.ops.action_op import ActionSession
from brainary.llm.llm import LLM

class Planning(Capability):
    NAME = "Abstract Planning"
    DESC = (
        "Abstract base class for Planning capabilities. "
        "Should implement plan(session: ActionSession) method."
    )

    def __init__(self, llm: LLM):
        super().__init__(llm)

    @abstractmethod
    def plan(self, session: ActionSession) -> str:
        raise NotImplementedError

    def perform(self, session: ActionSession) -> str:
        return self.plan(session)