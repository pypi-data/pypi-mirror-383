from typing import List, Dict
from .critical_thinking_base import CriticalThinking
from brainary.core.ops.action_op import ActionSession


class RootCauseAnalysisCriticalThinking(CriticalThinking):
    NAME = "Root Cause Analysis (Five Whys)"
    DESC = (
        "Performs concise root-cause analysis using an iterative 'Five Whys' approach to surface underlying causes and actionable remediations. "
        "Includes evidence checks and recommended corrective actions where possible."
    )

    def think(self, session: ActionSession) -> str:
        prompt = (
            "Perform a Five Whys root cause analysis for the reported problem. For each Why, give a concise causal statement (1 line) and, if available, cite the evidence or observation that supports it.\n\n"
            "Format:\n"
            "- Why 1: <one-line cause> (evidence: <short note or 'unknown'>)\n"
            "- Why 2: ...\n"
            "- Why 3: ...\n"
            "- Why 4: ...\n"
            "- Why 5: ...\n"
            "- Root Cause: <one-line summary>\n\n"
            "After the Five Whys, include a short Remediation section with 1–3 targeted actions and one quick validation check for each action.\n\n"
            "Output constraints:\n"
            "- Do not use '#' for headings.\n"
            "- Keep each Why to one concise sentence.\n"
            "- If evidence is unavailable, state 'unknown' and suggest a quick data check."
        )
        return self.llm.request(session.messages + [("user", prompt)]).strip()