# red_team_evaluation.py
from brainary.core.ops.action_op import ActionSession
from .evaluation_base import Evaluation

class RedTeamEvaluation(Evaluation):
    NAME = "Red Team Evaluation"
    DESC = (
        "Actively challenge the output to identify flaws, errors, or hidden assumptions. "
        "Use this when outputs may contain vulnerabilities or require adversarial testing."
    )

    def evaluate(self, session: ActionSession) -> str:
        prompt = (
            "You are performing adversarial testing of the given solution.\n\n"
            "Provide the following sections:\n"
            "- Vulnerability Scan: Systematic check for weak points\n"
            "- Edge Cases: Boundary conditions that may cause issues\n"
            "- Hidden Assumptions: Implicit beliefs that need validation\n"
            "- Attack Vectors: Potential exploitation pathways\n"
            "- Defense Recommendations: Specific hardening measures\n\n"
            "## Output Constraints\n"
            "- Do not use '#' for headings, as it is reserved as a system markup tag.\n"
            "- Focus on actionable findings.\n"
            "- Use numbered or bullet points.\n"
            "- Do not include explanations, comments, or extra content."
        )
        return self.llm.request(session.messages + [("user", prompt)]).strip()
