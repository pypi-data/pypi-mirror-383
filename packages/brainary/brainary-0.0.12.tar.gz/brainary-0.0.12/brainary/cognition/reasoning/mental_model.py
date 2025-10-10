# -*- coding: utf-8 -*-
"""
Mental Model Reasoning (enhanced)
- Adds schema alignment between Step4 and scoring
- Adds 4->2 refinement loop when hypothesis is fundamentally flawed
- Enforces iteration counting & early stop
- Adds debug flags to print intermediate responses (JSON / summaries)
- Improves JSON cleaning robustness
"""

import json
import time
import os
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from brainary.cognition.reasoning.reasoning_base import Reasoning
from openai import AzureOpenAI

from brainary.core.ops.action_op import ActionSession

# from reasoning.reasoning_base import Reasoning

# =========================
# Configuration knobs
# =========================

# Early stop when a strong ACCEPT is found (can adjust via env)
EARLY_STOP_SCORE = float(os.getenv("MMR_EARLY_STOP_SCORE", "0.85"))

# How many times we allow 4->2 hypothesis regeneration
MAX_REFINEMENT_ROUNDS = int(os.getenv("MMR_MAX_REFINEMENTS", "2"))

# Hard cap to avoid runaway growth of hypotheses
MAX_HYPOTHESES = int(os.getenv("MMR_MAX_HYPOTHESES", "12"))

# Map confidence string to numeric value
DEFAULT_CONFIDENCE_MAP = {"High": 0.9, "Medium": 0.6, "Low": 0.3}

# --- Debug flags (toggle via env) ---
# If set to 1, print the full cleaned JSON from LLM for each step
DEBUG_JSON = bool(int(os.getenv("MMR_DEBUG_JSON", "1")))
# If set to 1, print concise parsed summaries for each step
DEBUG_SUMMARY = bool(int(os.getenv("MMR_DEBUG_SUMMARY", "1")))


@dataclass
class HypothesisState:
    """Track individual hypothesis state"""
    id: int
    description: str
    rationale: str
    approach: str
    score: float = 0.0  # Final score for this hypothesis
    is_modified: bool = False  # Whether this hypothesis has been modified once
    reasoning_result: Optional[Dict] = None
    reasoning_confidence: str = "Medium"
    modification_guidance: str = ""
    reasoning_history: List[Dict] = field(default_factory=list)
    best_confidence: float = 0.0
    complete_answer: str = ""  # Complete answer to the original problem based on this hypothesis


@dataclass
class MentalModelState:
    """Track mental model reasoning state"""
    current_hypothesis_index: int = 0
    iteration_count: int = 0
    max_iterations: int = int(os.getenv("MMR_MAX_ITERATIONS", "50"))
    best_hypothesis: Optional[HypothesisState] = None
    best_confidence: float = 0.0
    problem_representation: str = ""
    all_hypotheses: List[HypothesisState] = field(default_factory=list)
    reasoning_history: List[Dict] = field(default_factory=list)
    hypotheses_generated: bool = False
    refinement_rounds: int = 0                              # NEW: count 4->2 regenerations
    tried_hypothesis_descriptions: Set[str] = field(default_factory=set)  # NEW: avoid duplicates


class MentalModelReasoning(Reasoning):
    """
    Psychology-based mental model reasoning framework
    Implements hypothesis-by-hypothesis testing with modification and abandonment logic
    """

    NAME = "Mental Model Reasoning"
    DESC = "Psychology-based mental model reasoning with iterative hypothesis testing and conflict monitoring"

    def __init__(self, llm):
        super().__init__(llm)

    # =========================
    # Debug helpers
    # =========================
    def _debug_print(self, title: str, payload):
        """Pretty-print helper controlled by DEBUG_* flags."""
        if DEBUG_JSON:
            try:
                print(f"{title} (JSON):\n" + json.dumps(payload, indent=2, ensure_ascii=False))
            except Exception:
                print(f"{title} (RAW): {payload}")

    # =========================
    # JSON cleaning
    # =========================
    def _clean_json_response(self, response: str) -> str:
        """
        Clean response to extract JSON from markdown code blocks and handle formatting issues.
        IMPROVED:
        - Accept both object `{}` and array `[]` top levels
        - Strip leading explanatory text
        - Best-effort substring extraction between first opening and matching closing brace/bracket
        """
        if not response:
            return response

        cleaned = response.strip()

        # Remove Markdown fences
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        # Fast path: already a valid JSON
        try:
            json.loads(cleaned)
            return cleaned
        except Exception:
            pass

        # Try object {...} or array [...]
        def _extract_balanced(s: str, open_ch: str, close_ch: str) -> Optional[str]:
            start = s.find(open_ch)
            if start == -1:
                return None
            depth = 0
            for i in range(start, len(s)):
                c = s[i]
                if c == open_ch:
                    depth += 1
                elif c == close_ch:
                    depth -= 1
                    if depth == 0:
                        return s[start:i + 1]
            return None

        obj = _extract_balanced(cleaned, "{", "}")
        if obj:
            try:
                json.loads(obj)
                return obj.strip()
            except Exception:
                pass

        arr = _extract_balanced(cleaned, "[", "]")
        if arr:
            try:
                json.loads(arr)
                return arr.strip()
            except Exception:
                pass

        # As a last resort return original cleaned string (caller will handle JSONDecodeError)
        return cleaned

    # =========================
    # Main entry
    # =========================
    def reason(self, session: ActionSession) -> str:
        """
        Main reasoning method implementing complete mental model workflow
        - ADD: Early stop when a strong ACCEPT is found
        - ADD: Enforce max_iterations across Step3/Step4 (and modification retries)
        - ADD: 4->2 feedback loop when a hypothesis is fundamentally flawed
        """
        state = MentalModelState()
        
        task = session.messages[0][1]

        print(f"[MMR] Start: {task}")

        # Step 1: Problem modeling (only once)
        if not self._step1_modeling(task, state):
            return self._format_final_result(state, "MODELING_FAILED")

        # Step 2: Generate initial hypotheses (only once)
        if not self._step2_hypothesis_generation(state):
            return self._format_final_result(state, "HYPOTHESIS_GENERATION_FAILED")

        # Main loop: test each hypothesis, give them scores, find the best one
        while state.current_hypothesis_index < len(state.all_hypotheses):
            if state.iteration_count >= state.max_iterations:
                print("[MMR] Reached max_iterations. Stopping.")
                break

            current_hypothesis = state.all_hypotheses[state.current_hypothesis_index]
            state.tried_hypothesis_descriptions.add(current_hypothesis.description.strip())

            print(f"\n=== Testing Hypothesis {current_hypothesis.id} ===")

            try:
                # Step 3: Reasoning for current hypothesis
                if not self._step3_reasoning(current_hypothesis, state):
                    state.iteration_count += 1  # count Step 3 attempt
                    current_hypothesis.score = 0.1  # Very low score for failed reasoning
                    state.current_hypothesis_index += 1
                    continue
                state.iteration_count += 1  # count Step 3

                # Step 4: Conflict monitoring for current hypothesis
                action, score, conflict_payload = self._step4_conflict_monitoring(current_hypothesis, state)
                current_hypothesis.score = score
                state.iteration_count += 1  # count Step 4

                # Early stop if strong ACCEPT
                if action == "ACCEPT" and score >= EARLY_STOP_SCORE:
                    print(f"[MMR] Early stop: hypothesis {current_hypothesis.id} ACCEPT with score {score:.2f}")
                    state.current_hypothesis_index += 1
                    break  # Strong enough to stop evaluating the rest

                if action == "MODIFY_REASONING" and not current_hypothesis.is_modified:
                    # Allow one reasoning modification attempt
                    current_hypothesis.is_modified = True
                    print(f"[MMR] Retrying reasoning for hypothesis {current_hypothesis.id} with modification guidance")
                    # Re-run step 3 on the same hypothesis with modification context
                    if not self._step3_reasoning(current_hypothesis, state):
                        state.iteration_count += 1
                        current_hypothesis.score = 0.1
                        state.current_hypothesis_index += 1
                        continue
                    state.iteration_count += 1
                    # Then re-run step 4
                    action, score, conflict_payload = self._step4_conflict_monitoring(current_hypothesis, state)
                    current_hypothesis.score = score
                    state.iteration_count += 1

                    if action == "ACCEPT" and score >= EARLY_STOP_SCORE:
                        print(f"[MMR] Early stop after modification: H{current_hypothesis.id} score {score:.2f}")
                        state.current_hypothesis_index += 1
                        break

                # NEW: If hypothesis is fundamentally flawed and not fixable -> 4->2 feedback (refine hypotheses)
                diag = conflict_payload.get("error_diagnosis", {})
                if (
                    action in ("ABANDON", "MODIFY_REASONING") and
                    diag.get("error_source") == "HYPOTHESIS_FUNDAMENTAL" and
                    str(diag.get("fixable", "No")).lower() in ("no", "false")
                ):
                    if state.refinement_rounds < MAX_REFINEMENT_ROUNDS and len(state.all_hypotheses) < MAX_HYPOTHESES:
                        refinement_reason = diag.get("explanation", "Fundamental issues found")
                        print(f"[MMR] Trigger refine: reason='{refinement_reason}'")
                        self._step2b_refine_hypotheses(state, current_hypothesis, refinement_reason)
                    else:
                        print("[MMR] Skip refine: max refinement rounds or hypotheses reached")

                # Move on to next hypothesis
                print(f"Hypothesis {current_hypothesis.id} scored {score:.2f}, moving to next")
                state.current_hypothesis_index += 1

            except Exception as e:
                print(f"[MMR] Error processing hypothesis {current_hypothesis.id}: {e}")
                current_hypothesis.score = 0.0
                state.current_hypothesis_index += 1

            if state.iteration_count >= state.max_iterations:
                print("[MMR] Reached max_iterations after loop body. Stopping.")
                break

        # All hypotheses tested, return the one with highest score
        result = self._format_final_result(state, "ALL_HYPOTHESES_SCORED")
        return json.dumps(result, indent=2)

    # =========================
    # Step 1: Modeling
    # =========================
    def _step1_modeling(self, task: str, state: MentalModelState) -> bool:
        """Step 1: Build problem representation and mental model"""
        print("Executing Step 1: Problem Modeling")

        prompt = f"""
You are a reasoning system executing STEP 1: PROBLEM MODELING.

Your task is to build a comprehensive mental model and representation of the given problem.

INSTRUCTIONS:
1. Read and analyze the problem carefully
2. Identify the core question or challenge
3. Break down the problem into key components
4. Identify relationships between components
5. Note any assumptions that need to be made
6. Determine what type of reasoning approach would be most effective
7. Assess your confidence in this understanding

PROBLEM TO MODEL:
{task}

RESPONSE FORMAT (JSON):
{{
    "problem_understanding": "Clear reformulation of the core problem",
    "key_components": [
        {{
            "component": "component name",
            "description": "what this component represents",
            "importance": "why this is important to the problem"
        }}
    ],
    "relationships": [
        {{
            "relationship": "description of how components relate",
            "type": "causal/correlational/functional/etc"
        }}
    ],
    "assumptions": [
        {{
            "assumption": "assumption being made",
            "justification": "why this assumption is reasonable",
            "risk": "what happens if this assumption is wrong"
        }}
    ],
    "reasoning_approach": {{
        "primary_method": "deductive/inductive/abductive/analogical/etc",
        "why_suitable": "explanation of why this approach fits",
        "potential_challenges": "what might be difficult with this approach"
    }},
    "confidence": "High/Medium/Low",
    "confidence_reasoning": "detailed explanation of confidence level",
    "next_step_guidance": "what to focus on in hypothesis generation"
}}
"""

        try:
            response = self.llm.request([prompt]).strip()
            if not response:
                print("Step 1 failed: No response from LLM")
                return False

            cleaned_response = self._clean_json_response(response)
            try:
                parsed_response = json.loads(cleaned_response)
            except json.JSONDecodeError as json_error:
                print(f"JSON decode error: {json_error}")
                return False

            state.problem_representation = parsed_response.get("problem_understanding", task)

            if DEBUG_SUMMARY:
                # print(f"[S1] understanding: {state.problem_representation[:180]}...")
                print(f"[S1] understanding: {state.problem_representation}")
                print(f"[S1] confidence: {parsed_response.get('confidence','')}")
            self._debug_print("[S1] cleaned response", parsed_response)

            step_record = {
                "step": 1,
                "name": "modeling",
                "response": parsed_response,
                "confidence": parsed_response.get("confidence", "Medium"),
                "timestamp": time.time()
            }
            state.reasoning_history.append(step_record)

            print(f"Problem modeling completed, confidence: {parsed_response.get('confidence', 'Medium')}")
            return True

        except Exception as e:
            print(f"Step 1 failed: {e}")
            return False

    # =========================
    # Step 2: Hypothesis generation
    # =========================
    def _step2_hypothesis_generation(self, state: MentalModelState) -> bool:
        """Step 2: Generate multiple hypotheses (only once)"""
        print("Executing Step 2: Hypothesis Generation")

        latest_modeling = state.reasoning_history[-1] if state.reasoning_history else {}
        problem_understanding = latest_modeling.get("response", {}).get("problem_understanding", state.problem_representation)
        next_step_guidance = latest_modeling.get("response", {}).get("next_step_guidance", "")

        prompt = f"""
You are a reasoning system executing STEP 2: HYPOTHESIS GENERATION.

Your task is to generate multiple distinct hypotheses that could explain or solve the problem.

INSTRUCTIONS:
1. Based on the problem understanding, generate 3-5 different hypotheses
2. Each hypothesis should be a potential solution or explanation
3. Ensure hypotheses are distinct and non-overlapping
4. Consider different angles and approaches
5. Make hypotheses testable through reasoning
6. Assign preliminary confidence to each hypothesis

PROBLEM UNDERSTANDING:
{problem_understanding}

GUIDANCE FROM MODELING STEP:
{next_step_guidance}

RESPONSE FORMAT (JSON):
{{
    "hypotheses": [
        {{
            "id": 1,
            "description": "clear description of the hypothesis",
            "rationale": "why this hypothesis makes sense given the problem",
            "approach": "what reasoning method would test this hypothesis",
            "testability": "how this hypothesis can be evaluated",
            "preliminary_confidence": "High/Medium/Low",
            "potential_evidence": ["what evidence would support this", "what evidence would refute this"]
        }}
    ],
    "generation_strategy": "explanation of how you chose these hypotheses",
    "coverage_assessment": "how well these hypotheses cover the problem space",
    "confidence": "High/Medium/Low",
    "confidence_reasoning": "why you have this confidence in the hypothesis set"
}}
"""

        try:
            response = self.llm.request([prompt]).strip()
            if not response:
                print("Step 2 failed: No response from LLM")
                return False

            cleaned_response = self._clean_json_response(response)
            parsed_response = json.loads(cleaned_response)

            # Convert to HypothesisState objects (avoid duplicates)
            n_before = len(state.all_hypotheses)
            for hyp_data in parsed_response.get("hypotheses", []):
                desc = hyp_data.get("description", "").strip()
                if not desc or desc in state.tried_hypothesis_descriptions:
                    continue
                if len(state.all_hypotheses) >= MAX_HYPOTHESES:
                    break
                hypothesis = HypothesisState(
                    id=hyp_data.get("id", len(state.all_hypotheses) + 1),
                    description=desc,
                    rationale=hyp_data.get("rationale", ""),
                    approach=hyp_data.get("approach", "")
                )
                state.all_hypotheses.append(hypothesis)

            if DEBUG_SUMMARY:
                hs = [h.description for h in state.all_hypotheses[n_before:]]
                print(f"[S2] hypotheses(+{len(hs)}): " + "; ".join(hs))
            self._debug_print("[S2] cleaned response", parsed_response)

            step_record = {
                "step": 2,
                "name": "hypothesis_generation",
                "response": parsed_response,
                "confidence": parsed_response.get("confidence", "Medium"),
                "timestamp": time.time()
            }
            state.reasoning_history.append(step_record)

            print(f"Generated {len(state.all_hypotheses) - n_before} new hypotheses (total={len(state.all_hypotheses)})")
            return len(state.all_hypotheses) > 0

        except Exception as e:
            print(f"Step 2 failed: {e}")
            return False

    # =========================
    # Step 2b: Refinement (NEW)
    # =========================
    def _step2b_refine_hypotheses(self, state: MentalModelState, failed_hypothesis: HypothesisState, reason: str) -> None:
        """
        NEW Step 2b: Regenerate/refine hypotheses when conflict monitoring indicates fundamental issues.
        - Feeds failure reasons as negative evidence
        - Adds only novel hypotheses (no duplicates)
        - Increments refinement_rounds
        """
        if state.refinement_rounds >= MAX_REFINEMENT_ROUNDS:
            return

        state.refinement_rounds += 1
        print(f"Executing Step 2b: Hypothesis Refinement (round {state.refinement_rounds})")

        prompt = f"""
You are executing STEP 2b: HYPOTHESIS REFINEMENT.

CONTEXT:
- Problem: {state.problem_representation}
- Failed hypothesis (fundamental issue): "{failed_hypothesis.description}"
- Failure explanation: {reason}

TASK:
Generate 2-4 NEW alternative hypotheses that explicitly avoid the identified failure modes.
Make them distinct, testable, and complementary to the existing set.

RESPONSE FORMAT (JSON):
{{
  "hypotheses": [
    {{
      "description": "new hypothesis avoiding the identified failure",
      "rationale": "why this is plausible and different from failed one",
      "approach": "how to test it"
    }}
  ],
  "note": "short explanation of how these avoid prior pitfalls"
}}
"""
        try:
            response = self.llm.request([prompt]).strip()
            if not response:
                print("Step 2b failed: No response")
                return
            cleaned = self._clean_json_response(response)
            parsed = json.loads(cleaned)

            added = 0
            for hyp in parsed.get("hypotheses", []):
                desc = hyp.get("description", "").strip()
                if not desc or desc in state.tried_hypothesis_descriptions:
                    continue
                if len(state.all_hypotheses) >= MAX_HYPOTHESES:
                    break
                new_h = HypothesisState(
                    id=len(state.all_hypotheses) + 1,
                    description=desc,
                    rationale=hyp.get("rationale", ""),
                    approach=hyp.get("approach", "")
                )
                state.all_hypotheses.append(new_h)
                added += 1

            if DEBUG_SUMMARY:
                print(f"[S2b] added={added}")
            self._debug_print("[S2b] cleaned response", parsed)

        except Exception as e:
            print(f"Step 2b failed: {e}")

    # =========================
    # Step 3: Reasoning
    # =========================
    def _step3_reasoning(self, hypothesis: HypothesisState, state: MentalModelState) -> bool:
        """Step 3: Detailed reasoning for specific hypothesis"""
        print(f"Executing Step 3: Reasoning for Hypothesis {hypothesis.id}")

        modification_context = ""
        if hypothesis.modification_guidance:
            modification_context = f"\n\nMODIFICATION GUIDANCE:\n{hypothesis.modification_guidance}"

        prompt = f"""
You are a reasoning system executing STEP 3: HYPOTHESIS REASONING.

Your task is to perform comprehensive step-by-step reasoning for the given hypothesis.

INSTRUCTIONS:
1. Take the hypothesis and reason through it systematically
2. Use appropriate reasoning methods (deductive, inductive, abductive, etc.)
3. Build a logical chain from premises to conclusions
4. Identify supporting evidence and potential counterevidence
5. Note any logical dependencies or assumptions
6. Assess the strength of each reasoning step
7. Provide an overall evaluation of the hypothesis validity

PROBLEM CONTEXT:
{state.problem_representation}

HYPOTHESIS TO ANALYZE:
ID: {hypothesis.id}
Description: {hypothesis.description}
Approach: {hypothesis.approach}
Rationale: {hypothesis.rationale}
{modification_context}

RESPONSE FORMAT (JSON):
{{
    "hypothesis_id": {hypothesis.id},
    "reasoning_chain": [
        {{
            "step": 1,
            "premise": "what we start with",
            "inference": "logical step taken",
            "conclusion": "what this step concludes",
            "reasoning_type": "deductive/inductive/abductive/etc",
            "confidence": "High/Medium/Low",
            "supporting_evidence": ["evidence for this step"],
            "potential_issues": ["possible problems with this step"]
        }}
    ],
    "overall_logic": {{
        "logical_structure": "how the reasoning steps connect",
        "strength_assessment": "evaluation of logical soundness",
        "key_dependencies": ["what this reasoning depends on"],
        "potential_weaknesses": ["where the reasoning might fail"]
    }},
    "evidence_evaluation": {{
        "supporting_evidence": ["evidence that supports the hypothesis"],
        "contradicting_evidence": ["evidence that challenges the hypothesis"],
        "missing_evidence": ["what evidence would strengthen the case"],
        "evidence_quality": "Strong/Medium/Weak"
    }},
    "conclusion": {{
        "hypothesis_validity": "Valid/Questionable/Invalid",
        "confidence": "High/Medium/Low",
        "confidence_reasoning": "detailed justification for confidence",
        "conditions": "under what conditions this hypothesis holds",
        "limitations": "known limitations of this reasoning"
    }},
    "next_step_recommendations": "what should be examined in conflict monitoring"
}}
"""

        try:
            response = self.llm.request([prompt]).strip()
            cleaned_response = self._clean_json_response(response)
            parsed_response = json.loads(cleaned_response)

            hypothesis.reasoning_result = parsed_response
            hypothesis.reasoning_confidence = parsed_response.get("conclusion", {}).get("confidence", "Medium")

            # Debug prints (concise + optional JSON)
            if DEBUG_SUMMARY:
                chain = parsed_response.get("reasoning_chain", [])
                evq = parsed_response.get("evidence_evaluation", {}).get("evidence_quality", "Unknown")
                valid = parsed_response.get("conclusion", {}).get("hypothesis_validity", "Unknown")
                print(f"[S3] chain_len={len(chain)}, evidence={evq}, validity={valid}")
                for step in chain[:2]:
                    s = step.get("step")
                    prem = step.get("premise", "")[:80]
                    concl = step.get("conclusion", "")[:80]
                    print(f"[S3] step{s}: {prem} -> {concl}")
            self._debug_print("[S3] cleaned response", parsed_response)

            # Generate complete answer based on this hypothesis
            if not self._generate_complete_answer(hypothesis, state):
                print(f"   Warning: Failed to generate complete answer for hypothesis {hypothesis.id}")

            confidence_score = self._convert_confidence_to_float(hypothesis.reasoning_confidence)
            hypothesis.best_confidence = max(hypothesis.best_confidence, confidence_score)

            # Update global best if this is better
            if confidence_score > state.best_confidence:
                state.best_confidence = confidence_score
                state.best_hypothesis = hypothesis

            step_record = {
                "step": 3,
                "name": "reasoning",
                "hypothesis_id": hypothesis.id,
                "response": parsed_response,
                "confidence": hypothesis.reasoning_confidence,
                "timestamp": time.time()
            }
            hypothesis.reasoning_history.append(step_record)

            print(f"Reasoning completed for hypothesis {hypothesis.id}, confidence: {hypothesis.reasoning_confidence}")
            return True

        except Exception as e:
            print(f"Step 3 failed for hypothesis {hypothesis.id}: {e}")
            return False

    # =========================
    # Generate complete answer
    # =========================
    def _generate_complete_answer(self, hypothesis: HypothesisState, state: MentalModelState) -> bool:
        """Generate a complete answer to the original problem based on this hypothesis"""
        print(f"   Generating complete answer for hypothesis {hypothesis.id}")

        reasoning_summary = ""
        if hypothesis.reasoning_result:
            reasoning_chain = hypothesis.reasoning_result.get("reasoning_chain", [])
            conclusion = hypothesis.reasoning_result.get("conclusion", {})
            reasoning_summary = f"""
REASONING SUMMARY:
- Reasoning steps: {len(reasoning_chain)}
- Conclusion validity: {conclusion.get('hypothesis_validity', 'Unknown')}
- Confidence: {conclusion.get('confidence', 'Medium')}
- Key dependencies: {hypothesis.reasoning_result.get('overall_logic', {}).get('key_dependencies', [])}
"""

        prompt = f"""
You are completing a reasoning task. Based on the hypothesis and reasoning analysis, provide a concise, complete answer to the original problem.

ORIGINAL PROBLEM:
{state.problem_representation}

HYPOTHESIS BEING TESTED:
{hypothesis.description}

REASONING ANALYSIS:
{reasoning_summary}

CONSTRAINTS:
- Under 1000 characters
- Include practical recommendations and acknowledge limitations

RESPONSE: (plain text)
"""

        try:
            response = self.llm.request([prompt]).strip()
            if response:
                hypothesis.complete_answer = response.strip()
                return True
            else:
                print(f"   Failed to generate complete answer: No response")
                return False

        except Exception as e:
            print(f"   Failed to generate complete answer: {e}")
            return False

    # =========================
    # Step 4: Conflict monitoring
    # =========================
    def _step4_conflict_monitoring(self, hypothesis: HypothesisState, state: MentalModelState) -> tuple[str, float, Dict]:
        """
        Step 4: Conflict monitoring and validation for specific hypothesis
        CHANGED: Response schema extended to match what the scoring function consumes.
        """
        print(f"Executing Step 4: Conflict Monitoring for Hypothesis {hypothesis.id}")

        # Build a readable reasoning chain string (for the prompt)
        reasoning_chain_str = ""
        if hypothesis.reasoning_result:
            chain_data = hypothesis.reasoning_result.get("reasoning_chain", [])
            if chain_data:
                reasoning_chain_str = "\n".join([
                    f"Step {step.get('step', i+1)}: {step.get('premise', '')} → {step.get('inference', '')} → {step.get('conclusion', '')}"
                    for i, step in enumerate(chain_data)
                ])

        prompt = f"""
You are a reasoning system executing STEP 4: CONFLICT MONITORING.

FOCUS ONLY ON REASONING LOGIC:
- Examine each reasoning step: does Step N logically lead to Step N+1?
- Identify logical gaps, invalid inferences, or unjustified conclusions
- Diagnose whether errors stem from poor reasoning OR from the hypothesis being fundamentally flawed

PROBLEM CONTEXT:
{state.problem_representation}

CURRENT HYPOTHESIS:
{hypothesis.description}

DETAILED REASONING CHAIN:
{reasoning_chain_str}

RESPONSE FORMAT (JSON):
{{
  "reasoning_analysis": {{
    "logical_errors": ["specific logical mistakes in reasoning steps"],
    "invalid_transitions": ["where step N does not lead to step N+1"],
    "unjustified_conclusions": ["conclusions not supported by premises"],
    "reasoning_quality": "Valid/Flawed/Broken"
  }},
  "error_diagnosis": {{
    "error_source": "REASONING_METHOD/HYPOTHESIS_FUNDAMENTAL",
    "explanation": "why the errors occurred",
    "fixable": "Yes/No"
  }},
  "objective_assessment": {{
    "hypothesis_reasonableness": "Reasonable/Questionable/Unreasonable",
    "logical_coherence": "Coherent/Partially_Coherent/Incoherent",
    "step_validity_score": "0.0-1.0"
  }},
  "step_by_step_analysis": {{
    "logical_transitions": ["S1->S2", "S2->S3"],
    "unjustified_leaps": ["S3->S4"]
  }},
  "decision": {{
    "recommended_action": "ACCEPT/ABANDON/MODIFY_REASONING",
    "action_justification": "why this action",
    "confidence_in_assessment": "High/Medium/Low",
    "modification_guidance": "if MODIFY_REASONING, give specific guidance or leave empty"
  }}
}}
"""

        try:
            response = self.llm.request([prompt]).strip()
            cleaned_response = self._clean_json_response(response)
            parsed_response = json.loads(cleaned_response)

            if DEBUG_SUMMARY:
                ra = parsed_response.get("reasoning_analysis", {})
                diag = parsed_response.get("error_diagnosis", {})
                dec = parsed_response.get("decision", {})
                print(f"[S4] quality={ra.get('reasoning_quality','')}, "
                      f"errors={len(ra.get('logical_errors',[]))}, "
                      f"invalid_transitions={len(ra.get('invalid_transitions',[]))}, "
                      f"unjustified={len(ra.get('unjustified_conclusions',[]))}")
                print(f"[S4] diagnosis: source={diag.get('error_source','')}, fixable={diag.get('fixable','')}")
                print(f"[S4] decision: action={dec.get('recommended_action','')}, "
                      f"conf={dec.get('confidence_in_assessment','')}")
            self._debug_print("[S4] cleaned response", parsed_response)

            decision = parsed_response.get("decision", {}) or {}
            recommended_action = decision.get("recommended_action", "ABANDON")
            modification_guidance = decision.get("modification_guidance", "")
            if modification_guidance:
                hypothesis.modification_guidance = modification_guidance

            # Calculate score using the aligned schema
            score = self._calculate_hypothesis_score(hypothesis, parsed_response, recommended_action)

            # Record step
            step_record = {
                "step": 4,
                "name": "conflict_monitoring",
                "hypothesis_id": hypothesis.id,
                "response": parsed_response,
                "confidence": decision.get("confidence_in_assessment", "Medium"),
                "timestamp": time.time(),
                "action": recommended_action,
                "score": score
            }
            hypothesis.reasoning_history.append(step_record)

            print(f"[CM] action={recommended_action}, score={score:.2f}")
            return recommended_action, score, parsed_response

        except Exception as e:
            print(f"Step 4 failed for hypothesis {hypothesis.id}: {e}")
            return "ABANDON", 0.0, {}

    # =========================
    # Scoring
    # =========================
    def _calculate_hypothesis_score(self, hypothesis: HypothesisState, conflict_response: Dict, recommended_action: str) -> float:
        """Calculate comprehensive score based on multiple factors (schema-aligned)"""
        print(f"   Calculating detailed score for hypothesis {hypothesis.id}...")

        # Base score from reasoning confidence (0.0-1.0)
        reasoning_confidence = self._convert_confidence_to_float(hypothesis.reasoning_confidence)

        # Evidence quality score (0.0-1.0)
        evidence_quality = hypothesis.reasoning_result.get("evidence_evaluation", {}).get("evidence_quality", "Medium") if hypothesis.reasoning_result else "Medium"
        evidence_score = {"Strong": 1.0, "Medium": 0.6, "Weak": 0.2}.get(evidence_quality, 0.6)

        # Hypothesis validity score (0.0-1.0)
        validity = hypothesis.reasoning_result.get("conclusion", {}).get("hypothesis_validity", "Questionable") if hypothesis.reasoning_result else "Questionable"
        validity_score = {"Valid": 1.0, "Questionable": 0.5, "Invalid": 0.1}.get(validity, 0.5)

        # From conflict monitoring (schema-aligned)
        objective_assessment = conflict_response.get("objective_assessment", {}) or {}
        step_analysis = conflict_response.get("step_by_step_analysis", {}) or {}

        hypothesis_reasonableness = objective_assessment.get("hypothesis_reasonableness", "Questionable")
        reasonableness_score = {"Reasonable": 1.0, "Questionable": 0.5, "Unreasonable": 0.1}.get(hypothesis_reasonableness, 0.5)

        logical_coherence = objective_assessment.get("logical_coherence", "Partially_Coherent")
        coherence_score = {"Coherent": 1.0, "Partially_Coherent": 0.6, "Incoherent": 0.1}.get(logical_coherence, 0.6)

        # Step validity numeric score
        step_validity_str = objective_assessment.get("step_validity_score", "0.6")
        try:
            step_validity_score = float(step_validity_str)
        except Exception:
            step_validity_score = 0.6

        unjustified_leaps = step_analysis.get("unjustified_leaps", []) or []
        transition_penalty = min(0.3, len(unjustified_leaps) * 0.1)  # Up to 0.3 penalty

        chain_length = len(hypothesis.reasoning_result.get("reasoning_chain", [])) if hypothesis.reasoning_result else 0
        chain_bonus = min(0.1, chain_length * 0.02)  # Max +0.1

        assessment_confidence = conflict_response.get("decision", {}).get("confidence_in_assessment", "Medium")
        assessment_score = self._convert_confidence_to_float(assessment_confidence)

        action_multiplier = {
            "ACCEPT": 1.0,
            "MODIFY_REASONING": 0.85,
            "ABANDON": 0.4
        }.get(recommended_action, 0.6)

        # Weights (easier to tune)
        weights = {
            "reasoning_confidence": 0.15,
            "evidence_quality": 0.15,
            "hypothesis_validity": 0.20,
            "hypothesis_reasonableness": 0.25,
            "logical_coherence": 0.20,
            "assessment_confidence": 0.05
        }

        weighted_score = (
            weights["reasoning_confidence"] * reasoning_confidence +
            weights["evidence_quality"] * evidence_score +
            weights["hypothesis_validity"] * validity_score +
            weights["hypothesis_reasonableness"] * reasonableness_score +
            weights["logical_coherence"] * coherence_score +
            weights["assessment_confidence"] * assessment_score
        )

        step_validity_bonus = (step_validity_score - 0.5) * 0.2  # -0.1 ~ +0.1
        final_weighted_score = weighted_score + step_validity_bonus - transition_penalty
        final_score = (final_weighted_score + chain_bonus) * action_multiplier
        final_score = max(0.0, min(1.0, final_score))

        print(f"   Score breakdown:")
        print(f"     Reasoning confidence: {reasoning_confidence:.2f} (w={weights['reasoning_confidence']})")
        print(f"     Evidence quality:     {evidence_score:.2f} (w={weights['evidence_quality']})")
        print(f"     Hypothesis validity:  {validity_score:.2f} (w={weights['hypothesis_validity']})")
        print(f"     Reasonableness:       {reasonableness_score:.2f} (w={weights['hypothesis_reasonableness']})")
        print(f"     Coherence:            {coherence_score:.2f} (w={weights['logical_coherence']})")
        print(f"     Step validity bonus: {step_validity_bonus:+.2f}")
        print(f"     Transition penalty:  -{transition_penalty:.2f} (leaps={len(unjustified_leaps)})")
        print(f"     Chain bonus:         +{chain_bonus:.2f}")
        print(f"     Action multiplier:    {action_multiplier:.2f}")
        print(f"     Final score:          {final_score:.3f}")

        return final_score

    def _convert_confidence_to_float(self, confidence_str: str) -> float:
        """Convert confidence string to numerical value"""
        return DEFAULT_CONFIDENCE_MAP.get(confidence_str, 0.5)

    # =========================
    # Final formatting
    # =========================
    def _format_final_result(self, state: MentalModelState, termination_reason: str) -> Dict:
        """Format final reasoning result"""

        # Find highest scoring hypothesis
        final_hypothesis = None
        highest_score = -1.0
        for hyp in state.all_hypotheses:
            if hyp.score > highest_score:
                highest_score = hyp.score
                final_hypothesis = hyp

        # If no scores, use best confidence
        if not final_hypothesis and state.best_hypothesis:
            final_hypothesis = state.best_hypothesis
            highest_score = max(highest_score, final_hypothesis.score)

        result = {
            "termination_reason": termination_reason,
            "iterations_completed": state.iteration_count,
            "final_answer": None,
            "best_score": max(0.0, highest_score),
            "problem_representation": state.problem_representation,
            "all_hypotheses_summary": [],
            "reasoning_history": state.reasoning_history,
            "summary": ""
        }

        for hyp in state.all_hypotheses:
            hyp_summary = {
                "id": hyp.id,
                "description": hyp.description,
                "score": hyp.score,
                "confidence": hyp.reasoning_confidence,
                "is_modified": hyp.is_modified,
                "reasoning_attempts": len(hyp.reasoning_history)
            }
            result["all_hypotheses_summary"].append(hyp_summary)

        if final_hypothesis:
            result["final_answer"] = {
                "hypothesis_id": final_hypothesis.id,
                "description": final_hypothesis.description,
                "complete_answer": final_hypothesis.complete_answer,
                "score": final_hypothesis.score,
                "reasoning_confidence": final_hypothesis.reasoning_confidence,
                "reasoning_chain": final_hypothesis.reasoning_result.get("reasoning_chain", []) if final_hypothesis.reasoning_result else [],
                "conclusion": final_hypothesis.reasoning_result.get("conclusion", {}) if final_hypothesis.reasoning_result else {}
            }

        result["summary"] = (
            f"Completed {state.iteration_count} iterations. "
            f"Best score: {max(0.0, highest_score):.2f}. "
            f"Refinements: {state.refinement_rounds}. "
            f"Reason for termination: {termination_reason}"
        )

        print(f"\n=== Mental Model Reasoning Complete ===")
        print(f"Termination reason: {termination_reason}")
        print(f"Iterations completed: {state.iteration_count}")
        print(f"Best score: {max(0.0, highest_score):.2f}")
        if final_hypothesis:
            print(f"Final answer: {final_hypothesis.description}")

        return result


# =========================
# Mock LLM class for testing
# =========================
class MockLLM:
    def __init__(self):
        self.endpoint = os.getenv("ENDPOINT_URL", "https://gpt4-func-sweden.openai.azure.com/")
        self.deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4o")
        self.subscription_key = os.getenv("AZURE_OPENAI_API_KEY", "-")

        # Initialize Azure OpenAI client exactly like your example
        self.client = AzureOpenAI(
            azure_endpoint=self.endpoint,
            api_key=self.subscription_key,
            api_version="2024-12-01-preview",
        )

    def request(self, messages: list) -> str:
        """
        Call Azure OpenAI API using the standard interface
        """
        try:
            # Take first message as prompt if it's a simple list
            if isinstance(messages[0], str):
                prompt = messages[0]
                formatted_messages = [
                    {"role": "user", "content": [{"type": "text", "text": prompt}]}
                ]
            else:
                formatted_messages = messages

            completion = self.client.chat.completions.create(
                model=self.deployment,
                messages=formatted_messages,
                max_completion_tokens=2000,
                stop=None,
                stream=False,
            )

            return completion.choices[0].message.content

        except Exception as e:
            print(f"API error: {e}")
            return None


# =========================
# CLI test
# =========================
if __name__ == "__main__":
    # Test case: Open-ended reasoning problem
    test_problem = """
    A small town has been experiencing a significant decline in local business revenue over the past two years.
    The town council is considering various interventions to revitalize the local economy.
    Some proposed solutions include: reducing business taxes, improving downtown parking,
    organizing community events, and attracting new businesses through incentives.

    What would be the most effective approach to revitalize this town's local economy,
    and what are the key factors that should be considered in making this decision?
    """

    print("=== Mental Model Reasoning Test Case ===")
    print(f"Problem: {test_problem}")
    print("\n" + "="*80 + "\n")

    # Initialize reasoning system
    llm = MockLLM()
    reasoning_system = MentalModelReasoning(llm)

    # Execute reasoning
    result = reasoning_system.reason(test_problem)

    print("\n" + "="*80)
    print("=== FINAL RESULT ===")
    # Uncomment to see full JSON result
    # print(json.dumps(result, indent=2, ensure_ascii=False))
