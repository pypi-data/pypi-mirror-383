# completeness_check.py
from brainary.core.ops.action_op import ActionSession
from .evaluation_base import Evaluation

class CompletenessCheck(Evaluation):
    NAME = "Completeness Check"
    DESC = (
        "Ensure all required components, steps, or elements are present. "
        "Use this when output must satisfy a checklist or cover multiple criteria."
    )

    def evaluate(self, session: ActionSession) -> str:
        prompt = (
            "You are examining the completeness of the given output.\n\n"
            "Provide the following sections:\n"
            "- Required Elements: List of expected components for the task\n"
            "- Coverage Analysis: Which requirements are met vs missing\n"
            "- Completion Status: Percentage complete with explanation\n"
            "- Gap Assessment: Specific missing or incomplete elements\n"
            "- Recommendations: Priority items to address\n\n"
            "## Output Constraints\n"
            "- Do not use '#' for headings, as it is reserved as a system markup tag.\n"
            "- Use numbered or bullet points.\n"
            "- Do not include explanations, comments, or extra content."
        )
        return self.llm.request(session.messages + [("user", prompt)]).strip()
