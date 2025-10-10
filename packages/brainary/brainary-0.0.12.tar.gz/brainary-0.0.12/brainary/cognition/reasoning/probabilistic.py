# brainary/capabilities/reasoning/probabilistic_reasoning.py
from brainary.cognition.reasoning.reasoning_base import Reasoning
from brainary.core.ops.action_op import ActionSession

class ProbabilisticReasoning(Reasoning):
    NAME = "Probabilistic Reasoning"
    DESC = (
        "Analyzes uncertainty and likelihood systematically to make informed predictions and decisions. "
        "Uses probability theory, Bayesian updating, and uncertainty quantification to reason about outcomes. "
        "Essential for risk assessment, forecasting, and decision-making with incomplete information."
    )

    def reason(self, session: ActionSession) -> str:
        prompt = (
            "You are a probabilistic analysis expert. For THIS specific task:\n\n"
            "Provide the following sections (exact headings):\n"
            "- Task Probabilities: initial odds for THIS case\n"
            "- Case Uncertainties: unknowns in THIS situation (2-4)\n"
            "- IF-THEN Analysis: how THIS case probabilities change\n"
            "- Data Effects: how THIS evidence updates odds\n"
            "- Decision Implications: probability-weighted recommendations\n\n"
            "Format constraints:\n"
            "- Do not use '#' for headings (system reserved)\n"
            "- Express probabilities as percentages or decimals\n"
            "- For each outcome list: P(outcome), key factors, confidence\n"
            "- Show conditional probability relationships\n"
            "- End with expected value calculations"
        )
        return self.llm.request(session.messages + [("user", prompt)]).strip()
