from brainary.cognition.planning.planning_base import Planning
from brainary.core.ops.action_op import ActionSession
from brainary.llm.llm import LLM

class DirectPlanning(Planning):
    NAME = "Direct Planning"
    DESC = (
        "Lightweight planning strategy for simple, well-defined tasks that don't require complex decomposition. "
        "Produces clear, actionable steps while avoiding unnecessary complexity. "
        "Ideal for straightforward tasks or quick execution plans."
    )

    def plan(self, session: ActionSession) -> str:
        prompt = (
            "You are a streamlined planning expert. Create a clear, minimal plan optimized for direct execution.\n\n"
            "Provide the following (exact headings):\n"
            "- Analysis: should this task be broken down? (Yes/No + one-line why)\n"
            "- Action Steps: 3-7 clear, concrete steps if breakdown needed\n"
            "- Quick Checks: 1-2 validation points for the steps\n\n"
            "Format constraints:\n"
            "- Do not use '#' for headings (system reserved)\n"
            "- Use imperative statements for actions\n"
            "- Keep each step focused and actionable\n"
            "- If no breakdown needed, state why in one line"
        )
        if session.cur_feedback:
            response = self.llm.request(session.messages + [
                ("user", prompt),
                ("user", f"Consider this feedback from previous execution: \n```text\n{session.cur_feedback}\n```")
            ]).strip()
        else:
            response = self.llm.request(session.messages + [("user", prompt)]).strip()
        return response