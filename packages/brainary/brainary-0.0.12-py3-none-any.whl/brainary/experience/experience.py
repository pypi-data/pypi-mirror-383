from pathlib import Path
from typing import List, Dict, Any, Optional
import statistics
import json
import pickle
import logging

from brainary.llm.llm import LLM, AUX_MODEL


class Experience:
    """Single record of a capability-strategy performance history."""

    def __init__(self, capability: str, strategy: str, metadata: Dict[str, Any] = None):
        self.capability = capability
        self.strategy = strategy
        self.metadata = metadata or {}
        self.outcomes: List[Dict[str, Any]] = []  # List of outcome records with additional data
        self.usage_count: int = 0
        self._cached_avg_outcome: Optional[float] = None
        self._cached_impact_score: Optional[float] = None

    def record_outcome(self, score: float, context: Dict[str, Any] = None):
        """
        Record an outcome with additional context.
        
        Args:
            score (float): The performance score (0-1)
            context (dict, optional): Additional context about the outcome
        """
        # Use empty dict if context is None to safely use .get()
        ctx = context if context is not None else {}
        outcome_record = {
            "score": score,
            "timestamp": ctx.get("timestamp"),
            "instruction": ctx.get("instruction"),
            "task_complexity": ctx.get("task_complexity", 0.5),
            "contribution": ctx.get("contribution", score)  # How much this capability contributed
        }
        self.outcomes.append(outcome_record)
        self.usage_count += 1
        # Invalidate caches
        self._cached_avg_outcome = None
        self._cached_impact_score = None

    @property
    def avg_outcome(self) -> float:
        """Calculate average outcome across all uses."""
        if self._cached_avg_outcome is None:
            if not self.outcomes:
                self._cached_avg_outcome = 0.0
            else:
                scores = [o["score"] for o in self.outcomes]
                self._cached_avg_outcome = statistics.mean(scores)
        return self._cached_avg_outcome

    @property
    def impact_score(self) -> float:
        """
        Calculate the impact score of this capability-strategy combination.
        Impact score considers:
        - Average outcome
        - Task complexity
        - Contribution to success
        - Recency of outcomes
        """
        if self._cached_impact_score is None:
            if not self.outcomes:
                self._cached_impact_score = 0.0
            else:
                # Calculate weighted score considering multiple factors
                total_weight = 0
                weighted_sum = 0
                
                for outcome in self.outcomes:
                    # Base score
                    score = outcome["score"]
                    
                    # Weight factors
                    complexity_weight = outcome.get("task_complexity", 0.5)  # Higher weight for complex tasks
                    contribution_weight = outcome.get("contribution", score)  # Higher weight when capability was crucial
                    
                    # Combine weights
                    weight = (1 + complexity_weight + contribution_weight) / 3
                    total_weight += weight
                    weighted_sum += score * weight
                
                self._cached_impact_score = weighted_sum / total_weight if total_weight > 0 else 0
                
        return self._cached_impact_score
    
    def __repr__(self):
        return json.dumps(self.to_dict(), indent=4)


    def to_dict(self) -> Dict[str, Any]:
        return {
            "capability": self.capability,
            "strategy": self.strategy,
            "avg_outcome": self.avg_outcome,
            "usage_count": self.usage_count,
            "metadata": self.metadata,
        }


class Knowledge:
    """Distilled abstract rules from raw experiences."""

    def __init__(self):
        self.rules: List[Dict] = []

    def add_rule(self, capability: str, condition: str, strategy: str, confidence: float):
        self.rules.append({
            "capability": capability,
            "condition": condition,  # textual condition (keywords, contexts)
            "strategy": strategy,
            "confidence": confidence,
        })

    def query(self, capability: str, context: str = "") -> List[Dict]:
        """Find matching rules given current context (simple keyword filter)."""
        matches = []
        for r in self.rules:
            if r["capability"] == capability and any(
                word in context.lower() for word in r["condition"].split()
            ):
                matches.append(r)
        return sorted(matches, key=lambda x: x["confidence"], reverse=True)


class ExperienceBase:
    """Collection of experiences across all capabilities and strategies."""

    def __init__(self, llm=None):
        self.llm = llm
        self.memory: Dict[str, Dict[str, Experience]] = {}  # cap -> strat -> Experience
        self.knowledge = Knowledge()
        self.update_counter = 0
        
    def __getstate__(self):
        """Customize what gets pickled by excluding the LLM object"""
        # Copy the object's state
        state = self.__dict__.copy()
        # Remove unpicklable LLM object
        if 'llm' in state:
            state['llm'] = None
        return state
        
    def display(self) -> str:
        serializable_memory = {
            cap: {strategy: exp.to_dict() for strategy, exp in strategies.items()}
            for cap, strategies in self.memory.items()
        }
        return json.dumps(serializable_memory, indent=4)


    def dump(self, path):
        try:
            with Path(path).open("wb") as f:
                pickle.dump(self, f)
        except (TypeError, AttributeError) as e:
            # Handle case where Python is shutting down or other issues
            logging.warning(f"Failed to dump experience base: {e}")

    @classmethod
    def load(cls, path):
        with Path(path).open("rb") as f:
            return pickle.load(f)

    # -------- Raw Experience --------
    def inject(
        self,
        capability: str,
        strategy: str,
        outcome: float = 1.0,
        metadata: Dict[str, Any] = None,
    ):
        cap_mem = self.memory.setdefault(capability, {})
        exp = cap_mem.get(strategy)
        if exp is None:
            exp = Experience(capability, strategy, metadata)
            cap_mem[strategy] = exp
        
        # Extract context information from metadata
        context = {}
        if metadata:
            # Map standard metadata fields to context
            context = {
                "timestamp": metadata.get("timestamp"),
                "instruction": metadata.get("instruction"),
                "task_complexity": metadata.get("task_complexity", 0.5),
                "contribution": metadata.get("contribution"),
                "task_type": metadata.get("cognitive_pattern", {}).get("task_type"),
                "sequence_position": metadata.get("cognitive_pattern", {}).get("sequence_position")
            }
            
        exp.record_outcome(outcome, context)

    def record(
        self,
        capability: str,
        strategy: str,
        outcome: float,
        metadata: Dict[str, Any] = None,
    ):
        self.inject(capability, strategy, outcome, metadata)
        self.update_counter += 1
        if self.update_counter % 10 == 0:  # auto-distill every 10 updates
            self.distill()

    def query(self, instruction: str = None, capability: str = None, min_outcome: float = None, 
             metadata_filter: Dict[str, Any] = None) -> List[Experience]:
        """
        Query experiences based on multiple criteria.
        
        Args:
            instruction (str, optional): The instruction to match against
            capability (str, optional): The specific capability to filter by
            min_outcome (float, optional): Minimum average outcome threshold
            metadata_filter (Dict[str, Any], optional): Nested filter for metadata
            
        Returns:
            List[Experience]: Sorted list of matching experiences by performance
        """
        results = []
        
        # If no capability specified, search all capabilities
        caps_to_search = [capability] if capability else self.memory.keys()
        
        for cap in caps_to_search:
            if cap not in self.memory:
                continue
                
            for exp in self.memory[cap].values():
                # Apply filters
                if min_outcome is not None and exp.avg_outcome < min_outcome:
                    continue
                    
                if instruction:
                    # Check instruction similarity using metadata
                    if not exp.metadata.get("instructions"):
                        continue
                    # Simple substring match for now, could be enhanced with semantic similarity
                    if instruction.lower() not in str(exp.metadata["instructions"]).lower():
                        continue
                
                # Apply metadata filter if provided
                if metadata_filter:
                    # Check if the experience matches all metadata filters
                    match = True
                    for key, value in metadata_filter.items():
                        if key not in exp.metadata:
                            match = False
                            break
                        
                        # Handle nested metadata (e.g., cognitive_pattern.task_type)
                        if isinstance(value, dict):
                            if not isinstance(exp.metadata[key], dict):
                                match = False
                                break
                                
                            for subkey, subvalue in value.items():
                                if subkey not in exp.metadata[key] or exp.metadata[key][subkey] != subvalue:
                                    match = False
                                    break
                        else:
                            # Direct value comparison
                            if exp.metadata[key] != value:
                                match = False
                                break
                                
                    if not match:
                        continue
                        
                results.append(exp)
                
        return sorted(results, key=lambda e: e.avg_outcome, reverse=True)

    def best_strategy(self, capability: str) -> str:
        """Return best-performing strategy for a capability (by average outcome)."""
        exps = self.query(capability)
        if not exps:
            return None
        return exps[0].strategy

    def all_strategies(self) -> Dict[str, List[str]]:
        return {cap: list(strats.keys()) for cap, strats in self.memory.items()}

    # -------- Distillation into Knowledge --------
    def distill(self):
        """
        Summarize experience records into abstract knowledge rules via LLM.
        Updates self.knowledge.
        """
        # Prepare experience data
        experiences = []
        for cap, strategies in self.memory.items():
            for strat, exp in strategies.items():
                experiences.append({
                    "capability": cap,
                    "strategy": strat,
                    "avg_outcome": round(exp.avg_outcome, 2),
                    "usage_count": exp.usage_count,
                    "metadata": exp.metadata
                })
                
        conversation = [
            {"role": "system", "content": "You are a meta-cognition learner distilling patterns from execution experiences."},
            {"role": "system", "content": (
                "Output requirements:\n"
                "Return a JSON array where each entry has:\n"
                "- capability: string (exact match to system capability)\n"
                "- condition: string (descriptive keywords)\n"
                "- strategy: string (exact match to system strategy)\n"
                "- confidence: float (0.0 to 1.0)"
            )},
            {"role": "user", "content": json.dumps({
                "task": "Analyze these experiences and extract rules about effective strategy use",
                "experiences": experiences
            }, indent=2)}
        ]

        response = self.llm.request(conversation)

        try:
            rules = json.loads(response)
            for r in rules:
                self.knowledge.add_rule(
                    capability=r["capability"],
                    condition=r["condition"],
                    strategy=r["strategy"],
                    confidence=r["confidence"],
                )
        except Exception:
            # fallback: ignore bad LLM output
            pass
