# brainary/capabilities/planning/adaptive_planning.py
from typing import List
from brainary.core.ops.action_op import ActionSession
from brainary.llm.llm import LLM, AUX_MODEL
from .planning_base import Planning

class AdaptivePlanning(Planning):
    NAME = "Adaptive Planning"
    DESC = (
        "Creates flexible, feedback-driven plans that dynamically adjust to changing conditions and new information. "
        "Emphasizes monitoring points, feedback loops, and decision gates to enable rapid course correction. "
        "Ideal for agile projects, dynamic environments, and situations with evolving requirements or high uncertainty."
    )

    def __init__(self, llm: LLM):
        super().__init__(llm)

    def plan(self, session: ActionSession) -> str:
        prompt = (
            "You are an agile planning expert. Create a flexible plan that can adapt to changing conditions.\n\n"
            "Provide the following sections (exact headings):\n"
            "- Initial Plan: 3-5 high-level phases with clear outcomes\n"
            "- Monitoring Points: 2-3 key checkpoints to assess progress/changes\n"
            "- Adaptation Triggers: specific conditions that would require plan adjustment\n"
            "- Alternative Paths: 1-2 backup approaches for high-risk phases\n"
            "- Success Criteria: 2-3 clear indicators of successful completion\n\n"
            "Format constraints:\n"
            "- Do not use '#' for headings (system reserved)\n"
            "- Use short, action-oriented bullet points\n"
            "- Include estimated effort/complexity (Low/Med/High) for each phase\n"
            "- End with key assumptions/dependencies (1-3 items)"
        )
        if session.cur_feedback:
            response = self.llm.request(session.messages + [
                ("user", prompt),
                ("user", f"Consider this feedback from previous execution: \n```text\n{session.cur_feedback}\n```")
            ]).strip()
        else:
            response = self.llm.request(session.messages + [("user", prompt)]).strip()
        return response
