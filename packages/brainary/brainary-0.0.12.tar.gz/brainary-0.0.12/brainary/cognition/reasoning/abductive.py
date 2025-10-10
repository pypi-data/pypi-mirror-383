# brainary/capabilities/reasoning/abductive_reasoning.py
from brainary.cognition.reasoning.reasoning_base import Reasoning
from brainary.core.ops.action_op import ActionSession

class AbductiveReasoning(Reasoning):
    NAME = "Abductive Reasoning"
    DESC = (
        "Develops and evaluates hypotheses to explain observations, focusing on finding the simplest and most likely explanations. "
        "Uses evidence strength, parsimony, and explanatory power to rank competing theories. "
        "Essential for diagnosis, investigation, and scientific discovery where complete data isn't available."
    )

    def reason(self, session: ActionSession) -> str:
        prompt = (
            "You are a diagnostic expert. Given the current task/context, use abductive reasoning to explain what's observed.\n\n"
            "Provide the following sections (exact headings):\n"
            "- Task Analysis: extract specific observations needing explanation\n"
            "- Key Patterns: list the main facts/patterns from THIS task (2-4 items)\n"
            "- Competing Hypotheses: propose 2-4 explanations specific to THIS case\n"
            "- Evidence Mapping: link task details to/against each hypothesis\n"
            "- Best Explanation: identify simplest theory that fits THIS case\n\n"
            "Format constraints:\n"
            "- Do not use '#' for headings (system reserved)\n"
            "- Use bullet points for lists\n"
            "- For each hypothesis note: explanation, key evidence, assumptions\n"
            "- End with confidence level (High/Medium/Low) in best explanation"
        )
        return self.llm.request(session.messages + [("user", prompt)]).strip()
