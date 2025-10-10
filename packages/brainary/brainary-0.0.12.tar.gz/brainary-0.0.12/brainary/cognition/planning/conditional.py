# brainary/capabilities/planning/conditional_planning.py
from typing import List
from brainary.core.ops.action_op import ActionSession
from brainary.llm.llm import LLM, AUX_MODEL
from .planning_base import Planning

class ConditionalPlanning(Planning):
    NAME = "Conditional Planning"
    DESC = (
        "Generates branching plans that explicitly handle different scenarios and outcomes using IF-THEN-ELSE structures. "
        "Maps decision points, conditions, and resulting action paths to handle uncertainty systematically. "
        "Ideal for complex workflows, decision automation, and handling variable inputs or states."
    )

    def __init__(self, llm: LLM):
        super().__init__(llm)

    def plan(self, session: ActionSession) -> str:
        """
        Generates a conditional plan that branches based on potential outcomes.
        """
        prompt = (
            "You are a conditional planning expert. Create a branching plan that handles different scenarios.\n\n"
            "Provide the following sections (exact headings):\n"
            "- Core Flow: the default/happy path steps (3-5 items)\n"
            "- Decision Points: key places where the path may branch (2-3 points)\n"
            "- Conditions: specific checks/tests at each decision point\n"
            "- Branch Actions: what to do for each condition outcome\n"
            "- Merge Points: where branches rejoin the main flow\n\n"
            "Format constraints:\n"
            "- Do not use '#' for headings (system reserved)\n"
            "- Use IF condition THEN action ELSE alternative format\n"
            "- Number decision points (D1, D2, etc.)\n"
            "- For each branch specify: condition, actions, and exit criteria\n"
            "- End with a coverage check of critical scenarios"
        )
        if session.cur_feedback:
            response = self.llm.request(session.messages + [
                ("user", prompt),
                ("user", f"Consider this feedback from previous execution: \n```text\n{session.cur_feedback}\n```")
            ]).strip()
        else:
            response = self.llm.request(session.messages + [("user", prompt)]).strip()
        return response