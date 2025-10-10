from typing import List, Dict

from brainary.core.ops.action_op import ActionSession
from .critical_thinking_base import CriticalThinking


class ReflectiveEquilibriumCriticalThinking(CriticalThinking):
    NAME = "Reflective Equilibrium / Dialectic"
    DESC = (
        "Applies dialectical reasoning to bring particular judgments and general principles into coherent balance. "
        "Iteratively tests principles against counterexamples and refines proposals to improve consistency, fairness, and justification. Ideal for ethical trade-offs and conflicting-value decisions."
    )

    def think(self, session: ActionSession) -> str:
        prompt = (
            "Use reflective equilibrium to reconcile specific judgments with broader principles. Work through the stages below and provide concise outputs under the listed headings.\n\n"
            "Stages and required output (exact headings):\n"
            "- Initial Judgments: list the specific intuitions or verdicts at stake (2–5 items).\n"
            "- Relevant Principles: list general principles or rules that apply (1–4 items).\n"
            "- Counterexamples & Tensions: provide short counterexamples or conflicts between judgments and principles.\n"
            "- Adjustments: propose specific adjustments to either judgments or principles (1–3), with brief rationale.\n"
            "- Equilibrium: state a concise reconciled position and any residual trade-offs or uncertainties.\n\n"
            "Output constraints:\n"
            "- Do not use '#' for headings.\n"
            "- Use short bullets and keep items directly relevant to the task.\n"
            "- End with a one-sentence recommended next step (policy change, further reflection, or testing)."
        )
        return self.llm.request(session.messages + [("user", prompt)]).strip()
