from typing import List, Dict

from brainary.core.ops.action_op import ActionSession
from .critical_thinking_base import CriticalThinking


class BloomCriticalThinking(CriticalThinking):
    NAME = "Bloom’s Taxonomy"
    DESC = (
        "Apply Bloom's higher-order cognitive skills to examine a task or problem. "
        "Performs structured Analysis (break down into component parts), Evaluation (assess quality, validity, and trade-offs), "
        "and Creation (synthesize alternatives or novel solutions). "
        "Use this when you need deep, instructional, or innovation-focused reasoning with clear, actionable outputs."
    )

    def think(self, session: ActionSession) -> str:
        prompt = (
            "You are an expert analyst. Using the task and conversation context provided, apply Bloom's higher-order taxonomy and produce a concise, actionable response.\n\n"
            "Process:\n"
            "1) Analyze: break the task into clear components or sub-problems and list key facts or inputs.\n"
            "2) Evaluate: for each component, assess strengths, weaknesses, assumptions, and uncertainties; call out important trade-offs.\n"
            "3) Create: propose 2–4 alternative solutions, improvements, or syntheses with brief pros/cons and a recommended next step.\n\n"
            "Output sections (exact headings): Analyze, Evaluate, Create. Under Create include a one-line Recommendation.\n\n"
            "Output constraints:\n"
            "- Do not use '#' for headings (system reserved).\n"
            "- Use clear numbered or bulleted lists under each heading.\n"
            "- Keep each bullet concise (1–2 sentences).\n"
            "- At the end, list any key uncertainties or assumptions (1–3 items)."
        )
        return self.llm.request(session.messages + [("user", prompt)]).strip()

