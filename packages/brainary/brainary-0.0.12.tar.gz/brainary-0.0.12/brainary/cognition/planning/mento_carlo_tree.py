# brainary/capabilities/planning/mcts_planning.py
from typing import List
from brainary.core.ops.action_op import ActionSession
from brainary.llm.llm import LLM, AUX_MODEL
from .planning_base import Planning

class MCTSPlanning(Planning):
    NAME = "Monte Carlo Tree Search Planning"
    DESC = (
        "Evaluates multiple possible action sequences through statistical sampling to find robust, high-value paths. "
        "Balances exploration of new strategies with exploitation of known good approaches. "
        "Ideal for complex decision spaces with uncertain outcomes or where optimal solutions are computationally intractable."
    )

    def __init__(self, llm: LLM):
        super().__init__(llm)

    def plan(self, session: ActionSession) -> str:
        """
        Generates a plan by performing Monte Carlo simulations of possible action sequences
        and selecting the sequence with the best expected outcome.
        """
        prompt = (
            "You are a Monte Carlo search expert. Create a statistically-optimized action plan.\n\n"
            "Provide the following sections (exact headings):\n"
            "- Action Space: possible actions at each decision point\n"
            "- Success Metrics: how to score different outcomes\n"
            "- Top Sequences: 2-3 highest-value action chains\n"
            "- Risk Analysis: failure modes and their probabilities\n"
            "- Recommended Path: best balance of value and risk\n\n"
            "Format constraints:\n"
            "- Do not use '#' for headings (system reserved)\n"
            "- For each sequence specify: Actions, Expected Value, Confidence\n"
            "- Mark high-risk decision points\n"
            "- Include min/max/expected outcomes\n"
            "- End with early-stopping conditions"
        )
        if session.cur_feedback:
            response = self.llm.request(session.messages + [
                ("user", prompt),
                ("user", f"Consider this feedback from previous execution: \n```text\n{session.cur_feedback}\n```")
            ]).strip()
        else:
            response = self.llm.request(session.messages + [("user", prompt)]).strip()
        return response