from typing import List, Dict
from .critical_thinking_base import CriticalThinking
from brainary.core.ops.action_op import ActionSession


class SocraticQuestioningCriticalThinking(CriticalThinking):
    NAME = "Socratic Questioning"
    DESC = (
        "Uses disciplined Socratic questioning to probe and strengthen reasoning by exposing gaps, hidden assumptions, and weak evidence. "
        "Produces targeted, answerable follow-up questions and suggested evidence or tests to close gaps."
    )

    def think(self, session: ActionSession) -> str:
        prompt = (
            "Use Socratic questioning to generate focused probes for the task/context. Produce clear, concise items under each category below.\n\n"
            "Categories (exact headings):\n"
            "- Clarification Questions: short, specific questions that remove ambiguity.\n"
            "- Assumption Probes: identify and question implicit assumptions (1–4 items).\n"
            "- Evidence Probes: what evidence would increase confidence; suggest 2 concrete tests or data checks.\n"
            "- Viewpoint Exploration: outline 2 alternative perspectives and the main argument each would make.\n"
            "- Implication Probes: list likely consequences or downstream effects to consider.\n"
            "- Questioning the Question: suggest reframings or better-focused questions (1–2).\n\n"
            "Output constraints:\n"
            "- Do not use '#' for headings.\n"
            "- Use short bullets; each item should be directly actionable (a single question or test).\n"
            "- At the end, include a one-line suggested next step (investigate, test, reframe)."
        )
        return self.llm.request(session.messages + [("user", prompt)]).strip()