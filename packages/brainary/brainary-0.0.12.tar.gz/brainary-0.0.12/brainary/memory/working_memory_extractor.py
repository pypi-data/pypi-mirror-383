from typing import Any, Dict, List, Optional, Union
import json
import hashlib
from dataclasses import dataclass
from datetime import datetime, timedelta
import inspect

# Try to import LLM, but don't fail if not available
try:
    from brainary.llm.llm import LLM
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    LLM = None

@dataclass
class StepExperience:
    """Represents experience from executing a specific step."""
    step_id: str
    step_name: str
    step_type: str  # "action", "examine", "extract", "analyze", etc.
    execution_method: str  # How the step was performed
    input_data: Dict[str, Any]  # Input parameters and data
    output_result: Any  # Result/output of the step
    success: bool  # Whether the step succeeded
    execution_time: float  # Time taken in seconds
    error_message: Optional[str] = None  # Error details if failed
    performance_metrics: Dict[str, Any] = None  # Quality, accuracy, etc.
    learning_insights: List[str] = None  # What was learned from this step
    metadata: Dict[str, Any] = None  # Additional context

@dataclass
class WorkingMemory:
    """Represents a working memory entry for short-term session awareness."""
    session_id: str
    timestamp: datetime
    current_task: str
    active_context: List[str]
    immediate_goals: List[str]
    attention_focus: str
    memory_hash: str
    summary_text: str
    # Enhanced fields for object analysis
    object_fields: Dict[str, Any] = None
    object_relationships: List[Dict[str, Any]] = None
    field_metadata: Dict[str, Any] = None
    # Experience module for step-by-step learning
    step_experiences: List[StepExperience] = None
    execution_summary: Dict[str, Any] = None  # Overall execution insights

class WorkingMemoryExtractor:
    """Extracts working memory information for short-term session awareness."""
    
    def __init__(self, llm_name: str = "gpt-4o-mini", cache_size: int = 1000):
        if not LLM_AVAILABLE:
            raise ImportError("LLM is not available. Please ensure brainary.llm is installed.")
        self.llm = LLM.get_by_name(llm_name)
        self.cache_size = cache_size
        self.working_cache = {}  # hash -> WorkingMemory
        
    def extract_working_memory(self, session_data: Dict[str, Any], session_id: str = None) -> WorkingMemory:
        """
        Extract working memory from session data.
        
        Args:
            session_data: Dictionary containing current session information
            session_id: Optional unique identifier for the session
            
        Returns:
            WorkingMemory containing extracted working memory information
        """
        # Generate hash for caching
        session_str = json.dumps(session_data, sort_keys=True)
        if session_id:
            session_str = f"{session_id}: {session_str}"
        
        memory_hash = hashlib.md5(session_str.encode()).hexdigest()
        
        # Check cache first
        if memory_hash in self.working_cache:
            return self.working_cache[memory_hash]
        
        # Extract working memory information using fallback method (no LLM logging)
        working_memory = self._fallback_extraction(session_data, session_id)
        working_memory.memory_hash = memory_hash
        working_memory.timestamp = datetime.now()
        
        # Cache the result
        self._add_to_cache(memory_hash, working_memory)
        
        return working_memory
    
    def extract_object_working_memory(self, obj: Any, session_id: str = None) -> WorkingMemory:
        """
        Extract working memory specifically for object analysis.
        
        Args:
            obj: The object to analyze
            session_id: Optional unique identifier for the session
            
        Returns:
            WorkingMemory containing extracted working memory information with object details
        """
        # Analyze object structure
        object_info = self._analyze_object_structure(obj)
        
        session_data = {
            'task': f'Analyzing object of type {obj.__class__.__name__}',
            'task_type': 'object_analysis',
            'context': [
                f'Object Type: {obj.__class__.__name__}',
                f'Object Fields: {list(object_info["fields"].keys())}',
                f'Object Content: {str(obj)[:200]}...' if len(str(obj)) > 200 else str(obj)
            ],
            'goals': ['Understand object structure', 'Extract field relationships', 'Store object in memory'],
            'focus': 'Object field analysis and relationship mapping',
            'object_info': object_info
        }
        
        # Use fallback extraction to avoid LLM logging
        working_memory = self._fallback_extraction(session_data, session_id)
        
        # Initialize experience tracking
        if working_memory.step_experiences is None:
            working_memory.step_experiences = []
        
        # Add initial step experience for object analysis
        analysis_experience = StepExperience(
            step_id=f"analysis_{len(working_memory.step_experiences) + 1}",
            step_name="Object Structure Analysis",
            step_type="analyze",
            execution_method="LLM-based field extraction",
            input_data={"object_type": obj.__class__.__name__, "object_content": str(obj)[:500]},
            output_result=object_info,
            success=True,
            execution_time=0.0,  # Will be updated by caller
            performance_metrics={"fields_extracted": len(object_info["fields"]), "relationships_found": len(object_info["relationships"])},
            learning_insights=["Object structure successfully analyzed", "Field relationships mapped"],
            metadata={"object_class": obj.__class__.__name__, "analysis_depth": "comprehensive"}
        )
        working_memory.step_experiences.append(analysis_experience)
        
        return working_memory
    
    def add_step_experience(self, working_memory: WorkingMemory, step_name: str, step_type: str, 
                           execution_method: str, input_data: Dict[str, Any], output_result: Any, 
                           success: bool, execution_time: float, error_message: str = None,
                           performance_metrics: Dict[str, Any] = None, learning_insights: List[str] = None,
                           metadata: Dict[str, Any] = None) -> StepExperience:
        """
        Add a step experience to working memory.
        
        Args:
            working_memory: The working memory to add experience to
            step_name: Name of the step
            step_type: Type of step (action, examine, extract, etc.)
            execution_method: How the step was performed
            input_data: Input parameters and data
            output_result: Result/output of the step
            success: Whether the step succeeded
            execution_time: Time taken in seconds
            error_message: Error details if failed
            performance_metrics: Quality, accuracy, etc.
            learning_insights: What was learned from this step
            metadata: Additional context
            
        Returns:
            The created StepExperience object
        """
        if working_memory.step_experiences is None:
            working_memory.step_experiences = []
        
        step_experience = StepExperience(
            step_id=f"step_{len(working_memory.step_experiences) + 1}",
            step_name=step_name,
            step_type=step_type,
            execution_method=execution_method,
            input_data=input_data,
            output_result=output_result,
            success=success,
            execution_time=execution_time,
            error_message=error_message,
            performance_metrics=performance_metrics or {},
            learning_insights=learning_insights or [],
            metadata=metadata or {}
        )
        
        working_memory.step_experiences.append(step_experience)
        
        # Update execution summary
        self._update_execution_summary(working_memory, step_experience)
        
        return step_experience
    
    def _update_execution_summary(self, working_memory: WorkingMemory, step_experience: StepExperience):
        """Update the overall execution summary based on new step experience."""
        if working_memory.execution_summary is None:
            working_memory.execution_summary = {
                "total_steps": 0,
                "successful_steps": 0,
                "failed_steps": 0,
                "total_execution_time": 0.0,
                "step_types": {},
                "common_errors": {},
                "performance_trends": [],
                "learning_progress": []
            }
        
        summary = working_memory.execution_summary
        summary["total_steps"] += 1
        
        if step_experience.success:
            summary["successful_steps"] += 1
        else:
            summary["failed_steps"] += 1
            # Track common errors
            error_type = type(step_experience.error_message).__name__ if step_experience.error_message else "Unknown"
            summary["common_errors"][error_type] = summary["common_errors"].get(error_type, 0) + 1
        
        summary["total_execution_time"] += step_experience.execution_time
        
        # Track step types
        step_type = step_experience.step_type
        if step_type not in summary["step_types"]:
            summary["step_types"][step_type] = {"count": 0, "success_rate": 0.0, "avg_time": 0.0}
        
        type_stats = summary["step_types"][step_type]
        type_stats["count"] += 1
        type_stats["success_rate"] = summary["successful_steps"] / summary["total_steps"]
        type_stats["avg_time"] = summary["total_execution_time"] / summary["total_steps"]
        
        # Add performance trend
        summary["performance_trends"].append({
            "step_id": step_experience.step_id,
            "success": step_experience.success,
            "execution_time": step_experience.execution_time,
            "timestamp": step_experience.metadata.get("timestamp", datetime.now().isoformat())
        })
        
        # Add learning insights
        if step_experience.learning_insights:
            summary["learning_progress"].extend(step_experience.learning_insights)
    
    def get_execution_insights(self, working_memory: WorkingMemory) -> Dict[str, Any]:
        """
        Get insights from the execution experience.
        
        Args:
            working_memory: The working memory to analyze
            
        Returns:
            Dictionary containing execution insights
        """
        if not working_memory.execution_summary:
            return {"message": "No execution data available"}
        
        summary = working_memory.execution_summary
        
        insights = {
            "overview": {
                "total_steps": summary["total_steps"],
                "success_rate": f"{(summary['successful_steps'] / summary['total_steps'] * 100):.1f}%" if summary["total_steps"] > 0 else "0%",
                "total_time": f"{summary['total_execution_time']:.2f}s",
                "avg_time_per_step": f"{summary['total_execution_time'] / summary['total_steps']:.2f}s" if summary["total_steps"] > 0 else "0s"
            },
            "step_type_analysis": summary["step_types"],
            "error_analysis": summary["common_errors"],
            "performance_trends": summary["performance_trends"][-10:],  # Last 10 steps
            "learning_progress": summary["learning_progress"][-10:]  # Last 10 insights
        }
        
        return insights
    
    def _analyze_object_structure(self, obj: Any) -> Dict[str, Any]:
        """Analyze the structure of an object and extract field information."""
        
        object_info = {
            'class_name': obj.__class__.__name__,
            'module': obj.__class__.__module__,
            'fields': {},
            'relationships': [],
            'metadata': {}
        }
        
        try:
            # Get all attributes of the object
            for attr_name in dir(obj):
                # Skip private attributes and methods
                if attr_name.startswith('_'):
                    continue
                
                try:
                    attr_value = getattr(obj, attr_name)
                    
                    # Skip methods
                    if callable(attr_value):
                        continue
                    
                    # Analyze the attribute
                    field_info = self._analyze_field(attr_name, attr_value)
                    object_info['fields'][attr_name] = field_info
                    
                    # Check for relationships (e.g., author in Review)
                    if self._is_relationship_field(attr_name, attr_value):
                        relationship = {
                            'field_name': attr_name,
                            'field_value': str(attr_value),
                            'relationship_type': self._determine_relationship_type(attr_name, attr_value),
                            'importance': self._assess_field_importance(attr_name, attr_value)
                        }
                        object_info['relationships'].append(relationship)
                    
                except Exception as e:
                    # Skip attributes that can't be accessed
                    continue
            
            # Add metadata about the object
            object_info['metadata'] = {
                'total_fields': len(object_info['fields']),
                'has_relationships': len(object_info['relationships']) > 0,
                'object_size': len(str(obj)),
                'field_types': {name: type(value).__name__ for name, value in object_info['fields'].items()}
            }
            
        except Exception as e:
            # Fallback analysis
            object_info['fields'] = {'content': str(obj)[:100] + "..." if len(str(obj)) > 100 else str(obj)}
            object_info['metadata'] = {'analysis_error': str(e)}
        
        return object_info
    
    def _analyze_field(self, field_name: str, field_value: Any) -> Dict[str, Any]:
        """Analyze a specific field of an object."""
        
        field_info = {
            'name': field_name,
            'value': str(field_value),
            'type': type(field_value).__name__,
            'length': len(str(field_value)) if hasattr(field_value, '__len__') else None,
            'is_empty': not bool(field_value) if hasattr(field_value, '__bool__') else None
        }
        
        # Add specific analysis based on field name
        if field_name.lower() in ['author', 'user', 'creator', 'owner']:
            field_info['field_type'] = 'entity_identifier'
            field_info['importance'] = 'high'
        elif field_name.lower() in ['text', 'content', 'message', 'description']:
            field_info['field_type'] = 'content'
            field_info['importance'] = 'high'
        elif field_name.lower() in ['id', 'uuid', 'key']:
            field_info['field_type'] = 'identifier'
            field_info['importance'] = 'medium'
        elif field_name.lower() in ['timestamp', 'date', 'time', 'created_at']:
            field_info['field_type'] = 'temporal'
            field_info['importance'] = 'medium'
        else:
            field_info['field_type'] = 'general'
            field_info['importance'] = 'low'
        
        return field_info
    
    def _is_relationship_field(self, field_name: str, field_value: Any) -> bool:
        """Determine if a field represents a relationship."""
        
        # Check field name patterns
        relationship_patterns = [
            'author', 'user', 'creator', 'owner', 'contributor',
            'parent', 'child', 'related', 'reference', 'link'
        ]
        
        field_name_lower = field_name.lower()
        for pattern in relationship_patterns:
            if pattern in field_name_lower:
                return True
        
        # Check if it's a string that looks like an identifier
        if isinstance(field_value, str) and len(field_value) > 0:
            # Simple heuristic: if it's not too long and doesn't contain spaces, might be an identifier
            if len(field_value) < 50 and ' ' not in field_value:
                return True
        
        return False
    
    def _determine_relationship_type(self, field_name: str, field_value: Any) -> str:
        """Determine the type of relationship a field represents."""
        
        field_name_lower = field_name.lower()
        
        if 'author' in field_name_lower or 'creator' in field_name_lower:
            return 'creation_relationship'
        elif 'user' in field_name_lower or 'owner' in field_name_lower:
            return 'ownership_relationship'
        elif 'parent' in field_name_lower:
            return 'hierarchical_relationship'
        elif 'related' in field_name_lower or 'reference' in field_name_lower:
            return 'reference_relationship'
        else:
            return 'general_relationship'
    
    def _assess_field_importance(self, field_name: str, field_value: Any) -> str:
        """Assess the importance of a field."""
        
        field_name_lower = field_name.lower()
        
        # High importance fields
        if field_name_lower in ['author', 'text', 'content', 'user', 'id']:
            return 'high'
        
        # Medium importance fields
        if field_name_lower in ['title', 'name', 'description', 'timestamp', 'date']:
            return 'medium'
        
        # Low importance fields (default)
        return 'low'
    
    def _extract_with_llm(self, session_data: Dict[str, Any], session_id: str = None) -> WorkingMemory:
        """Extract working memory information using LLM."""
        
        # Check if LLM is available
        if not LLM_AVAILABLE or self.llm is None:
            return self._fallback_extraction(session_data, session_id)
        
        # Prepare the input for LLM analysis
        session_repr = self._prepare_session_representation(session_data, session_id)
        
        # Create the extraction prompt
        prompt = self._create_extraction_prompt(session_repr)
        
        try:
            # Get LLM response
            response = self.llm.request([prompt])
            if response and len(response) > 0:
                result_text = response[0]
            else:
                result_text = ""
            
            # Parse the LLM response
            working_memory = self._parse_llm_response(result_text, session_data, session_id)
            
        except Exception as e:
            # Fallback to basic extraction if LLM fails
            working_memory = self._fallback_extraction(session_data, session_id)
        
        return working_memory
    
    def _prepare_session_representation(self, session_data: Dict[str, Any], session_id: str = None) -> str:
        """Prepare session representation for LLM analysis."""
        
        # Convert session data to a readable format
        session_repr = json.dumps(session_data, indent=2, default=str)
        
        if session_id:
            session_repr = f"Session ID: {session_id}\nSession Data: {session_repr}"
        
        return session_repr
    
    def _create_extraction_prompt(self, session_repr: str) -> str:
        """Create the prompt for working memory extraction."""
        
        prompt = f"""
You are a working memory extractor. Analyze the following session data and extract current working memory information.

## Session Data to Analyze
{session_repr}

## Task
Extract working memory information in the following JSON format:

{{
    "session_id": "unique_identifier",
    "current_task": "description of what is currently being worked on",
    "active_context": ["context1", "context2", "context3"],
    "immediate_goals": ["goal1", "goal2"],
    "attention_focus": "what the system should focus on right now",
    "summary_text": "A concise summary of current working state",
    "object_fields": {{
        "field_name": {{
            "value": "field_value",
            "type": "field_type",
            "importance": "high|medium|low",
            "field_type": "entity_identifier|content|identifier|temporal|general"
        }}
    }},
    "object_relationships": [
        {{
            "field_name": "field_name",
            "field_value": "field_value",
            "relationship_type": "creation_relationship|ownership_relationship|hierarchical_relationship|reference_relationship|general_relationship",
            "importance": "high|medium|low"
        }}
    ]
}}

## Guidelines for Working Memory
- **current_task**: Describe what task or activity is currently in progress
- **active_context**: List the most relevant contextual information for the current session
- **immediate_goals**: List the immediate objectives or next steps
- **attention_focus**: Specify what should be the primary focus of attention right now
- **summary_text**: A concise summary of the current working state and immediate priorities

## Guidelines for Object Analysis
When analyzing objects with fields:
- **object_fields**: Extract all important fields and their characteristics
- **object_relationships**: Identify fields that represent relationships to other entities
- **field_importance**: Assess importance based on field name and content
- **relationship_type**: Categorize relationships (creation, ownership, hierarchical, etc.)

## Examples of Good Working Memory Summaries:
- "Currently analyzing Review object with author 'suryanmukul' and text content, focusing on extracting author-content relationships"
- "Processing object with multiple fields including author, text, and metadata, immediate goal is to understand field relationships"
- "Analyzing complex object structure with hierarchical relationships, focusing on entity identification and content extraction"

## Output
Provide only the JSON response, no additional text.
"""
        return prompt
    
    def _parse_llm_response(self, response: str, session_data: Dict[str, Any], session_id: str = None) -> WorkingMemory:
        """Parse LLM response into WorkingMemory."""
        
        try:
            # Try to extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
                
                return WorkingMemory(
                    session_id=data.get('session_id', session_id or 'unknown'),
                    timestamp=datetime.now(),
                    current_task=data.get('current_task', ''),
                    active_context=data.get('active_context', []),
                    immediate_goals=data.get('immediate_goals', []),
                    attention_focus=data.get('attention_focus', ''),
                    memory_hash='',  # Will be set by caller
                    summary_text=data.get('summary_text', ''),
                    object_fields=data.get('object_fields', {}),
                    object_relationships=data.get('object_relationships', []),
                    field_metadata=data.get('field_metadata', {})
                )
            else:
                # Fallback if JSON parsing fails
                return self._fallback_extraction(session_data, session_id)
                
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Fallback if parsing fails
            return self._fallback_extraction(session_data, session_id)
    
    def _fallback_extraction(self, session_data: Dict[str, Any], session_id: str = None) -> WorkingMemory:
        """Fallback extraction when LLM is not available."""
        
        # Basic working memory extraction
        current_task = session_data.get('task', 'unknown task')
        active_context = session_data.get('context', [])
        immediate_goals = session_data.get('goals', [])
        attention_focus = session_data.get('focus', 'general')
        
        # Extract object information if available
        object_fields = {}
        object_relationships = []
        field_metadata = {}
        
        if 'object_info' in session_data:
            object_info = session_data['object_info']
            object_fields = object_info.get('fields', {})
            object_relationships = object_info.get('relationships', [])
            field_metadata = object_info.get('metadata', {})
        
        # Generate basic summary
        summary = f"Currently working on {current_task}"
        if immediate_goals:
            summary += f" with goals: {', '.join(immediate_goals[:2])}"
        
        if object_fields:
            summary += f". Object has {len(object_fields)} fields"
            if object_relationships:
                summary += f" with {len(object_relationships)} relationships"
        
        return WorkingMemory(
            session_id=session_id or 'fallback_session',
            timestamp=datetime.now(),
            current_task=current_task,
            active_context=active_context[:5],  # Limit to 5 contexts
            immediate_goals=immediate_goals[:3],  # Limit to 3 goals
            attention_focus=attention_focus,
            memory_hash='',
            summary_text=summary,
            object_fields=object_fields,
            object_relationships=object_relationships,
            field_metadata=field_metadata
        )
    
    def _add_to_cache(self, memory_hash: str, memory: WorkingMemory):
        """Add working memory to cache with size management."""
        
        if len(self.working_cache) >= self.cache_size:
            # Remove oldest entry (simple FIFO)
            oldest_key = next(iter(self.working_cache))
            del self.working_cache[oldest_key]
        
        self.working_cache[memory_hash] = memory
    
    def get_working_summary(self, session_data: Dict[str, Any], session_id: str = None) -> str:
        """Get a text summary of working memory."""
        memory = self.extract_working_memory(session_data, session_id)
        return memory.summary_text
    
    def get_object_analysis_summary(self, memory: WorkingMemory) -> str:
        """Get a summary of object analysis from working memory."""
        if not memory.object_fields:
            return "No object fields analyzed"
        
        field_summary = f"Object has {len(memory.object_fields)} fields: "
        field_names = list(memory.object_fields.keys())
        field_summary += ", ".join(field_names[:5])  # Show first 5 fields
        
        if len(memory.object_relationships) > 0:
            relationship_summary = f" with {len(memory.object_relationships)} relationships"
            field_summary += relationship_summary
        
        return field_summary
    
    def clear_cache(self):
        """Clear the working memory cache."""
        self.working_cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            'cache_size': len(self.working_cache),
            'max_cache_size': self.cache_size,
            'cache_usage_percentage': (len(self.working_cache) / self.cache_size) * 100
        }

# Global extractor instance
_working_extractor_instance = None

def get_working_extractor(llm_name: str = "gpt-4o-mini") -> WorkingMemoryExtractor:
    """Get the global working memory extractor instance."""
    global _working_extractor_instance
    if _working_extractor_instance is None:
        try:
            _working_extractor_instance = WorkingMemoryExtractor(llm_name)
        except ImportError:
            # Create a fallback extractor that only uses basic extraction
            _working_extractor_instance = FallbackWorkingExtractor()
    return _working_extractor_instance

class FallbackWorkingExtractor:
    """Fallback working memory extractor that doesn't require LLM."""
    
    def __init__(self):
        self.working_cache = {}
    
    def extract_working_memory(self, session_data: Dict[str, Any], session_id: str = None) -> WorkingMemory:
        """Extract working memory using basic methods."""
        session_str = json.dumps(session_data, sort_keys=True)
        if session_id:
            session_str = f"{session_id}: {session_str}"
        
        memory_hash = hashlib.md5(session_str.encode()).hexdigest()
        
        # Check cache first
        if memory_hash in self.working_cache:
            return self.working_cache[memory_hash]
        
        # Use basic extraction
        memory = self._fallback_extraction(session_data, session_id)
        memory.memory_hash = memory_hash
        
        # Cache the result
        self.working_cache[memory_hash] = memory
        return memory
    
    def extract_object_working_memory(self, obj: Any, session_id: str = None) -> WorkingMemory:
        """Extract working memory specifically for object analysis."""
        # Basic object analysis
        object_fields = {}
        object_relationships = []
        
        try:
            for attr_name in dir(obj):
                if attr_name.startswith('_') or callable(getattr(obj, attr_name)):
                    continue
                
                try:
                    attr_value = getattr(obj, attr_name)
                    object_fields[attr_name] = {
                        'name': attr_name,
                        'value': str(attr_value),
                        'type': type(attr_value).__name__
                    }
                    
                    # Simple relationship detection
                    if attr_name.lower() in ['author', 'user', 'creator']:
                        object_relationships.append({
                            'field_name': attr_name,
                            'field_value': str(attr_value),
                            'relationship_type': 'creation_relationship',
                            'importance': 'high'
                        })
                except:
                    continue
        except:
            pass
        
        session_data = {
            'task': f'Analyzing object of type {obj.__class__.__name__}',
            'context': [f'Object Type: {obj.__class__.__name__}', f'Fields: {list(object_fields.keys())}'],
            'goals': ['Understand object structure', 'Extract field relationships'],
            'focus': 'Object field analysis',
            'object_info': {
                'fields': object_fields,
                'relationships': object_relationships,
                'metadata': {'total_fields': len(object_fields)}
            }
        }
        
        return self.extract_working_memory(session_data, session_id)
    
    def _fallback_extraction(self, session_data: Dict[str, Any], session_id: str = None) -> WorkingMemory:
        """Basic working memory extraction without LLM."""
        current_task = session_data.get('task', 'unknown task')
        active_context = session_data.get('context', [])
        immediate_goals = session_data.get('goals', [])
        attention_focus = session_data.get('focus', 'general')
        
        # Extract object information if available
        object_fields = {}
        object_relationships = []
        field_metadata = {}
        
        if 'object_info' in session_data:
            object_info = session_data['object_info']
            object_fields = object_info.get('fields', {})
            object_relationships = object_info.get('relationships', [])
            field_metadata = object_info.get('metadata', {})
        
        summary = f"Currently working on {current_task}"
        if immediate_goals:
            summary += f" with goals: {', '.join(immediate_goals[:2])}"
        
        if object_fields:
            summary += f". Object has {len(object_fields)} fields"
            if object_relationships:
                summary += f" with {len(object_relationships)} relationships"
        
        return WorkingMemory(
            session_id=session_id or 'fallback_session',
            timestamp=datetime.now(),
            current_task=current_task,
            active_context=active_context[:5],
            immediate_goals=immediate_goals[:3],
            attention_focus=attention_focus,
            memory_hash='',
            summary_text=summary,
            object_fields=object_fields,
            object_relationships=object_relationships,
            field_metadata=field_metadata
        )
    
    def get_working_summary(self, session_data: Dict[str, Any], session_id: str = None) -> str:
        """Get a text summary of working memory."""
        memory = self.extract_working_memory(session_data, session_id)
        return memory.summary_text
    
    def get_object_analysis_summary(self, memory: WorkingMemory) -> str:
        """Get a summary of object analysis from working memory."""
        if not memory.object_fields:
            return "No object fields analyzed"
        
        field_summary = f"Object has {len(memory.object_fields)} fields: "
        field_names = list(memory.object_fields.keys())
        field_summary += ", ".join(field_names[:5])
        
        if len(memory.object_relationships) > 0:
            relationship_summary = f" with {len(memory.object_relationships)} relationships"
            field_summary += relationship_summary
        
        return field_summary

# Convenience functions
def extract_working_memory(session_data: Dict[str, Any], session_id: str = None) -> WorkingMemory:
    """Convenience function to extract working memory."""
    extractor = get_working_extractor()
    return extractor.extract_working_memory(session_data, session_id)

def extract_object_working_memory(obj: Any, session_id: str = None) -> WorkingMemory:
    """Convenience function to extract working memory for object analysis."""
    extractor = get_working_extractor()
    return extractor.extract_object_working_memory(obj, session_id)

def get_working_summary(session_data: Dict[str, Any], session_id: str = None) -> str:
    """Convenience function to get working memory summary."""
    extractor = get_working_extractor()
    return extractor.get_working_summary(session_data, session_id)

def get_object_analysis_summary(memory: WorkingMemory) -> str:
    """Convenience function to get object analysis summary."""
    extractor = get_working_extractor()
    return extractor.get_object_analysis_summary(memory)
