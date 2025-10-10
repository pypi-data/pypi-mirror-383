# core/ops/ctx_op.py
from dataclasses import dataclass, field
from typing import Union, Dict

from brainary.core.ops.base_op import BaseOp

INDENT_UNIT = "  "

@dataclass(slots=True)
class CtxOp(BaseOp):
    name: str
    value: Union[str, Dict] = field(default_factory=dict)

    def flatten_dict(self, d: Dict, level=0):
        frags = []
        for k, v in d.items():
            if isinstance(v, str):
                frags.append(INDENT_UNIT * level + f"- {k}: {v}")
            elif isinstance(v, dict):
                frags.append(INDENT_UNIT * level + f"- {k}:\n{self.flatten_dict(v, level + 1)}")
        return "\n".join(frags)
    
    def render(self, **kwargs):
        lines = [
            f"#### {self.name.replace('_',' ').title()}"
        ]
        if isinstance(self.value, str):
            lines.append(self.value)
        else:
            lines.append(self.flatten_dict(self.value))
        return '\n'.join(lines)