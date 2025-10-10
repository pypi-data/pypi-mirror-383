# peer_review.py
from brainary.core.ops.action_op import ActionSession
from .evaluation_base import Evaluation

class PeerReview(Evaluation):
    NAME = "Peer Review"
    DESC = (
        "Simulate peer review to assess clarity, quality, and compliance with best practices. "
        "Use this in formal quality control, structured evaluation, or professional standards."
    )

    def evaluate(self, session: ActionSession) -> str:
        prompt = (
            "You are conducting a professional peer review of the solution.\n\n"
            "Provide the following sections:\n"
            "- Methodology Review: Assessment of approach and methods\n"
            "- Quality Analysis: Evaluation against professional standards\n"
            "- Notable Strengths: Key positive aspects (2-3 points)\n"
            "- Areas for Enhancement: Specific improvement opportunities\n"
            "- Overall Assessment: Summary judgment with rationale\n\n"
            "## Output Constraints\n"
            "- Do not use '#' for headings, as it is reserved as a system markup tag.\n"
            "- Maintain professional, constructive tone.\n"
            "- Use numbered or bullet points.\n"
            "- Do not include explanations, comments, or extra content."
        )
        return self.llm.request(session.messages + [("user", prompt)]).strip()
