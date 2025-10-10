# brainary/capabilities/reasoning/deductive_reasoning.py
from brainary.cognition.reasoning.reasoning_base import Reasoning
from brainary.core.ops.action_op import ActionSession

class DeductiveReasoning(Reasoning):
    NAME = "Deductive Reasoning"
    DESC = (
        "Uses formal logical rules to derive guaranteed conclusions from given premises. "
        "Ensures validity through strict application of logical principles and explicit tracking of assumptions. "
        "Essential for proofs, formal verification, and rigorous argument analysis."
    )

    def reason(self, session: ActionSession) -> str:
        prompt = (
            "You are a logical proof expert. For THIS specific task/argument:\n\n"
            "Provide the following sections (exact headings):\n"
            "- Task Premises: exact facts/rules stated in THIS case\n"
            "- Relevant Logic: rules that apply to THESE premises\n"
            "- Proof Steps: derive conclusions from THESE specifics\n"
            "- Step Results: what each step proves about THIS case\n"
            "- Proof Check: verify THIS deduction is complete/valid\n\n"
            "Format constraints:\n"
            "- Do not use '#' for headings (system reserved)\n"
            "- Number all premises and conclusions\n"
            "- For each step cite: premises used, rule applied\n"
            "- Mark any hidden assumptions\n"
            "- End with proof completeness check"
        )
        return self.llm.request(session.messages + [("user", prompt)]).strip()
