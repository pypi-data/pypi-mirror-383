# core/ops/action_op.py
from dataclasses import dataclass, field
import json
import logging
from typing import Any, List, Dict, Union, Optional

from brainary.core.ops.base_op import BaseOp
from brainary.core.ops.ctx_op import CtxOp

MAX_ENERGY = 100000


@dataclass(slots=True)
class ActionOp(BaseOp):
    instruction: str
    instruction_planned: str = field(init=False)
    params: tuple = field(default_factory=tuple)
    contexts: List[CtxOp] = field(default_factory=list)
    tools: List[callable] = field(default_factory=list)
    input_constraints: Dict[str, Any] = field(default_factory=dict)
    output_constraints: Dict[str, Any] = field(default_factory=dict)
    callbacks: List[callable] = field(default_factory=list)
    attentions: List[Dict[str, Any]] = field(default_factory=list)
    energy: int = MAX_ENERGY
    problem_solving: Optional[str] = None
    critical_thinking: Optional[str] = None
    planning: Optional[str] = None
    reasoning: Optional[str] = None
    evaluation: Optional[str] = None
    memory_recall: Optional[str] = None
    simulation: Optional[str] = None
    abstraction: Optional[str] = None
    expectation: Optional[float] = None
    return_in_json: bool = False

    def __post_init__(self):
        self.instruction_planned = self.instruction
        # Validate strategies against registries if set
        from brainary.core.registry import CAPABILITIES, PROBLEM_SOLVING_REGISTRY
        if self.problem_solving and not PROBLEM_SOLVING_REGISTRY.validate(self.problem_solving):
            raise ValueError(f"Invalid problem_solving strategy: {self.problem_solving}")
        for cap in ["critical_thinking", "planning", "reasoning", "evaluation", "memory_recall", "simulation", "abstraction"]:
            strat = getattr(self, cap)
            if strat and cap in CAPABILITIES and not CAPABILITIES[cap].validate(strat):
                raise ValueError(f"Invalid {cap} strategy: {strat}")

    def update_planning(self, instruction: str):
        self.instruction_planned = instruction

    def rollback_planning(self):
        self.instruction_planned = self.instruction

    def _check_input_constraints(self, **kwargs):
        for name, value in self.input_constraints.items():
            # TODO: validate constraint
            pass

    def render(self, **kwargs) -> str:
        """
        Render the instruction with contexts, arguments, output constraints,
        and capability traces (critical thinking, planning, reasoning,
        evaluation, simulation), including strategy names.
        """
        segments = []

        kwargs_copy = dict(kwargs)

        # --- Instruction ---
        segments.append(f"### Instruction\n{self.instruction_planned}\n\n")

        # --- Contexts ---
        if self.contexts:
            contexts = "\n\n".join(ctx.render() for ctx in self.contexts)
            segments.append(f"### Contexts\n{contexts}\n\n")

        # --- Pre-analysis traces with strategy names ---
        for cap in ["abstraction", "critical_thinking", "evaluation", "planning", "reasoning", "simulation"]:
            strategy_name = getattr(self, cap, None)
            trace_name = f"{cap}_trace"
            trace = kwargs_copy.pop(trace_name, None)

            if trace and not (cap == "planning" and trace == self.instruction_planned):
                display_name = cap.replace("_", " ").title() + " Trace"
                segments.append(f"### {display_name} (Strategy: {strategy_name})\n")
                if isinstance(trace, dict):
                    trace_str = json.dumps(trace, indent=2)
                else:
                    trace_str = str(trace)
                # Truncate if too long
                if len(trace_str) > 10000:
                    trace_str = trace_str[:10000] + "\n<truncated>"
                segments.append(f"{trace_str}\n\n")

        # --- Arguments ---
        if kwargs_copy:
            arguments = []
            for k, v in kwargs_copy.items():
                k_fmt = " ".join(w[0].upper() + w[1:] for w in k.split("_"))
                arguments.append(f"#### {k_fmt}\n{v}")
            arguments = "\n\n".join(arguments)
            segments.append(f"### Arguments\n{arguments}\n\n")

        # --- Output Constraints ---
        if self.output_constraints:
            if isinstance(self.output_constraints, dict):
                constraints = "\n".join(f"- {k}: {v}" for k, v in self.output_constraints.items())
            elif isinstance(self.output_constraints, (list, tuple, set)):
                constraints = "\n".join(f"- {v}" for v in self.output_constraints)
            else:
                constraints = self.output_constraints
            segments.append(f"### Output Constraints\n{constraints}")

        return "".join(segments)
    
    def light_render(self, **kwargs) -> str:
        """
        A simplified render method for estimation purposes, focusing on the instruction and arguments.
        """
        segments = []

        # --- Instruction ---
        segments.append(f"### Instruction\n{self.instruction_planned}\n\n")

        # --- Contexts ---
        if self.contexts:
            contexts = "\n\n".join(ctx.render() for ctx in self.contexts)
            segments.append(f"### Contexts\n{contexts}\n\n")
        
        kwargs_copy = dict(kwargs)
        # --- Arguments ---
        if kwargs_copy:
            arguments = []
            for k, v in kwargs_copy.items():
                k_fmt = " ".join(w[0].upper() + w[1:] for w in k.split("_"))
                arguments.append(f"#### {k_fmt}\n{v}")
            arguments = "\n\n".join(arguments)
            segments.append(f"### Arguments\n{arguments}\n\n")

        return "".join(segments)

    def resolve(self, response):
        if self.return_in_json:
            try:
                return json.loads(response.strip())
            except json.JSONDecodeError as e:
                logging.error(f"JSON resolve failed: {e}")
                return {}
        return response


class ActionSession:
    def __init__(self, action: ActionOp, last_feedback: str=None, **kwargs):
        self.action = action
        self.kwargs = kwargs
        self.messages = []
        self.task_type = "general"  # or "coding", "math", etc.
        self.state = "idle"  # or "pre-execution", "executing", "post-execution"
        self.problem_solving = None  # currently selected problem solving strategy
        self.capability = None  # currently selected capability
        self.strategy = None  # currently selected strategy
        self.last_feedback = last_feedback  # last feedback from monitor
        self.cur_feedback = None  # feedback from monitor for rescheduling
        self.used_capabilities = []  # track capabilities used in this session
        self.used_strategies = {}  # track strategies used for each capability
        self.outcomes = {}  # track outcomes for each capability used

    def prepare(self):
        self.messages = [("user", self.action.render(**self.kwargs))]
        self.state = "pre-execution"

    def reset(self):
        self.messages = []
        self.state = "idle"

    def push_message(self, role: str, message: str):
        self.messages.append((role, message))

    def get_messages(self):
        return self.messages
        
    def record_capability_use(self, capability: str, strategy: str = None, outcome: float = None):
        """
        Record the use of a capability, its strategy, and outcome.
        
        Args:
            capability (str): The capability that was used
            strategy (str, optional): The specific strategy used for this capability
            outcome (float, optional): The outcome score for this capability use
        """
        if capability not in self.used_capabilities:
            self.used_capabilities.append(capability)
        
        if strategy is not None:
            self.used_strategies[capability] = strategy
            
        if outcome is not None:
            self.outcomes[capability] = outcome
            
    def get_capability_outcomes(self) -> dict:
        """Get all recorded capability outcomes for this session."""
        return self.outcomes.copy()
    
    def get_capability_strategies(self) -> dict:
        """Get all recorded capability-strategy mappings for this session."""
        return self.used_strategies.copy()
        
    def has_used_capability(self, capability: str, strategy: str = None) -> bool:
        """
        Check if a capability (and optionally a specific strategy) has been used.
        
        Args:
            capability (str): The capability to check
            strategy (str, optional): If provided, check if this specific strategy was used
            
        Returns:
            bool: True if the capability (and strategy if specified) was used
        """
        if capability not in self.used_capabilities:
            return False
        if strategy is None:
            return True
        return self.used_strategies.get(capability) == strategy
    
