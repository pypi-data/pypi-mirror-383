from typing import List, Dict

from brainary.core.ops.action_op import ActionSession
from .critical_thinking_base import CriticalThinking


class SixThinkingHatsCriticalThinking(CriticalThinking):
    NAME = "Six Thinking Hats"
    DESC = (
        "Structured multi-perspective analysis using de Bono's Six Thinking Hats. "
        "Separately surfaces facts, emotions, risks, benefits, creative alternatives, and process control to produce a balanced assessment and ideas. "
        "Useful for group facilitation, decision framing, and generating practical creative options."
    )

    def think(self, session: ActionSession) -> str:
        prompt = (
            "Apply the Six Thinking Hats method to the task. For each hat, provide 2–5 concise bullets focused on the hat's role.\n\n"
            "Hats (exact headings):\n"
            "- White Hat (facts & data): list verified facts, missing data, and data needs.\n"
            "- Red Hat (feelings & intuition): capture likely emotional reactions or stakeholder intuitions.\n"
            "- Black Hat (risks & problems): list feasible risks, failure modes, and critical weaknesses.\n"
            "- Yellow Hat (benefits & positives): list benefits, opportunities, and supporting arguments.\n"
            "- Green Hat (creativity & alternatives): propose 3 alternative ideas or angles (brief).\n"
            "- Blue Hat (process & control): recommend next steps, decision criteria, or governance.\n\n"
            "Output constraints:\n"
            "- Do not use '#' for headings.\n"
            "- Use short bulleted lists (1–2 sentence bullets).\n"
            "- Avoid long explanations; be action-oriented.\n"
            "- If any hat has no relevant content, write 'None' under that heading."
        )
        return self.llm.request(session.messages + [("user", prompt)]).strip()