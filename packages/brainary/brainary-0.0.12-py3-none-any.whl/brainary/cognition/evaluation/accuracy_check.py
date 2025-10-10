# accuracy_check.py
from brainary.core.ops.action_op import ActionSession
from .evaluation_base import Evaluation

class AccuracyCheck(Evaluation):
    NAME = "Accuracy Check"
    DESC = (
        "Compare outputs against reference or gold standard for correctness. "
        "Use this when verification against known answers, benchmarks, or expected values is required."
    )

    def evaluate(self, session: ActionSession) -> str:
        prompt = (
            "You are an evaluation agent focused on the current output's accuracy.\n\n"
            "Provide the following sections:\n"
            "- Reference Data: Relevant benchmarks for the specific task\n"
            "- Accuracy Analysis: Point-by-point comparison with references\n"
            "- Precision Score: Numeric rating (0.0-1.0) with brief explanation\n"
            "- Key Deviations: Notable differences from expected results\n"
            "- Confidence Level: Strength of the accuracy assessment\n\n"
            "## Output Constraints\n"
            "- Do not use '#' for headings, as it is reserved as a system markup tag.\n"
            "- Use numbered or bullet points.\n"
            "- Do not include explanations, comments, or extra content."
        )
        return self.llm.request(session.messages + [("user", prompt)]).strip()
