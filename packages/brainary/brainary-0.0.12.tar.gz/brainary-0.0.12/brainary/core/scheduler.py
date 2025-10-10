import logging
import time
import heapq
import json
from typing import List, Dict, Any, Union, Optional

from brainary.core.ops.action_op import ActionSession, ActionOp
from brainary.core.ops.examine_op import ExamineOp
from brainary.llm.llm import LLM, AUX_MODEL
from brainary.core.ops import *
from brainary.experience.experience import ExperienceBase
from brainary.core.registry import CAPABILITIES, PROBLEM_SOLVING_REGISTRY
from brainary.core.runtime import Runtime

class Scheduler:
    def __init__(self, runtime: Runtime, experience: ExperienceBase, llm: LLM=None):
        self.experience = experience
        self.ready_queue = []
        self.runtime = runtime
        self.llm = llm or LLM.get_by_name(AUX_MODEL)

    def enqueue(self, op: ActionOp, feedback: str=None, **kwargs):
        session = ActionSession(op, last_feedback=feedback, **kwargs)
        session.prepare()
        
        # Infer task type early in the session lifecycle and store it in the session
        task_type = self._infer_task_type(session)
        
        self.plan(session)
        self._infer_context(op)
        kwargs = self._infer_args(op, **kwargs)
        session.kwargs = kwargs
        self._infer_expectation(op)
        session.prepare()
        timestamp = time.time()
        heapq.heappush(self.ready_queue, (timestamp, session))
        
    def _infer_task_type(self, session: ActionSession) -> str:
        """
        Infers the cognitive task type based on instruction analysis.
        
        Args:
            session (ActionSession): The current action session
            
        Returns:
            str: The inferred task type
        """
        task_type_prompt = [
            {"role": "system", "content": (
                "You are an expert system analyzing task types based on instructions and context.\n\n"
                "Task Types:\n"
                "1. analytical - Tasks requiring critical analysis and evaluation\n"
                "2. planning - Tasks involving strategy development and structured reasoning\n"
                "3. memory_based - Tasks needing context recall and knowledge integration\n"
                "4. abstraction - Tasks requiring concept generalization or pattern extraction\n"
                "5. simulation - Tasks involving scenario exploration or outcome prediction\n"
                "6. problem_solving - Tasks focused on finding concrete solutions\n\n"
                "Output: Return only the single most appropriate task type from the list above."
            )},
            {"role": "user", "content": json.dumps({
                "instruction": session.action.instruction,
                "context_count": len(session.action.contexts),
                "has_tools": bool(session.action.tools),
                "has_constraints": bool(session.action.input_constraints or session.action.output_constraints)
            }, indent=2)}
        ]
        
        try:
            task_type = self.llm.request(task_type_prompt).strip().lower()
            if task_type not in {"analytical", "planning", "memory_based", "abstraction", "simulation", "problem_solving"}:
                task_type = "unknown"
        except Exception as e:
            logging.error(f"[SCHED] Task type inference failed: {e}")
            task_type = "unknown"
            
        logging.info(f"[SCHED] Inferred task type: {task_type}")
        # Store the task type properly in the session
        setattr(session, "task_type", task_type)
        return task_type
        
    def is_empty(self) -> bool:
        return len(self.ready_queue) == 0
    
    def next_action(self) -> ActionSession:
        if not self.is_empty():
            _, session = heapq.heappop(self.ready_queue)
            return session
        return None

    def _check_capability_necessity(self, session: ActionSession, capability: str) -> bool:
        """
        Check if a capability is truly necessary based on task semantics and experience.
        
        Args:
            session (ActionSession): Current session
            capability (str): Capability to check
            
        Returns:
            bool: True if capability is necessary, False otherwise
        """
        # First get semantic task type analysis
        task_analysis_prompt = [
            {"role": "system", "content": (
                "Analyze if the given capability is truly necessary for this task.\n\n"
                "Consider:\n"
                "1. Task complexity and requirements\n"
                "2. Alternative simpler approaches\n"
                "3. Critical path dependencies\n"
                "4. Potential overhead vs benefit\n"
                "5. Resource efficiency\n\n"
                "Output: Return only 'necessary' or 'optional'"
            )},
            {"role": "user", "content": json.dumps({
                "instruction": session.action.instruction,
                "capability": capability,
                "context_dependencies": [ctx.name for ctx in session.action.contexts],
                "existing_capabilities": list(session.used_capabilities),
                "tools_available": bool(session.action.tools)
            }, indent=2)}
        ]
        
        try:
            semantic_necessity = self.llm.request(task_analysis_prompt).strip().lower() == "necessary"
        except Exception as e:
            logging.error(f"Semantic necessity check failed: {e}")
            semantic_necessity = True  # Default to necessary if analysis fails
            
        if not semantic_necessity:
            logging.info(f"[SCHED] Capability '{capability}' deemed semantically unnecessary")
            return False
            
        # Then check if similar tasks succeeded without this capability
        similar_successes = self.experience.query(
            instruction=session.action.instruction,
            capability=None,  # Find cases where capability wasn't used
            min_outcome=0.8,  # High success threshold
            metadata_filter={"cognitive_pattern": {"task_type": session.task_type}}
        )
        if similar_successes:
            logging.info(f"[SCHED] Found successful executions without capability '{capability}'")
            return False
            
        # Check experience for this capability with similar task types
        similar_uses = self.experience.query(
            instruction=session.action.instruction,
            capability=capability,
            metadata_filter={"cognitive_pattern": {"task_type": session.task_type}}
        )
        if similar_uses:
            # Check impact scores
            total_impact = sum(exp.impact_score for exp in similar_uses)
            avg_impact = total_impact / len(similar_uses)
            
            # Check cognitive patterns
            effective_count = 0
            ineffective_count = 0
            for exp in similar_uses:
                metadata = exp.metadata.get("cognitive_pattern", {})
                if metadata.get("effectiveness", 0) >= 0.7:
                    effective_count += 1
                if metadata.get("effectiveness", 0) <= 0.3:
                    ineffective_count += 1
                    
            # Calculate weighted necessity score with cognitive pattern emphasis
            impact_weight = 0.3
            effectiveness_weight = 0.5
            ineffectiveness_weight = 0.2
            
            necessity_score = (
                impact_weight * avg_impact +
                effectiveness_weight * (effective_count / len(similar_uses)) -
                ineffectiveness_weight * (ineffective_count / len(similar_uses))
            )
            
            if necessity_score < 0.3:  # Low necessity threshold
                logging.info(
                    f"[SCHED] Capability '{capability}' deemed unnecessary "
                    f"(score: {necessity_score:.2f}, impacts: {avg_impact:.2f}, "
                    f"effective: {effective_count}, ineffective: {ineffective_count})"
                )
                return False
                
            # Log if highly necessary for debugging
            if necessity_score > 0.7:
                logging.info(
                    f"[SCHED] Capability '{capability}' deemed highly necessary "
                    f"(score: {necessity_score:.2f}, impacts: {avg_impact:.2f}, "
                    f"effective: {effective_count}, ineffective: {ineffective_count})"
                )
                
        return True

    def schedule(self, session: ActionSession):
        """
        Generator that handles the execution flow of an action session through its various states.
        States: pre-execution -> executing -> post-execution -> idle
        
        Args:
            session (ActionSession): The session to process
            
        Yields:
            None: After each state transition that requires external processing
        """
        if not isinstance(session, ActionSession):
            raise ValueError("Session must be an instance of ActionSession")

        while session.state != "idle":
            try:
                if session.state in ["pre-execution", "post-execution"]:
                    # Check experience first
                    recommended_capability = None
                    similar_cases = self.experience.query(
                        instruction=session.action.instruction,
                        min_outcome=0.8
                    )
                    if similar_cases:
                        # Get most successful capability from similar cases
                        capability_scores = {}
                        for case in similar_cases:
                            if case.capability:
                                capability_scores[case.capability] = capability_scores.get(case.capability, 0) + case.outcome
                        if capability_scores:
                            recommended_capability = max(capability_scores.items(), key=lambda x: x[1])[0]
                            logging.info(f"[SCHED] Experience recommends capability: {recommended_capability}")
                    
                    # If no strong recommendation from experience, consult LLM
                    if not recommended_capability:
                        phase = "Prior to" if session.state == "pre-execution" else "After"
                        prompt = (
                            f"{phase} executing the task, carefully evaluate if any cognitive capability is required.\n\n"
                            "Important Guidelines:\n"
                            "1. Carefully consider if reusing a previously used capability is truly necessary\n"
                            "2. Only suggest a capability if it is absolutely necessary for the task\n"
                            "3. Consider if the task can be completed without additional cognitive processing\n"
                            "4. Avoid redundant capabilities that don't add significant value\n"
                            "5. If a simpler approach would work, prefer that over complex cognitive capabilities\n"
                            "## Available Capabilities\n" + "\n".join(f"- {cap}" for cap in CAPABILITIES) + "\n\n"
                            "## Current Context\n"
                            "Previous capabilities used:\n" +
                            ('\n'.join([f"- {cap} (strategy: {session.used_strategies.get(cap, 'none')})" 
                                      for cap in session.used_capabilities]) 
                             if session.used_capabilities else "- None") +
                            "\n\n"
                            "## Output Constraints\n"
                        "- Output 'none' if no capability is needed or if a simpler approach would suffice\n"
                        "- Otherwise, output only the exact strategy name\n"
                        "- Do not output explanations or comments"
                    )
                    
                    capability = recommended_capability
                    if not capability:
                        # Get capability recommendation from LLM
                        capability = self.llm.request(
                            session.messages + [("user", prompt)]
                        ).strip().lower()
                    
                    if capability == "none":
                        # Move to next state if no capability needed
                        session.state = "executing" if session.state == "pre-execution" else "idle"
                        logging.info("[SCHED] No cognitive capability needed for this step")
                        continue
                        
                    if capability not in CAPABILITIES:
                        logging.warning(f"[SCHED] Invalid capability '{capability}' recommended")
                        session.state = "executing" if session.state == "pre-execution" else "idle"
                        continue
                        
                    # Check if capability has already been used and verify necessity
                    if capability in session.used_capabilities:
                        # Add extra validation for reusing capabilities
                        prompt = (
                            "A capability is being suggested that was previously used in this session.\n\n"
                            f"Capability: {capability}\n"
                            f"Previous usage: strategy '{session.used_strategies.get(capability)}'\n\n"
                            "Analyze if reusing this capability would:\n"
                            "1. Serve a distinctly different purpose than its previous use\n"
                            "2. Be essential for the current step\n"
                            "3. Add significant new value\n\n"
                            "Output only 'yes' if reuse is justified, or 'no' if it would be redundant."
                        )
                        reuse_justified = self.llm.request(
                            session.messages + [("user", prompt)]
                        ).strip().lower() == 'yes'
                        
                        if not reuse_justified:
                            logging.info(f"[SCHED] Skipping capability '{capability}' as reuse was not justified")
                            session.state = "executing" if session.state == "pre-execution" else "idle"
                            continue
                        else:
                            logging.info(f"[SCHED] Allowing justified reuse of capability '{capability}'")
                    
                    # Double-check necessity based on experience
                    if not self._check_capability_necessity(session, capability):
                        logging.info(f"[SCHED] Skipping unnecessary capability '{capability}' based on experience")
                        session.state = "executing" if session.state == "pre-execution" else "idle"
                        continue

                    # Get or select strategy for the capability
                    strategy = getattr(session.action, capability, None)
                    if not strategy or not CAPABILITIES[capability].validate(strategy):
                        strategy = self.select_strategy(session, capability)
                        
                    if CAPABILITIES[capability].validate(strategy):
                        session.capability = capability
                        session.strategy = strategy
                        session.record_capability_use(capability, strategy)
                        logging.info(f"[SCHED] Selected strategy '{strategy}' for capability '{capability}'")
                        yield
                    else:
                        logging.warning(f"[SCHED] Invalid strategy '{strategy}' for capability '{capability}'")
                        session.state = "executing" if session.state == "pre-execution" else "idle"
                
                elif session.state == "executing":
                    # Handle problem-solving strategy selection
                    problem_solving = session.action.problem_solving
                    if not PROBLEM_SOLVING_REGISTRY.validate(problem_solving):
                        prompt = (
                            "Decide which problem solving strategy is needed.\n\n"
                            "## Available Strategies\n"
                            f"{PROBLEM_SOLVING_REGISTRY.list_all()}\n\n"
                            "## Output Constraints\n"
                            "- Output the name of the needed strategy\n"
                            "- Ensure the full strategy name is preserved exactly as it appears\n"
                            "- Include any portion between '-' and ':' in the strategy name\n"
                            "- Do not include explanations or comments"
                        )
                        try:
                            problem_solving = self.llm.request(
                                session.messages + [("user", prompt)]
                            ).strip()
                        except Exception as e:
                            logging.error(f"[SCHED] Error getting problem solving strategy: {str(e)}")
                            problem_solving = None
                        
                    if PROBLEM_SOLVING_REGISTRY.validate(problem_solving):
                        session.problem_solving = problem_solving
                        session.record_capability_use('problem_solving', problem_solving)
                        logging.info(f"[SCHED] Selected problem solving strategy: {problem_solving}")
                    else:
                        logging.warning(f"[SCHED] Invalid or missing problem solving strategy: {problem_solving}")
                        
                    yield
                    session.state = "post-execution"

            except Exception as e:
                logging.error(f"[SCHED] Error in state {session.state}: {str(e)}")
                if session.state == "pre-execution":
                    session.state = "executing"
                elif session.state == "executing":
                    session.state = "post-execution"
                else:
                    session.state = "idle"
    
    
    def plan(self, session: ActionSession):
        planner_name = getattr(session.action, "planning", None)
        if not planner_name:        
            conversation = [
                {"role": "user", "content": (
                    "You are a strategy selector specializing in task planning approaches.\n"
                    "Output requirements:\n"
                    "- Return only the exact strategy name\n"
                    "- No explanations or additional text\n"
                    "- Strategy must be from the provided list"
                )},
                {"role": "user", "content": (
                    f"Select the most suitable planning strategy for this task:\n"
                    f"{session.action.light_render(**session.kwargs)}\n\n"
                    f"Available strategies:\n{CAPABILITIES['planning'].list_all()}"
                )}
            ]
            
            if session.last_feedback:
                conversation.append({
                    "role": "user", 
                    "content": f"Consider this feedback from previous execution: \n```text\n{session.last_feedback}\n```"
                })
                
            planner_name = self.llm.request(conversation).strip()

        if planner_name and CAPABILITIES["planning"].validate(planner_name):
            planner_cls = CAPABILITIES["planning"].get(planner_name)
            if planner_cls:
                planner_instance = planner_cls(self.llm)
                perform_method = getattr(planner_instance, "perform", None)
                planning_result = perform_method(session)
                logging.info(f"[SCHED] Apply 'Planning ({planner_name})' to generate a new instrution.\n- Raw Instruction:\n{session.action.instruction}\n- New Instruction:\n{planning_result}")
                session.action.update_planning(planning_result)
                
                
    def select_strategy(self, session: ActionSession, capability: str) -> str:
        # Check base rules first
        rules = self.experience.knowledge.query(capability, session.action.instruction)
        if rules:
            return rules[0]["strategy"]

        # First, analyze task type semantically
        task_type_prompt = [
            {"role": "system", "content": (
                "You are an expert system analyzing task types based on instructions and context.\n\n"
                "Task Types:\n"
                "1. analytical - Tasks requiring critical analysis and evaluation\n"
                "2. planning - Tasks involving strategy development and structured reasoning\n"
                "3. memory_based - Tasks needing context recall and knowledge integration\n"
                "4. abstraction - Tasks requiring concept generalization or pattern extraction\n"
                "5. simulation - Tasks involving scenario exploration or outcome prediction\n"
                "6. problem_solving - Tasks focused on finding concrete solutions\n\n"
                "Output: Return only the single most appropriate task type from the list above."
            )},
            {"role": "user", "content": json.dumps({
                "instruction": session.action.instruction,
                "current_capability": capability,
                "context_count": len(session.action.contexts),
                "has_tools": bool(session.action.tools),
                "has_constraints": bool(session.action.input_constraints or session.action.output_constraints)
            }, indent=2)}
        ]
        
        try:
            task_type = self.llm.request(task_type_prompt).strip().lower()
            if task_type not in {"analytical", "planning", "memory_based", "abstraction", "simulation", "problem_solving"}:
                task_type = "unknown"
        except Exception as e:
            logging.error(f"Task type inference failed: {e}")
            task_type = "unknown"

        # Query experience with semantic understanding
        similar_experiences = self.experience.query(
            instruction=session.action.instruction,
            capability=capability,
            metadata_filter={"cognitive_pattern": {"task_type": task_type}}
        )
        
        # First look for task-specific recommended patterns
        recommended_strategies = []
        for exp in similar_experiences:
            metadata = exp.metadata.get("cognitive_pattern", {})
            if metadata.get("is_recommended", False) and metadata.get("task_type") == task_type:
                recommended_strategies.append((
                    exp.strategy,
                    exp.avg_outcome,
                    metadata.get("sequence_position", 0)
                ))
                
        if recommended_strategies:
            # Sort by outcome and sequence position (earlier is better)
            recommended_strategies.sort(key=lambda x: (x[1], -x[2]), reverse=True)
            return recommended_strategies[0][0]

        # Check for task-specific strategies to avoid
        strategies_to_avoid = set()
        for exp in similar_experiences:
            metadata = exp.metadata.get("cognitive_anti_pattern", {})
            if metadata.get("is_recommended") is False and metadata.get("task_type") == task_type:
                strategies_to_avoid.add(exp.strategy)
        
                # Get best strategy for this task type excluding avoided ones
        best_for_task = None
        max_outcome = -1
        for exp in similar_experiences:
            metadata = exp.metadata.get("cognitive_pattern", {})
            if (exp.strategy not in strategies_to_avoid and 
                exp.avg_outcome > max_outcome and 
                metadata.get("task_type") == task_type):
                max_outcome = exp.avg_outcome
                best_for_task = exp.strategy
        
        if best_for_task:
            return best_for_task
            
        # If no good strategy found from experience, use LLM
        prompt = (
            f"Given the task, decide the most suitable strategy for {capability.replace('_',' ').title()}.\n\n"
            "## Available Strategies\n"
            f"{CAPABILITIES[capability].list_all()}\n\n"
            "## Output Constraints\n"
            "- Output only the exact strategy name.\n"
            "- Do not output explanations or comments."
        )
        strategy = self.llm.request(session.messages + [("user", prompt)]).strip()
        return strategy


    def _infer_expectation(self, op: Union[ActionOp]) -> float:
        """
        Compute expected reward of an operation using:
        1. Knowledge-based confidence (weight: 0.4)
        2. Episodic average outcome (weight: 0.4)
        3. Trace scores of the capabilities (weight: 0.2)

        Returns:
            float: The normalized expectation score between 0 and 1
        """
        if op.expectation is not None:
            return op.expectation

        strategies = {
            cap: getattr(op, cap) for cap in CAPABILITIES if getattr(op, cap)
        }

        if not strategies:
            op.expectation = 0.0
            return 0.0

        total_score = 0.0
        strategy_scores = []

        for cap, strat in strategies.items():
            if not strat:
                continue

            score_components = []

            # Step 1: Knowledge-based confidence (40%)
            try:
                rules = self.experience.knowledge.query(cap, op.instruction)
                if rules and "confidence" in rules[0]:
                    confidence = max(0.0, min(1.0, float(rules[0]["confidence"])))
                    score_components.append(("knowledge", confidence, 0.4))
            except (IndexError, KeyError, ValueError, TypeError):
                pass

            # Step 2: Episodic average outcome (40%)
            try:
                exp = self.experience.memory.get(cap, {}).get(strat)
                if exp and hasattr(exp, "avg_outcome"):
                    outcome = max(0.0, min(1.0, float(exp.avg_outcome)))
                    score_components.append(("episodic", outcome, 0.4))
            except (KeyError, ValueError, TypeError, AttributeError):
                pass

            # Step 3: Trace scores contribution (20%)
            try:
                if exp and hasattr(exp, "avg_trace_scores"):
                    trace_scores = exp.avg_trace_scores()
                    if cap in trace_scores:
                        trace_score = max(0.0, min(1.0, float(trace_scores[cap])))
                        score_components.append(("trace", trace_score, 0.2))
            except (KeyError, ValueError, TypeError, AttributeError):
                pass

            if score_components:
                # Calculate weighted average for this strategy
                strategy_score = sum(score * weight for _, score, weight in score_components)
                actual_weight_sum = sum(weight for _, _, weight in score_components)
                if actual_weight_sum > 0:
                    strategy_score /= actual_weight_sum
                    strategy_scores.append(strategy_score)

        # Average across all strategies
        if strategy_scores:
            total_score = sum(strategy_scores) / len(strategy_scores)
        
        # Ensure final score is between 0 and 1
        op.expectation = max(0.0, min(1.0, total_score))
        return op.expectation


    
    # -------- Context/Args Completion --------
    def _infer_args(self, op: Union[ActionOp, ExamineOp], **kwargs):
        if len(self.runtime.heap.objs) == 0:
            return kwargs
        existing_params = "\n".join(f"- {param}" for param in op.params)
        missing_params = self.llm.request([(
            "Infer the missing parameter names for the given instruction. The inferred names must exactly match entries (class names) from the list of valid data types.\n\n"
            f"## Instruction: {op.instruction}\n\n"
            f"## Existing Parameter Names\n{existing_params}\n\n"
            f"## Valid Data Types\n{self.runtime.heap.display_types()}\n\n"
            "## Output Constraints\n"
            "- Output as list in the following format:\n"
            "   - Name 1\n"
            "   - Name 2\n"
            "   - ...\n"
            "- Do not include explanations, comments, or extra content."
        )])
        params = list(op.params)
        for param in missing_params.split("\n"):
            if param.strip():
                params.append(param.strip("- ").replace(" ", "_").lower())
        op.params = tuple(params)
        missings = [p for p in op.params if p not in kwargs]
        for param in missings:
            obj = self.runtime.heap.resolve_obj(param)
            kwargs[param] = obj if obj is not None else "Not specified"
        return kwargs

    def _infer_context(self, op: Union[ActionOp, ExamineOp]):
        if len(self.runtime.heap.ctxs) == 0:
            return
        existing_ctxs = "\n".join(f"- {ctx.name}" for ctx in op.contexts)
        missing_ctxs = self.llm.request([(
            "Infer the missing context fields for the given instruction. The inferred names must exactly match entries from the list of valid context fields.\n\n"
            f"## Instruction\n{op.instruction}\n\n"
            f"## Existing Context Fields\n{existing_ctxs}\n\n"
            f"## Valid Context Fields\n{self.runtime.heap.display_ctxs()}\n\n"
            "## Output Constraints\n"
            "- Output as list in the following format:\n"
            "   - Field 1\n"
            "   - Field 2\n"
            "   - ...\n"
            "- Do not include explanations, comments, or extra content."

        )])
        contexts = list(op.contexts)
        for ctx in missing_ctxs.split("\n"):
            ctx = self.runtime.heap.resolve_ctx(ctx)
            if ctx:
                contexts.append(ctx)
        op.contexts = tuple(contexts)
