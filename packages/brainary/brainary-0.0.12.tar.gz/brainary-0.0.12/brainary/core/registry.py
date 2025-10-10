# brainary/capabilities/registry.py
import logging

from typing import TypeVar, Generic, Type, Dict
T = TypeVar("T")

class StrategyRegistry(Generic[T]):
    """Generic registry for any type of strategy."""
    def __init__(self):
        self._registry: Dict[str, Type[T]] = {}

    def register(self, strategy_cls: Type[T]):
        logging.info(f"{strategy_cls.NAME} is registered.")
        if not isinstance(strategy_cls, type):
            raise TypeError("Only classes can be registered.")
        if not hasattr(strategy_cls, "NAME"):
            raise AttributeError("Strategy class must have a NAME attribute.")
        self._registry[strategy_cls.NAME] = strategy_cls
        return strategy_cls

    def list_all(self) -> str:
        lines = []
        for _, cls in self._registry.items():
            desc = getattr(cls, "DESC", "")
            lines.append(f"### {cls.NAME}\n{desc}\n")
        return "\n".join(lines)

    def validate(self, name: str) -> bool:
        return name in self._registry

    def get(self, name: str) -> Type[T]:
        return self._registry.get(name, None)

    def create(self, name: str, *args, **kwargs) -> T:
        cls = self.get(name)
        if cls is None:
            raise ValueError(f"Capability '{name}' not found in registry.")
        return cls(*args, **kwargs)



"""
Define registries.
"""
from brainary.cognition.abstraction.abstraction_base import Abstraction
from brainary.cognition.critical_thinking.critical_thinking_base import CriticalThinking
from brainary.cognition.evaluation.evaluation_base import Evaluation
from brainary.cognition.planning.planning_base import Planning
from brainary.cognition.reasoning.reasoning_base import Reasoning
from brainary.cognition.simulation.simulation_base import Simulation

from brainary.solvers.base import ProblemSolving

ABSTRACTION_REGISTRY = StrategyRegistry[Abstraction]()
CRITICAL_THINKING_REGISTRY = StrategyRegistry[CriticalThinking]()
EVALUATION_REGISTRY = StrategyRegistry[Evaluation]()
PLANNING_REGISTRY = StrategyRegistry[Planning]()
REASONING_REGISTRY = StrategyRegistry[Reasoning]()
SIMULATION_REGISTRY = StrategyRegistry[Simulation]()

CAPABILITIES: Dict[str, StrategyRegistry] = {
    "abstraction": ABSTRACTION_REGISTRY,
    "critical_thinking": CRITICAL_THINKING_REGISTRY,
    "evaluation": EVALUATION_REGISTRY,
    "planning": PLANNING_REGISTRY,
    "reasoning": REASONING_REGISTRY,
    "simulation": SIMULATION_REGISTRY
}

PROBLEM_SOLVING_REGISTRY = StrategyRegistry[ProblemSolving]()
    

def scan():
    # This import is important to ensure the retristry can discover the problem solving and capability strategies.
    import importlib
    import pkgutil
    import brainary.cognition
    import brainary.solvers
    def import_all_submodules(package):
        """
        Recursively import all submodules in a package.
        """
        if not hasattr(package, "__path__"):
            # Single file module, nothing to traverse
            return
        for loader, name, is_pkg in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
            importlib.import_module(name)
            if is_pkg:
                # Recursively traverse subpackage
                subpackage = importlib.import_module(name)
                import_all_submodules(subpackage)
    import_all_submodules(brainary.cognition)
    import_all_submodules(brainary.solvers)
    
    logging.info(f"[VM] Scanning available strategies for abstraction...")    
    for cls in Abstraction.__subclasses__():
        ABSTRACTION_REGISTRY.register(cls)
    logging.info(f"[VM] Scanning available strategies for critical thinking...")    
    for cls in CriticalThinking.__subclasses__():
        CRITICAL_THINKING_REGISTRY.register(cls)
    logging.info(f"[VM] Scanning available strategies for evaluation...")    
    for cls in Evaluation.__subclasses__():
        EVALUATION_REGISTRY.register(cls)
    logging.info(f"[VM] Scanning available strategies for planning...")    
    for cls in Planning.__subclasses__():
        PLANNING_REGISTRY.register(cls)
    logging.info(f"[VM] Scanning available strategies for reasoning...")    
    for cls in Reasoning.__subclasses__():
        REASONING_REGISTRY.register(cls)
    logging.info(f"[VM] Scanning available strategies for simulation...")    
    for cls in Simulation.__subclasses__():
        SIMULATION_REGISTRY.register(cls)
    
    logging.info(f"[VM] Scanning available strategies for problem solving...")    
    for cls in ProblemSolving.__subclasses__():
        PROBLEM_SOLVING_REGISTRY.register(cls)