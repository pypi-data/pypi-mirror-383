# brainary/capabilities/planning/htn_planning.py
from typing import List
from brainary.core.ops.action_op import ActionSession
from brainary.llm.llm import LLM, AUX_MODEL
from .planning_base import Planning

class HTNPlanning(Planning):
    NAME = "Hierarchical Task Network (HTN) Planning"
    DESC = (
        "Decomposes complex goals into a structured hierarchy of increasingly specific subtasks. "
        "Maps task relationships, dependencies, and execution order while maintaining clear abstraction levels. "
        "Ideal for large projects, complex workflows, or any task requiring organized breakdown from strategy to tactics."
    )

    def __init__(self, llm: LLM):
        super().__init__(llm)

    def plan(self, session: ActionSession) -> str:
        """
        Generates a hierarchical decomposition of the task into subtasks.
        """
        prompt = (
            "You are a hierarchical planning expert. Create a multi-level task breakdown.\n\n"
            "Provide the following sections (exact headings):\n"
            "- Strategic Goals: top-level objectives (2-3)\n"
            "- Major Components: key workstreams per goal\n"
            "- Detailed Tasks: specific actions per component\n"
            "- Dependencies: relationships between components\n"
            "- Integration Points: where components interact\n\n"
            "Format constraints:\n"
            "- Do not use '#' for headings (system reserved)\n"
            "- Use hierarchical numbering (1, 1.1, 1.1.1)\n"
            "- Maximum 3 levels of depth\n"
            "- For each level specify: Outcome, Subtasks, Owner Role\n"
            "- Mark parallel vs sequential relationships\n"
            "- End with execution sequence across components"
        )
        if session.cur_feedback:
            response = self.llm.request(session.messages + [
                ("user", prompt),
                ("user", f"Consider this feedback from previous execution: \n```text\n{session.cur_feedback}\n```")
            ]).strip()
        else:
            response = self.llm.request(session.messages + [("user", prompt)]).strip()
        return response