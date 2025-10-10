from typing import List, Dict

from brainary.core.ops.action_op import ActionSession
from .critical_thinking_base import CriticalThinking


class RedTeamCriticalThinking(CriticalThinking):
    NAME = "Debiasing / Red Teaming"
    DESC = (
        "Simulates adversarial review and debiasing: identifies hidden assumptions, cognitive biases, and failure modes. "
        "Produces targeted counterarguments, attack scenarios, and concrete mitigation suggestions to improve robustness, safety, and fairness. "
        "Use this when you need to stress-test claims, designs, or policies against adversarial or biased reasoning."
    )

    def think(self, session: ActionSession) -> str:
        prompt = (
            "You are an adversarial reviewer focused on uncovering biases and failure modes. Given the task and context, perform the following:\n\n"
            "Process:\n"
            "1) List explicit and implicit assumptions (1–6 items) and rate each as High/Medium/Low risk.\n"
            "2) Enumerate potential biases or blind spots (e.g., sampling, confirmation, scale) and provide brief examples or attack scenarios.\n"
            "3) Provide concrete counterarguments or test-cases that would falsify the claim or expose failure.\n"
            "4) Recommend specific mitigations, safe guards, or validation steps (tools, checks, data requirements).\n\n"
            "Output sections (exact headings): Assumptions, Biases & Attack Scenarios, Counterarguments/Tests, Mitigations.\n\n"
            "Output constraints:\n"
            "- Do not use '#' for headings.\n"
            "- Use numbered or bulleted lists.\n"
            "- Keep items concise; include one short example per bias or test.\n"
            "- End with a 1–2 sentence overall risk assessment (Low/Medium/High)."
        )
        return self.llm.request(session.messages + [("user", prompt)]).strip()

