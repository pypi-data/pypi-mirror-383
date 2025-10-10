# brainary/capabilities/planning/critical_path_planning.py
from typing import List
from brainary.core.ops.action_op import ActionSession
from brainary.llm.llm import LLM, AUX_MODEL
from .planning_base import Planning

class CriticalPathPlanning(Planning):
    NAME = "Critical Path Planning"
    DESC = (
        "Identifies and optimizes the sequence of tasks that directly determine the minimum completion time. "
        "Maps dependencies, slack time, and resource constraints to highlight the critical execution path. "
        "Essential for project scheduling, parallel execution, and minimizing delivery time."
    )

    def __init__(self, llm: LLM):
        super().__init__(llm)

    def plan(self, session: ActionSession) -> str:
        """
        Generates a plan highlighting the critical path steps and dependencies.
        """
        prompt = (
            "You are a critical path analysis expert. Create a time-optimized execution plan.\n\n"
            "Provide the following sections (exact headings):\n"
            "- Task Network: all required steps with dependencies\n"
            "- Critical Path: sequence that determines minimum duration\n"
            "- Time Estimates: duration for each task (in consistent units)\n"
            "- Parallel Tracks: tasks that can run concurrently\n"
            "- Resource Requirements: key resources needed per task\n\n"
            "Format constraints:\n"
            "- Do not use '#' for headings (system reserved)\n"
            "- Use task IDs (T1, T2, etc.) for clear references\n"
            "- For each task specify: ID, Duration, Dependencies, Resources\n"
            "- Mark critical path tasks with [CP]\n"
            "- Include slack time for non-critical tasks\n"
            "- End with total duration and critical resource peaks"
        )
        if session.cur_feedback:
            response = self.llm.request(session.messages + [
                ("user", prompt),
                ("user", f"Consider this feedback from previous execution: \n```text\n{session.cur_feedback}\n```")
            ]).strip()
        else:
            response = self.llm.request(session.messages + [("user", prompt)]).strip()
        return response