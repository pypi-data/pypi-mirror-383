# critical_reflection.py
from brainary.core.ops.action_op import ActionSession
from .evaluation_base import Evaluation

class CriticalReflection(Evaluation):
    NAME = "Critical Reflection"
    DESC = (
        "Evaluate outputs by considering broader implications, consequences, or systemic impacts. "
        "Use this in ethical, strategic, or high-stakes decision-making contexts."
    )

    def evaluate(self, session: ActionSession) -> str:
        prompt = (
            "You are conducting in-depth reflection on the provided output.\n\n"
            "Provide the following sections:\n"
            "- Immediate Effects: Direct consequences of the solution\n"
            "- Broader Impact: Long-term and systemic implications\n"
            "- Stakeholder Analysis: Effects on different groups\n"
            "- Risk Assessment: Potential negative outcomes\n"
            "- Strategic Insights: Key learnings and considerations\n\n"
            "## Output Constraints\n"
            "- Do not use '#' for headings, as it is reserved as a system markup tag.\n"
            "- Present insights in clear, structured format.\n"
            "- Use numbered or bullet points.\n"
            "- Do not include explanations, comments, or extra content."
        )
        return self.llm.request(session.messages + [("user", prompt)]).strip()
