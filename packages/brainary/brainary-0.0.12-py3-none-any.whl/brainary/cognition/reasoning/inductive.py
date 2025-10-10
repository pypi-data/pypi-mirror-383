# brainary/capabilities/reasoning/inductive_reasoning.py
from brainary.cognition.reasoning.reasoning_base import Reasoning
from brainary.core.ops.action_op import ActionSession

class InductiveReasoning(Reasoning):
    NAME = "Inductive Reasoning"
    DESC = (
        "Identifies patterns and regularities in specific observations to form general principles or predictions. "
        "Uses statistical thinking and careful pattern analysis to move from examples to broader rules. "
        "Critical for scientific discovery, trend analysis, and making predictions from limited data."
    )

    def reason(self, session: ActionSession) -> str:
        prompt = (
            "You are a pattern analysis expert. For THIS specific task/dataset:\n\n"
            "Provide the following sections (exact headings):\n"
            "- Available Data: concrete examples/facts from THIS case\n"
            "- Case Patterns: regularities in THIS specific dataset\n"
            "- Task Rules: generalizations that fit THIS case (2-3)\n"
            "- Pattern Support: how THIS data backs each rule\n"
            "- Rule Strength: how well rules fit THIS situation\n\n"
            "Format constraints:\n"
            "- Do not use '#' for headings (system reserved)\n"
            "- Group related observations\n"
            "- For each pattern note: frequency, exceptions, context\n"
            "- Rate confidence (Strong/Moderate/Weak)\n"
            "- End with suggested validation tests"
        )
        return self.llm.request(session.messages + [("user", prompt)]).strip()
