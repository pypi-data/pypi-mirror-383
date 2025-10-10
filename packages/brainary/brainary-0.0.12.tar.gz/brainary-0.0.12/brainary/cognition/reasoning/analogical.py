# brainary/capabilities/reasoning/analogical_reasoning.py
from brainary.cognition.reasoning.reasoning_base import Reasoning
from brainary.core.ops.action_op import ActionSession

class AnalogicalReasoning(Reasoning):
    NAME = "Analogical Reasoning"
    DESC = (
        "Maps knowledge from familiar domains to understand or solve problems in unfamiliar contexts. "
        "Identifies structural similarities between source and target domains to transfer insights and solution patterns. "
        "Powerful for innovation, teaching, and problem-solving when direct experience is limited."
    )

    def reason(self, session: ActionSession) -> str:
        prompt = (
            "You are an analogical reasoning expert. For THIS specific task/problem:\n\n"
            "Provide the following sections (exact headings):\n"
            "- Task Decomposition: break current task into key structural elements\n"
            "- Relevant Analogies: 2-3 similar situations matching THIS task's structure\n"
            "- Direct Mapping: how each analogy element matches THIS task\n"
            "- Solution Transfer: concrete steps from analogies for THIS case\n"
            "- Application Gaps: aspects of THIS task not covered by analogies\n\n"
            "Format constraints:\n"
            "- Do not use '#' for headings (system reserved)\n"
            "- For each source domain specify: domain, key features, relevance\n"
            "- Use parallel structures to show mappings clearly\n"
            "- Mark any assumptions about structural similarity\n"
            "- End with concrete applications from analogy"
        )
        return self.llm.request(session.messages + [("user", prompt)]).strip()
