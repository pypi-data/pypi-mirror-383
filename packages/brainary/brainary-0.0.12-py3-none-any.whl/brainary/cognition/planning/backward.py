# brainary/capabilities/planning/backward_planning.py
from typing import List
from brainary.core.ops.action_op import ActionSession
from brainary.llm.llm import LLM, AUX_MODEL
from .planning_base import Planning

class BackwardPlanning(Planning):
    NAME = "Backward Planning"
    DESC = (
        "Goal-driven planning that works backward from the desired outcome to identify necessary preconditions and dependencies. "
        "Systematically maps required capabilities, resources, and intermediate states to reach the goal. "
        "Best for well-defined objectives where intermediate requirements need to be clearly understood."
    )

    def __init__(self, llm: LLM):
        super().__init__(llm)

    def plan(self, session: ActionSession) -> str:
        """
        Generates a plan by reasoning backward from the goal.
        """
        prompt = (
            "You are an expert goal-driven planner. Working backward from the goal, create a detailed dependency chain.\n\n"
            "Provide the following sections (exact headings):\n"
            "- Goal State: precise description of the desired outcome\n"
            "- Required Capabilities: technical skills, resources, or tools needed\n"
            "- Dependency Chain: work backward through required states/conditions\n"
            "- Initial Requirements: starting conditions that must be true\n"
            "- Risk Points: potential blockers or critical dependencies\n\n"
            "Format constraints:\n"
            "- Do not use '#' for headings (system reserved)\n"
            "- Number steps in reverse order (goal = step 1)\n"
            "- For each step list: Action, Required State, and Dependencies\n"
            "- Mark any assumptions about initial state\n"
            "- End with validation checks for each major step"
        )
        if session.cur_feedback:
            response = self.llm.request(session.messages + [
                ("user", prompt),
                ("user", f"Consider this feedback from previous execution: \n```text\n{session.cur_feedback}\n```")
            ]).strip()
        else:
            response = self.llm.request(session.messages + [("user", prompt)]).strip()
        return response