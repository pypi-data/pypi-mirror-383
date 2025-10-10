from abc import ABCMeta, abstractmethod
from typing import Dict, List, Type, Optional, Any
import json, re, random, copy, hashlib
from datetime import datetime
from functools import wraps
from brainary.core.ops.action_op import ActionOp
from brainary.llm.llm import LLM, AUX_MODEL
from brainary.solvers.base import ProblemSolving
from brainary.memory.retriever import create_retriever, retrieve_memory
from brainary.memory.episodic_memory_extractor import extract_content_relation_memory
from brainary.memory.working_memory_extractor import extract_working_memory, get_working_extractor, WorkingMemory
from brainary.memory.semantic_memory_extractor import extract_semantic_info, SemanticSummary

# =============== Metacognition Decorator ===============
"""
┌─────────────────────────────────────────────────────────────┐
│  1. Planning Phase (before main loop)                       │
│     _planning() → generates execution_plan                  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  2. Component Execution (with @with_metacognition decorator)│
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ wrapper() calls:                                    │    │
│  │   1. func(self, *args, **kwargs)                   │    │
│  │      ↓                                              │    │
│  │   2. _metacognition_check()                         │    │
│  │      - Compares actual vs expected                  │    │
│  │      - Returns adjustment_suggestions               │    │
│  │      ↓                                              │    │
│  │   3. _apply_metacognition_adjustment()              │    │
│  │      - Stores adjustments in                        │    │
│  │        self.metacognition_adjustments[comp_name]    │    │
│  │      ↓                                              │    │
│  │   4. Re-run if severe deviation                     │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  3. Next Execution (re-run or next iteration)                │
│                                                              │
│  Component function:                                         │
│    messages = [original prompt messages]                    │
│    messages = self._get_adjusted_prompt(comp_name, messages)│
│    ↓                                                         │
│  _get_adjusted_prompt():                                     │
│    - Reads self.metacognition_adjustments[comp_name]        │
│    - Injects prompt_modifications at position 1             │
│    - Appends additional_context at end                      │
│    ↓                                                         │
│  Adjusted messages sent to LLM                               │
└─────────────────────────────────────────────────────────────┘
"""

def with_metacognition(component_name: str, max_retries: int = 1):
    """
    Decorator for metacognition monitoring on component execution.

    This decorator wraps component methods to automatically:
    1. Execute the component
    2. Check execution against planned expectations
    3. Apply adjustments if severe deviations are detected
    4. Optionally re-run the component with adjustments

    Args:
        component_name (str): Name of the component being monitored
            Options: 'problem_modeling', 'problem_representation', 'strategy_selection',
                    'strategy_heuristic_llm', 'strategy_case_based'
        max_retries (int): Maximum number of re-runs if severe deviation detected (default: 1)

    Usage:
        @with_metacognition('problem_modeling')
        def _problem_modeling(self, ...):
            ...

    Notes:
        - The decorated method must be part of PSFrameworkCall class
        - Requires self.execution_plan to be initialized
        - Stores metacognition results in self.feedback['metacognition']
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Execute the original function
            result = func(self, *args, **kwargs)

            # Skip metacognition if execution_plan not available
            if not hasattr(self, 'execution_plan') or not self.execution_plan:
                return result

            # Perform metacognition check
            execution_context = {
                "args": str(args)[:500],
                "kwargs": str(kwargs)[:500],
                "function_name": func.__name__
            }

            # Format result for metacognition check based on component type
            if isinstance(result, dict):
                actual_output = result
            elif isinstance(result, tuple):
                # Handle strategy functions that return (solution, score)
                if component_name in ['strategy_heuristic_llm', 'strategy_case_based']:
                    actual_output = {
                        "solution_text": str(result[0])[:1000] if result[0] else "",
                        "score": result[1] if len(result) > 1 else None,
                        "output_type": "tuple"
                    }
                else:
                    actual_output = {"result": str(result)[:1000], "output_type": "tuple"}
            elif isinstance(result, str):
                # Handle strategy_selection that returns strategy name
                if component_name == 'strategy_selection':
                    actual_output = {"selected_strategy": result, "output_type": "string"}
                else:
                    actual_output = {"result": result[:1000], "output_type": "string"}
            else:
                actual_output = {"result": str(result)[:1000], "output_type": type(result).__name__}

            metacog_result = self._metacognition_check(
                component_name=component_name,
                actual_output=actual_output,
                execution_context=execution_context
            )

            # Handle adjustment based on severity
            if metacog_result.get("adjustment_needed"):
                severity = metacog_result.get('deviation_severity', 'none')
                suggestions = metacog_result.get("adjustment_suggestions", [])

                if severity == 'severe':
                    # For severe deviations: apply immediately and retry
                    print(f"[Metacognition] Severe deviation in {component_name}, applying adjustments immediately...")
                    self._apply_metacognition_adjustment(component_name, suggestions)

                    retry_count = 0
                    while retry_count < max_retries:
                        print(f"[Metacognition] Re-running {component_name} with adjustments (attempt {retry_count + 1}/{max_retries})...")
                        result = func(self, *args, **kwargs)

                        # Format result for re-check (same logic as above)
                        if isinstance(result, dict):
                            actual_output_retry = result
                        elif isinstance(result, tuple):
                            if component_name in ['strategy_heuristic_llm', 'strategy_case_based']:
                                actual_output_retry = {
                                    "solution_text": str(result[0])[:1000] if result[0] else "",
                                    "score": result[1] if len(result) > 1 else None,
                                    "output_type": "tuple"
                                }
                            else:
                                actual_output_retry = {"result": str(result)[:1000], "output_type": "tuple"}
                        elif isinstance(result, str):
                            if component_name == 'strategy_selection':
                                actual_output_retry = {"selected_strategy": result, "output_type": "string"}
                            else:
                                actual_output_retry = {"result": result[:1000], "output_type": "string"}
                        else:
                            actual_output_retry = {"result": str(result)[:1000], "output_type": type(result).__name__}

                        # Re-check after adjustment
                        metacog_result = self._metacognition_check(
                            component_name=component_name,
                            actual_output=actual_output_retry,
                            execution_context={**execution_context, "retry_attempt": retry_count + 1}
                        )

                        # Stop retrying if deviation is resolved or becomes non-severe
                        if not metacog_result.get("adjustment_needed") or metacog_result.get('deviation_severity') != 'severe':
                            break

                        # Apply new adjustments for next retry if still severe
                        if metacog_result.get("adjustment_suggestions"):
                            self._apply_metacognition_adjustment(
                                component_name,
                                metacog_result.get("adjustment_suggestions", [])
                            )

                        retry_count += 1

                elif severity == 'moderate':
                    # For moderate deviations: store adjustments for next round
                    print(f"[Metacognition] Moderate deviation in {component_name}, storing adjustments for next execution...")
                    self._apply_metacognition_adjustment(component_name, suggestions)

                elif severity == 'minor':
                    # For minor deviations: optionally store, but don't retry
                    print(f"[Metacognition] Minor deviation in {component_name}, storing adjustments for next execution...")
                    self._apply_metacognition_adjustment(component_name, suggestions)

            return result
        return wrapper
    return decorator


def process_problem_description(action,kwargs):
    """following the implementation of `action.render`
    return a list of the raw problem description and reference materials
    """
    arguments = []
    problem_description = []
    problem_description.append(f"### Instruction\n{action.instruction}\n\n")
    for k, v in kwargs.items():
        k_fmt = " ".join(w[0].upper() + w[1:] for w in k.split("_"))
        arguments.append(f"#### {k_fmt}\n{v}")
    arguments = "\n\n".join(arguments)
    problem_description.append(f"### Arguments\n{arguments}\n\n")
    return problem_description


def _parse_first_json(text: str) -> dict | None:
    """
    Parse the first valid JSON object from text, handling various formats.

    Supports:
    - Plain JSON: {...}
    - Markdown code blocks: ```json\n{...}\n```
    - Markdown code blocks: ```\n{...}\n```
    - Mixed text with embedded JSON

    Args:
        text: String potentially containing JSON

    Returns:
        Parsed dict or None if no valid JSON found
    """
    if not text:
        return None

    text = text.strip()

    # Method 1: Try to extract from markdown code blocks first
    # Pattern: ```json\n{...}\n``` or ```\n{...}\n```
    code_block_pattern = r"```(?:json)?\s*\n(.*?)\n```"
    code_match = re.search(code_block_pattern, text, flags=re.S)
    if code_match:
        json_content = code_match.group(1).strip()
        try:
            return json.loads(json_content)
        except json.JSONDecodeError:
            pass  # Fall through to other methods

    # Method 2: Remove markdown code fences and try to find JSON
    # This handles cases like: ```json {...} ``` or ``` {...} ```
    clean = re.sub(r"```(?:json)?\s*", "", text, flags=re.I)
    clean = clean.strip()

    # Method 3: Find the first complete JSON object in the cleaned text
    # Use a greedy match to capture the entire JSON structure
    m = re.search(r"\{.*\}", clean, flags=re.S)
    if not m:
        return None

    json_str = m.group(0)

    # Try to parse the extracted JSON
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        # Method 4: Try to find balanced braces (in case of nested structures)
        # This is more robust for complex nested JSON
        try:
            return _extract_json_with_balanced_braces(clean)
        except Exception:
            return None

def _extract_json_with_balanced_braces(text: str) -> dict | None:
    """
    Extract JSON by finding balanced braces, handling nested structures.

    This is a fallback method for complex JSON with nested objects/arrays.
    """
    first_brace = text.find('{')
    if first_brace == -1:
        return None

    brace_count = 0
    in_string = False
    escape_next = False

    for i in range(first_brace, len(text)):
        char = text[i]

        if escape_next:
            escape_next = False
            continue

        if char == '\\':
            escape_next = True
            continue

        if char == '"':
            in_string = not in_string
            continue

        if not in_string:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    # Found complete JSON object
                    json_str = text[first_brace:i+1]
                    try:
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        return None

    return None


class PSFrameworkCall(ProblemSolving):
    NAME = "Problem Solving Framework Call (DISABLED)"
    DESC = "Use the problem-solving framework and generate solutions for complex problems iteratively."
    #  Contain four stages: (1) Problem definition and abstraction, (2) Solution generation, (3) Solution execution, and (4) Feedback. \n Three types of solution generation strategies: heuristic search, analogical reasoning and creative thinking.\nTODO: Analogy reasoning, creative reasoning (from creativity module), literature review (need to access web stations)
    
    def __init__(self, llm: LLM):
        super().__init__(llm)

    def init_memory(self, memory_heap=None):
        """
        Initialize memory heap so that retrieval works out-of-the-box.

        - Map legacy fields from Memory (obj_index/objs) to what the retriever expects (index/objects).
        - Ensure three memory buckets exist: episodic_memory, working_memory, semantic_memory.
        (Use empty lists so retrieval APIs won't crash even if there's no data yet.)
        """
        self.heap = memory_heap

        if self.heap is None:
            # If needed, you could instantiate your Memory class here.
            # But per your note, an instance is already provided upstream.
            raise ValueError("memory_heap must be a valid Memory instance")

        # ---- Compatibility mappings (retriever expects these names) ----
        # MemoryRetriever.resolve() checks heap.index and heap.objects. :contentReference[oaicite:2]{index=2}
        # Your Memory class defines obj_index and objs. :contentReference[oaicite:3]{index=3}
        if not hasattr(self.heap, "index"):
            # Point retriever-visible 'index' to existing obj_index
            if hasattr(self.heap, "obj_index"):
                self.heap.index = self.heap.obj_index
            else:
                # Fallback to an empty dict-like structure
                from collections import defaultdict
                self.heap.index = defaultdict(list)

        if not hasattr(self.heap, "objects"):
            if hasattr(self.heap, "objs"):
                self.heap.objects = self.heap.objs
            else:
                self.heap.objects = []

        # ---- Ensure three memory buckets exist (even if empty) ----
        if not hasattr(self.heap, "episodic_memory"):
            self.heap.episodic_memory = []  # list of EpisodicMemory
        if not hasattr(self.heap, "working_memory"):
            self.heap.working_memory = []   # list of WorkingMemory
        if not hasattr(self.heap, "semantic_memory"):
            self.heap.semantic_memory = []  # list of SemanticSummary

        # (Optional) Ensure embedding_model attribute exists (retriever may use it for semantic search)
        if not hasattr(self.heap, "embedding_model"):
            self.heap.embedding_model = None

        # ---- Finally, create the retriever ----
        self.retriever = create_retriever(self.heap)

    def init_feedback(self,budget=3,earlystop=True):
        """
        Initialize feedback state for the problem-solving loop.

        Returns:
            dict: feedback info to be updated each iteration in `validate_feedback`.
        """
        feedback = {
            # Status
            "budget_remaining": budget,
            "early_stop": earlystop,
            "stop": False,
            "iteration": 0,

            # Results
            "solved": False,
            "key_point": None, # (HDR)
            "strategy": None,
            "solution": None,
            "score": None,

            # Feedback
            "restart_from":None,#TODO: restart from specific stage and keep the former stages' outputs
            "reflection": {
                "rollback_to": None,        # e.g., "problem_representation" / "strategy_selection" / "solution_generation" / "execution"）
                "notes": ""                 # feedback note
            }
        }
        return feedback

    def solve(self, action: ActionOp, pre_analysis: dict = None, **kwargs):
        from brainary.core.registry import CAPABILITIES
        self.problem_description=process_problem_description(action,kwargs)

        ## Step0: Initialize
        # Generate unique session_id for this problem-solving session (for short-term memory)
        desc_str = str(self.problem_description) + str(kwargs)
        self.session_id = f"ps_session_{hashlib.md5(desc_str.encode()).hexdigest()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self.feedback=self.init_feedback()
        self.solution=None
        if action.critical_thinking:
            self.strategy_cls=CAPABILITIES["critical_thinking"].get(action.critical_thinking)#
        if self.strategy_cls:
            self.strategy_cls=self.strategy_cls(self.llm)
            self.critical_thinking_method = getattr(self.strategy_cls, "perform", None)# the input of self.critical_thinking_method should be a string (which needs to be critic by it)

        ## Step0.5: Metacognition Planning - Generate execution plan before entering the loop
        print("=====Metacognition: Generating Execution Plan=====")
        self.execution_plan = self._planning(self.problem_description)
        self.metacognition_adjustments = {}  # Reset adjustments for new solve session
        print(f"=====Plan Generated: {len(self.execution_plan)} components=====")

        while not self.feedback["stop"]:
            print("=====Remaining Trials are: {} =====".format(self.feedback['budget_remaining']))
            # self.restart_from = self.feedback.get("restart_from")
            ## Step1: Problem Definition & Abstraction. TODO: Waiting for the Planning Capability for the Decomposition Module
            self.problem_definition()# meta cog 对接，每部都要有
            ## Step2: Solution Generation. TODO: Waiting for literature review
            self.solution_generation()
            ## Step3: Exectuion and Feedback. TODO: Waiting for metacognition module
            self.validate_feedback()

        if self.solution==None:
            # if not solution, use Direct LLM Call as substitute
            task = action.render(**(kwargs | pre_analysis))
            return self.llm.request(task)
        return self.solution
    
    # =================== Main Steps ===================
    def problem_definition(self):
        """
        Step 1: Problem Definition & Abstraction
        - Modeling: Extract G/E/C from the original description -> self.problem_brief
        - (Decomposition: TODO) Split the problem -> Recursively solve the subproblems and merge them
        - Representation: Generate the problem signature -> self.problem_signature
        * Metacognition monitoring via @with_metacognition decorator on component methods
        """
        ### Modeling (with metacognition monitoring via decorator)
        self.problem_brief = self._problem_modeling()

        ### Decomposition (with critical thinking, with memory)
        # self.sub_solutions = self._problem_decomposition(self.problem_brief)

        ### Representation (with metacognition monitoring via decorator)
        self.problem_signature = self._problem_representation(self.problem_brief)
        if isinstance(self.problem_signature, dict):
            self.feedback["key_point"] = self.problem_signature.get("HDR")


    def solution_generation(self):
        """
        Step 2: Solution Generation
        - Strategy Selection: choose a strategy using memory-weighted sampling.
        - Solution Generation: run the chosen strategy to produce a candidate solution.
        - Save solution to working memory (short-term, current problem session)
        """
        ### Literature Review
        # literature_list=_literature_review() #TODO: waiting for the literature reviews (maybe from lvye?)
        literature_list=[]

        ### Strategy Selection (memory-aware weighted sampling)
        strategy = self._strategy_selection(self.problem_brief, self.problem_signature)
        self.feedback["strategy"] = strategy
        ### Solution Candidates Generation
        score_internal=None
        if strategy == "heuristic_llm":
            sol, score_internal = self._strategy_heuristic_llm(self.problem_signature)
        elif strategy == "case_based_analogy":
            sol, _ = self._strategy_case_based(self.problem_signature,literature_list)
        else:
            # Fallback: default to iterative LLM if unexpected strategy shows up
            sol, score_internal = self._strategy_heuristic_llm(self.problem_signature)

        # Store draft solution (final scoring remains in validate_feedback)
        self.solution = sol
        # You may optionally keep the internal evaluator's score for reference:
        # (Do NOT overwrite feedback['score']; that belongs to the Evaluation stage.)
        self.feedback.setdefault("internal", {})["solution_gen_score"] = score_internal

        # --- Save solution to working memory (short-term, current problem session) ---
        try:
            key_point = self.feedback.get("key_point") or self.problem_signature.get("HDR", "")
            session_id = getattr(self, 'session_id', None)
            working_mem = extract_working_memory(
                step_name=f"solution_generation_{strategy}",
                step_type="solution_generation",
                execution_method=strategy,
                input_data={
                    "problem_signature": self.problem_signature,
                    "strategy": strategy
                },
                output_result=sol,
                success=True,
                execution_time=0.0,
                metadata={
                    "session_id": session_id,
                    "key_point": key_point,
                    "solution_text": sol,
                    "strategy": strategy,
                }
            )
            if hasattr(self.heap, "working_memory") and working_mem:
                self.heap.working_memory.append(working_mem)
        except Exception as e:
            # Keep the main loop robust even if memory write fails
            pass


    def validate_feedback(self):
        """
        Step 3: Execution and Feedback

        Components:
        A) Execute solution and evaluate effectiveness against G/E (get a score).
        B) Use LLM to analyze the result + signature and:
            - Update memory with strategy/solution outcomes.
            - Produce feedback including: key_point, strategy, solution, score, reflection, rollback_to.
            - Decide whether to restart and from which stage; also suggest which stages to skip next loop.

        Side effects:
        - self.feedback: updates score/notes/rollback_to/strategy/solution, plus restart plan.
        - episodic memory is appended with feedback entries usable by other modules.
        """
        ### Execution and Collect Feedback
        score=0
        solution_text = self.feedback.get("solution") or self.solution
        score, exec_notes = self._execute_and_score(solution_text, getattr(self, "problem_signature", {}))
        self.feedback["score"] = score

        ### Analyze Feedback TODO: use metacognition to get feedback
        self._feedback(score=score, exec_notes=exec_notes)

        ### Budget & loop control
        self.feedback["iteration"] += 1
        self.feedback["budget_remaining"] = max(0, int(self.feedback["budget_remaining"]) - 1)

        ###  Decide stop / restart based on current feedback info
        self._decide_next_step()

        # # Persist reflection fields into feedback
        # self.feedback["reflection"]["notes"] = (reflection.get("reflection", "") or "").strip()
        # if reflection.get("rollback_to"):
        #     self.feedback["reflection"]["rollback_to"] = reflection["rollback_to"]
        # ### Save and update memory
        # score = self.feedback.get("score", None)
        # if score is not None:
        #     self._record_keypoint_performance(self.feedback.get("key_point",""), score, extra={
        #         "goals": self.problem_brief.get("G", []),
        #         "constraints": self.problem_brief.get("C", []),
        #     })

        #     extract_content_relation_memory(
        #         content=f"Strategy '{self.feedback.get('strategy')}' achieved score {final_score}",
        #         entity_name="system",
        #         entity_type="agent",
        #         content_type="strategy_eval",           # ← distinct from 'key_point_eval'
        #         relationship_type="evaluated",
        #         episode_id=None,
        #         metadata={
        #             "strategy": self.feedback.get("strategy"),
        #             "score": float(final_score),
        #             "key_point": self.feedback.get("key_point"),
        #             "goals": self.problem_brief.get("G", []),
        #         }
        #     )

        # pass

    # =================== Step Implementation ===================
    @with_metacognition('problem_modeling', max_retries=1)
    def _problem_modeling(self, prompt=None):
        """
        Build a Problem Brief via LLM.

        Args:
            prompt (str | None): Optional custom modeling prompt. If None, a default
                general-purpose modeling prompt is used.

        Returns:
            dict: Problem Brief with keys {G, E, C}.
                - G: list[str]       (verifiable goals / acceptance criteria)
                - E: str             (evaluation / judgment criteria)
                - C: list[str]       (key constraints)

        Notes:
            - Resources (R) field has been removed from the current implementation
            - The default implementation uses the LLM for general modeling.
            - In practice, you may design task-specific modelers, e.g.:
                * For NL tasks: extract keywords and causal relations.
                * For code repos / error logs: reproduce errors and record
                input-symptom relationships for downstream steps.
        """
        problem_description = self.problem_description
        description_text = (
            "\n".join(problem_description) if isinstance(problem_description, list)
            else str(problem_description)
        )
        if prompt is None:
            messages = [
                "You are a problem modeler. Extract verifiable goals (G), evaluation criteria (E), and constraints (C) from the given description.",
                "Return a single JSON object with the keys: G, E, C.",
                "- G: 1-3 verifiable goals or final acceptance criteria (list)",
                "- E: Evaluation / judgment criteria (how to measure performance, success thresholds, etc.)",
                "- C: Key constraints (time/budget/environment/interfaces/dependencies, etc.) (list)",
                "If any field is missing, use an empty list or empty string as a placeholder.",
                "=== Problem Description ===",
                description_text
            ]
        else:
            # Allow advanced users to supply a custom modeling prompt.
            messages = [str(prompt), "=== Problem Description ===", description_text]

        # -------- Apply metacognition adjustments to prompt --------
        messages = self._get_adjusted_prompt('problem_modeling', messages)

        # -------- Query LLM and parse --------
        raw = self.llm.request(messages)
        parsed = _parse_first_json(raw)

        # Light-weight retry with a stricter instruction if parsing failed.
        if parsed is None:
            retry_messages = messages[:1] + [
                "Return ONLY a valid JSON object with keys G, E, C. No explanations.",
            ] + messages[1:]
            raw_retry = self.llm.request(retry_messages)
            parsed = _parse_first_json(raw_retry)

        # -------- Build normalized brief --------
        brief = {"G": [], "E": "", "C": []}#, "R": []
        if parsed is not None:
            brief.update({
                "G": parsed.get("G", brief["G"]) or [],
                "E": parsed.get("E", brief["E"]) or "",
                "C": parsed.get("C", brief["C"]) or [],
                # "R": parsed.get("R", brief["R"]) or [],
            })
        else:
            # Fallback: store the raw text in E so downstream steps have context.
            brief["E"] = raw

        return brief

    def _problem_decomposition(self, problem_brief: dict, enable_recursive: bool = False):
        """
        TODO: Update
        Decompose the problem into smaller subproblems.

        Args:
            problem_brief (dict): The current Problem Brief (G, E, C).
            enable_recursive (bool): If True, attempt to propose subproblems via LLM
                and recursively solve them. If False (default), this function acts
                as a placeholder and returns None.

        Returns:
            dict | None: If enabled and successful, a dict such as:
                {
                    "subproblems": [ ... ],       # a list of subproblem briefs/specs
                    "subsolutions": [ ... ],      # results from solving each subproblem
                    "combined_solution": None     # merged/aggregated final solution (placeholder)
                }
            Otherwise, returns None.

        Notes:
            - This is a placeholder for now. The typical flow would be:
                1) Use the LLM to propose a top-down decomposition based on G/C.
                2) For each subproblem, call back into the solver (recursion) with
                a proper "action" and context, then collect subsolutions.
                3) Aggregate/merge subsolutions using E (or domain-specific rules).
            - Because "action" varies across domains, the recursive call is not
            implemented here; you can plug in your own logic later.
        """

        if not enable_recursive:
            return None

        # --- Ask LLM for a structured decomposition plan ---
        messages = [
            "You are a decomposition planner. Propose a top-down decomposition for the given problem.",
            "Return a JSON object with the keys:",
            "  - subproblems: a list of subproblem specs; each item should include a short name, a brief goal, and key constraints.",
            "  - aggregation: a short note describing how to combine subsolutions.",
            "=== Problem Brief ===",
            str(problem_brief),
        ]


        raw = self.llm.request(messages)
        plan = _parse_first_json(raw)
        if plan is None:
            # Small retry to enforce JSON-only output
            retry_messages = [
                "Return ONLY a valid JSON object with keys: subproblems, aggregation.",
            ] + messages
            raw_retry = self.llm.request(retry_messages)
            plan = _parse_first_json(raw_retry)

        if plan is None:
            # Could not get a structured plan; fallback to None but keep context in reflection.
            self.feedback["reflection"]["notes"] += "\n[decomposition] Failed to obtain a structured plan."
            return None

        # Placeholder structure. In a real implementation, loop over subproblems,
        # create sub-actions, call self.solve(...), and aggregate results.
        result = {
            "subproblems": plan.get("subproblems", []),
            "subsolutions": [],        # TODO: fill by recursively solving each subproblem
            "combined_solution": None, # TODO: aggregate with domain-specific logic
            "aggregation_note": plan.get("aggregation", ""),
        }
        return result


    def _select_key_point(self, problem_brief: dict):
        """
        Pick HDR (key point) using semantic memory (long-term, cross-problem) when available; otherwise ask LLM.
        Memory strategy:
        - Retrieve from semantic memory based on similar task descriptions and goals (G)
        - Aggregate past performance per key_point from metadata.score
        - Choose the highest avg score (tie-breaker: most recent)
        Required metadata keys: task_description, G, key_point, score
        """
        # Get task description from problem_description
        task_desc = ""
        if hasattr(self, "problem_description"):
            task_desc = (
                "\n".join(self.problem_description) if isinstance(self.problem_description, list)
                else str(self.problem_description)
            )

        goals_txt = "; ".join(problem_brief.get("G", [])) or "current goals"

        # 1) Try semantic memory (long-term, cross-problem)
        if self.retriever is not None and self.heap is not None:
            query = f"task: {task_desc[:500]} goals: {goals_txt} key point HDR selection"
            buckets = self.retriever.retrieve_memory(query=query, memory_types=["semantic"], top_k=10)

            # Aggregate scores from semantic memories where metadata carries {'task_description', 'G', 'key_point', 'score'}
            kp_stats = {}  # key_point -> {'sum':..., 'cnt':..., 'latest_ts':...}
            for sem in buckets.get("semantic", []) or []:
                md = getattr(sem, "metadata", None)
                kp = md.get("key_point") if md else None
                sc = md.get("score") if (md and isinstance(md.get("score"), (int, float))) else None
                if not kp:
                    continue
                stat = kp_stats.setdefault(kp, {'sum': 0.0, 'cnt': 0, 'latest_ts': getattr(sem, "timestamp", None)})
                if sc is not None:
                    stat['sum'] += float(sc)
                    stat['cnt'] += 1
                # Keep the most recent timestamp
                ts = getattr(sem, "timestamp", None)
                if ts and (stat['latest_ts'] is None or ts > stat['latest_ts']):
                    stat['latest_ts'] = ts

            if kp_stats:
                # Choose best by avg score; tie-breaker by recency
                def _score_item(item):
                    kp, s = item
                    avg = s['sum'] / max(1, s['cnt'])
                    return (avg, s['latest_ts'] or 0)
                best_kp = sorted(kp_stats.items(), key=_score_item, reverse=True)[0][0]
                return best_kp

        # 2) Fallback to LLM suggestion
        prompt = [
            "You are selecting the single most critical key point (HDR) for solving the task.",
            "Given the Problem Brief (G/E/C), return ONLY a short phrase for HDR.",
            "=== Problem Brief ===",
            str(problem_brief)
        ]
        hdr = self.llm.request(prompt)
        # keep it compact
        return (hdr or "").strip().splitlines()[0][:120]

    @with_metacognition('problem_representation', max_retries=1)
    def _problem_representation(self, problem_brief: dict, custom_prompt: str | None = None, max_iters: int = 3):
        """
        Build a problem representation (signature) with a critical-thinking gate and
        memory-informed key point (HDR) selection.

        Iterative process (up to `max_iters`):
        1) Generate a representation via LLM (JSON: S0, G, O, C, E, K, HDR).
        2) Run critical thinking to judge reasonableness.
        3) If unreasonable, capture feedback, amend the instruction, and retry.

        Args:
            problem_brief (dict): Current Problem Brief (G, E, C).
            custom_prompt (str | None): Optional custom instruction for representation.
            max_iters (int): Maximum refinement rounds (default: 3).

        Returns:
            dict: Representation with keys {S0, G, O, C, E, K, HDR}.
        """

        problem_description = self.problem_description
        description_text = (
            "\n".join(problem_description) if isinstance(problem_description, list)
            else str(problem_description)
        )
        def _build_rep_messages(instruction: str, brief: dict, description_text:str):
            """Compose LLM messages for representation generation."""
            return [
                instruction,
                "Return ONLY a valid JSON object with the keys: S0, G, O, C, E, K, HDR.",
                "- S0: initial state / known conditions (list or bullets).",
                "- G : target state / acceptance tests (aligned/refined from Brief's G).",
                "- O : available operators/actions (executable edit/analyze/verify moves).",
                "- C : constraints (aligned/refined from Brief's C).",
                "- E : evaluation/judgment criteria (quantifiable/executable when possible).",
                "- K : knowledge/example keywords for retrieval and prompts.",
                "- HDR: the single most critical key point for this round.",
                "=== Problem Brief ===",
                str(brief),
                "=== Problem Description ===",
                description_text,
            ]#TODO: knowledge and operators should be extracted and detailed in literature review

        def _critique_and_fix(rep: dict) -> dict | None:
            """
            Ask the critical-thinking module to judge reasonableness and propose fixes.
            Expected JSON from the critic:
            {
                "is_reasonable": true|false,
                "issues": ["...", "..."],
                "fix_instruction": "Concise guidance to improve the next representation.",
                "rollback_to": "problem_modeling|problem_representation|strategy_selection|solution_generation|execution"  # optional
            }
            Returns the parsed dict or None on failure.
            """
            if not getattr(self, "critical_thinking_method", None):
                return {"is_reasonable": True, "issues": [], "fix_instruction": ""}

            critic_messages = [
                "You are a critical-thinking checker. Judge if the following representation is reasonable and actionable.",
                "Return ONLY a JSON object with keys: is_reasonable, issues, fix_instruction, rollback_to (optional).",
                "- is_reasonable: boolean",
                "- issues: list of short strings",
                "- fix_instruction: concise, directly usable instruction to repair the representation",
                "- rollback_to (optional): one of 'problem_modeling','problem_representation','strategy_selection','solution_generation','execution'",
                "=== Representation ===",
                str(rep),
            ]
            raw_critique = self.critical_thinking_method("\n".join(critic_messages))  # expects str in your implementation
            parsed = _parse_first_json(raw_critique or "")
            if parsed is None:
                # Fallback to heuristic: if critic text contains "good"/"reasonable", pass; else fail.
                heuristic_pass = bool(re.search(r"\b(reasonable|sound|good enough|looks good)\b", str(raw_critique), re.I))
                parsed = {
                    "is_reasonable": heuristic_pass,
                    "issues": [] if heuristic_pass else [str(raw_critique)[:500]],
                    "fix_instruction": "" if heuristic_pass else "Tighten definitions for S0/G; ensure O are executable and E is measurable.",
                }
            # Persist notes and optional rollback target
            notes_prev = self.feedback["reflection"].get("notes", "")
            self.feedback["reflection"]["notes"] = (notes_prev + ("\n" if notes_prev else "") + str(raw_critique or "")).strip()
            # rb = parsed.get("rollback_to")
            # if rb:
            #     self.feedback["reflection"]["rollback_to"] = rb
            return parsed
    
        # ---------- memory-informed HDR preference ----------
        # Prefer a key point from memory when available; fallback to LLM if not.
        preselected_hdr = ""
        try:
            if hasattr(self, "_select_key_point"):
                preselected_hdr = (self._select_key_point(problem_brief) or "").strip()
        except Exception as e:
            preselected_hdr = ""

        # ---------- initial instruction ----------
        base_instruction = (
            custom_prompt
            if custom_prompt is not None
            else "You are a problem representation builder. Produce a precise, operational representation."
        )
        if preselected_hdr:
            base_instruction += (
                f"\n\nPreference: set HDR (key point) to '{preselected_hdr}' if it is reasonable given the brief."
            )
        

        # ---------- iteration loop ----------
        rep = {"S0": [], "G": [], "O": [], "C": [], "E": "", "K": [], "HDR": ""}
        extra_fix = ""  # will be appended from critic's fix_instruction
        for _round in range(max_iters):
            # 1) Current instruction with any accumulated fixes
            instruction = base_instruction if not extra_fix else f"{base_instruction}\n\nRefinement hints:\n{extra_fix}"
            messages = _build_rep_messages(instruction, problem_brief,description_text)

            # 1.5) Apply metacognition adjustments to prompt
            messages = self._get_adjusted_prompt('problem_representation', messages)

            # 2) Generate representation via LLM
            raw = self.llm.request(messages)
            parsed = _parse_first_json(raw)

            if parsed is None:
                # One strict retry to enforce JSON-only output
                retry_messages = ["Return ONLY a valid JSON object with keys: S0, G, O, C, E, K, HDR. No explanations."] + messages
                raw_retry = self.llm.request(retry_messages)
                parsed = _parse_first_json(raw_retry)

            # Normalize candidate representation (keep raw in E as a fallback context)
            cand = {"S0": [], "G": [], "O": [], "C": [], "E": "", "K": [], "HDR": ""}
            if parsed is not None:
                for k in cand.keys():
                    cand[k] = parsed.get(k, cand[k]) or cand[k]
                # If memory suggested an HDR and model omitted it, gently set it if empty.
                if preselected_hdr and not cand.get("HDR"):
                    cand["HDR"] = preselected_hdr
            else:
                cand["E"] = raw

            # 3) Critical-thinking gate
            critique = _critique_and_fix(cand)
            if critique.get("is_reasonable", False):
                rep = cand
                break  # pass gate
            else:
                # Amend instruction for the next round
                extra_fix = (critique.get("fix_instruction", "") or "").strip()
                rep = cand  # keep latest candidate for visibility

        # ---------- finalize ----------
        # If representation remains weak after all refinements, annotate (non-fatal).
        if not any([rep.get("G"), rep.get("O"), rep.get("E")]):
            prev_notes = self.feedback["reflection"].get("notes", "")
            self.feedback["reflection"]["notes"] = (
                (prev_notes + ("\n" if prev_notes else "") + "[representation] Weak representation after max refinements.")
            ).strip()

        return rep


    def _literature_review(self, problem_signature: dict, method: str = 'local_db') -> dict:
        """
        Retrieve relevant knowledge and operators from local database to enrich problem signature.

        Objective:
            - Based on the problem signature's K (knowledge keywords), HDR (key point), and G (goals),
              query local database for similar cases, domain knowledge, and available operators.
            - Extend knowledge K with retrieved domain-specific knowledge.
            - Extend operators O with retrieved action operators.
            - Return enriched knowledge and operators for solution generation.

        Args:
            problem_signature (dict): Current problem signature with keys {S0, G, O, C, E, K, HDR}.
            method (str): Retrieval method. Options:
                - 'local_db': Query local knowledge database (default)
                - 'web': Web search (future implementation)
                - 'hybrid': Combine local_db and web (future implementation)

        Returns:
            dict: Enriched knowledge and operators with keys:
                - 'knowledge_K': list[str] - Extended knowledge items (original K + retrieved knowledge)
                - 'operators_O': list[str] - Extended operators (original O + retrieved operators)
                - 'sources': list[dict] - Source references for traceability
                    Each source: {'type': 'knowledge'|'operator', 'content': str, 'score': float, 'metadata': dict}

        Implementation Notes:
            - Uses problem signature fields for matching:
                * HDR (key point): Primary matching criterion
                * K (knowledge keywords): Secondary matching criterion
                * G (goals): Contextual matching criterion
            - Database query stub: _query_knowledge_database() (to be implemented)
            - Ranking: By relevance score, recency, and credibility
            - Deduplication: Remove redundant knowledge/operators

        TODO:
            - Implement _query_knowledge_database() to interface with local knowledge base
            - Add web search integration for 'web' and 'hybrid' methods
            - Implement ranking and filtering logic
            - Add caching mechanism for frequently queried patterns
        """
        # Extract query fields from problem signature
        hdr = problem_signature.get("HDR", "")
        knowledge_keywords = problem_signature.get("K", [])
        goals = problem_signature.get("G", [])
        current_operators = problem_signature.get("O", [])

        # Initialize result structure
        result = {
            "knowledge_K": list(knowledge_keywords),  # Start with original K
            "operators_O": list(current_operators),    # Start with original O
            "sources": []
        }

        # Method dispatch
        if method == 'local_db':
            # Query local database (stub for now)
            retrieved = self._query_knowledge_database(
                hdr=hdr,
                keywords=knowledge_keywords,
                goals=goals
            )
            #TODO: implement the knowledge database query

            # Extend knowledge K
            for knowledge_item in retrieved.get("knowledge", []):
                content = knowledge_item.get("content", "")
                if content and content not in result["knowledge_K"]:
                    result["knowledge_K"].append(content)
                    result["sources"].append({
                        "type": "knowledge",
                        "content": content,
                        "score": knowledge_item.get("score", 0.0),
                        "metadata": knowledge_item.get("metadata", {})
                    })

            # Extend operators O
            for operator_item in retrieved.get("operators", []):
                content = operator_item.get("content", "")
                if content and content not in result["operators_O"]:
                    result["operators_O"].append(content)
                    result["sources"].append({
                        "type": "operator",
                        "content": content,
                        "score": operator_item.get("score", 0.0),
                        "metadata": operator_item.get("metadata", {})
                    })

        elif method == 'web':
            # TODO: Implement web search integration
            pass

        elif method == 'hybrid':
            # TODO: Combine local_db and web results
            pass

        return result

    def _query_knowledge_database(self, hdr: str, keywords: list, goals: list) -> dict:
        """
        Query local knowledge database for relevant knowledge and operators.

        Args:
            hdr (str): Key point (HDR) for primary matching
            keywords (list): Knowledge keywords for secondary matching
            goals (list): Goals for contextual matching

        Returns:
            dict: Retrieved knowledge and operators with keys:
                - 'knowledge': list[dict] - Each item: {'content': str, 'score': float, 'metadata': dict}
                - 'operators': list[dict] - Each item: {'content': str, 'score': float, 'metadata': dict}

        TODO: Implement actual database query logic.
        Current implementation is a stub that returns empty results.

        Implementation Plan:
            1. Build query vector from hdr, keywords, goals (e.g., using embeddings)
            2. Query vector database (e.g., FAISS, Chroma, Pinecone) for similar entries
            3. Filter and rank results by:
                - Semantic similarity score
                - Recency (timestamp)
                - Credibility (source quality)
            4. Return top-k results (k=5 for knowledge, k=3 for operators)
        """
        # STUB: Return empty results for now
        # TODO: Replace with actual database query implementation
        return {
            "knowledge": [],
            "operators": []
        }

        # Example implementation skeleton (commented out):
        # if self.knowledge_db is None:
        #     return {"knowledge": [], "operators": []}
        #
        # # Build query
        # query_text = f"HDR: {hdr}; Keywords: {', '.join(keywords)}; Goals: {', '.join(goals)}"
        #
        # # Query knowledge base
        # knowledge_results = self.knowledge_db.query(
        #     query_text=query_text,
        #     collection="domain_knowledge",
        #     top_k=5
        # )
        #
        # # Query operators base
        # operator_results = self.knowledge_db.query(
        #     query_text=query_text,
        #     collection="action_operators",
        #     top_k=3
        # )
        #
        # return {
        #     "knowledge": knowledge_results,
        #     "operators": operator_results
        # }

    @with_metacognition('strategy_selection', max_retries=1)
    def _strategy_selection(self, brief: dict, rep: dict) -> str:
        """
        Choose a strategy based on historical performance in semantic memory (long-term, cross-problem).
        When memory is available:
            - Retrieve from semantic memory based on similar task descriptions, goals (G), and key_point (HDR)
            - Aggregate average score per strategy
            - Sample a strategy with probability proportional to avg score (softmax-like)
        When no memory:
            - Uniform random selection among available strategies.
        Required metadata keys: task_description, G, key_point, strategy, score

        Returns:
            str: chosen strategy name in {"heuristic_llm", "case_based_analogy"}
        """
        strategies = ["heuristic_llm", "case_based_analogy"]
        kp = self.feedback.get("key_point") or rep.get("HDR", "")
        goals = brief.get("G", [])

        # Get task description from problem_description
        task_desc = ""
        if hasattr(self, "problem_description"):
            task_desc = (
                "\n".join(self.problem_description) if isinstance(self.problem_description, list)
                else str(self.problem_description)
            )

        # Try to fetch historical strategy performance from semantic memory (long-term, cross-problem)
        weights = {s: 0.0 for s in strategies}
        if self.retriever is not None and self.heap is not None:
            query = f"task: {task_desc[:500]} goals: {('; '.join(goals) or 'N/A')} key point: {kp or 'N/A'} strategy performance"
            buckets = self.retriever.retrieve_memory(query=query, memory_types=["semantic"], top_k=20)

            # Expect semantic items whose metadata carry {'task_description', 'G', 'key_point', 'strategy', 'score'}
            stats = {}  # strategy -> {'sum': float, 'cnt': int}
            for sem in (buckets.get("semantic") or []):
                md = getattr(sem, "metadata", None)
                if not md:
                    continue
                sname = md.get("strategy")
                sc = md.get("score")
                if sname in weights and isinstance(sc, (int, float)):
                    slot = stats.setdefault(sname, {"sum": 0.0, "cnt": 0})
                    slot["sum"] += float(sc)
                    slot["cnt"] += 1

            for s in strategies:
                if s in stats and stats[s]["cnt"] > 0:
                    weights[s] = stats[s]["sum"] / stats[s]["cnt"]

        # Weighted sampling; if all zero, uniform random
        total = sum(max(0.0, w) for w in weights.values())
        if total <= 1e-9:
            return random.choice(strategies)

        # Normalize to probabilities; softmax-like temperature could be added if desired
        probs = {s: max(0.0, w) / total for s, w in weights.items()}
        r = random.random()
        cum = 0.0
        for s in strategies:
            cum += probs[s]
            if r <= cum:
                return s
        return strategies[-1]  # fallback

    @with_metacognition('strategy_heuristic_llm', max_retries=1)
    def _strategy_heuristic_llm(self, rep: dict, max_iters: int = 3, earlystop_score=0.95):
        """
        Multi-round solution generation with self-evaluation loop.
        Each round:
            1) Generate a candidate solution from the problem signature.
            2) Evaluate the candidate via LLM (score + critique).
            3) Inject critique back into the prompt to improve next round.

        Returns:
            (best_solution_text, best_internal_score)
        """
        history_feedback = ""
        best_sol, best_score = "", -1.0

        for i in range(max_iters):
            origin_messages = [
                "You are a solution generator. Produce a concrete, executable solution to the problem.",
                "Use the provided problem signature (S0/G/O/C/E/K/HDR).",
                "Return comprehensive steps, rationale, and potential failure checks.",
                "=== Problem Signature ===",
                json.dumps(rep, ensure_ascii=False),
            ]
            if history_feedback:
                messages = copy.deepcopy(origin_messages) + [
                    "=== Reviewer Feedback (from previous round) ===",
                    '\n'.join(history_feedback),
                    "Please refine your solution based on the feedback above.",
                ]
            else:
                messages=copy.deepcopy(origin_messages)

            # Apply metacognition adjustments to prompt
            messages = self._get_adjusted_prompt('strategy_heuristic_llm', messages)

            candidate = self.llm.request(messages)
            # Evaluate the candidate solution
            eval_res = self._evaluate_candidate(candidate, rep)
            score = float(eval_res.get("score", 0.0))
            critique = eval_res.get("critique", "")

            # Keep best
            if score > best_score:
                best_score, best_sol = score, candidate

            # Prepare feedback for the next round
            history_feedback = critique or ""
            if history_feedback=="" or best_score>=earlystop_score:
                return best_sol, best_score # early stop
        return best_sol, best_score


    @with_metacognition('strategy_case_based', max_retries=1)
    def _strategy_case_based(self, rep: dict, literature: dict, top_k: int = 3):
        """
        Retrieve prior solutions from working memory (short-term, current problem session)
        based on HDR (key point), then combine with knowledge K and operators O to produce a new solution.

        Expected memory format for solutions (working memory):
            - metadata may include:
                * 'session_id': current problem session ID
                * 'key_point' (HDR): task key point
                * 'solution_text': full solution text
        Maximum 3 reference solutions are retrieved.
        """
        knowledge_snippets = []
        kp = rep.get('HDR', '')

        if self.retriever is not None and self.heap is not None:
            # Build query based on HDR (key point) from current session
            query = f"session solution for HDR: {kp or 'N/A'}"

            # Filter working memory by session_id
            session_id = getattr(self, 'session_id', None)
            buckets = self.retriever.retrieve_memory(
                query=query,
                memory_types=["working"],
                top_k=top_k  # max 3 solutions
            )

            # Collect solutions from working memory for current session
            for wm in (buckets.get("working") or []):
                md = getattr(wm, "metadata", None) or {}
                # Filter by session_id to ensure short-term memory for current problem
                if session_id and md.get("session_id") != session_id:
                    continue

                solution_text = md.get("solution_text") or getattr(wm, "output_result", None) or ""
                if solution_text:
                    knowledge_snippets.append({
                        "source": "working_memory",
                        "snippet": str(solution_text),
                        "key_point": md.get("key_point", "")
                    })
                    if len(knowledge_snippets) >= top_k:  # max 3 solutions
                        break

        # Build an adaptation prompt combining retrieved solutions, knowledge K, and operators O
        context_block = "\n\n".join(
            f"- Reference solution {i+1} (HDR: {k['key_point']}): {k['snippet'][:800]}"
            for i, k in enumerate(knowledge_snippets[:top_k])
        ) or "None."

        knowledge_k = rep.get('K', [])
        operators_o = rep.get('O', [])

        messages = [
            "You are a case-based reasoner. Combine prior solutions, knowledge, and available operators to solve the current problem.",
            "Synthesize a new solution that fits the current constraints and goals.",
            "Be explicit about how retrieved cases, knowledge, and operators inform your steps.",
            "=== Current Problem Signature ===",
            json.dumps(rep, ensure_ascii=False),
            "=== Retrieved Reference Solutions (from current session) ===",
            context_block,
            "=== Available Knowledge (K) ===",
            json.dumps(knowledge_k, ensure_ascii=False),
            "=== Available Operators (O) ===",
            json.dumps(operators_o, ensure_ascii=False),
            "=== Your Task ===",
            "Produce a step-by-step solution with clear justifications and checks.",
        ]
        # if literature != []:
        #     messages += ["=== Literature Reference ===", str(literature)]

        # Apply metacognition adjustments to prompt
        messages = self._get_adjusted_prompt('strategy_case_based', messages)

        candidate = self.llm.request(messages)

        score = None  # not assign a score now
        return candidate, score


    def _evaluate_candidate(self, solution_text: str, rep: dict) -> dict:
        """
        Ask the LLM to evaluate a solution against the representation's E (evaluation criteria)
        and G (goals). The model must return JSON:
            { "score": <float-0to1>, "critique": "<short text>" }
        """
        eval_messages = [
            "You are a strict evaluator. Assess the solution quality against goals (G) and evaluation criteria (E).",
            "Return ONLY a JSON object with keys: score, critique.",
            "- score: a float in [0,1] reflecting expected effectiveness and feasibility.",
            "- critique: 3-5 concise points on strengths and improvements.",
            "=== Problem Signature (E & G) ===",
            json.dumps({"G": rep.get("G", []), "E": rep.get("E", "")}, ensure_ascii=False),
            "=== Candidate Solution ===",
            str(solution_text),
        ]
        raw = self.llm.request(eval_messages)
        parsed = _parse_first_json(raw) or {}
        # Normalize fields
        try:
            parsed["score"] = float(parsed.get("score", 0.0))
        except Exception:
            parsed["score"] = 0.0
        parsed["critique"] = parsed.get("critique", "") or ""
        return parsed


    def _execute_and_score(self, solution_text: str, rep: dict) -> tuple[float, str]:
        """
        Execute the solution and compute an effectiveness score.
        For now, use _evaluate_candidate as a proxy evaluator (0..1).
        Returns:
            (score, execution_notes)
        """
        if not solution_text:
            return 0.0, "No solution available to execute."

        eval_res = self._evaluate_candidate(solution_text, rep)
        score = float(eval_res.get("score", 0.0))
        notes = eval_res.get("critique", "") or ""
        return score, notes

    def _feedback(self, score: float, exec_notes: str = "", truncated: int = 5000):
        """
        Use the LLM to analyze execution results and produce structured feedback.
        Persist feedback into semantic memory (long-term, cross-problem) with required metadata keys:
        - For key_point evaluation: task_description, G, key_point, score
        - For strategy evaluation: task_description, G, key_point, strategy, score
        Also update self.feedback fields (reflection, solved, restart_from).
        """
        # Build a concise context for the feedback model
        rep = getattr(self, "problem_signature", {}) or {}
        brief = getattr(self, "problem_brief", {}) or {}
        key_point = self.feedback.get("key_point") or rep.get("HDR", "")
        strategy = self.feedback.get("strategy") or "unknown"
        solution_text = (self.feedback.get("solution") or self.solution or "").strip()

        # Get task description
        task_desc = ""
        if hasattr(self, "problem_description"):
            task_desc = (
                "\n".join(self.problem_description) if isinstance(self.problem_description, list)
                else str(self.problem_description)
            )

        # Ask LLM to synthesize reflection and rollback target
        fb_messages = [
            "You are a metacognitive analyst. Given the problem signature, strategy, solution, and execution score,",
            "produce a concise JSON feedback with keys:",
            "  - reflection: short text (2-5 sentences) summarizing strengths and issues",
            "  - rollback_to: one of 'problem_modeling','problem_representation','strategy_selection','solution_generation','execution' (if restart is needed)",
            "  - suggestions: 3-5 bullet improvements for the next iteration",
            "Return ONLY a valid JSON object.",
            "=== Problem Signature ===",
            json.dumps(rep, ensure_ascii=False),
            "=== Strategy ===",
            str(strategy),
            "=== Key Point (HDR) ===",
            str(key_point),
            "=== Solution (truncated to first 5000 chars) ===",
            solution_text[:truncated],
            "=== Execution Score & Notes ===",
            json.dumps({"score": score, "notes": exec_notes}, ensure_ascii=False),
        ]
        raw_fb = self.llm.request(fb_messages)
        parsed_fb = _parse_first_json(raw_fb) or {}
        reflection_text = (parsed_fb.get("reflection") or "").strip()
        rollback_to = (parsed_fb.get("rollback_to") or "").strip().lower() or None
        suggestions = parsed_fb.get("suggestions") or []

        # Update feedback fields
        self.feedback["reflection"]["notes"] = reflection_text or exec_notes or self.feedback["reflection"].get("notes", "")
        if rollback_to in {"problem_modeling","problem_representation","strategy_selection","solution_generation","execution"}:
            self.feedback["reflection"]["rollback_to"] = rollback_to

        # --- Persist semantic memory: key_point evaluation (long-term, cross-problem) ---
        # Required metadata: task_description, G, key_point, score
        try:
            semantic_summary_kp = SemanticSummary(
                key_concepts=[key_point] if key_point else [],
                relationships=[f"key_point->{strategy}"],
                context=f"Task: {task_desc[:500]}; Goals: {brief.get('G', [])}",
                importance_score=float(score),
                semantic_hash=hashlib.md5(f"{task_desc}{key_point}".encode()).hexdigest(),
                summary_text=f"Key point '{key_point}' scored {score:.3f} on goals {brief.get('G', [])}",
                metadata={
                    "task_description": task_desc[:1000],
                    "G": brief.get("G", []),
                    "key_point": key_point,
                    "score": float(score),
                }
            )
            if hasattr(self.heap, "semantic_memory"):
                self.heap.semantic_memory.append(semantic_summary_kp)
        except Exception as e:
            # Keep the main loop robust even if memory write fails
            pass

        # --- Persist semantic memory: strategy evaluation (long-term, cross-problem) ---
        # Required metadata: task_description, G, key_point, strategy, score
        try:
            semantic_summary_strategy = SemanticSummary(
                key_concepts=[key_point, strategy] if key_point else [strategy],
                relationships=[f"strategy->{key_point}", f"score->{score}"],
                context=f"Task: {task_desc[:500]}; Goals: {brief.get('G', [])}; HDR: {key_point}",
                importance_score=float(score),
                semantic_hash=hashlib.md5(f"{task_desc}{key_point}{strategy}".encode()).hexdigest(),
                summary_text=f"Strategy '{strategy}' with key point '{key_point}' scored {score:.3f} on goals {brief.get('G', [])}",
                metadata={
                    "task_description": task_desc[:1000],
                    "G": brief.get("G", []),
                    "key_point": key_point,
                    "strategy": strategy,
                    "score": float(score),
                }
            )
            if hasattr(self.heap, "semantic_memory"):
                self.heap.semantic_memory.append(semantic_summary_strategy)
        except Exception as e:
            pass

        # Surface a compact feedback string for visibility (optional)
        self.feedback.setdefault("summary", {})
        self.feedback["summary"]["feedback_short"] = {
            "key_point": key_point,
            "strategy": strategy,
            "score": score,
            "rollback_to": rollback_to,
        }

    def _decide_next_step(self, success_threshold: float = 0.95):
        """
        Decide whether to stop or restart based on:
        - score vs threshold
        - early_stop setting
        - budget remaining
        - reflection.rollback_to
        Updates:
        - self.feedback['solved'], ['stop']
        - self.feedback['restart_from'] (optional hint for the next loop)
        """
        score = float(self.feedback.get("score") or 0.0)
        budget = int(self.feedback.get("budget_remaining") or 0)
        early = bool(self.feedback.get("early_stop"))
        rollback_to = self.feedback["reflection"].get("rollback_to")

        # Success condition
        if score >= success_threshold:
            self.feedback["solved"] = True
            if early:
                self.feedback["stop"] = True
            return

        # Budget check
        if budget <= 0:
            self.feedback["stop"] = True
            return

        # Restart plan
        # Set a hint for the next iteration about where to resume work.
        # The outer loop still calls `problem_definition -> solution_generation -> validate_feedback`,
        # but you can use `self.feedback['restart_from']` inside those steps to skip/fast-path.
        restart_from = None
        valid_stages = {
            "problem_modeling",
            "problem_representation",
            "strategy_selection",
            "solution_generation",
            "execution"
        }
        if rollback_to in valid_stages:
            restart_from = rollback_to
        else:
            # If no explicit rollback target, default to improving strategy/solution.
            restart_from = "strategy_selection"

        self.feedback["restart_from"] = restart_from
        # Keep the loop going
        self.feedback["stop"] = False

    # =================== Metacognition Module ===================
    def _planning(self, problem_description: list) -> dict:
        """
        Pre-execution planning: Use LLM to generate expected execution plan for all components.

        This function is called before entering the problem-solving loop to establish
        expectations for each component's execution. The plan serves as a baseline for
        metacognition monitoring during actual execution.

        Args:
            problem_description (list): Processed problem description from process_problem_description()

        Returns:
            dict: Planning expectations for each component with keys:
                - 'problem_modeling': Expected G/E/C structure and key elements
                - 'problem_representation': Expected S0/G/O/C/E/K/HDR and key challenges
                - 'strategy_selection': Expected suitable strategies and reasoning
                - 'strategy_heuristic_llm': Expected solution approach and iteration needs
                - 'strategy_case_based': Expected analogies and adaptation strategy
                - 'overall_plan': High-level execution plan and potential issues

        Each component expectation contains:
            - 'expected_output': Description of expected outputs
            - 'key_considerations': Important factors to consider
            - 'potential_issues': Anticipated challenges
            - 'success_criteria': Criteria to judge if execution is on track
        """
        description_text = (
            "\n".join(problem_description) if isinstance(problem_description, list)
            else str(problem_description)
        )

        planning_messages = [
            "You are a metacognitive planning agent. Analyze the problem and create execution expectations for each component.",
            "Generate a structured plan with expectations for: problem_modeling, problem_representation, strategy_selection, strategy_heuristic_llm, strategy_case_based.",
            "For each component, specify: expected_output, key_considerations, potential_issues, success_criteria.",
            "Return a JSON object with keys for each component plus 'overall_plan'.",
            "",
            "=== Problem Description ===",
            description_text,
            "",
            "=== Component Descriptions ===",
            "1. problem_modeling: Extracts verifiable goals (G), evaluation criteria (E), and constraints (C) from problem description",
            "   - Output format: {'G': [...], 'E': '...', 'C': [...]}",
            "",
            "2. problem_representation: Builds operational representation with initial state (S0), goals (G), operators (O), constraints (C), evaluation (E), knowledge (K), and key point (HDR)",
            "   - Output format: {'S0': [...], 'G': [...], 'O': [...], 'C': [...], 'E': '...', 'K': [...], 'HDR': '...'}",
            "",
            "3. strategy_selection: Selects solution strategy based on problem characteristics and memory",
            "   - Output format: string, one of ['heuristic_llm', 'case_based_analogy']",
            "",
            "4. strategy_heuristic_llm: Generates solutions iteratively with self-evaluation",
            "   - Output format: tuple (solution_text: str, score: float)",
            "",
            "5. strategy_case_based: Retrieves and adapts prior solutions from working memory",
            "   - Output format: tuple (solution_text: str, score: float or None)",
            "",
            "=== Expected JSON Structure ===",
            "{",
            "  'problem_modeling': {",
            "    'expected_output': 'What G/E/C structure should contain (NOTE: no R field)',",
            "    'key_considerations': ['Completeness of goals', 'Clarity of constraints', 'Measurability of criteria'],",
            "    'potential_issues': ['Missing constraints', 'Vague goals', 'Unmeasurable evaluation'],",
            "    'success_criteria': 'G contains 1-3 verifiable goals, C lists key constraints, E is clear and measurable'",
            "  },",
            "  'problem_representation': {",
            "    'expected_output': 'What S0/G/O/C/E/K/HDR should contain',",
            "    'key_considerations': ['Actionable operators', 'Retrievable knowledge', 'Critical key point'],",
            "    'potential_issues': ['Abstract operators', 'Missing HDR', 'Incomplete state'],",
            "    'success_criteria': 'All fields populated, HDR identifies critical focus, O are executable'",
            "  },",
            "  'strategy_selection': {",
            "    'expected_output': 'Which strategy (heuristic_llm or case_based_analogy) and why',",
            "    'key_considerations': ['Problem novelty', 'Memory availability', 'Time constraints'],",
            "    'potential_issues': ['Insufficient memory for case-based', 'Wrong strategy choice'],",
            "    'success_criteria': 'Strategy aligns with problem characteristics and available resources'",
            "  },",
            "  'strategy_heuristic_llm': {",
            "    'expected_output': 'Solution quality and iteration efficiency',",
            "    'key_considerations': ['Solution completeness', 'Iteration convergence', 'Score improvement'],",
            "    'potential_issues': ['Non-converging iterations', 'Low quality solutions'],",
            "    'success_criteria': 'Solution score > 0.7, addresses all goals in G, respects constraints in C'",
            "  },",
            "  'strategy_case_based': {",
            "    'expected_output': 'Adapted solution from retrieved cases',",
            "    'key_considerations': ['Case relevance', 'Adaptation quality', 'Knowledge integration'],",
            "    'potential_issues': ['No relevant cases', 'Poor adaptation', 'Overfitting to cases'],",
            "    'success_criteria': 'Retrieved 1-3 relevant cases, solution integrates K and O, addresses current problem'",
            "  },",
            "  'overall_plan': 'High-level execution strategy and timeline'",
            "}",
        ]

        raw = self.llm.request(planning_messages)
        plan = _parse_first_json(raw)

        # Fallback to empty plan if parsing fails
        if plan is None:
            plan = {
                "problem_modeling": {"expected_output": "", "key_considerations": [], "potential_issues": [], "success_criteria": ""},
                "problem_representation": {"expected_output": "", "key_considerations": [], "potential_issues": [], "success_criteria": ""},
                "strategy_selection": {"expected_output": "", "key_considerations": [], "potential_issues": [], "success_criteria": ""},
                "strategy_heuristic_llm": {"expected_output": "", "key_considerations": [], "potential_issues": [], "success_criteria": ""},
                "strategy_case_based": {"expected_output": "", "key_considerations": [], "potential_issues": [], "success_criteria": ""},
                "overall_plan": "No plan generated"
            }

        return plan

    def _metacognition_check(self, component_name: str, actual_output: dict, execution_context: dict = None) -> dict:
        """
        Metacognition monitoring: Compare actual execution with planned expectations.

        This function is called after each component execution to detect significant
        deviations from the plan. If deviation is detected, it suggests prompt/content
        adjustments to realign execution with expectations.

        Args:
            component_name (str): Name of the component being checked
                Options: 'problem_modeling', 'problem_representation', 'strategy_selection',
                        'strategy_heuristic_llm', 'strategy_case_based'
            actual_output (dict): Actual output from the component execution
            execution_context (dict): Additional context (e.g., intermediate states, errors)

        Returns:
            dict: Metacognition assessment with keys:
                - 'deviation_detected': bool - Whether significant deviation from plan was found
                - 'deviation_severity': str - 'none'|'minor'|'moderate'|'severe'
                - 'deviation_details': str - Specific deviations identified
                - 'root_cause_analysis': str - Potential reasons for deviation
                - 'adjustment_needed': bool - Whether prompt/content adjustment is recommended
                - 'adjustment_suggestions': list[str] - List of adjustment suggestions (each is a string)
                - 'continue_execution': bool - Whether to continue or restart component

        Notes:
            - This is NOT evaluating final solution quality (that's in _feedback)
            - This monitors whether execution PROCESS aligns with expectations
            - Focus on detecting: missing expected elements, unexpected behaviors,
              structural issues, constraint violations
        """
        # Get the expected plan for this component
        expected = self.execution_plan.get(component_name, {})
        if not expected:
            # No plan available, skip metacognition check
            return {
                "deviation_detected": False,
                "deviation_severity": "none",
                "deviation_details": "No plan available for comparison",
                "root_cause_analysis": "",
                "adjustment_needed": False,
                "adjustment_suggestions": [],
                "continue_execution": True
            }

        # Build metacognition prompt
        context_text = json.dumps(execution_context or {}, ensure_ascii=False)
        metacog_messages = [
            f"You are a metacognition monitor for component: {component_name}.",
            "Compare the EXPECTED execution plan with ACTUAL execution results.",
            "Detect deviations in the execution PROCESS (not final solution quality).",
            "Return a JSON object with: deviation_detected, deviation_severity, deviation_details, root_cause_analysis, adjustment_needed, adjustment_suggestions, continue_execution.",
            "",
            "IMPORTANT: 'adjustment_suggestions' must be a LIST of strings (not a dict or list of dicts).",
            "Each string should describe ONE specific adjustment suggestion for the component.",
            "Example: \"adjustment_suggestions\": [\"Include more specific constraints in the prompt\", \"Add validation for edge cases\"]",
            "",
            "=== Expected Plan ===",
            json.dumps(expected, ensure_ascii=False),
            "",
            "=== Actual Output ===",
            json.dumps(actual_output, ensure_ascii=False),
            "",
            "=== Execution Context ===",
            context_text,
            "",
            "Focus on:",
            "- Are expected output elements present?",
            "- Are there unexpected behaviors or errors?",
            "- Are key considerations addressed?",
            "- Do potential issues manifest?",
            "- Does output meet success criteria?",
            "",
            "Severity levels:",
            "- 'none': Execution matches expectations",
            "- 'minor': Small deviations, acceptable",
            "- 'moderate': Notable deviations, monitoring needed",
            "- 'severe': Major deviations, adjustment required",
        ]

        raw = self.llm.request(metacog_messages)
        assessment = _parse_first_json(raw)

        # Fallback to default assessment if parsing fails
        if assessment is None:
            assessment = {
                "deviation_detected": False,
                "deviation_severity": "none",
                "deviation_details": "Unable to assess deviation",
                "root_cause_analysis": "",
                "adjustment_needed": False,
                "adjustment_suggestions": [],
                "continue_execution": True
            }

        # Normalize fields
        assessment["deviation_detected"] = bool(assessment.get("deviation_detected", False))
        assessment["deviation_severity"] = assessment.get("deviation_severity", "none")
        assessment["adjustment_needed"] = bool(assessment.get("adjustment_needed", False))
        assessment["continue_execution"] = bool(assessment.get("continue_execution", True))

        # Store assessment in feedback for tracking
        self.feedback.setdefault("metacognition", {})[component_name] = assessment

        return assessment

    def _apply_metacognition_adjustment(self, component_name: str, adjustment_suggestions: list):
        """
        Apply metacognition adjustments to component prompts and parameters.

        This function modifies the execution context based on metacognition feedback
        to realign component execution with planned expectations.

        Args:
            component_name (str): Name of the component to adjust
            adjustment_suggestions (list[str]): List of adjustment suggestions from _metacognition_check.
                Each item is a string describing a suggested adjustment.

        Side Effects:
            - Updates self.metacognition_adjustments with component-specific modifications
            - These adjustments are picked up by components during execution

        Notes:
            - Adjustments are cumulative within a solve() session
            - Each call appends new suggestions to the existing list
            - Adjustments reset when solve() is called again
        """
        if not hasattr(self, 'metacognition_adjustments'):
            self.metacognition_adjustments = {}

        # Initialize component adjustment list if not exists
        if component_name not in self.metacognition_adjustments:
            self.metacognition_adjustments[component_name] = []

        # Append each adjustment suggestion string to the list
        for suggestion in adjustment_suggestions:
            if suggestion:  # Skip empty strings
                self.metacognition_adjustments[component_name].append({
                    "suggestion": suggestion,
                    "timestamp": datetime.now().isoformat()
                })

        # Log adjustment for visibility
        print(f"[Metacognition] Applied {len(adjustment_suggestions)} adjustment(s) to {component_name}")
        for i, suggestion in enumerate(adjustment_suggestions):
            if suggestion:
                print(f"  [{i+1}] {suggestion[:150]}...")

    def _get_adjusted_prompt(self, component_name: str, base_messages: list) -> list:
        """
        Augment base prompt messages with metacognition adjustments.

        This helper function should be called by components before sending messages to LLM.
        It injects metacognition adjustments into the prompt to guide execution.

        Args:
            component_name (str): Name of the component requesting adjusted prompt
            base_messages (list): Original prompt messages (list of strings)

        Returns:
            list: Augmented messages with metacognition adjustments injected

        Usage in components:
            messages = self._get_adjusted_prompt('problem_modeling', base_messages)
            result = self.llm.request(messages)
        """
        # Return base messages if no adjustments available
        if not hasattr(self, 'metacognition_adjustments') or self.metacognition_adjustments == {}:
            return base_messages

        adjustment_list = self.metacognition_adjustments.get(component_name, [])
        if not adjustment_list:
            return base_messages

        # Start with base messages
        adjusted_messages = list(base_messages)

        # Collect all adjustment suggestions
        all_suggestions = [adj.get("suggestion", "") for adj in adjustment_list if adj.get("suggestion")]

        # Inject all adjustments at position 1
        if all_suggestions:
            adjustment_block = "[Metacognition Adjustments]\n" + "\n".join(
                f"- {suggestion}" for suggestion in all_suggestions
            )
            adjusted_messages.insert(1, adjustment_block)

        return adjusted_messages
