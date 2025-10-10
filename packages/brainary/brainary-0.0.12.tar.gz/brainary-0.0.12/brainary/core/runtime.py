from typing import Any
from brainary.core.ops.action_op import ActionOp
from brainary.memory.memory import Memory


class Runtime:
    def __init__(self):
        self.heap: Memory = Memory()
        self.execution = []
        self.session = []
        self.state = "idle"  # or "pre-execution", "executing", "post-execution"
        
    def reset_session(self):
        self.session = []
        self.state = "idle"
    
    def push_message(self, role: str, message: str):
        self.session.append((role, message))

    def record_execution(self, op: ActionOp, kwargs:Any, pre_analysis:dict, result:Any, cost:Any):
        self.execution.append((op, kwargs, pre_analysis, result, cost))




    