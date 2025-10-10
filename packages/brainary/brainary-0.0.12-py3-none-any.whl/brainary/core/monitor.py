# core/monitor.py
import logging
from typing import Any, Dict
from brainary.core.ops.action_op import ActionOp
from brainary.core.runtime import Runtime
from brainary.core.ops.action_op import ActionSession
from brainary.experience.experience import ExperienceBase
from brainary.llm.llm import LLM, AUX_MODEL
import json
import statistics

class Monitor:
    """
    Tracks system performance, capability trace quality, and execution outcomes.
    Provides feedback metrics for the scheduler and experience updates.
    """

    def __init__(self, experience: ExperienceBase, llm: LLM = None):
        self.experience = experience
        self.llm = llm or LLM.get_by_name(AUX_MODEL)

    def monitor_security(self, session: ActionSession):
        """Monitor execution security concerns."""
        conversation = [
            {"role": "system", "content": "You are a security monitor analyzing execution for potential risks."},
            {"role": "system", "content": (
                "Analysis focus:\n"
                "1. Input/output validation\n"
                "2. Resource usage patterns\n"
                "3. Permission boundaries\n"
                "4. Data handling practices"
            )},
            {"role": "user", "content": json.dumps({
                "action": session.action.instruction,
                "execution_history": [
                    {"role": role, "content": content}
                    for role, content in session.messages
                ]
            }, indent=2)}
        ]
        
        try:
            analysis = json.loads(self.llm.request(conversation))
            if analysis.get("security_issues"):
                logging.warning(f"Security concerns detected: {analysis['security_issues']}")
        except Exception as e:
            logging.error(f"Security monitoring failed: {e}")
        
    def monitor_safety(self, session: ActionSession):
        """Monitor execution safety concerns."""
        conversation = [
            {"role": "system", "content": "You are a safety monitor checking execution for potential harmful behaviors."},
            {"role": "system", "content": (
                "Analysis focus:\n"
                "1. Content safety\n"
                "2. Ethical considerations\n"
                "3. Bias detection\n"
                "4. Output verification"
            )},
            {"role": "user", "content": json.dumps({
                "action": session.action.instruction,
                "execution_history": [
                    {"role": role, "content": content}
                    for role, content in session.messages
                ]
            }, indent=2)}
        ]
        
        try:
            analysis = json.loads(self.llm.request(conversation))
            if analysis.get("safety_issues"):
                logging.warning(f"Safety concerns detected: {analysis['safety_issues']}")
        except Exception as e:
            logging.error(f"Safety monitoring failed: {e}")
    
    def monitor_cost(self, session: ActionSession):
        """Monitor resource usage and costs."""
        conversation = [
            {"role": "system", "content": "You are a cost efficiency monitor analyzing resource usage."},
            {"role": "system", "content": (
                "Analysis focus:\n"
                "1. Token usage efficiency\n"
                "2. Capability utilization\n"
                "3. Response optimization\n"
                "4. Resource consumption"
            )},
            {"role": "user", "content": json.dumps({
                "action": session.action.instruction,
                "execution_history": [
                    {"role": role, "content": content}
                    for role, content in session.messages
                ]
            }, indent=2)}
        ]
        
        try:
            analysis = json.loads(self.llm.request(conversation))
            if analysis.get("inefficiencies"):
                logging.warning(f"Cost inefficiencies detected: {analysis['inefficiencies']}")
        except Exception as e:
            logging.error(f"Cost monitoring failed: {e}")
        