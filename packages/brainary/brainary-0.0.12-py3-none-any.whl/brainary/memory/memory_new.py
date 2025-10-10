from collections import defaultdict
from typing import Any, Dict, List, OrderedDict, Tuple

from brainary.core.ops.type_op import TypeOp
from brainary.memory.embedding_model import SimpleEmbeddingModel
from brainary.memory.semantic_memory_extractor import extract_semantic_info, SemanticSummary
from brainary.memory.episodic_memory_extractor import (
    extract_episodic_memory, extract_content_relation_memory, extract_multi_entity_memory, 
    extract_object_episodic_memory,
    EpisodicMemory, ContentRelation
)
from brainary.memory.working_memory_extractor import extract_working_memory, extract_object_working_memory, WorkingMemory
from brainary.memory.retriever import MemoryRetriever, resolve, retrieve_memory, create_contextual_prompt, find_objects_for_parameter


"""
Maybe we can refer to the JVM memory model. For example, we can allocte a seperate area for storing instructions, enabling better instruction scheduling.
┌────────────────────────────┐
│       JVM Memory Model     │
├─────────────┬──────────────┤
│  Heap       │  Stores object instances, arrays, Class objects      │
├─────────────┼──────────────┤
│  Method Area│  Stores class-level metadata, including:             │
│             │  ├─ Class name, superclasses, interfaces             │
│             │  ├─ Constant pool (literals, symbols)                │
│             │  ├─ Method info (including bytecode instructions)    │
│             │  └─ Field info, annotations, access flags, etc.      │
│             │                                                      │
│             │  🔸 Bytecode is stored here!                         │
├─────────────┼──────────────┤
│  Stack      │  Per-thread call stacks (frames for each method call)│
├─────────────┼──────────────┤
│ Native Stack│  Supports native (JNI) method calls                  │
├─────────────┼──────────────┤
│ PC Register │  Program Counter: points to current bytecode instruction │
└─────────────┴──────────────┘
"""

class Heap:
    def __init__(self, max_capacity=100, embedding_model=None, enable_memory_extraction=True):
        self.types = set()
        self.objects = list()
        self.index = defaultdict(list)
        self.embedding_model = embedding_model
        self.enable_memory_extraction = enable_memory_extraction  # Control memory extraction
        self.working_memory = list()  # Store temporal working memories
        self.semantic_memory = list()  # Store semantic summaries
        self.episodic_memory = list()  # Store episodic memories

        
    def add_obj(self, obj:TypeOp):
        self.types.add(obj.__class__)
        self.objects.append(obj)
        self.index[obj.__class__.__name__.split(".")[-1].lower()].append(obj)
        
        # Only extract memory information if enabled
        if not self.enable_memory_extraction:
            return
        
        # 1. Extract working memory information FIRST with object analysis
        try:
            # Use enhanced object analysis for working memory
            working_memory_entry = extract_object_working_memory(obj, f"obj_{len(self.objects)}")
            
            # Add a step experience for object addition to working memory
            # try:
            #     from brainary.memory.working_memory_extractor import StepExperience
            #     from datetime import datetime
            #
            #     object_step = StepExperience(
            #         step_id=f"obj_add_{len(self.objects)}",
            #         step_name=f"Add {obj.__class__.__name__} Object",
            #         step_type="object_management",
            #         execution_method="heap.add_obj()",
            #         input_data={"object_type": obj.__class__.__name__, "object_id": len(self.objects)},
            #         output_result=f"Object {obj.__class__.__name__} added to memory",
            #         success=True,
            #         execution_time=0.0,
            #         learning_insights=[f"Successfully processed {obj.__class__.__name__} object"],
            #         metadata={"operation": "add_obj", "timestamp": datetime.now().isoformat()}
            #     )
            #
            #     if working_memory_entry.step_experiences is None:
            #         working_memory_entry.step_experiences = []
            #     working_memory_entry.step_experiences.append(object_step)
            #
            # except Exception as e:
            #     pass
            
            self.working_memory.append(working_memory_entry)
        except Exception as e:
            # Fallback for working memory extraction
            # Create a basic working memory entry
            try:
                from brainary.memory.working_memory_extractor import WorkingMemory
                from datetime import datetime
                basic_working = WorkingMemory(
                    session_id=f"fallback_session_{len(self.objects)}",
                    timestamp=datetime.now(),
                    current_task=f"Processing {obj.__class__.__name__} object",
                    active_context=[f"Object: {obj.__class__.__name__}"],
                    immediate_goals=["Store object in memory"],
                    attention_focus="Object processing",
                    memory_hash="",
                    summary_text=f"Processing {obj.__class__.__name__} object"
                )
                self.working_memory.append(basic_working)
            except Exception as fallback_e:
                pass
        
        # 2. Extract episodic memory information SECOND with content analysis
        try:
            # Use the enhanced object episodic memory extraction
            episodic_memory_entry = extract_object_episodic_memory(obj, f"episode_{len(self.objects)}")
            
            # Check if we have working memory with step experiences to create a summary
            if self.working_memory:
                latest_working_memory = self.working_memory[-1]
                if hasattr(latest_working_memory, 'step_experiences') and latest_working_memory.step_experiences:
                    try:
                        from brainary.memory.episodic_memory_extractor import EpisodicMemoryExtractor
                        extractor = EpisodicMemoryExtractor()
                        
                        step_summary = extractor.create_step_experience_summary(latest_working_memory.step_experiences)
                        if step_summary:
                            episodic_memory_entry.step_experience_summary = step_summary
                        else:
                            pass
                            
                    except Exception as e:
                        pass
                else:
                    pass
            
            self.episodic_memory.append(episodic_memory_entry)
                
        except Exception as e:
            # Fallback for episodic memory extraction
            # Create a basic episodic memory entry
            try:
                from brainary.memory.episodic_memory_extractor import EpisodicMemory
                from datetime import datetime
                basic_episodic = EpisodicMemory(
                    episode_id=f"fallback_episode_{len(self.objects)}",
                    timestamp=datetime.now(),
                    event_type="object_creation",
                    participants=["system", "memory_manager"],
                    actions=[f"Created {obj.__class__.__name__} object"],
                    outcomes=["Object stored in memory"],
                    emotional_context="neutral",
                    episode_hash="",
                    summary_text=f"Created {obj.__class__.__name__} object and stored in memory"
                )
                
                # Also try to add step experience summary to fallback episodic memory
                if self.working_memory:
                    latest_working_memory = self.working_memory[-1]
                    if hasattr(latest_working_memory, 'step_experiences') and latest_working_memory.step_experiences:
                        try:
                            from brainary.memory.episodic_memory_extractor import EpisodicMemoryExtractor
                            extractor = EpisodicMemoryExtractor()
                            
                            step_summary = extractor.create_step_experience_summary(latest_working_memory.step_experiences)
                            if step_summary:
                                basic_episodic.step_experience_summary = step_summary
                                
                        except Exception as e:
                            pass
                
                self.episodic_memory.append(basic_episodic)
            except Exception as fallback_e:
                pass
        
        # 3. Extract semantic information using LLM LAST
        try:
            semantic_memory_entry = extract_semantic_info(obj, obj.__class__.__name__)
            self.semantic_memory.append(semantic_memory_entry)
        except Exception as e:
            # If semantic extraction fails, create a basic summary
            try:
                # Create basic semantic summary without LLM
                basic_summary = SemanticSummary(
                    key_concepts=[obj.__class__.__name__],
                    relationships=[],
                    context="Basic extraction",
                    importance_score=0.3,
                    semantic_hash="",
                    summary_text=str(obj)[:100] + "..." if len(str(obj)) > 100 else str(obj)
                )
                self.semantic_memory.append(basic_summary)
            except Exception as fallback_e:
                # Last resort: create minimal semantic summary
                try:
                    from brainary.memory.semantic_memory_extractor import SemanticSummary
                    minimal_summary = SemanticSummary(
                        key_concepts=[obj.__class__.__name__],
                        relationships=[],
                        context="Minimal extraction",
                        importance_score=0.1,
                        semantic_hash="",
                        summary_text=f"Object of type {obj.__class__.__name__}"
                    )
                    self.semantic_memory.append(minimal_summary)
                except Exception as minimal_e:
                    pass
    
    def add_content_relation(self, 
                           content: str, 
                           entity_name: str, 
                           entity_type: str = "user",
                           content_type: str = "message",
                           relationship_type: str = "created",
                           episode_id: str = None,
                           llm_context: Dict[str, Any] = None,
                           metadata: Dict[str, Any] = None):
        """
        Add content-entity relationship to episodic memory.
        
        Args:
            content: The content text or data
            entity_name: The name/identifier of the entity
            entity_type: Type of entity (e.g., "user", "author", "system", "agent", "llm")
            content_type: Type of content (e.g., "message", "review", "action", "comment", "llm_response")
            relationship_type: Type of relationship (e.g., "created", "modified", "responded_to", "llm_communication")
            episode_id: Optional unique identifier for the episode
            llm_context: LLM-specific context (model, temperature, tokens, etc.)
            metadata: Additional metadata for the relationship
        """
        # Only extract memory information if enabled
        if not self.enable_memory_extraction:
            return
            
        try:
            # Extract episodic memory with content-entity relations
            episodic_memory_entry = extract_content_relation_memory(
                content=content,
                entity_name=entity_name,
                entity_type=entity_type,
                content_type=content_type,
                relationship_type=relationship_type,
                episode_id=episode_id,
                llm_context=llm_context,
                metadata=metadata
            )
            self.episodic_memory.append(episodic_memory_entry)
        except Exception as e:
            # Fallback for episodic memory extraction
            pass
    
    def add_llm_communication(self, 
                             source_llm: str, 
                             target_llm: str, 
                             communication_type: str, 
                             message: str, 
                             context: Dict[str, Any] = None, 
                             episode_id: str = None):
        """
        Add LLM-to-LLM communication to episodic memory.
        
        Args:
            source_llm: Name/identifier of the source LLM
            target_llm: Name/identifier of the target LLM
            communication_type: Type of communication (e.g., "query", "response", "instruction", "feedback")
            message: The communication message content
            context: Additional context about the communication
            episode_id: Optional unique identifier for the episode
        """
        # Only extract memory information if enabled
        if not self.enable_memory_extraction:
            return
            
        try:
            from brainary.memory.episodic_memory_extractor import extract_llm_communication_memory
            episodic_memory_entry = extract_llm_communication_memory(
                source_llm=source_llm,
                target_llm=target_llm,
                communication_type=communication_type,
                message=message,
                context=context,
                episode_id=episode_id
            )
            self.episodic_memory.append(episodic_memory_entry)
        except Exception as e:
            # Fallback for episodic memory extraction
            pass
    
    def add_multi_entity_interaction(self, entities: List[Dict[str, Any]], episode_id: str = None):
        """
        Add multi-entity interaction to episodic memory.
        
        Args:
            entities: List of entity dictionaries with their content and relationships
            episode_id: Optional unique identifier for the episode
        """
        try:
            # Extract episodic memory with multi-entity relations
            episodic_memory_entry = extract_multi_entity_memory(entities, episode_id)
            self.episodic_memory.append(episodic_memory_entry)
        except Exception as e:
            # Fallback for episodic memory extraction
            pass
    
    def get_content_relations(self, entity_name: str = None, entity_type: str = None) -> list:
        """
        Get content relations from episodic memory.
        
        Args:
            entity_name: Optional entity name to filter by
            entity_type: Optional entity type to filter by
            
        Returns:
            List of content relations
        """
        content_relations = []
        for memory in self.episodic_memory:
            if memory.content_relations:
                for relation in memory.content_relations:
                    if entity_name is None or relation.entity_name == entity_name:
                        if entity_type is None or relation.entity_type == entity_type:
                            content_relations.append(relation)
        return content_relations
    
    def get_entity_summary(self, entity_name: str, entity_type: str = None) -> str:
        """
        Get a summary of all content by a specific entity.
        
        Args:
            entity_name: Name of the entity
            entity_type: Optional entity type to filter by
            
        Returns:
            Summary string of the entity's contributions
        """
        content_relations = self.get_content_relations(entity_name, entity_type)
        if not content_relations:
            return f"No content found for entity '{entity_name}'"
        
        summaries = []
        for relation in content_relations:
            summary = f"{relation.content_type} with {relation.sentiment} sentiment"
            if relation.content_summary:
                summary += f": {relation.content_summary}"
            summaries.append(summary)
        
        return f"Entity '{entity_name}' has {len(content_relations)} contributions: " + "; ".join(summaries)
    
    # Backward compatibility methods
    def add_author_comment(self, text: str, author: str, content_type: str = "comment", episode_id: str = None):
        """Backward compatibility method for author-comment relationships."""
        return self.add_content_relation(
            content=text,
            entity_name=author,
            entity_type="author",
            content_type=content_type,
            relationship_type="created",
            episode_id=episode_id
        )
    
    def get_author_relations(self, author_name: str = None) -> list:
        """Backward compatibility method for author relations."""
        return self.get_content_relations(author_name, "author")
    
    def _extract_object_content_episodic(self, obj: Any, episode_id: str = None):
        """
        Extract episodic memory with content-entity relationships from an object.
        
        Args:
            obj: The object to analyze
            episode_id: Optional episode ID
            
        Returns:
            EpisodicMemory with content relations, or None if no content found
        """
        try:
            # Analyze object for content and entity fields
            content_info = self._analyze_object_content(obj)
            
            if not content_info['has_content']:
                return None  # No content to extract
            
            # Extract episodic memory with content relations
            episodic_memory = extract_content_relation_memory(
                content=content_info['content'],
                entity_name=content_info['entity_name'],
                entity_type=content_info['entity_type'],
                content_type=content_info['content_type'],
                relationship_type="created",
                episode_id=episode_id,
                metadata=content_info['metadata']
            )
            
            return episodic_memory
            
        except Exception as e:
            return None
    
    def _analyze_object_content(self, obj: Any) -> Dict[str, Any]:
        """
        Analyze an object to extract content and entity information.
        
        Args:
            obj: The object to analyze
            
        Returns:
            Dictionary with content analysis results
        """
        content_info = {
            'has_content': False,
            'content': '',
            'entity_name': '',
            'entity_type': 'user',
            'content_type': 'message',
            'metadata': {}
        }
        
        try:
            # Get all attributes of the object
            for attr_name in dir(obj):
                if attr_name.startswith('_') or callable(getattr(obj, attr_name)):
                    continue
                
                try:
                    attr_value = getattr(obj, attr_name)
                    
                    # Look for content fields
                    if attr_name.lower() in ['text', 'content', 'message', 'description', 'body']:
                        if attr_value and str(attr_value).strip():
                            content_info['content'] = str(attr_value)
                            content_info['has_content'] = True
                            content_info['content_type'] = self._determine_content_type(attr_name, attr_value)
                    
                    # Look for entity fields
                    elif attr_name.lower() in ['author', 'user', 'creator', 'owner', 'writer']:
                        if attr_value and str(attr_value).strip():
                            content_info['entity_name'] = str(attr_value)
                            content_info['entity_type'] = self._determine_entity_type(attr_name)
                    
                    # Collect metadata
                    elif attr_value:
                        content_info['metadata'][attr_name] = str(attr_value)
                        
                except Exception:
                    continue
            
            # If we found content but no entity, try to infer entity
            if content_info['has_content'] and not content_info['entity_name']:
                content_info['entity_name'] = 'unknown_user'
                content_info['entity_type'] = 'user'
            
            # If we found entity but no content, try to infer content
            if content_info['entity_name'] and not content_info['has_content']:
                content_info['content'] = f"Content from {content_info['entity_name']}"
                content_info['has_content'] = True
                content_info['content_type'] = 'message'
            
        except Exception as e:
            pass
        
        return content_info
    
    def _determine_content_type(self, field_name: str, field_value: Any) -> str:
        """Determine the type of content based on field name and value."""
        field_name_lower = field_name.lower()
        
        if 'text' in field_name_lower:
            return 'text'
        elif 'content' in field_name_lower:
            return 'content'
        elif 'message' in field_name_lower:
            return 'message'
        elif 'description' in field_name_lower:
            return 'description'
        elif 'body' in field_name_lower:
            return 'body'
        elif 'review' in field_name_lower or 'comment' in field_name_lower:
            return 'review'
        else:
            return 'content'
    
    def _determine_entity_type(self, field_name: str) -> str:
        """Determine the type of entity based on field name."""
        field_name_lower = field_name.lower()
        
        if 'author' in field_name_lower:
            return 'author'
        elif 'user' in field_name_lower:
            return 'user'
        elif 'creator' in field_name_lower:
            return 'creator'
        elif 'owner' in field_name_lower:
            return 'owner'
        elif 'writer' in field_name_lower:
            return 'writer'
        else:
            return 'user'
    

    
    def get_author_summary(self, author_name: str) -> str:
        """Backward compatibility method for author summary."""
        return self.get_entity_summary(author_name, "author")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about all memory types."""
        return {
            'objects': len(self.objects),
            'types': len(self.types),
            'working_memory': len(self.working_memory),
            'episodic_memory': len(self.episodic_memory),
            'semantic_memory': len(self.semantic_memory),
            'working_memory_summaries': [wm.summary_text for wm in self.working_memory[-3:]],  # Last 3
            'episodic_memory_summaries': [em.summary_text for em in self.episodic_memory[-3:]],  # Last 3
            'semantic_memory_summaries': [sm.summary_text for sm in self.semantic_memory[-3:]]   # Last 3
        }
    
    def display_memory_status(self):
        """Display the current status of all memory types."""
        stats = self.get_memory_stats()
        return stats

    def display_types(self):
        return "\n\n".join(t.type_repr() for t in self.types)



    def resolve(self, ref: str, top_k=1, memory_types=None, use_memory=True, use_semantic=True, task_type=None) -> str:
        """
        Enhanced resolve method that delegates to the MemoryRetriever.
        
        Args:
            ref: Reference string to resolve (object name, class name, or description)
            top_k: Number of top results to return (default: 1)
            memory_types: List of memory types to search ["working", "episodic", "semantic", "all"] (default: ["all"])
            use_memory: Whether to use memory-based retrieval (default: True)
            use_semantic: Whether to use semantic search (default: True)
            task_type: Type of task for context-aware retrieval (default: None)
            
        Returns:
            Resolved object or None
            
        Examples:
            # Basic resolution
            obj = heap.resolve("movie")
            
            # Memory-specific resolution
            obj = heap.resolve("review", memory_types=["episodic"])
            
            # Task-aware resolution
            obj = heap.resolve("user_input", task_type="parameter_recovery")
            
            # Semantic-only resolution
            obj = heap.resolve("sci-fi film", use_memory=False, use_semantic=True)
            
            # Memory-only resolution
            obj = heap.resolve("author", use_memory=True, use_semantic=False)
        """
        return resolve(self, ref, top_k, memory_types, use_memory, use_semantic, task_type)
    
    def retrieve_memory(self, query, memory_types=None, target_object=None, top_k=1, task_type=None):
        """Delegate to the MemoryRetriever class."""
        return retrieve_memory(self, query, memory_types, target_object, top_k, task_type)
    
    def create_contextual_prompt(self, query, target_object=None, memory_types=None, task_type=None):
        """Delegate to the MemoryRetriever class."""
        return create_contextual_prompt(self, query, target_object, memory_types, task_type)
    
    def find_objects_for_parameter(self, param_name: str, task_type: str = "parameter_recovery"):
        """Delegate to the MemoryRetriever class."""
        return find_objects_for_parameter(self, param_name, task_type)
    
    def store_action_memory(self, action_type: str, action_instruction: str, action_params: list, 
                           result: str = None, entity_name: str = "system", entity_type: str = "agent"):
        """
        Store episodic memory for an action execution.
        This method can be used by external modules like vm.py to create action memories.
        
        Args:
            action_type: Type of action (e.g., "ActionOp", "summarize", "examine")
            action_instruction: The instruction/description of the action
            action_params: List of parameter names used in the action
            result: The result/output of the action execution
            entity_name: Name of the entity performing the action
            entity_type: Type of the entity (e.g., "agent", "user", "system")
            
        Returns:
            The created episodic memory object
        """
        # Only extract memory information if enabled
        if not self.enable_memory_extraction:
            return None
            
        try:
            from brainary.memory.episodic_memory_extractor import extract_content_relation_memory
            from datetime import datetime
            
            # First, collect existing step experiences from working memory
            step_experiences_to_summarize = []
            try:
                if self.working_memory:
                    # Use the most recent working memory entry
                    latest_working_memory = self.working_memory[-1]
                    
                    # Collect existing step experiences for summary
                    if hasattr(latest_working_memory, 'step_experiences') and latest_working_memory.step_experiences:
                        step_experiences_to_summarize = latest_working_memory.step_experiences
                        
                        # Only add new step experience if we don't have any yet
                        if len(step_experiences_to_summarize) == 0:
                            from brainary.memory.retriever import add_step_experience
                            
                            step_experience = add_step_experience(
                                heap=self,
                                step_name=f"Action: {action_instruction[:50]}...",
                                step_type="action",
                                execution_method=f"{action_type}.execute()",
                                input_data={
                                    "instruction": action_instruction,
                                    "parameters": action_params,
                                    "entity": entity_name
                                },
                                output_result=str(result) if result else None,
                                success=True,
                                execution_time=0.0,  # Will be updated by caller if timing is available
                                learning_insights=[
                                    f"Action '{action_type}' executed successfully",
                                    f"Used {len(action_params)} parameters",
                                    f"Result: {str(result)[:100] if result else 'None'}"
                                ],
                                metadata={
                                    "operation_type": action_type,
                                    "timestamp": datetime.now().isoformat(),
                                    "memory_type": "episodic"
                                }
                            )
                            
                            if step_experience:
                                # Update the list to include the new experience
                                step_experiences_to_summarize = latest_working_memory.step_experiences
                    else:
                        step_experiences_to_summarize = []
                        
            except Exception as e:
                step_experiences_to_summarize = []
            
            # Create episodic memory for the action
            action_memory = extract_content_relation_memory(
                content=str(result) if result else "Action executed",
                entity_name=entity_name,
                entity_type=entity_type,
                content_type="action_execution",
                relationship_type="performed",
                episode_id=f"action_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                metadata={
                    "action_type": action_type,
                    "action_instruction": action_instruction,
                    "action_params": action_params,
                    "result": str(result) if result else None
                }
            )
            
            # Create step experience summary if we have step experiences
            if step_experiences_to_summarize:
                try:
                    from brainary.memory.episodic_memory_extractor import EpisodicMemoryExtractor
                    extractor = EpisodicMemoryExtractor()
                    
                    step_summary = extractor.create_step_experience_summary(step_experiences_to_summarize)
                    if step_summary:
                        action_memory.step_experience_summary = step_summary
                    else:
                        pass
                        
                except Exception as e:
                    pass
            
            # Add to episodic memory
            self.episodic_memory.append(action_memory)
            return action_memory
            
        except Exception as e:
            return None
    
    def track_step_experience(self, step_name: str, step_type: str, execution_method: str,
                            input_data: Dict[str, Any], output_result: Any, success: bool,
                            execution_time: float = 0.0, error_message: str = None,
                            performance_metrics: Dict[str, Any] = None,
                            learning_insights: List[str] = None,
                            metadata: Dict[str, Any] = None) -> Any:
        """
        Track a step experience in working memory.
        This method can be used by external modules to track their execution steps.
        
        Args:
            step_name: Name of the step
            step_type: Type of step (action, examine, extract, analyze, etc.)
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
            The created StepExperience object or None if failed
        """
        try:
            from brainary.memory.retriever import add_step_experience
            
            if not self.working_memory:
                return None
            
            step_experience = add_step_experience(
                heap=self,
                step_name=step_name,
                step_type=step_type,
                execution_method=execution_method,
                input_data=input_data,
                output_result=output_result,
                success=success,
                execution_time=execution_time,
                error_message=error_message,
                performance_metrics=performance_metrics,
                learning_insights=learning_insights,
                metadata=metadata
            )
            
            return step_experience
            
        except Exception as e:
            return None
    
    def get_execution_insights(self) -> Dict[str, Any]:
        """
        Get execution insights from working memory.
        
        Returns:
            Dictionary containing execution insights
        """
        try:
            from brainary.memory.retriever import get_execution_insights
            return get_execution_insights(self)
        except Exception as e:
            return {"message": "Failed to retrieve execution insights"}
    
    def create_semantic_experience_summary(self) -> Any:
        """
        Create very high-level semantic summary and abstracted insights from all step experiences.
        
        Returns:
            SemanticExperienceSummary containing high-level insights
        """
        try:
            from brainary.memory.semantic_memory_extractor import SemanticMemoryExtractor
            extractor = SemanticMemoryExtractor()
            
            # Get all memories for analysis
            episodic_memories = self.episodic_memory
            working_memories = self.working_memory
            
            if not episodic_memories and not working_memories:
                return None
            
            # Create semantic experience summary
            semantic_summary = extractor.create_semantic_experience_summary(episodic_memories, working_memories)
            
            return semantic_summary
            
        except Exception as e:
            return None
    
    def add_step_experience_to_working_memory(self, step_name: str, step_type: str, execution_method: str,
                                            input_data: Dict[str, Any], output_result: Any, success: bool,
                                            execution_time: float = 0.0, error_message: str = None,
                                            performance_metrics: Dict[str, Any] = None,
                                            learning_insights: List[str] = None,
                                            metadata: Dict[str, Any] = None) -> Any:
        """
        Add a step experience directly to the current working memory.
        This is useful for tracking execution steps without going through the retriever.
        
        Args:
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
            The created StepExperience object, or None if failed
        """
        # Only extract memory information if enabled
        if not self.enable_memory_extraction:
            return None
            
        try:
            if not self.working_memory:
                return None
            
            from brainary.memory.working_memory_extractor import StepExperience
            from datetime import datetime
            
            # Create step experience
            step_experience = StepExperience(
                step_id=f"step_{len(self.working_memory[-1].step_experiences) + 1 if self.working_memory[-1].step_experiences else 1}",
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
            
            # Add to working memory
            latest_working_memory = self.working_memory[-1]
            if latest_working_memory.step_experiences is None:
                latest_working_memory.step_experiences = []
            
            latest_working_memory.step_experiences.append(step_experience)
            
            # Update execution summary
            if latest_working_memory.execution_summary is None:
                latest_working_memory.execution_summary = {
                    "total_steps": 0,
                    "successful_steps": 0,
                    "failed_steps": 0,
                    "total_execution_time": 0.0
                }
            
            summary = latest_working_memory.execution_summary
            summary["total_steps"] += 1
            if success:
                summary["successful_steps"] += 1
            else:
                summary["failed_steps"] += 1
            summary["total_execution_time"] += execution_time
            
            return step_experience
            
        except Exception as e:
            return None

    def _semantic_search(self, query: str, top_k=1):
        """Search STM + LTM for best semantic match to query."""
        all_entries = self.objects  # List[(key, value)]
        if not all_entries:
            return None
        
        return all_entries[-1]

        # Embed query
        query_emb = self.embedding_model.embed(query)

        # Score by similarity
        scored = []
        for key, value in all_entries:
            score = self.embedding_model.similarity(query_emb, key)
            scored.append((score, value))

        scored.sort(reverse=True)
        return scored[0][1] if scored else None
    
class Stack:
    def __init__(self, max_capacity=100, embedding_model=None):
        self.objects = OrderedDict()
        self.embedding_model = embedding_model
        
    def add_obj(self, obj_name:str, obj_repr:str):
        self.objects[obj_name.lower()] = obj_repr

    def resolve(self, ref: str, top_k=1) -> str:
        # 1. Try exact match
        obj = self.objects.get(ref.lower())
        if obj is not None:
            return obj

        # 2. Semantic search
        if self.embedding_model:
            return self._semantic_search(ref, top_k=top_k)

        return None

    def _semantic_search(self, query: str, top_k=1):
        """Search STM + LTM for best semantic match to query."""
        all_entries = self.objects.items()  # List[(key, value)]
        if not all_entries:
            return None
        
        return all_entries[0][1]

        # Embed query
        query_emb = self.embedding_model.embed(query)

        # Score by similarity
        scored = []
        for key, value in all_entries:
            score = self.embedding_model.similarity(query_emb, key)
            scored.append((score, value))

        scored.sort(reverse=True)
        return scored[0][1] if scored else None

