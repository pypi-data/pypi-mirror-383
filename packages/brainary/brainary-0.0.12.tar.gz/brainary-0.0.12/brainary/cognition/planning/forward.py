# brainary/capabilities/planning/forward_planning.py
from typing import List
from brainary.core.ops.action_op import ActionSession
from brainary.llm.llm import LLM, AUX_MODEL
from .planning_base import Planning

class ForwardPlanning(Planning):
    NAME = "Forward Planning"
    DESC = (
        "Creates step-by-step plans starting from the current state, carefully tracking available actions and their effects. "
        "Ensures each step builds on verified outcomes from previous steps. "
        "Best for concrete tasks where the initial state is well-understood and actions have predictable results."
    )

    def __init__(self, llm: LLM):
        super().__init__(llm)

    def plan(self, session: ActionSession) -> str:
        """
        Generates a plan using forward-chaining reasoning from initial conditions to goal.
        """
        prompt = (
            "You are a forward planning expert. Create a progressive plan from current state to goal.\n\n"
            "Provide the following sections (exact headings):\n"
            "- Initial State: current conditions and available resources\n"
            "- Action Sequence: ordered steps with clear state changes\n"
            "- Progress Markers: observable outcomes after each step\n"
            "- Goal Alignment: how final state achieves objectives\n\n"
            "Format constraints:\n"
            "- Do not use '#' for headings (system reserved)\n"
            "- Number steps sequentially\n"
            "- For each step specify: Action, New State, and Verification\n"
            "- Mark any required resources or tools\n"
            "- End with completion criteria"
        )
        if session.cur_feedback:
            response = self.llm.request(session.messages + [
                ("user", prompt),
                ("user", f"Consider this feedback from previous execution: \n```text\n{session.cur_feedback}\n```")
            ]).strip()
        else:
            response = self.llm.request(session.messages + [("user", prompt)]).strip()
        return response