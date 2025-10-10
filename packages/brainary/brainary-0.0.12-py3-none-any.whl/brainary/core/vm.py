# core/vm.py
import json
from pathlib import Path
from typing import Any, Union
import logging
import atexit
import weakref

from brainary.core.ops.action_op import ActionSession
from brainary.core.runtime import Runtime
from brainary.core.scheduler import Scheduler
from brainary.core.monitor import Monitor
from brainary.experience.experience import ExperienceBase
from brainary.core.ops import *
from brainary.llm.llm import LLM
from brainary.solvers.base import ProblemSolving
from brainary.core.registry import CAPABILITIES, PROBLEM_SOLVING_REGISTRY


AUX_MODEL = "gpt-4o-mini"


class VM:
    def __init__(self, model_name: str, temperature=1.0, experience_base_path: str = None, experience_learning=False, scheduler: Scheduler = None, monitor: Monitor = None):
        self.llm: LLM = LLM.get_by_name(model_name, temperature=temperature)
        self.runtime: Runtime = Runtime()
        self.experience_base_path = experience_base_path
        if self.experience_base_path and Path(self.experience_base_path).exists():
            self.experience_base: ExperienceBase = ExperienceBase.load(self.experience_base_path)
            self.experience_base.llm = self.llm
        else:
            self.experience_base: ExperienceBase = ExperienceBase(llm=self.llm)
        self.experience_learning = experience_learning

        self.scheduler: Scheduler = scheduler or Scheduler(self.runtime, self.experience_base, llm=self.llm)
        self.monitor: Monitor = monitor or Monitor(self.experience_base, llm=self.llm)
        
        # Register an exit handler to save experience before shutdown
        if self.experience_base_path and self.experience_learning:
            # Use a weakref to avoid keeping VM alive just for the exit handler
            atexit.register(self._save_at_exit, self.experience_base, self.experience_base_path)

    @staticmethod
    def _save_at_exit(experience_base, path):
        """Static method used as an exit handler to save experience base before shutdown.
        This runs before Python's import machinery is dismantled."""
        try:
            logging.info(f"Saving experience base to `{path}` at exit")
            experience_base.dump(path)
        except Exception as e:
            logging.warning(f"Failed to save experience at exit: {e}")
    
    def save_experience(self):
        """Explicitly save the experience base to disk.
        This method should be called before program termination if experience needs to be saved."""
        if self.experience_base_path and self.experience_learning and hasattr(self, 'experience_base'):
            self.experience_base.dump(self.experience_base_path)
            
    def __del__(self):
        # We no longer need to save experience here as atexit handler will do it
        # This is just a fallback with minimal error handling
        try:
            if hasattr(self, 'experience_base_path') and hasattr(self, 'experience_learning') and \
               self.experience_base_path and self.experience_learning and \
               hasattr(self, 'experience_base'):
                logging.debug("VM.__del__ called, but experience will be saved by atexit handler")
        except:
            pass

    def accept_op(self, op: BaseOp, **kwargs):
        logging.info(f"[VM] Accept an operation.\n- Operation:\n{op}\n- Arguments:\n{kwargs}")
        if isinstance(op, TypeOp):
            self.runtime.heap.add_obj(op)
        elif isinstance(op, CtxOp):
            self.runtime.heap.add_ctx(op)
        elif isinstance(op, ExamineOp):
            self.scheduler._infer_context(op)
            kwargs = self.scheduler._infer_args(op, **kwargs)
            try:
                response = self.llm.request(op.render(**kwargs))
            except Exception as e:
                logging.error(f"LLM request failed: {e}")
                response = ""  # Fallback
            return op.resolve(response)
        elif isinstance(op, ActionOp):
            logging.info(f"[VM] Enqueue the op into scheduler.\n- Operation:\n{op}")
            self.scheduler.enqueue(op, **kwargs)
            return self._execute()

    # -------- Self-Regulation Loop per operation --------
    def _execute(self) -> Any:
        """
        Self-regulation loop per operation:
        1. Estimate capabilities and contexts
        2. Generate traces for critical thinking, planning, reasoning,
        evaluation, and simulation
        3. Execute operation via problem solver
        4. Monitor outcomes
        5. Update experience base
        6. Optional replanning
        """
        result = None

        while not self.scheduler.is_empty():
            session_list: list[ActionSession] = []
            session: ActionSession = self.scheduler.next_action()
            session_list.append(session)
            logging.info(f"[VM] Pick the next operation.\n- Operation:\n{session.action}")
            
            for _ in self.scheduler.schedule(session):
                if session.state == "pre-execution":
                    strategy_cls = CAPABILITIES[session.capability].get(session.strategy)
                    if strategy_cls:
                        capability_instance = strategy_cls(self.llm)
                        perform_method = getattr(capability_instance, "perform", None)
                        if perform_method:
                            logging.info(f"[VM] Apply '{session.capability}' with '{session.strategy}' strategy for the operation.")
                            try:
                                trace = perform_method(session)
                                session.push_message("user", f"Apply {session.capability} with {session.strategy} strategy.")
                                session.push_message("assistant", trace)
                            except Exception as e:
                                logging.error(f"Error in {session.capability} perform: {e}")
                elif session.state == "executing":
                    solver: ProblemSolving = PROBLEM_SOLVING_REGISTRY.get(session.problem_solving)(self.llm)
                    response = solver.solve(action=session, **session.kwargs)
                    result = session.action.resolve(response)
                    session.push_message("assistant", response)
                elif session.state == "post-execution":
                    strategy_cls = CAPABILITIES[session.capability].get(session.strategy)
                    if strategy_cls:
                        capability_instance = strategy_cls(self.llm)
                        perform_method = getattr(capability_instance, "perform", None)
                        if perform_method:
                            logging.info(f"[VM] Apply '{session.capability}' with '{session.strategy}' strategy for the operation.")
                            try:
                                trace = perform_method(session)
                                session.push_message("user", f"Apply {session.capability} with {session.strategy} strategy.")
                                session.push_message("assistant", trace)
                            except Exception as e:
                                logging.error(f"Error in {session.capability} perform: {e}")
                                
            reward = self.estimate_reward(session)
            logging.info(f"[VM] Monitor overall result and estimate reward.\n- Reward:\n{reward}")
            if reward - session.action.expectation < 0.:
                feedback = self.generate_negative_feedback(session)
                session.cur_feedback = feedback
                
                logging.info(f"[VM] Performance low. Triggering rescheduling with feedback.\n- Feedback:\n{feedback}")
                self.scheduler.enqueue(session.action, feedback, session.kwargs)
            else:
                feedback = self.generate_positive_feedback(session)
                session.cur_feedback = feedback
                
            if self.experience_learning:
                logging.info(f"[VM] Update experience base from the execution.")
                self.summarize_experience(session_list)
                    

        return result
    
    def estimate_reward(self, session: ActionSession) -> float:
        """
        Returns a performance metric (0..1) based on the last execution,
        taking into account capability traces (reasoning, critical thinking, evaluation, simulation).
        
        Args:
            session: The action session containing execution history and traces
            
        Returns:
            float: Performance score between 0 and 1
        """
        # Convert session history to structured conversation
        conversation = [
            {"role": "system", "content": "You are a performance evaluation expert analyzing execution quality."},
            {"role": "system", "content": (
                "Evaluation criteria:\n"
                "1. Task completion and accuracy\n"
                "2. Reasoning quality and logical coherence\n"
                "3. Critical thinking and evaluation depth\n"
                "4. Creative problem solving approaches"
            )},
            {"role": "system", "content": (
                "Output requirements:\n"
                "- A single float between 0.0 and 1.0\n"
                "- Higher scores for better quality (1.0 = perfect)\n"
                "- Return only the numeric score"
            )}
        ]
        
        # Add execution history as structured messages
        for role, content in session.messages:
            conversation.append({
                "role": role,
                "content": content
            })
            
        try:
            # Request evaluation through structured conversation
            score = float(self.llm.request(conversation).strip())
            
            # Apply capability weights
            weights = {
                "critical_thinking": 0.3,
                "reasoning": 0.3, 
                "planning": 0.2,
                "evaluation": 0.1,
                "simulation": 0.1
            }
            
            weighted_score = score
            for cap, weight in weights.items():
                if getattr(session.action, cap):
                    # Boost score if useful capabilities were applied
                    weighted_score *= (1 + weight)
                    
            return max(0.0, min(1.0, weighted_score))
        except (ValueError, Exception) as e:
            logging.error(f"Reward estimation failed: {e}")
            return 0.5  # fallback
            
    def generate_negative_feedback(self, session: ActionSession) -> str:
        """
        Generate constructive feedback when performance is below expectations.
        
        Args:
            session: The action session with execution history
            
        Returns:
            str: Detailed feedback with improvement suggestions
        """
        # Build structured conversation for feedback generation
        conversation = [
            {"role": "system", "content": "You are an expert advisor analyzing task execution and providing constructive feedback."},
            {"role": "system", "content": (
                "Analysis focus areas:\n"
                "1. Identify key gaps or mistakes\n"
                "2. Missing cognitive capabilities\n" 
                "3. Alternative strategies to try\n"
                "4. Specific improvements needed"
            )},
            {"role": "system", "content": (
                "Output requirements:\n"
                "- Clear, actionable feedback\n"
                "- Specific strategy suggestions\n"
                "- Focus on most impactful improvements\n"
                "- Structured in markdown format"
            )}
        ]
        
        # Add execution history as structured messages
        for role, content in session.messages:
            conversation.append({
                "role": role,
                "content": content
            })
        
        try:
            feedback = self.llm.request(conversation)
            return feedback
        except Exception as e:
            logging.error(f"Feedback generation failed: {e}")
            return "Performance below expectations. Consider alternative strategies."
            
    def generate_positive_feedback(self, session: ActionSession) -> str:
        """
        Generate feedback for successful execution to reinforce effective patterns.
        
        Args:
            session: The action session with execution history
        
        Returns:
            str: Feedback highlighting successful strategies
        """
        # Build structured conversation for success analysis
        conversation = [
            {"role": "system", "content": "You are an expert analyst identifying successful execution patterns and strategies."},
            {"role": "system", "content": (
                "Analysis focus areas:\n"
                "1. Effective strategies used\n"
                "2. Quality of reasoning and analysis\n"
                "3. Novel or creative approaches\n"
                "4. Reusable patterns"
            )},
            {"role": "system", "content": (
                "Output requirements:\n"
                "- Highlight specific successful techniques\n"
                "- Identify reusable strategies\n"
                "- Note any novel approaches\n"
                "- Structured in markdown format"
            )}
        ]
        
        # Add execution history as structured messages
        for role, content in session.messages:
            conversation.append({
                "role": role,
                "content": content
            })
        
        try:
            feedback = self.llm.request(conversation)
            return feedback
        except Exception as e:
            logging.error(f"Feedback generation failed: {e}")
            return "Execution successful. Effective strategies applied."
            
    def summarize_experience(self, sessions: list[ActionSession]):
        """
        Analyze execution sessions to extract reusable patterns and update experience base.
        
        Args:
            sessions: List of completed action sessions to analyze
        """
        # Build execution summaries with structured information
        summaries = []
        for session in sessions:
            # Get actually used capabilities (excluding problem_solving) and validate against registry
            used_capabilities = session.used_capabilities
            used_strategies = session.used_strategies
            
            # Only include capabilities and strategies that were both used and valid
            valid_capabilities = {}
            for cap in used_capabilities:
                strategy = used_strategies.get(cap)
                # Validate capability exists and strategy is valid for that capability
                if (cap in CAPABILITIES and 
                    strategy and 
                    CAPABILITIES[cap].validate(strategy)):
                    valid_capabilities[cap] = strategy
            
            # Split capabilities into cognitive and problem-solving
            cognitive_capabilities = {
                cap: strategy for cap, strategy in valid_capabilities.items()
                if cap != "problem_solving"
            }
            
            problem_solving_strategy = (session.problem_solving 
                                     if session.has_used_capability('problem_solving') and 
                                     PROBLEM_SOLVING_REGISTRY.validate(session.problem_solving)
                                     else None)
            

                
            # Make sure task_type is properly accessed from the session
            task_type = getattr(session, "task_type", "unknown")
            if task_type == "unknown":
                logging.warning(f"[VM] Session task type is unknown, this may affect experience quality")
                
            summary = {
                "instruction": session.action.instruction,
                "task_type": task_type,
                "cognitive": {
                    "capabilities": cognitive_capabilities,
                    "execution_results": {
                        cap: next((content for role, content in reversed(session.messages) 
                                if role == "assistant" and 
                                f"Apply {cap} with {cognitive_capabilities[cap]}" in 
                                session.messages[session.messages.index((role, content)) - 1][1]),
                                None)
                        for cap in cognitive_capabilities
                    }
                },
                "problem_solving": {
                    "strategy": problem_solving_strategy,
                    "execution_result": next((content for role, content in session.messages 
                                          if role == "assistant" and content.strip() and
                                          not any(f"Apply {cap}" in content 
                                                for cap in cognitive_capabilities)),
                                          None)
                } if problem_solving_strategy else None,
                "feedback": session.cur_feedback,
                "reward": self.estimate_reward(session)
            }
            
            # Include if either cognitive capabilities or problem-solving strategy is valid
            if summary["cognitive"]["capabilities"] or summary["problem_solving"]:
                summaries.append(summary)
            
        # Create structured conversation for pattern analysis
        # Collect all valid capabilities and their strategies across sessions
        valid_capability_strategies = {}
        for session in sessions:
            for cap in session.used_capabilities:
                strategy = session.used_strategies.get(cap)
                if strategy:
                    if cap not in valid_capability_strategies:
                        valid_capability_strategies[cap] = set()
                    valid_capability_strategies[cap].add(strategy)

        conversation = [
            {"role": "system", "content": "You are an expert system analyzing both cognitive and problem-solving execution patterns."},
            {"role": "system", "content": (
                "Analysis objectives:\n"
                "1. Identify effective cognitive capability sequences\n"
                "2. Map task types to successful cognitive & problem-solving strategies\n"
                "3. Detect ineffective patterns to avoid\n"
                "4. Extract reusable execution patterns"
            )},
            {"role": "system", "content": (
                "Output format requirements:\n"
                "Return a JSON object with:\n"
                "- cognitive_patterns: Array of {\n"
                "    task_type: string,  # The type of task this pattern applies to\n"
                "    capability_sequence: Array of {  # Ordered sequence of capabilities to apply\n"
                "      capability: string,  # Capability name\n"
                "      strategy: string,    # Strategy to use with this capability\n"
                "      rationale: string    # Why this capability is effective here\n"
                "    }\n"
                "  }\n"
                "- cognitive_anti_patterns: Array of {\n"
                "    task_type: string,\n"
                "    conditions: string[],  # When this anti-pattern applies\n"
                "    avoid: Array of {      # Capabilities/strategies to avoid\n"
                "      capability: string,\n"
                "      strategy: string,\n"
                "      reason: string       # Why to avoid this combination\n"
                "    }\n"
                "  }\n"
                "- solving_patterns: Array of {\n"
                "    task_type: string,     # Type of task\n"
                "    cognitive_prereqs: Array of {  # Required cognitive processing before solving\n"
                "      capability: string,\n"
                "      strategy: string\n"
                "    },\n"
                "    strategy: string,      # Problem solving strategy to use\n"
                "    conditions: string[],   # When this solving pattern is effective\n"
                "    rationale: string      # Why this solving approach works\n"
                "  }\n"
                "\nNote: Use capabilities/strategies from these validated lists:\n" +
                "Cognitive Capabilities:\n" +
                "\n".join(f"- {cap}: {', '.join(strats)}" 
                         for cap, strats in valid_capability_strategies.items()
                         if cap != "problem_solving") +
                "\n\nProblem Solving Strategies:\n" +
                ", ".join(PROBLEM_SOLVING_REGISTRY.list_all())
            )},
            {"role": "user", "content": json.dumps({
                "execution_summaries": summaries,
                "valid_capabilities": {
                    cap: list(strats) for cap, strats in valid_capability_strategies.items()
                    if cap != "problem_solving"
                },
                "valid_solving_strategies": PROBLEM_SOLVING_REGISTRY.list_all()
            }, indent=2)}
        ]
        
        try:
            # Get analysis through structured conversation
            analysis = json.loads(self.llm.request(conversation))
        except Exception as e:
            logging.error(f"Experience summarization failed: {e}")
            return
                
        # Process cognitive capability patterns
        for pattern in analysis.get("cognitive_patterns", []):
            task_type = pattern.get("task_type")
            if not task_type:
                continue
                
            for step in pattern.get("capability_sequence", []):
                capability = step.get("capability")
                strategy = step.get("strategy")
                
                # Skip if not a valid cognitive capability-strategy pair
                if (not capability or not strategy or 
                    capability == "problem_solving" or
                    not capability in CAPABILITIES or
                    not CAPABILITIES[capability].validate(strategy)):
                    continue
                    
                # Record if capability and strategy were used
                if any(session.has_used_capability(capability, strategy) 
                        for session in sessions):
                    # Find the session that used this capability (for better context)
                    matching_session = next((s for s in sessions if s.has_used_capability(capability, strategy)), None)
                    source_session = matching_session or session
                    
                    # Build complete metadata with all required context
                    pattern_metadata = {
                        "cognitive_pattern": {
                            "task_type": task_type,
                            "sequence_position": pattern["capability_sequence"].index(step),
                            "rationale": step.get("rationale", ""),
                            "is_recommended": True,
                            "effectiveness": 1.0  # High effectiveness for recommended patterns
                        },
                        # Add required context fields
                        "timestamp": source_session.action.timestamp if hasattr(source_session.action, 'timestamp') else None,
                        "instruction": source_session.action.instruction,
                        "task_complexity": len(pattern.get("capability_sequence", [])) / 5.0,  # Complexity based on steps
                        "contribution": step.get("importance", 1.0),  # Default high contribution for pattern
                        "instructions": [s.action.instruction for s in sessions],  # Store for similarity matching
                    }
                    
                    self.experience_base.record(
                        capability=capability,
                        strategy=strategy,
                        outcome=1.0,  # High outcome for effective strategies
                        metadata=pattern_metadata
                    )
            
        # Process cognitive capability anti-patterns
        for anti_pattern in analysis.get("cognitive_anti_patterns", []):
            task_type = anti_pattern.get("task_type")
            if not task_type:
                continue
                
            for avoid_step in anti_pattern.get("avoid", []):
                capability = avoid_step.get("capability")
                strategy = avoid_step.get("strategy")
                
                # Skip if not a valid cognitive capability-strategy pair
                if (not capability or not strategy or 
                    capability == "problem_solving" or
                    not capability in CAPABILITIES or
                    not CAPABILITIES[capability].validate(strategy)):
                    continue
                    
                # Record if capability and strategy were used
                if any(session.has_used_capability(capability, strategy)
                        for session in sessions):
                    # Find the session that used this capability (for better context)
                    matching_session = next((s for s in sessions if s.has_used_capability(capability, strategy)), None)
                    source_session = matching_session or session
                    
                    # Build complete metadata with all required context for anti-patterns
                    anti_pattern_metadata = {
                        "cognitive_anti_pattern": {
                            "task_type": task_type,
                            "conditions": anti_pattern.get("conditions", []),
                            "reason": avoid_step.get("reason", ""),
                            "is_recommended": False,
                            "effectiveness": 0.0  # Low effectiveness for anti-patterns
                        },
                        # Add required context fields
                        "timestamp": source_session.action.timestamp if hasattr(source_session.action, 'timestamp') else None,
                        "instruction": source_session.action.instruction,
                        "task_complexity": 0.5,  # Neutral complexity for anti-patterns
                        "contribution": 0.0,  # Zero contribution since it's to be avoided
                        "instructions": [s.action.instruction for s in sessions],  # Store for similarity matching
                    }
                    
                    self.experience_base.record(
                        capability=capability,
                        strategy=strategy,
                        outcome=0.0,  # Low outcome for strategies to avoid
                        metadata=anti_pattern_metadata
                    )
                    
        # Process problem-solving patterns
        for pattern in analysis.get("solving_patterns", []):
            task_type = pattern.get("task_type")
            strategy = pattern.get("strategy")
            
            # Skip if not a valid problem-solving strategy
            if (not task_type or not strategy or
                not PROBLEM_SOLVING_REGISTRY.validate(strategy)):
                continue
            
            # Record if strategy was used
            if any(session.problem_solving == strategy
                    for session in sessions):
                # Find the specific session that used this strategy
                matching_session = next((s for s in sessions if s.problem_solving == strategy), None)
                source_session = matching_session or session
                
                # Build complete metadata with all required context for solving patterns
                solving_pattern_metadata = {
                    "solving_pattern": {
                        "task_type": task_type,
                        "conditions": pattern.get("conditions", []),
                        "rationale": pattern.get("rationale", ""),
                        "cognitive_prereqs": pattern.get("cognitive_prereqs", []),
                        "is_recommended": True,
                        "effectiveness": 1.0  # High effectiveness for recommended patterns
                    },
                    # Add required context fields
                    "timestamp": source_session.action.timestamp if hasattr(source_session.action, 'timestamp') else None,
                    "instruction": source_session.action.instruction,
                    "task_complexity": (0.3 + len(pattern.get("cognitive_prereqs", [])) / 5.0),  # Complexity based on prerequisites
                    "contribution": 1.0,  # High contribution for solving strategies
                    "instructions": [s.action.instruction for s in sessions],  # Store for similarity matching
                }
                
                self.experience_base.record(
                    capability="problem_solving",
                    strategy=strategy,
                    outcome=1.0,  # High outcome for effective strategies
                    metadata=solving_pattern_metadata
                )
            
        
            
    def _validate_strategy_names(self, strategies: list[str]) -> bool:
        """
        Validate that strategy names exist in the system capabilities.
        
        Args:
            strategies: List of strategy names to validate
            
        Returns:
            bool: True if all strategies are valid, False otherwise
        """
        try:
            for strategy in strategies:
                # Check if strategy exists in any capability
                found = False
                for cap in CAPABILITIES.values():
                    if cap.validate(strategy):
                        found = True
                        break
                else:
                    if PROBLEM_SOLVING_REGISTRY.validate(strategy):
                        found = True
                    
                if not found:
                    logging.warning(f"Invalid strategy name: {strategy}")
                    return False
            return True
        except Exception as e:
            logging.error(f"Strategy validation failed: {e}")
            return False


__VM__: VM = None


def install_vm(model_name: str, temperature=1.0, experience_base: str = None, experience_learning=False):
    import brainary.core.registry
    brainary.core.registry.scan()
    global __VM__
    if __VM__ is None:
        __VM__ = VM(model_name, temperature=temperature, experience_base_path=experience_base, experience_learning=experience_learning)
    from brainary.core.vm_bus import VMBus
    VMBus.set_vm(__VM__)