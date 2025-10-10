# brainary/capabilities/simulation_base.py
from abc import abstractmethod
from typing import List

from brainary.cognition.base import Capability

class Simulation(Capability):
    NAME = "Abstract Simulation"
    DESC = (
        "Abstract base class for Simulation capabilities. "
        "Should implement simulate(task: str) method."
    )

    def __init__(self, llm):
        super().__init__(llm)

    @abstractmethod
    def simulate(self, task: str):
        raise NotImplementedError

    def perform(self, task: str):
        return self.simulate(task)
