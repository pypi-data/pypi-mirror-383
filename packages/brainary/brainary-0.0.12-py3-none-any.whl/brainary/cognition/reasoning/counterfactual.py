# brainary/capabilities/reasoning/counterfactual_reasoning.py
from brainary.cognition.reasoning.reasoning_base import Reasoning
from brainary.core.ops.action_op import ActionSession

class CounterfactualReasoning(Reasoning):
    NAME = "Counterfactual Reasoning"
    DESC = (
        "Systematically explores alternative scenarios by varying key conditions or decisions to understand causality and options. "
        "Maps out consequence chains and identifies critical decision points or assumptions. "
        "Vital for risk assessment, decision analysis, and learning from past events."
    )

    def reason(self, session: ActionSession) -> str:
        prompt = (
            "You are a scenario analysis expert. For THIS specific task/situation:\n\n"
            "Provide the following sections (exact headings):\n"
            "- Current State: exact details of THIS case now\n"
            "- Changeable Factors: what could be different in THIS situation\n"
            "- Key What-Ifs: how THIS case changes under different conditions\n"
            "- Chain Reactions: specific effects in THIS context\n"
            "- Decision Points: where changes matter most for THIS case\n\n"
            "Format constraints:\n"
            "- Do not use '#' for headings (system reserved)\n"
            "- For each scenario specify: changed factor, implications, likelihood\n"
            "- Use IF [change] THEN [effects] BECAUSE [reason] format\n"
            "- Mark compound effects across scenarios\n"
            "- End with most important scenarios to consider"
        )
        return self.llm.request(session.messages + [("user", prompt)]).strip()
