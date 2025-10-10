from typing import Any, Dict, List, Optional, Union
import json
import hashlib
from dataclasses import dataclass

# Try to import LLM, but don't fail if not available
try:
    from brainary.llm.llm import LLM
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    LLM = None

@dataclass
class SemanticSummary:
    """Represents a semantic summary of an object."""
    key_concepts: List[str]
    relationships: List[str]
    context: str
    importance_score: float
    semantic_hash: str
    summary_text: str

@dataclass
class ExperienceInsight:
    """High-level semantic insights derived from step experiences across all memories."""
    insight_id: str
    insight_type: str  # "performance", "learning", "pattern", "optimization"
    title: str
    description: str
    confidence_score: float
    supporting_evidence: List[str]
    applicability_scope: List[str]  # Which types of operations this applies to
    recommended_actions: List[str]
    metadata: Dict[str, Any] = None

@dataclass
class SemanticExperienceSummary:
    """Very high-level summary and abstracted insights from all step experiences."""
    total_episodes: int
    total_steps: int
    overall_success_rate: float
    dominant_patterns: List[str]
    key_optimization_areas: List[str]
    critical_learning_points: List[str]
    system_capabilities: List[str]
    experience_insights: List[ExperienceInsight]
    metadata: Dict[str, Any] = None

class SemanticMemoryExtractor:
    """Extracts semantic information from objects using LLM."""
    
    def __init__(self, llm_name: str = "gpt-4o-mini", cache_size: int = 1000):
        if not LLM_AVAILABLE:
            raise ImportError("LLM is not available. Please ensure brainary.llm is installed.")
        self.llm = LLM.get_by_name(llm_name)
        self.cache_size = cache_size
        self.semantic_cache = {}  # hash -> SemanticSummary
        
    def extract_semantic_info(self, obj: Any, obj_name: str = None) -> SemanticSummary:
        """
        Extract semantic information from an object.
        
        Args:
            obj: The object to extract semantic information from
            obj_name: Optional name/identifier for the object
            
        Returns:
            SemanticSummary containing extracted semantic information
        """
        # Generate hash for caching
        obj_str = str(obj)
        if obj_name:
            obj_str = f"{obj_name}: {obj_str}"
        
        obj_hash = hashlib.md5(obj_str.encode()).hexdigest()
        
        # Check cache first
        if obj_hash in self.semantic_cache:
            return self.semantic_cache[obj_hash]
        
        # Extract semantic information using LLM
        semantic_summary = self._extract_with_llm(obj, obj_name)
        semantic_summary.semantic_hash = obj_hash
        
        # Cache the result
        self._add_to_cache(obj_hash, semantic_summary)
        
        return semantic_summary
    
    def create_semantic_experience_summary(self, episodic_memories: List[Any], working_memories: List[Any]) -> SemanticExperienceSummary:
        """
        Create very high-level semantic summary and abstracted insights from all step experiences.
        
        Args:
            episodic_memories: List of EpisodicMemory objects
            working_memories: List of WorkingMemory objects
            
        Returns:
            SemanticExperienceSummary containing high-level insights
        """
        if not episodic_memories and not working_memories:
            return None
        
        # Aggregate statistics from episodic memories
        total_episodes = len(episodic_memories)
        total_steps = 0
        total_successful_steps = 0
        total_execution_time = 0.0
        
        # Collect step experience summaries from episodic memories
        step_summaries = []
        for memory in episodic_memories:
            if hasattr(memory, 'step_experience_summary') and memory.step_experience_summary:
                summary = memory.step_experience_summary
                step_summaries.append(summary)
                total_steps += summary.total_steps
                total_successful_steps += summary.successful_steps
                total_execution_time += summary.total_execution_time
        
        # Aggregate from working memories if no episodic summaries
        if not step_summaries and working_memories:
            for memory in working_memories:
                if hasattr(memory, 'step_experiences') and memory.step_experiences:
                    total_steps += len(memory.step_experiences)
                    total_successful_steps += sum(1 for step in memory.step_experiences if getattr(step, 'success', False))
                    total_execution_time += sum(getattr(step, 'execution_time', 0) for step in memory.step_experiences)
        
        # Calculate overall success rate
        overall_success_rate = total_successful_steps / total_steps if total_steps > 0 else 0.0
        
        # Analyze dominant patterns
        dominant_patterns = self._extract_dominant_patterns(step_summaries, working_memories)
        
        # Identify key optimization areas
        key_optimization_areas = self._identify_optimization_areas(step_summaries, working_memories)
        
        # Extract critical learning points
        critical_learning_points = self._extract_critical_learning_points(step_summaries, working_memories)
        
        # Determine system capabilities
        system_capabilities = self._determine_system_capabilities(step_summaries, working_memories)
        
        # Generate high-level insights
        experience_insights = self._generate_experience_insights(step_summaries, working_memories)
        
        return SemanticExperienceSummary(
            total_episodes=total_episodes,
            total_steps=total_steps,
            overall_success_rate=overall_success_rate,
            dominant_patterns=dominant_patterns,
            key_optimization_areas=key_optimization_areas,
            critical_learning_points=critical_learning_points,
            system_capabilities=system_capabilities,
            experience_insights=experience_insights,
            metadata={
                'summary_generated_at': self._get_current_timestamp(),
                'source_episodic_count': len(episodic_memories),
                'source_working_count': len(working_memories)
            }
        )
    
    def _extract_dominant_patterns(self, step_summaries: List[Any], working_memories: List[Any]) -> List[str]:
        """Extract dominant patterns from step experiences."""
        patterns = []
        
        # Analyze step types
        step_type_counts = {}
        for summary in step_summaries:
            for step_type in summary.step_types:
                step_type_counts[step_type] = step_type_counts.get(step_type, 0) + 1
        
        # Add dominant step types
        if step_type_counts:
            dominant_types = sorted(step_type_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            for step_type, count in dominant_types:
                patterns.append(f"Frequent {step_type} operations ({count} occurrences)")
        
        # Analyze execution methods
        method_counts = {}
        for summary in step_summaries:
            for method in summary.execution_methods:
                method_counts[method] = method_counts.get(method, 0) + 1
        
        if method_counts:
            dominant_methods = sorted(method_counts.items(), key=lambda x: x[1], reverse=True)[:2]
            for method, count in dominant_methods:
                patterns.append(f"Common execution method: {method} ({count} uses)")
        
        return patterns[:5]  # Limit to top 5 patterns
    
    def _identify_optimization_areas(self, step_summaries: List[Any], working_memories: List[Any]) -> List[str]:
        """Identify areas for optimization based on step experiences."""
        optimization_areas = []
        
        # Find steps with high failure rates
        for summary in step_summaries:
            if summary.failed_steps > 0:
                failure_rate = summary.failed_steps / summary.total_steps
                if failure_rate > 0.3:  # More than 30% failure rate
                    optimization_areas.append(f"High failure rate in {summary.step_types[0]} operations ({failure_rate:.1%})")
        
        # Find slow operations
        for summary in step_summaries:
            if summary.avg_time_per_step > 2.0:  # More than 2 seconds average
                optimization_areas.append(f"Slow execution in {summary.step_types[0]} operations ({summary.avg_time_per_step:.1f}s avg)")
        
        # Find error patterns
        for summary in step_summaries:
            if summary.error_patterns:
                optimization_areas.append(f"Error patterns detected in {summary.step_types[0]} operations")
        
        return optimization_areas[:5]  # Limit to top 5 areas
    
    def _extract_critical_learning_points(self, step_summaries: List[Any], working_memories: List[Any]) -> List[str]:
        """Extract critical learning points from step experiences."""
        learning_points = []
        
        # Collect key learning points from summaries
        for summary in step_summaries:
            if summary.key_learning_points:
                learning_points.extend(summary.key_learning_points[:2])  # Take top 2 per summary
        
        # Add performance insights
        for summary in step_summaries:
            if summary.performance_highlights:
                learning_points.extend(summary.performance_highlights[:1])  # Take top 1 per summary
        
        # Remove duplicates and limit
        unique_points = list(set(learning_points))
        return unique_points[:8]  # Limit to top 8 learning points
    
    def _determine_system_capabilities(self, step_summaries: List[Any], working_memories: List[Any]) -> List[str]:
        """Determine system capabilities based on step experiences."""
        capabilities = []
        
        # Analyze successful step types
        successful_types = set()
        for summary in step_summaries:
            if summary.success_rate > 0.8:  # High success rate
                for step_type in summary.step_types:
                    successful_types.add(step_type)
        
        for step_type in list(successful_types)[:5]:
            capabilities.append(f"Reliable {step_type} operations")
        
        # Analyze execution methods
        successful_methods = set()
        for summary in step_summaries:
            if summary.success_rate > 0.8:
                for method in summary.execution_methods:
                    successful_methods.add(method)
        
        for method in list(successful_methods)[:3]:
            capabilities.append(f"Proven {method} execution")
        
        return capabilities[:8]  # Limit to top 8 capabilities
    
    def _generate_experience_insights(self, step_summaries: List[Any], working_memories: List[Any]) -> List[ExperienceInsight]:
        """Generate high-level experience insights."""
        insights = []
        
        # Performance insight
        if step_summaries:
            avg_success_rate = sum(s.success_rate for s in step_summaries) / len(step_summaries)
            if avg_success_rate > 0.9:
                insights.append(ExperienceInsight(
                    insight_id="high_performance",
                    insight_type="performance",
                    title="High Overall System Performance",
                    description=f"System demonstrates excellent reliability with {avg_success_rate:.1%} success rate",
                    confidence_score=0.9,
                    supporting_evidence=[f"Average success rate: {avg_success_rate:.1%}"],
                    applicability_scope=["all operations"],
                    recommended_actions=["Maintain current execution patterns", "Document successful approaches"]
                ))
        
        # Learning insight
        if step_summaries:
            total_learning_points = sum(len(s.key_learning_points) for s in step_summaries)
            if total_learning_points > 5:
                insights.append(ExperienceInsight(
                    insight_id="active_learning",
                    insight_type="learning",
                    title="Active Learning System",
                    description="System is actively learning and improving from experiences",
                    confidence_score=0.8,
                    supporting_evidence=[f"Total learning points: {total_learning_points}"],
                    applicability_scope=["system improvement"],
                    recommended_actions=["Continue monitoring learning progress", "Apply insights to new operations"]
                ))
        
        # Pattern insight
        if step_summaries:
            step_types = set()
            for summary in step_summaries:
                step_types.update(summary.step_types)
            
            if len(step_types) > 3:
                insights.append(ExperienceInsight(
                    insight_id="diverse_operations",
                    insight_type="pattern",
                    title="Diverse Operation Types",
                    description=f"System handles {len(step_types)} different types of operations",
                    confidence_score=0.7,
                    supporting_evidence=[f"Operation types: {', '.join(list(step_types)[:5])}"],
                    applicability_scope=["system design", "capability assessment"],
                    recommended_actions=["Leverage diverse capabilities", "Explore new operation types"]
                ))
        
        return insights
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _extract_with_llm(self, obj: Any, obj_name: str = None) -> SemanticSummary:
        """Extract semantic information using LLM."""
        
        # Check if LLM is available
        if not LLM_AVAILABLE or self.llm is None:
            return self._fallback_extraction(obj, obj_name)
        
        # Prepare the input for LLM analysis
        obj_repr = self._prepare_object_representation(obj, obj_name)
        
        # Create the extraction prompt
        prompt = self._create_extraction_prompt(obj_repr)
        
        try:
            # Get LLM response
            response = self.llm.request([prompt])
            if response and len(response) > 0:
                result_text = response[0]
            else:
                result_text = ""
            
            # Parse the LLM response
            semantic_summary = self._parse_llm_response(result_text, obj_repr)
            
        except Exception as e:
            # Fallback to basic extraction if LLM fails
            semantic_summary = self._fallback_extraction(obj, obj_name)
        
        return semantic_summary
    
    def _prepare_object_representation(self, obj: Any, obj_name: str = None) -> str:
        """Prepare object representation for LLM analysis."""
        
        if hasattr(obj, 'render'):
            # Use object's render method if available
            obj_repr = obj.render()
        elif hasattr(obj, '__dict__'):
            # Use object's attributes
            obj_repr = str(obj.__dict__)
        else:
            # Use string representation
            obj_repr = str(obj)
        
        if obj_name:
            obj_repr = f"Object Name: {obj_name}\nObject Content: {obj_repr}"
        
        return obj_repr
    
    def _create_extraction_prompt(self, obj_repr: str) -> str:
        """Create the prompt for semantic extraction."""
        
        prompt = f"""
You are an expert semantic analyzer. Your task is to extract meaningful semantic information from objects and create insightful summaries.

## Object to Analyze
{obj_repr}

## Task
Analyze the object and extract semantic information in the following JSON format:

{{
    "key_concepts": ["concept1", "concept2", "concept3"],
    "relationships": ["relationship1", "relationship2"],
    "context": "Brief context description",
    "importance_score": 0.85,
    "summary_text": "A meaningful semantic summary"
}}

## Guidelines for Summary Text
The summary_text should be:
- **Meaningful**: Explain what the object represents semantically, not just its structure
- **Concise**: 1-2 sentences maximum
- **Insightful**: Capture the purpose, function, or meaning of the object
- **Contextual**: Relate to the domain or use case if apparent

## Examples of Good vs Bad Summaries:
- ❌ Bad: "Object Name: Review, Object Content: class Review with text and author fields"
- ✅ Good: "A user review system component that stores feedback with author attribution"
- ❌ Bad: "Class with name, age, and email properties"
- ✅ Good: "A person entity representing user profile data with contact information"

## Guidelines for Other Fields:
- **key_concepts**: Extract the most important semantic concepts, entities, or ideas (not field names)
- **relationships**: Describe how this object relates to other entities or concepts
- **context**: Provide domain context or situational information
- **importance_score**: Score from 0.0 to 1.0 based on semantic significance

## Output
Provide only the JSON response, no additional text.
"""
        return prompt
    
    def _parse_llm_response(self, response: str, obj_repr: str) -> SemanticSummary:
        """Parse LLM response into SemanticSummary."""
        
        try:
            # Try to extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
                
                return SemanticSummary(
                    key_concepts=data.get('key_concepts', []),
                    relationships=data.get('relationships', []),
                    context=data.get('context', ''),
                    importance_score=float(data.get('importance_score', 0.5)),
                    semantic_hash='',  # Will be set by caller
                    summary_text=data.get('summary_text', '')
                )
            else:
                # Fallback if JSON parsing fails
                return self._fallback_extraction_from_text(response, obj_repr)
                
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Fallback if parsing fails
            return self._fallback_extraction_from_text(response, obj_repr)
    
    def _fallback_extraction_from_text(self, response: str, obj_repr: str) -> SemanticSummary:
        """Fallback extraction when JSON parsing fails."""
        
        # Extract concepts from response text
        concepts = []
        if 'concept' in response.lower():
            # Try to extract concepts mentioned in response
            lines = response.split('\n')
            for line in lines:
                if 'concept' in line.lower() or 'key' in line.lower():
                    concepts.append(line.strip())
        
        # If no concepts found, use basic extraction
        if not concepts:
            return self._fallback_extraction(obj_repr, None)
        
        return SemanticSummary(
            key_concepts=concepts[:5],  # Limit to 5 concepts
            relationships=[],
            context="Extracted from LLM response",
            importance_score=0.5,
            semantic_hash='',
            summary_text=response[:200] if response else "No summary available"
        )
    
    def _fallback_extraction(self, obj: Any, obj_name: str = None) -> SemanticSummary:
        """Fallback extraction when LLM is not available."""
        
        obj_str = str(obj)
        
        # Basic concept extraction
        concepts = []
        if hasattr(obj, '__class__'):
            concepts.append(obj.__class__.__name__)
        
        # Extract words that might be concepts
        words = obj_str.split()
        for word in words:
            if len(word) > 3 and word[0].isupper():
                concepts.append(word)
        
        # Limit concepts
        concepts = concepts[:5]
        
        return SemanticSummary(
            key_concepts=concepts,
            relationships=[],
            context="Basic extraction",
            importance_score=0.3,
            semantic_hash='',
            summary_text=obj_str[:100] + "..." if len(obj_str) > 100 else obj_str
        )
    
    def _add_to_cache(self, obj_hash: str, summary: SemanticSummary):
        """Add semantic summary to cache with size management."""
        
        if len(self.semantic_cache) >= self.cache_size:
            # Remove oldest entry (simple FIFO)
            oldest_key = next(iter(self.semantic_cache))
            del self.semantic_cache[oldest_key]
        
        self.semantic_cache[obj_hash] = summary
    
    def get_semantic_summary(self, obj: Any, obj_name: str = None) -> str:
        """Get a text summary of semantic information."""
        summary = self.extract_semantic_info(obj, obj_name)
        return summary.summary_text
    
    def get_key_concepts(self, obj: Any, obj_name: str = None) -> List[str]:
        """Get key concepts from an object."""
        summary = self.extract_semantic_info(obj, obj_name)
        return summary.key_concepts
    
    def get_importance_score(self, obj: Any, obj_name: str = None) -> float:
        """Get importance score for an object."""
        summary = self.extract_semantic_info(obj, obj_name)
        return summary.importance_score
    
    def clear_cache(self):
        """Clear the semantic cache."""
        self.semantic_cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            'cache_size': len(self.semantic_cache),
            'max_cache_size': self.cache_size,
            'cache_usage_percentage': (len(self.semantic_cache) / self.cache_size) * 100
        }

# Global extractor instance
_extractor_instance = None

def get_semantic_extractor(llm_name: str = "gpt-4o-mini") -> SemanticMemoryExtractor:
    """Get the global semantic extractor instance."""
    global _extractor_instance
    if _extractor_instance is None:
        try:
            _extractor_instance = SemanticMemoryExtractor(llm_name)
        except ImportError:
            # Create a fallback extractor that only uses basic extraction
            _extractor_instance = FallbackSemanticExtractor()
    return _extractor_instance

class FallbackSemanticExtractor:
    """Fallback semantic extractor that doesn't require LLM."""
    
    def __init__(self):
        self.semantic_cache = {}
    
    def extract_semantic_info(self, obj: Any, obj_name: str = None) -> SemanticSummary:
        """Extract semantic information using basic methods."""
        obj_str = str(obj)
        if obj_name:
            obj_str = f"{obj_name}: {obj_str}"
        
        obj_hash = hashlib.md5(obj_str.encode()).hexdigest()
        
        # Check cache first
        if obj_hash in self.semantic_cache:
            return self.semantic_cache[obj_hash]
        
        # Use basic extraction
        summary = self._fallback_extraction(obj, obj_name)
        summary.semantic_hash = obj_hash
        
        # Cache the result
        self.semantic_cache[obj_hash] = summary
        return summary
    
    def _fallback_extraction(self, obj: Any, obj_name: str = None) -> SemanticSummary:
        """Basic semantic extraction without LLM."""
        obj_str = str(obj)
        
        # Basic concept extraction
        concepts = []
        if hasattr(obj, '__class__'):
            concepts.append(obj.__class__.__name__)
        
        # Extract words that might be concepts
        words = obj_str.split()
        for word in words:
            if len(word) > 3 and word[0].isupper():
                concepts.append(word)
        
        # Limit concepts
        concepts = concepts[:5]
        
        return SemanticSummary(
            key_concepts=concepts,
            relationships=[],
            context="Basic extraction (LLM not available)",
            importance_score=0.3,
            semantic_hash='',
            summary_text=obj_str[:100] + "..." if len(obj_str) > 100 else obj_str
        )
    
    def get_semantic_summary(self, obj: Any, obj_name: str = None) -> str:
        """Get a text summary of semantic information."""
        summary = self.extract_semantic_info(obj, obj_name)
        return summary.summary_text
    
    def get_key_concepts(self, obj: Any, obj_name: str = None) -> List[str]:
        """Get key concepts from an object."""
        summary = self.extract_semantic_info(obj, obj_name)
        return summary.key_concepts
    
    def get_importance_score(self, obj: Any, obj_name: str = None) -> float:
        """Get importance score for an object."""
        summary = self.extract_semantic_info(obj, obj_name)
        return summary.importance_score

def extract_semantic_info(obj: Any, obj_name: str = None) -> SemanticSummary:
    """Convenience function to extract semantic information."""
    extractor = get_semantic_extractor()
    return extractor.extract_semantic_info(obj, obj_name)

def get_semantic_summary(obj: Any, obj_name: str = None) -> str:
    """Convenience function to get semantic summary."""
    extractor = get_semantic_extractor()
    return extractor.get_semantic_summary(obj, obj_name)
