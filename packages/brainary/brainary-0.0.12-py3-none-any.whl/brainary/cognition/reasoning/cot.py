# brainary/capabilities/reasoning/cot_reasoning.py
from brainary.cognition.reasoning.reasoning_base import Reasoning
from brainary.core.ops.action_op import ActionSession

class CoTReasoning(Reasoning):
    NAME = "Chain-of-Thought Reasoning"
    DESC = (
        "Breaks down complex reasoning into explicit, verifiable steps to ensure logical progression and catch errors. "
        "Makes implicit logical connections explicit and validates each step's soundness. "
        "Critical for complex problem-solving, mathematical proofs, and ensuring reasoning transparency."
    )

    def reason(self, session: ActionSession) -> str:
        prompt = (
            "You are a logical analysis expert. For THIS specific task/problem:\n\n"
            "Provide the following sections (exact headings):\n"
            "- Task Starting Point: exact information given in THIS case\n"
            "- Required Steps: numbered logical steps for THIS task\n"
            "- Progress Tracking: what changes/improves at each step\n"
            "- Step Validation: how to verify each step in THIS case\n"
            "- Chain Review: check step sequence fits THIS task\n\n"
            "Format constraints:\n"
            "- Do not use '#' for headings (system reserved)\n"
            "- Number all steps sequentially\n"
            "- For each step list: inference made, reason, validation\n"
            "- Mark any assumptions used in steps\n"
            "- End with key dependencies between steps"
        )
        return self.llm.request(session.messages + [("user", prompt)]).strip()
