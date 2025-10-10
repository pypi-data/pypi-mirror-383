# brainary/capabilities/planning/means_end_planning.py
from typing import List
from brainary.core.ops.action_op import ActionSession
from brainary.llm.llm import LLM, AUX_MODEL
from .planning_base import Planning

class MeansEndPlanning(Planning):
    NAME = "Means-End Planning"
    DESC = (
        "Links concrete actions (means) to specific desired outcomes (ends) through systematic gap analysis. "
        "Focuses on identifying the most efficient bridges between current state and sub-goals. "
        "Effective for complex goals where the path isn't obvious but intermediate states can be clearly defined."
    )

    def __init__(self, llm: LLM):
        super().__init__(llm)

    def plan(self, session: ActionSession) -> str:
        """
        Generates a plan by breaking the goal into sub-goals and identifying actions for each.
        """
        prompt = (
            "You are a means-end analysis expert. Create a gap-bridging action plan.\n\n"
            "Provide the following sections (exact headings):\n"
            "- Goal Decomposition: break main goal into 3-5 sub-goals\n"
            "- Current State: relevant existing conditions per sub-goal\n"
            "- Gap Analysis: key differences between current and desired states\n"
            "- Action Mapping: specific means to bridge each gap\n"
            "- Integration: how sub-goal achievements combine\n\n"
            "Format constraints:\n"
            "- Do not use '#' for headings (system reserved)\n"
            "- For each sub-goal specify: Desired State, Gap, Required Actions\n"
            "- List means in priority order\n"
            "- Mark any shared means across sub-goals\n"
            "- End with verification method per sub-goal"
        )
        if session.cur_feedback:
            response = self.llm.request(session.messages + [
                ("user", prompt),
                ("user", f"Consider this feedback from previous execution: \n```text\n{session.cur_feedback}\n```")
            ]).strip()
        else:
            response = self.llm.request(session.messages + [("user", prompt)]).strip()
        return response