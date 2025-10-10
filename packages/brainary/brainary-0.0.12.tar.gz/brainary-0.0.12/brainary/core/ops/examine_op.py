# core/ops/examine_op.py
from dataclasses import dataclass, field
import json
from typing import Any, List, Dict, Union, Optional

from brainary.core.ops.base_op import BaseOp
from brainary.core.ops.ctx_op import CtxOp

@dataclass(slots=True)
class ExamineOp(BaseOp):
    condition: str
    params: tuple = field(default_factory=tuple)
    contexts: List[CtxOp] = field(default_factory=list)
    attentions: List[Dict[str, Any]] = field(default_factory=list)
    thinking: Optional[str] = None
    instruction: str = field(init=False)
    instruction_planned: str = field(init=False)
    planning: Optional[str] = None
    critical_thinking: Optional[str] = None
    reasoning: Optional[str] = None
    evaluation: Optional[str] = None
    simulation: Optional[str] = None
    abstraction: Optional[str] = None
    problem_solving: Optional[str] = None
    energy: int = 1000

    def __post_init__(self):
        self.instruction = f"Judge: {self.condition}"
        self.instruction_planned = self.instruction
        # Validate strategies against registries if set
        from brainary.core.registry import CAPABILITIES, PROBLEM_SOLVING_REGISTRY
        if self.problem_solving and not PROBLEM_SOLVING_REGISTRY.validate(self.problem_solving):
            raise ValueError(f"Invalid problem_solving strategy: {self.problem_solving}")
        for cap in ["critical_thinking", "planning", "reasoning", "evaluation", "simulation", "abstraction"]:
            strat = getattr(self, cap)
            if strat and cap in CAPABILITIES and not CAPABILITIES[cap].validate(strat):
                raise ValueError(f"Invalid {cap} strategy: {strat}")

    def update_planning(self, instruction: str):
        self.instruction_planned = instruction

    def rollback_planning(self):
        self.instruction_planned = self.instruction

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

            if trace:
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
        segments.append("## Output Constraints\nOnly output YES or NO without any comments or explanations.")
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
        

    def resolve(self, response) -> bool:
        return response.lower().strip() == "yes"