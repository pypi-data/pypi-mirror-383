# brainary/cognition/base.py
from abc import ABCMeta, abstractmethod
from typing import List
from brainary.core.ops.action_op import ActionSession

class Capability(metaclass=ABCMeta):
    NAME = "Generic Capability"
    DESC = "Abstract base class for all cognitive capabilities. Should be extended by concrete implementations."

    def __init__(self, llm):
        self.llm = llm

    @abstractmethod
    def perform(self, session: ActionSession) -> str:
        """Execute the cognitive capability on a given task."""
        raise NotImplementedError
