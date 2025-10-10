# Divergent Thinking
# Convergent Thinking
# Critical Thinking (Brainstorming, Validity Check, Critique, Aggregation)
# Triz-40 Principles 


from abc import ABCMeta, abstractmethod
from typing import Dict, List, Type

from brainary.core.ops.action_op import ActionOp
from brainary.core.ops.action_op import ActionSession
from brainary.llm.llm import LLM, AUX_MODEL
from brainary.solvers.base import ProblemSolving

    
class DirectLLMCall(ProblemSolving):
    NAME = "Direct LLM Call"
    DESC = "Invoke LLMs directly without applying complex problem-solving strategies. This approach is best suited for simple, straightforward instructions or when no suitable strategy exists."
    
    def __init__(self, llm: LLM):
        super().__init__(llm)
    
    def solve(self, action: ActionSession, pre_analysis: dict = None, **kwargs):
        action.push_message("user", "Execute the task and give the final answer.")
        return self.llm.request(action.messages, tools=action.action.tools)