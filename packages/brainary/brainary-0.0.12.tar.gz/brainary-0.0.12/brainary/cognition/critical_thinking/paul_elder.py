from typing import List, Dict
from brainary.cognition.critical_thinking.critical_thinking_base import CriticalThinking
from brainary.core.ops.action_op import ActionSession


class PaulElderCriticalThinking(CriticalThinking):
    NAME = "Paul–Elder Framework"
    DESC = (
        "Structured evaluation using the Paul–Elder model: breaks down thinking into the eight elements of thought and evaluates each against intellectual standards. "
        "Helps surface weaknesses in reasoning and produces prioritized recommendations to improve argument quality and rigor."
    )

    def think(self, session: ActionSession) -> str:
        prompt = (
            "Apply the Paul–Elder framework to the task. For each element of thought, provide a brief assessment (1–3 bullets) and a short rating: Good / Needs Work / Missing.\n\n"
            "Elements of thought (exact headings): Purpose, Question, Information, Inference, Concepts, Assumptions, Implications, Point of View.\n\n"
            "For each element, also note any of the intellectual standards that are relevant (clarity, accuracy, precision, relevance, depth, breadth, logic, fairness) and flag which standards are failing, if any.\n\n"
            "After the element assessments, include a Recommendations section with 3 prioritized actions to improve reasoning quality.\n\n"
            "Output constraints:\n"
            "- Do not use '#' for headings.\n"
            "- Use concise bullets and the exact headings listed above.\n"
            "- End with a one-paragraph summary judgment (2–3 sentences)."
        )
        return self.llm.request(session.messages + [("user", prompt)]).strip()