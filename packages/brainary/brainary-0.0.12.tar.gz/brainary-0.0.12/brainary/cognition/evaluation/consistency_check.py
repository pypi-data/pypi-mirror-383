# consistency_check.py
from brainary.core.ops.action_op import ActionSession
from .evaluation_base import Evaluation

class ConsistencyCheck(Evaluation):
    NAME = "Consistency Check"
    DESC = (
        "Verify that outputs are logically consistent with constraints, prior facts, or rules. "
        "Use this when correctness depends on logical coherence or adherence to structured rules, e.g., calculations, schedules, sequences."
    )

    def evaluate(self, session: ActionSession) -> str:
        prompt = (
            "You are an evaluation agent. Analyze the execution output for logical consistency.\n\n"
            "## Guidelines\n"
            "- Check for contradictions or violations of constraints.\n"
            "- Highlight inconsistencies with concise reasoning.\n"
            "- Output only 'consistent' or 'inconsistent' with a brief rationale.\n\n"
            "## Output Constraints\n"
            "- Do not use '#' for headings, as it is reserved as a system markup tag.\n"
            "- Use numbered or bullet points.\n"
            "- Do not include explanations, comments, or extra content."
        )
        return self.llm.request(session.messages + [("user", prompt)]).strip()
