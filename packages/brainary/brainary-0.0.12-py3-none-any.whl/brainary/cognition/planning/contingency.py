# brainary/capabilities/planning/contingency_planning.py
from typing import List
from brainary.core.ops.action_op import ActionSession
from brainary.llm.llm import LLM, AUX_MODEL
from .planning_base import Planning

class ContingencyPlanning(Planning):
    NAME = "Contingency Planning"
    DESC = (
        "Creates robust plans with pre-defined fallback strategies and recovery actions for potential failures. "
        "Focuses on risk mitigation, early warning indicators, and clear fallback protocols. "
        "Essential for critical operations, disaster response, and high-reliability scenarios."
    )

    def __init__(self, llm: LLM):
        super().__init__(llm)

    def plan(self, session: ActionSession) -> str:
        """
        Generates a plan with contingencies for possible failures or deviations.
        """
        prompt = (
            "You are a contingency planning expert. Create a comprehensive plan with fallbacks.\n\n"
            "Provide the following sections (exact headings):\n"
            "- Primary Plan: main sequence of steps (4-6 items)\n"
            "- Risk Points: identify critical steps where failures could occur\n"
            "- Early Warnings: specific indicators that signal potential issues\n"
            "- Fallback Actions: clear steps to take if primary plan fails\n"
            "- Recovery Paths: how to return to main plan or gracefully abort\n\n"
            "Format constraints:\n"
            "- Do not use '#' for headings (system reserved)\n"
            "- Use numbered steps for primary plan\n"
            "- For each risk point specify: trigger conditions, immediate actions, and next steps\n"
            "- Include timing/resource requirements for fallback actions\n"
            "- End with communication protocols for each contingency"
        )
        if session.cur_feedback:
            response = self.llm.request(session.messages + [
                ("user", prompt),
                ("user", f"Consider this feedback from previous execution: \n```text\n{session.cur_feedback}\n```")
            ]).strip()
        else:
            response = self.llm.request(session.messages + [("user", prompt)]).strip()
        return response