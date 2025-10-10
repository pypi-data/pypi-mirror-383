# brainary/capabilities/reasoning/commonsense_reasoning.py
from brainary.cognition.reasoning.reasoning_base import Reasoning
from brainary.core.ops.action_op import ActionSession

class CommonsenseReasoning(Reasoning):
    NAME = "Commonsense Reasoning"
    DESC = (
        "Applies everyday knowledge, cultural understanding, and practical heuristics to interpret situations and predict outcomes. "
        "Leverages implicit human knowledge about physics, social norms, and typical patterns of behavior. "
        "Essential for natural interaction, understanding context, and making practical judgments."
    )

    def reason(self, session: ActionSession) -> str:
        prompt = (
            "You are a practical reasoning expert. For THIS specific task/situation:\n\n"
            "Provide the following sections (exact headings):\n"
            "- Task Context: how THIS case fits into everyday experience\n"
            "- Missing Information: unstated but important factors for THIS case\n"
            "- Relevant Rules: commonsense principles that apply HERE\n"
            "- Expected Outcome: how THIS situation normally develops\n"
            "- Action Guide: practical next steps for THIS case\n\n"
            "Format constraints:\n"
            "- Do not use '#' for headings (system reserved)\n"
            "- List key assumptions about normal behavior/outcomes\n"
            "- Note any cultural/contextual dependencies\n"
            "- Include everyday examples that illustrate points\n"
            "- End with practical dos and don'ts (2-3 each)"
        )
        return self.llm.request(session.messages + [("user", prompt)]).strip()
