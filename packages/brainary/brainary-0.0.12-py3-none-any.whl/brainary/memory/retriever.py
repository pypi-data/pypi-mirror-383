#!/usr/bin/env python3
"""
Memory Retrieval System

This module provides comprehensive memory retrieval capabilities including
enhanced object resolution, memory-based search, and contextual retrieval.
"""

from typing import List, Any, Dict, Optional
from datetime import datetime, timedelta


class MemoryRetriever:
    """
    A comprehensive memory retrieval system that can search across different memory types
    and provide enhanced object resolution capabilities.
    """
    
    def __init__(self, heap):
        """
        Initialize the memory retriever with a heap instance.
        
        Args:
            heap: The heap instance containing all memory types
        """
        self.heap = heap
    
    def resolve(self, ref: str, top_k: int = 1, memory_types: Optional[List[str]] = None, 
                use_memory: bool = True, use_semantic: bool = True, task_type: Optional[str] = None) -> Any:
        """
        Enhanced resolve method with comprehensive memory retrieval API.
        
        This method provides a flexible API for object resolution with multiple strategies:
        1. Exact match (by class name, object name, title)
        2. Semantic search (if embedding model available)
        3. Memory-based retrieval (across working, episodic, semantic memory)
        
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
            obj = retriever.resolve("movie")
            
            # Memory-specific resolution
            obj = retriever.resolve("review", memory_types=["episodic"])
            
            # Task-aware resolution
            obj = retriever.resolve("user_input", task_type="parameter_recovery")
            
            # Semantic-only resolution
            obj = retriever.resolve("sci-fi film", use_memory=False, use_semantic=True)
            
            # Memory-only resolution
            obj = retriever.resolve("author", use_memory=True, use_semantic=False)
        """
        # 1. Try exact match first - check by class name
        if ref.lower() in self.heap.index:
            objects = self.heap.index[ref.lower()]
            if objects:
                return objects[-1]  # Return the most recent object of this type
        
        # 2. Try exact match by object name/title
        for obj in self.heap.objects:
            if hasattr(obj, 'name') and obj.name == ref:
                return obj
            if hasattr(obj, 'title') and obj.title == ref:
                return obj
            if hasattr(obj, '__class__') and obj.__class__.__name__ == ref:
                return obj

        # 3. Try semantic search if enabled and embedding model is available
        if use_semantic and self.heap.embedding_model:
            semantic_result = self._semantic_search(ref, top_k=top_k)
            if semantic_result is not None:
                return semantic_result
        
        # 4. Try memory-based retrieval if enabled
        if use_memory:
            found_objects = self._find_objects_in_memory_enhanced(ref, memory_types, task_type)
            if found_objects:
                return found_objects[0]  # Return the first match
        
        return None
    
    def _find_objects_in_memory_enhanced(self, ref: str, memory_types: Optional[List[str]] = None, 
                                        task_type: Optional[str] = None) -> List[Any]:
        """
        Enhanced memory-based object finding with configurable memory types and task context.
        
        Args:
            ref: Reference string to search for
            memory_types: List of memory types to search ["working", "episodic", "semantic", "all"]
            task_type: Type of task for context-aware retrieval
            
        Returns:
            List of matching objects
        """
        if memory_types is None:
            memory_types = ["all"]
        
        if "all" in memory_types:
            memory_types = ["working", "episodic", "semantic"]
        
        found_objects = []
        
        # Search in working memory
        if "working" in memory_types and self.heap.working_memory:
            for memory in self.heap.working_memory:
                if hasattr(memory, 'object_fields') and memory.object_fields:
                    for field_name, field_info in memory.object_fields.items():
                        if ref.lower() in field_name.lower() or ref.lower() in str(field_info).lower():
                            value = field_info.get('value', field_info)
                            if value and value not in found_objects:
                                found_objects.append(value)
                
                # Check task relevance if task_type is provided
                if task_type and hasattr(memory, 'current_task'):
                    if task_type.lower() in memory.current_task.lower():
                        # Add objects from this memory context
                        for obj in self.heap.objects:
                            if obj not in found_objects:
                                found_objects.append(obj)
        
        # Search in episodic memory
        if "episodic" in memory_types and self.heap.episodic_memory:
            for memory in self.heap.episodic_memory:
                if memory.content_relations:
                    for relation in memory.content_relations:
                        # Check if reference matches content type or entity type
                        if ref.lower() in relation.content_type.lower() or ref.lower() in relation.entity_type.lower():
                            # Try to find matching objects in heap
                            for obj in self.heap.objects:
                                if hasattr(obj, 'name') and ref.lower() in obj.name.lower():
                                    if obj not in found_objects:
                                        found_objects.append(obj)
                                elif hasattr(obj, 'title') and ref.lower() in obj.title.lower():
                                    if obj not in found_objects:
                                        found_objects.append(obj)
                        
                        # Check mentioned entities
                        if relation.mentioned_entities:
                            for entity in relation.mentioned_entities:
                                if ref.lower() in entity.lower():
                                    # Try to find matching objects in heap
                                    for obj in self.heap.objects:
                                        if hasattr(obj, 'name') and entity.lower() in obj.name.lower():
                                            if obj not in found_objects:
                                                found_objects.append(obj)
                                        elif hasattr(obj, 'title') and entity.lower() in obj.title.lower():
                                            if obj not in found_objects:
                                                found_objects.append(obj)
                        
                        # Check task relevance
                        if task_type and task_type.lower() in relation.content_type.lower():
                            for obj in self.heap.objects:
                                if obj not in found_objects:
                                    found_objects.append(obj)
        
        # Search in semantic memory
        if "semantic" in memory_types and self.heap.semantic_memory:
            for memory in self.heap.semantic_memory:
                if memory.key_concepts:
                    for concept in memory.key_concepts:
                        if ref.lower() in concept.lower():
                            # Try to find matching objects by class name
                            for obj in self.heap.objects:
                                if hasattr(obj, '__class__') and ref.lower() in obj.__class__.__name__.lower():
                                    if obj not in found_objects:
                                        found_objects.append(obj)
        
        return found_objects
    
    def _semantic_search(self, query: str, top_k: int = 1) -> Any:
        """Search for best semantic match to query."""
        all_entries = self.heap.objects
        if not all_entries:
            return None
        
        return all_entries[-1]  # Return last object as fallback
    
    def _find_objects_in_memory(self, ref: str) -> List[Any]:
        """
        Find objects in memory that match the reference.
        
        Args:
            ref: Reference string to search for
            
        Returns:
            List of matching objects
        """
        found_objects = []
        
        # Search in working memory
        if self.heap.working_memory:
            for memory in self.heap.working_memory:
                if hasattr(memory, 'object_fields') and memory.object_fields:
                    for field_name, field_info in memory.object_fields.items():
                        if ref.lower() in field_name.lower() or ref.lower() in str(field_info).lower():
                            value = field_info.get('value', field_info)
                            if value and value not in found_objects:
                                found_objects.append(value)
        
        # Search in episodic memory
        if self.heap.episodic_memory:
            for memory in self.heap.episodic_memory:
                if memory.content_relations:
                    for relation in memory.content_relations:
                        # Check if reference matches content type or entity type
                        if ref.lower() in relation.content_type.lower() or ref.lower() in relation.entity_type.lower():
                            # Try to find matching objects in heap
                            for obj in self.heap.objects:
                                if hasattr(obj, 'name') and ref.lower() in obj.name.lower():
                                    if obj not in found_objects:
                                        found_objects.append(obj)
                                elif hasattr(obj, 'title') and ref.lower() in obj.title.lower():
                                    if obj not in found_objects:
                                        found_objects.append(obj)
                        
                        # Check mentioned entities
                        if relation.mentioned_entities:
                            for entity in relation.mentioned_entities:
                                if ref.lower() in entity.lower():
                                    # Try to find matching objects in heap
                                    for obj in self.heap.objects:
                                        if hasattr(obj, 'name') and entity.lower() in obj.name.lower():
                                            if obj not in found_objects:
                                                found_objects.append(obj)
                                        elif hasattr(obj, 'title') and entity.lower() in obj.title.lower():
                                            if obj not in found_objects:
                                                found_objects.append(obj)
        
        # Search in semantic memory
        if self.heap.semantic_memory:
            for memory in self.heap.semantic_memory:
                if memory.key_concepts:
                    for concept in memory.key_concepts:
                        if ref.lower() in concept.lower():
                            # Try to find matching objects by class name
                            for obj in self.heap.objects:
                                if hasattr(obj, '__class__') and ref.lower() in obj.__class__.__name__.lower():
                                    if obj not in found_objects:
                                        found_objects.append(obj)
        
        return found_objects
    
    def retrieve_memory(self, query: str, memory_types: Optional[List[str]] = None, 
                       target_object=None, top_k: int = 1, task_type: Optional[str] = None) -> Dict[str, List]:
        """
        General memory retrieval framework that can retrieve from multiple memory types.
        
        Args:
            query: The query or context for retrieval
            memory_types: List of memory types to search ("working", "episodic", "semantic", "all")
            target_object: The target object for context-aware retrieval
            top_k: Number of top results to return per memory type
            task_type: Type of task for context-aware retrieval
            
        Returns:
            Dict containing retrieved memories organized by type
        """
        if memory_types is None:
            memory_types = ["all"]
        
        if "all" in memory_types:
            memory_types = ["working", "episodic", "semantic"]
        
        results = {}
        
        # Retrieve from each requested memory type
        for memory_type in memory_types:
            if memory_type == "working":
                results["working"] = self._retrieve_working_memory(query, target_object, top_k, task_type)
            elif memory_type == "episodic":
                results["episodic"] = self._retrieve_episodic_memory(query, target_object, top_k, task_type)
            elif memory_type == "semantic":
                results["semantic"] = self._retrieve_semantic_memory(query, target_object, top_k, task_type)
        
        return results
    
    def _retrieve_working_memory(self, query: str, target_object=None, top_k: int = 5, 
                                task_type: Optional[str] = None) -> List:
        """
        Retrieve relevant working memory entries.
        
        Args:
            query: The query or context
            target_object: Target object for context
            top_k: Number of results to return
            task_type: Type of task
            
        Returns:
            List of relevant working memory entries
        """
        if not self.heap.working_memory:
            return []
        
        relevant_memories = []
        
        for memory in self.heap.working_memory:
            relevance_score = 0
            
            # 1. Check current task relevance
            if task_type and task_type.lower() in memory.current_task.lower():
                relevance_score += 3
            
            # 2. Check active context relevance
            if memory.active_context:
                for context in memory.active_context:
                    if query.lower() in context.lower():
                        relevance_score += 2
                    if target_object and target_object.__class__.__name__.lower() in context.lower():
                        relevance_score += 2
            
            # 3. Check attention focus relevance
            if memory.attention_focus and query.lower() in memory.attention_focus.lower():
                relevance_score += 2
            
            # 4. Check immediate goals relevance
            if memory.immediate_goals:
                for goal in memory.immediate_goals:
                    if query.lower() in goal.lower():
                        relevance_score += 1
            
            # 5. Check object field relationships
            if memory.object_relationships and target_object:
                for rel in memory.object_relationships:
                    if hasattr(target_object, rel.get('field_name', '')):
                        relevance_score += 1
            
            # 6. Temporal relevance (working memory is short-term)
            if memory.timestamp:
                time_diff = datetime.now() - memory.timestamp
                if time_diff < timedelta(minutes=30):
                    relevance_score += 3
                elif time_diff < timedelta(hours=2):
                    relevance_score += 2
                elif time_diff < timedelta(hours=6):
                    relevance_score += 1
            
            if relevance_score > 0:
                relevant_memories.append((relevance_score, memory))
        
        # Sort by relevance and return top_k
        relevant_memories.sort(key=lambda x: x[0], reverse=True)
        return [memory for score, memory in relevant_memories[:top_k]]
    
    def _retrieve_episodic_memory(self, query: str, target_object=None, top_k: int = 5, 
                                 task_type: Optional[str] = None) -> List:
        """
        Retrieve relevant episodic memories.
        
        Args:
            query: The query or context
            target_object: Target object for context
            top_k: Number of results to return
            task_type: Type of task
            
        Returns:
            List of relevant episodic memories
        """
        if not self.heap.episodic_memory:
            return []
        
        relevant_memories = []
        
        for memory in self.heap.episodic_memory:
            relevance_score = 0
            
            # 1. Check event type relevance
            if task_type and task_type.lower() in memory.event_type.lower():
                relevance_score += 3
            
            # 2. Check participants relevance
            if query.lower() in " ".join(memory.participants).lower():
                relevance_score += 2
            
            # 3. Check actions relevance
            if memory.actions:
                for action in memory.actions:
                    if query.lower() in action.lower():
                        relevance_score += 2
            
            # 4. Check content relations
            if memory.content_relations:
                for relation in memory.content_relations:
                    # Check content type relevance
                    if query.lower() in relation.content_type.lower():
                        relevance_score += 2
                    
                    # Check content summary relevance
                    if query.lower() in relation.content_summary.lower():
                        relevance_score += 3
                    
                    # Check entity relevance
                    if target_object and relation.mentioned_entities:
                        target_name = getattr(target_object, 'name', None) or getattr(target_object, 'title', None)
                        if target_name:
                            target_name_lower = target_name.lower()
                            for entity in relation.mentioned_entities:
                                if target_name_lower in entity.lower() or entity.lower() in target_name_lower:
                                    relevance_score += 4
                    
                    # Check sentiment relevance
                    if relation.sentiment in ["positive", "negative"]:
                        relevance_score += 1
            
            # 5. Check summary text relevance
            if query.lower() in memory.summary_text.lower():
                relevance_score += 2
            
            # 6. Temporal relevance
            if memory.timestamp:
                time_diff = datetime.now() - memory.timestamp
                if time_diff < timedelta(hours=1):
                    relevance_score += 2
                elif time_diff < timedelta(days=1):
                    relevance_score += 1
            
            if relevance_score > 0:
                relevant_memories.append((relevance_score, memory))
        
        # Sort by relevance and return top_k
        relevant_memories.sort(key=lambda x: x[0], reverse=True)
        return [memory for score, memory in relevant_memories[:top_k]]
    
    def _retrieve_semantic_memory(self, query: str, target_object=None, top_k: int = 5, 
                                 task_type: Optional[str] = None) -> List:
        """
        Retrieve relevant semantic memories.
        
        Args:
            query: The query or context
            target_object: Target object for context
            top_k: Number of results to return
            task_type: Type of task
            
        Returns:
            List of relevant semantic memories
        """
        if not self.heap.semantic_memory:
            return []
        
        relevant_memories = []
        
        for memory in self.heap.semantic_memory:
            relevance_score = 0
            
            # 1. Check key concepts relevance
            if memory.key_concepts:
                for concept in memory.key_concepts:
                    if query.lower() in concept.lower():
                        relevance_score += 3
                    if target_object and target_object.__class__.__name__.lower() in concept.lower():
                        relevance_score += 2
            
            # 2. Check relationships relevance
            if memory.relationships:
                for rel in memory.relationships:
                    if query.lower() in str(rel).lower():
                        relevance_score += 2
            
            # 3. Check context relevance
            if memory.context and query.lower() in memory.context.lower():
                relevance_score += 2
            
            # 4. Check summary text relevance
            if query.lower() in memory.summary_text.lower():
                relevance_score += 3
            
            # 5. Check importance score
            relevance_score += memory.importance_score
            
            if relevance_score > 0:
                relevant_memories.append((relevance_score, memory))
        
        # Sort by relevance and return top_k
        relevant_memories.sort(key=lambda x: x[0], reverse=True)
        return [memory for score, memory in relevant_memories[:top_k]]
    
    def create_contextual_prompt(self, query: str, target_object=None, memory_types: Optional[List[str]] = None, 
                                task_type: Optional[str] = None) -> str:
        """
        Create a contextual prompt using retrieved memories from specified memory types.
        
        Args:
            query: The base query or prompt
            target_object: The target object for context
            memory_types: List of memory types to use ("working", "episodic", "semantic", "all")
            task_type: Type of task for context
            
        Returns:
            Enhanced prompt with memory context
        """
        # Retrieve relevant memories
        retrieved_memories = self.retrieve_memory(
            query=query,
            memory_types=memory_types,
            target_object=target_object,
            top_k=3,
            task_type=task_type
        )
        
        enhanced_prompt = query + "\n\n"
        
        # Add working memory context
        if "working" in retrieved_memories and retrieved_memories["working"]:
            enhanced_prompt += "=== Current Working Context ===\n"
            for i, memory in enumerate(retrieved_memories["working"][:2], 1):
                enhanced_prompt += f"{i}. Current Task: {memory.current_task}\n"
                if memory.attention_focus:
                    enhanced_prompt += f"   Focus: {memory.attention_focus}\n"
                if memory.immediate_goals:
                    enhanced_prompt += f"   Goals: {', '.join(memory.immediate_goals[:2])}\n"
            enhanced_prompt += "\n"
        
        # Add episodic memory context
        if "episodic" in retrieved_memories and retrieved_memories["episodic"]:
            enhanced_prompt += "=== Relevant Past Experiences ===\n"
            for i, memory in enumerate(retrieved_memories["episodic"][:2], 1):
                enhanced_prompt += f"{i}. Event: {memory.event_type}\n"
                enhanced_prompt += f"   Summary: {memory.summary_text}\n"
                if memory.content_relations:
                    for rel in memory.content_relations[:1]:
                        enhanced_prompt += f"   Key Insight: {rel.content_summary[:100]}...\n"
            enhanced_prompt += "\n"
        
        # Add semantic memory context
        if "semantic" in retrieved_memories and retrieved_memories["semantic"]:
            enhanced_prompt += "=== Relevant Knowledge ===\n"
            for i, memory in enumerate(retrieved_memories["semantic"][:2], 1):
                enhanced_prompt += f"{i}. Concepts: {', '.join(memory.key_concepts[:3])}\n"
                enhanced_prompt += f"   Context: {memory.context}\n"
                enhanced_prompt += f"   Summary: {memory.summary_text[:100]}...\n"
            enhanced_prompt += "\n"
        
        return enhanced_prompt
    
    def find_objects_for_parameter(self, param_name: str, task_type: str = "parameter_recovery") -> List[Any]:
        """
        Find objects in memory that match a parameter name.
        
        Args:
            param_name: The parameter name to search for
            task_type: Type of task for context
            
        Returns:
            List of matching objects
        """
        return self._find_objects_in_memory(param_name)


# Convenience functions for easy access
def create_retriever(heap):
    """
    Create a memory retriever instance for the given heap.
    
    Args:
        heap: The heap instance
        
    Returns:
        MemoryRetriever instance
    """
    return MemoryRetriever(heap)


def resolve(heap, ref: str, top_k: int = 1, memory_types: Optional[List[str]] = None, 
           use_memory: bool = True, use_semantic: bool = True, task_type: Optional[str] = None) -> Any:
    """
    Convenience function to resolve a reference using memory retrieval.
    
    Args:
        heap: The heap instance
        ref: The reference string to resolve
        top_k: Number of top results to return (default: 1)
        memory_types: List of memory types to search ["working", "episodic", "semantic", "all"] (default: ["all"])
        use_memory: Whether to use memory-based retrieval (default: True)
        use_semantic: Whether to use semantic search (default: True)
        task_type: Type of task for context-aware retrieval (default: None)
        
    Returns:
        Resolved object or None
        
    Examples:
        # Basic resolution
        obj = resolve(heap, "movie")
        
        # Memory-specific resolution
        obj = resolve(heap, "review", memory_types=["episodic"])
        
        # Task-aware resolution
        obj = resolve(heap, "user_input", task_type="parameter_recovery")
        
        # Semantic-only resolution
        obj = resolve(heap, "sci-fi film", use_memory=False, use_semantic=True)
        
        # Memory-only resolution
        obj = resolve(heap, "author", use_memory=True, use_semantic=False)
    """
    retriever = MemoryRetriever(heap)
    return retriever.resolve(ref, top_k, memory_types, use_memory, use_semantic, task_type)


def retrieve_memory(heap, query: str, memory_types: Optional[List[str]] = None, 
                   target_object=None, top_k: int = 1, task_type: Optional[str] = None) -> Dict[str, List]:
    """
    Convenience function to retrieve memory from a heap.
    
    Args:
        heap: The heap instance
        query: The query or context for retrieval
        memory_types: List of memory types to search
        target_object: The target object for context
        top_k: Number of top results to return per memory type
        task_type: Type of task for context
        
    Returns:
        Dict containing retrieved memories organized by type
    """
    retriever = MemoryRetriever(heap)
    return retriever.retrieve_memory(query, memory_types, target_object, top_k, task_type)


def create_contextual_prompt(heap, query: str, target_object=None, memory_types: Optional[List[str]] = None, 
                           task_type: Optional[str] = None) -> str:
    """
    Convenience function to create a contextual prompt.
    
    Args:
        heap: The heap instance
        query: The base query or prompt
        target_object: The target object for context
        memory_types: List of memory types to use
        task_type: Type of task for context
        
    Returns:
        Enhanced prompt with memory context
    """
    retriever = MemoryRetriever(heap)
    return retriever.create_contextual_prompt(query, target_object, memory_types, task_type)


def find_objects_for_parameter(heap, param_name: str, task_type: str = "parameter_recovery") -> List[Any]:
    """
    Convenience function to find objects for a parameter.
    
    Args:
        heap: The heap instance
        param_name: The parameter name to search for
        task_type: Type of task for context
        
    Returns:
        List of matching objects
    """
    retriever = MemoryRetriever(heap)
    return retriever.find_objects_for_parameter(param_name, task_type)


def store_action_memory(heap, action_type: str, action_instruction: str, action_params: list, 
                       result: str = None, entity_name: str = "system", entity_type: str = "agent"):
    """
    Convenience function to store action episodic memory.
    
    Args:
        heap: The heap instance
        action_type: Type of action (e.g., "ActionOp", "summarize", "examine")
        action_instruction: The instruction/description of the action
        action_params: List of parameter names used in the action
        result: The result/output of the action execution
        entity_name: Name of the entity performing the action
        entity_type: Type of the entity (e.g., "agent", "user", "system")
        
    Returns:
        The created episodic memory object
    """
    return heap.store_action_memory(action_type, action_instruction, action_params, result, entity_name, entity_type)


def add_step_experience(heap, step_name: str, step_type: str, execution_method: str,
                       input_data: Dict[str, Any], output_result: Any, success: bool,
                       execution_time: float, error_message: str = None,
                       performance_metrics: Dict[str, Any] = None,
                       learning_insights: List[str] = None,
                       metadata: Dict[str, Any] = None):
    """
    Convenience function to add step experience to working memory.
    
    Args:
        heap: The heap instance
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
    if not heap.working_memory:
        return None
    
    # Use the most recent working memory entry
    latest_working_memory = heap.working_memory[-1]
    
    # Import the extractor to add experience
    from brainary.memory.working_memory_extractor import WorkingMemoryExtractor
    extractor = WorkingMemoryExtractor()
    
    return extractor.add_step_experience(
        latest_working_memory, step_name, step_type, execution_method,
        input_data, output_result, success, execution_time, error_message,
        performance_metrics, learning_insights, metadata
    )


def get_execution_insights(heap) -> Dict[str, Any]:
    """
    Convenience function to get execution insights from working memory.
    
    Args:
        heap: The heap instance
        
    Returns:
        Dictionary containing execution insights
    """
    if not heap.working_memory:
        return {"message": "No working memory available"}
    
    # Use the most recent working memory entry
    latest_working_memory = heap.working_memory[-1]
    
    # Import the extractor to get insights
    from brainary.memory.working_memory_extractor import WorkingMemoryExtractor
    extractor = WorkingMemoryExtractor()
    
    return extractor.get_execution_insights(latest_working_memory)


def create_semantic_experience_summary(heap) -> Any:
    """
    Convenience function to create semantic experience summary.
    
    Args:
        heap: The heap instance
        
    Returns:
        SemanticExperienceSummary containing high-level insights
    """
    return heap.create_semantic_experience_summary()


def get_memory_hierarchy_insights(heap) -> Dict[str, Any]:
    """
    Get insights from all three memory levels: Working, Episodic, and Semantic.
    
    Args:
        heap: The heap instance
        
    Returns:
        Dictionary containing insights from all memory levels
    """
    insights = {}
    
    # Working memory insights (detailed step experiences)
    working_insights = get_execution_insights(heap)
    insights['working_memory'] = working_insights
    
    # Episodic memory insights (abstracted step summaries)
    episodic_insights = {}
    if heap.episodic_memory:
        episodic_insights['total_episodes'] = len(heap.episodic_memory)
        episodic_insights['episodes_with_step_summaries'] = sum(
            1 for mem in heap.episodic_memory 
            if hasattr(mem, 'step_experience_summary') and mem.step_experience_summary
        )
        
        # Collect step experience summaries
        step_summaries = []
        for memory in heap.episodic_memory:
            if hasattr(memory, 'step_experience_summary') and memory.step_experience_summary:
                step_summaries.append(memory.step_experience_summary)
        
        if step_summaries:
            episodic_insights['total_steps_abstracted'] = sum(s.total_steps for s in step_summaries)
            episodic_insights['overall_success_rate'] = sum(s.success_rate for s in step_summaries) / len(step_summaries)
            episodic_insights['step_types_covered'] = list(set(
                step_type for summary in step_summaries 
                for step_type in summary.step_types
            ))
    
    insights['episodic_memory'] = episodic_insights
    
    # Semantic memory insights (very high-level patterns)
    semantic_summary = create_semantic_experience_summary(heap)
    if semantic_summary:
        insights['semantic_memory'] = {
            'total_episodes': semantic_summary.total_episodes,
            'total_steps': semantic_summary.total_steps,
            'overall_success_rate': semantic_summary.overall_success_rate,
            'dominant_patterns': semantic_summary.dominant_patterns,
            'key_optimization_areas': semantic_summary.key_optimization_areas,
            'critical_learning_points': semantic_summary.critical_learning_points,
            'system_capabilities': semantic_summary.system_capabilities,
            'experience_insights_count': len(semantic_summary.experience_insights)
        }
    else:
        insights['semantic_memory'] = {"message": "No semantic experience summary available"}
    
    return insights
