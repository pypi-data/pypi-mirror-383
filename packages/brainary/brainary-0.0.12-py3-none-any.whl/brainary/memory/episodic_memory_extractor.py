from typing import Any, Dict, List, Optional, Union, Set, Tuple
import json
import hashlib
from dataclasses import dataclass, field
from datetime import datetime

# Try to import LLM, but don't fail if not available
try:
    from brainary.llm.llm import LLM
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    LLM = None

@dataclass
class ContentRelation:
    """Represents a relationship between an entity and content."""
    entity_id: str
    entity_name: str
    entity_type: str  # e.g., "author", "user", "system", "agent", "llm"
    content_type: str  # e.g., "review", "comment", "post", "message", "action", "llm_response"
    content_summary: str
    sentiment: str  # positive, negative, neutral
    relationship_type: str  # e.g., "created", "modified", "responded_to", "interacted_with", "llm_communication"
    timestamp: datetime
    mentioned_entities: List[str] = None  # List of entities mentioned in the content
    llm_context: Dict[str, Any] = None  # LLM-specific context (model, temperature, tokens, etc.)
    metadata: Dict[str, Any] = None  # Additional flexible metadata



@dataclass
class StepExperienceSummary:
    """Abstracted summary of step experiences for episodic memory."""
    total_steps: int
    successful_steps: int
    failed_steps: int
    total_execution_time: float
    step_types: List[str]
    key_learning_points: List[str]
    performance_highlights: List[str]
    error_patterns: List[str]
    execution_methods: List[str]
    success_rate: float
    avg_time_per_step: float
    metadata: Dict[str, Any] = None

@dataclass
class EpisodicMemory:
    """Represents an episodic memory entry."""
    episode_id: str
    timestamp: datetime
    event_type: str
    participants: List[str]
    actions: List[str]
    outcomes: List[str]
    emotional_context: str
    episode_hash: str
    summary_text: str
    # Content relations with mentioned entities
    content_relations: List[ContentRelation] = None
    # Abstracted step experience summary
    step_experience_summary: StepExperienceSummary = None
    metadata: Dict[str, Any] = None  # Additional flexible metadata


class EpisodicMemoryExtractor:
    """Extracts episodic memory information from interactions and events."""
    
    def __init__(self, llm_name: str = "gpt-4o-mini", cache_size: int = 1000):
        if not LLM_AVAILABLE:
            raise ImportError("LLM is not available. Please ensure brainary.llm is installed.")
        self.llm = LLM.get_by_name(llm_name)
        self.cache_size = cache_size
        self.episodic_cache = {}  # hash -> EpisodicMemory
        
    def extract_episodic_memory(self, interaction_data: Dict[str, Any], episode_id: str = None) -> EpisodicMemory:
        """
        Extract episodic memory from interaction data.
        
        Args:
            interaction_data: Dictionary containing interaction information
            episode_id: Optional unique identifier for the episode
            
        Returns:
            EpisodicMemory containing extracted episodic information
        """
        # Generate hash for caching
        interaction_str = json.dumps(interaction_data, sort_keys=True)
        if episode_id:
            interaction_str = f"{episode_id}: {interaction_str}"
        
        episode_hash = hashlib.md5(interaction_str.encode()).hexdigest()
        
        # Check cache first
        if episode_hash in self.episodic_cache:
            return self.episodic_cache[episode_hash]
        
        # Extract episodic information using LLM
        episodic_memory = self._extract_with_llm(interaction_data, episode_id)
        episodic_memory.episode_hash = episode_hash
        episodic_memory.timestamp = datetime.now()
        
        # Cache the result
        self._add_to_cache(episode_hash, episodic_memory)
        
        return episodic_memory
    
    def extract_content_relation_memory(self, 
                                      content: str, 
                                      entity_name: str, 
                                      entity_type: str = "user",
                                      content_type: str = "message",
                                      relationship_type: str = "created",
                                      episode_id: str = None,
                                      llm_context: Dict[str, Any] = None,
                                      metadata: Dict[str, Any] = None) -> EpisodicMemory:
        """
        Extract episodic memory for content-entity relationships.
        
        Args:
            content: The content text or data
            entity_name: The name/identifier of the entity
            entity_type: Type of entity (e.g., "user", "author", "system", "agent", "llm")
            content_type: Type of content (e.g., "message", "review", "action", "comment", "llm_response")
            relationship_type: Type of relationship (e.g., "created", "modified", "responded_to", "llm_communication")
            episode_id: Optional unique identifier for the episode
            llm_context: LLM-specific context (model, temperature, tokens, etc.)
            metadata: Additional metadata for the relationship
            
        Returns:
            EpisodicMemory containing extracted episodic information with content relations
        """
        interaction_data = {
            'type': 'content_relation',
            'content': content,
            'entity_name': entity_name,
            'entity_type': entity_type,
            'content_type': content_type,
            'relationship_type': relationship_type,
            'participants': [entity_name, 'system'],
            'actions': [f'{entity_name} {relationship_type} {content_type}'],
            'outcomes': [f'{content_type} stored with {entity_type} attribution'],
            'metadata': metadata or {}
        }
        
        return self.extract_episodic_memory(interaction_data, episode_id)
    
    def extract_llm_communication_memory(self,
                                       source_llm: str,
                                       target_llm: str,
                                       communication_type: str,
                                       message: str,
                                       context: Dict[str, Any] = None,
                                       episode_id: str = None) -> EpisodicMemory:
        """
        Extract episodic memory for LLM-to-LLM communication.
        
        Args:
            source_llm: Name/identifier of the source LLM
            target_llm: Name/identifier of the target LLM
            communication_type: Type of communication (e.g., "query", "response", "instruction", "feedback")
            message: The communication message content
            context: Additional context about the communication
            episode_id: Optional unique identifier for the episode
            
        Returns:
            EpisodicMemory containing extracted LLM communication information
        """
        interaction_data = {
            'type': 'llm_communication',
            'source_llm': source_llm,
            'target_llm': target_llm,
            'communication_type': communication_type,
            'message': message,
            'participants': [source_llm, target_llm],
            'actions': [f'{source_llm} communicated with {target_llm}'],
            'outcomes': [f'LLM communication of type {communication_type} completed'],
            'context': context or {}
        }
        
        return self.extract_episodic_memory(interaction_data, episode_id)
    
    def extract_multi_entity_memory(self, 
                                  entities: List[Dict[str, Any]], 
                                  episode_id: str = None) -> EpisodicMemory:
        """
        Extract episodic memory for interactions involving multiple entities.
        
        Args:
            entities: List of entity dictionaries with their content and relationships
            episode_id: Optional unique identifier for the episode
            
        Returns:
            EpisodicMemory containing extracted episodic information with multiple entity relations
        """
        interaction_data = {
            'type': 'multi_entity_interaction',
            'entities': entities,
            'participants': [entity.get('entity_name', 'unknown') for entity in entities],
            'actions': [f"{entity.get('entity_name', 'unknown')} {entity.get('relationship_type', 'interacted')}" for entity in entities],
            'outcomes': ['Multi-entity interaction recorded']
        }
        
        return self.extract_episodic_memory(interaction_data, episode_id)
    
    def extract_object_episodic_memory(self, obj: Any, episode_id: str = None) -> EpisodicMemory:
        """
        Extract episodic memory directly from an object by analyzing its content and entity fields.
        
        Args:
            obj: The object to analyze for content and entity relationships
            episode_id: Optional unique identifier for the episode
            
        Returns:
            EpisodicMemory containing extracted episodic information with content relations
        """
        # Analyze the object for content and entity information
        content_info = self._analyze_object_content(obj)
        
        if not content_info['has_content']:
            # If no content found, create basic object creation memory
            return self._create_basic_object_memory(obj, episode_id)
        
        # Extract episodic memory with content relations
        episodic_memory = self.extract_content_relation_memory(
            content=content_info['content'],
            entity_name=content_info['entity_name'],
            entity_type=content_info['entity_type'],
            content_type=content_info['content_type'],
            relationship_type="created",
            episode_id=episode_id,
            metadata=content_info['metadata']
        )
        
        # Add mentioned entities based on content analysis
        if content_info['content']:
            self._add_mentioned_entities(episodic_memory, content_info['content'])
        
        return episodic_memory
    
    def create_step_experience_summary(self, step_experiences: List[Any]) -> StepExperienceSummary:
        """
        Create an abstracted summary of step experiences for episodic memory.
        
        Args:
            step_experiences: List of StepExperience objects from working memory
            
        Returns:
            StepExperienceSummary containing abstracted insights
        """
        if not step_experiences:
            return None
        
        # Calculate basic statistics
        total_steps = len(step_experiences)
        successful_steps = sum(1 for step in step_experiences if getattr(step, 'success', False))
        failed_steps = total_steps - successful_steps
        success_rate = successful_steps / total_steps if total_steps > 0 else 0.0
        
        # Calculate timing statistics
        total_execution_time = sum(getattr(step, 'execution_time', 0) for step in step_experiences)
        avg_time_per_step = total_execution_time / total_steps if total_steps > 0 else 0.0
        
        # Extract unique step types and execution methods
        step_types = list(set(getattr(step, 'step_type', 'unknown') for step in step_experiences))
        execution_methods = list(set(getattr(step, 'execution_method', 'unknown') for step in step_experiences))
        
        # Extract key learning points
        key_learning_points = []
        for step in step_experiences:
            insights = getattr(step, 'learning_insights', [])
            if insights:
                key_learning_points.extend(insights[:2])  # Take first 2 insights per step
        
        # Extract performance highlights
        performance_highlights = []
        for step in step_experiences:
            if getattr(step, 'success', False):
                metrics = getattr(step, 'performance_metrics', {})
                if metrics:
                    if 'execution_time' in metrics and metrics['execution_time'] < avg_time_per_step:
                        performance_highlights.append(f"Fast execution: {getattr(step, 'step_name', 'Unknown')}")
                    if 'accuracy' in metrics and metrics.get('accuracy', 0) > 0.9:
                        performance_highlights.append(f"High accuracy: {getattr(step, 'step_name', 'Unknown')}")
        
        # Extract error patterns
        error_patterns = []
        for step in step_experiences:
            if not getattr(step, 'success', False):
                error_msg = getattr(step, 'error_message', 'Unknown error')
                step_name = getattr(step, 'step_name', 'Unknown')
                error_patterns.append(f"{step_name}: {error_msg[:50]}...")
        
        # Limit lists to prevent memory bloat
        key_learning_points = key_learning_points[:10]
        performance_highlights = performance_highlights[:5]
        error_patterns = error_patterns[:5]
        
        return StepExperienceSummary(
            total_steps=total_steps,
            successful_steps=successful_steps,
            failed_steps=failed_steps,
            total_execution_time=total_execution_time,
            step_types=step_types,
            key_learning_points=key_learning_points,
            performance_highlights=performance_highlights,
            error_patterns=error_patterns,
            execution_methods=execution_methods,
            success_rate=success_rate,
            avg_time_per_step=avg_time_per_step,
            metadata={
                'summary_generated_at': datetime.now().isoformat(),
                'source_working_memory_count': len(step_experiences)
            }
        )

    
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
    
    def _create_basic_object_memory(self, obj: Any, episode_id: str = None) -> EpisodicMemory:
        """
        Create basic episodic memory for object creation when no content is found.
        
        Args:
            obj: The object that was created
            episode_id: Optional episode ID
            
        Returns:
            Basic EpisodicMemory for object creation
        """
        interaction_data = {
            'type': 'object_creation',
            'object_type': obj.__class__.__name__,
            'participants': ['system', 'memory_manager'],
            'actions': [f'Created {obj.__class__.__name__} object'],
            'outcomes': ['Object stored in memory']
        }
        
        return self.extract_episodic_memory(interaction_data, episode_id)
    
    def _add_mentioned_entities(self, episodic_memory: EpisodicMemory, content: str):
        """
        Add mentioned entities to content relations based on content analysis.
        
        Args:
            episodic_memory: The episodic memory to add mentioned entities to
            content: The content to analyze for entities
        """
        if not episodic_memory.content_relations:
            return
        
        # Extract entities from content (simple approach)
        import re
        
        # Look for movie titles (capitalized words that might be titles)
        potential_titles = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)
        mentioned_entities = []
        
        for title in potential_titles[:2]:  # Limit to first 2
            if len(title.split()) >= 2:  # At least 2 words
                mentioned_entities.append(title)
        
        # Add mentioned entities to the first content relation
        if mentioned_entities and episodic_memory.content_relations:
            episodic_memory.content_relations[0].mentioned_entities = mentioned_entities
    

    
    def _extract_with_llm(self, interaction_data: Dict[str, Any], episode_id: str = None) -> EpisodicMemory:
        """Extract episodic information using LLM."""
        
        # Check if LLM is available
        if not LLM_AVAILABLE or self.llm is None:
            return self._fallback_extraction(interaction_data, episode_id)
        
        # Prepare the input for LLM analysis
        interaction_repr = self._prepare_interaction_representation(interaction_data, episode_id)
        
        # Create the extraction prompt
        prompt = self._create_extraction_prompt(interaction_repr)
        
        try:
            # Get LLM response
            response = self.llm.request([prompt])
            if response and len(response) > 0:
                result_text = response[0]
            else:
                result_text = ""
            
            # Parse the LLM response
            episodic_memory = self._parse_llm_response(result_text, interaction_data, episode_id)
            
        except Exception as e:
            # Fallback to basic extraction if LLM fails
            episodic_memory = self._fallback_extraction(interaction_data, episode_id)
        
        return episodic_memory
    
    def _prepare_interaction_representation(self, interaction_data: Dict[str, Any], episode_id: str = None) -> str:
        """Prepare interaction representation for LLM analysis."""
        
        # Convert interaction data to a readable format
        interaction_repr = json.dumps(interaction_data, indent=2, default=str)
        
        if episode_id:
            interaction_repr = f"Episode ID: {episode_id}\nInteraction Data: {interaction_repr}"
        
        return interaction_repr
    
    def _create_extraction_prompt(self, interaction_repr: str) -> str:
        """Create the prompt for episodic memory extraction."""
        
        prompt = f"""
You are an episodic memory extractor. Analyze the following interaction and extract key episodic information.

## Interaction to Analyze
{interaction_repr}

## Task
Extract episodic memory information in the following JSON format:

{{
    "episode_id": "unique_identifier",
    "event_type": "conversation|task_completion|error|decision|learning|content_relation|multi_entity_interaction",
    "participants": ["entity1", "entity2", "system"],
    "actions": ["action1", "action2", "action3"],
    "outcomes": ["outcome1", "outcome2"],
    "emotional_context": "positive|negative|neutral|frustrated|satisfied",
    "summary_text": "A concise summary of what happened in this episode",
    "content_relations": [
        {{
            "entity_id": "unique_entity_id",
            "entity_name": "entity_name",
            "entity_type": "user|author|system|agent",
            "content_type": "message|review|action|comment|post",
            "content_summary": "Brief summary of the content",
            "sentiment": "positive|negative|neutral",
            "relationship_type": "created|modified|responded_to|interacted_with",
            "mentioned_entities": ["entity1", "entity2"]
        }}
    ]
}}

## Guidelines for Episodic Memory
- **event_type**: Categorize the type of interaction (conversation, task completion, error, decision, learning, content_relation, multi_entity_interaction, llm_communication)
- **participants**: List all entities involved in the interaction (including LLM names)
- **actions**: Describe the key actions or steps taken during the interaction
- **outcomes**: List the results, consequences, or learnings from the interaction
- **emotional_context**: Capture the emotional tone or satisfaction level
- **summary_text**: A concise narrative of what happened, focusing on the sequence of events

## Guidelines for Content Relations
When analyzing content-entity relationships:
- **content_relations**: Extract entity information with their relationship to content
- **mentioned_entities**: List entities mentioned in the content (e.g., movie titles, people, places)
- **sentiment**: Analyze the emotional tone of the content
- **content_summary**: Provide a brief summary of what the entity said or created
- **relationship_type**: Describe the type of relationship (created, modified, responded_to, etc.)

## Examples of Good Episodic Summaries:
- "User 'john' created a review expressing positive sentiment about the movie's quality"
- "Agent 'assistant' responded to user query with helpful guidance, user expressed satisfaction"
- "System 'memory_manager' processed multiple entity interactions and stored relationship data"
- "Author 'acedj' shared personal experience about watching The Matrix with roommate, expressing strong positive sentiment"
- "LLM 'gpt-4' communicated with LLM 'claude-3' via query-response pattern, successfully exchanging information about memory optimization"
- "LLM 'llama-2' provided feedback to LLM 'mistral-7b' regarding code generation quality, resulting in improved output"

## Output
Provide only the JSON response, no additional text.
"""
        return prompt
    
    def _parse_llm_response(self, response: str, interaction_data: Dict[str, Any], episode_id: str = None) -> EpisodicMemory:
        """Parse LLM response into EpisodicMemory."""
        
        try:
            # Try to extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
                
                # Parse content relations if present
                content_relations = []
                if 'content_relations' in data and isinstance(data['content_relations'], list):
                    for relation_data in data['content_relations']:
                        relation = ContentRelation(
                            entity_id=relation_data.get('entity_id', 'unknown'),
                            entity_name=relation_data.get('entity_name', 'unknown'),
                            entity_type=relation_data.get('entity_type', 'user'),
                            content_type=relation_data.get('content_type', 'message'),
                            content_summary=relation_data.get('content_summary', ''),
                            sentiment=relation_data.get('sentiment', 'neutral'),
                            relationship_type=relation_data.get('relationship_type', 'created'),
                            timestamp=datetime.now(),
                            metadata=relation_data.get('metadata', {})
                        )
                        content_relations.append(relation)
                
                return EpisodicMemory(
                    episode_id=data.get('episode_id', episode_id or 'unknown'),
                    timestamp=datetime.now(),
                    event_type=data.get('event_type', 'conversation'),
                    participants=data.get('participants', []),
                    actions=data.get('actions', []),
                    outcomes=data.get('outcomes', []),
                    emotional_context=data.get('emotional_context', 'neutral'),
                    episode_hash='',  # Will be set by caller
                    summary_text=data.get('summary_text', ''),
                    content_relations=content_relations,
                    metadata=data.get('metadata', {})
                )
            else:
                # Fallback if JSON parsing fails
                return self._fallback_extraction(interaction_data, episode_id)
                
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Fallback if parsing fails
            return self._fallback_extraction(interaction_data, episode_id)
    
    def _fallback_extraction(self, interaction_data: Dict[str, Any], episode_id: str = None) -> EpisodicMemory:
        """Fallback extraction when LLM is not available."""
        
        # Basic episodic extraction
        event_type = interaction_data.get('type', 'conversation')
        participants = interaction_data.get('participants', ['user', 'agent'])
        actions = interaction_data.get('actions', [])
        outcomes = interaction_data.get('outcomes', [])
        
        # Extract content relations if available
        content_relations = []
        if 'content' in interaction_data and 'entity_name' in interaction_data:
            entity_name = interaction_data['entity_name']
            entity_type = interaction_data.get('entity_type', 'user')
            content_type = interaction_data.get('content_type', 'message')
            content = interaction_data['content']
            relationship_type = interaction_data.get('relationship_type', 'created')
            
            # Basic sentiment analysis
            sentiment = 'neutral'
            if any(word in content.lower() for word in ['great', 'good', 'excellent', 'amazing', 'love']):
                sentiment = 'positive'
            elif any(word in content.lower() for word in ['bad', 'terrible', 'awful', 'hate', 'shit']):
                sentiment = 'negative'
            
            relation = ContentRelation(
                entity_id=entity_name,
                entity_name=entity_name,
                entity_type=entity_type,
                content_type=content_type,
                content_summary=content[:100] + "..." if len(content) > 100 else content,
                sentiment=sentiment,
                relationship_type=relationship_type,
                timestamp=datetime.now(),
                metadata=interaction_data.get('metadata', {})
            )
            content_relations.append(relation)
            
            # Add entity to participants if not already there
            if entity_name not in participants:
                participants.append(entity_name)
        
        # Handle multi-entity interactions
        if 'entities' in interaction_data and isinstance(interaction_data['entities'], list):
            for entity_data in interaction_data['entities']:
                entity_name = entity_data.get('entity_name', 'unknown')
                entity_type = entity_data.get('entity_type', 'user')
                content_type = entity_data.get('content_type', 'message')
                content = entity_data.get('content', '')
                relationship_type = entity_data.get('relationship_type', 'interacted')
                
                # Basic sentiment analysis
                sentiment = 'neutral'
                if content and any(word in content.lower() for word in ['great', 'good', 'excellent', 'amazing', 'love']):
                    sentiment = 'positive'
                elif content and any(word in content.lower() for word in ['bad', 'terrible', 'awful', 'hate', 'shit']):
                    sentiment = 'negative'
                
                relation = ContentRelation(
                    entity_id=entity_name,
                    entity_name=entity_name,
                    entity_type=entity_type,
                    content_type=content_type,
                    content_summary=content[:100] + "..." if len(content) > 100 else content,
                    sentiment=sentiment,
                    relationship_strength=0.8,
                    relationship_type=relationship_type,
                    timestamp=datetime.now(),
                    metadata=entity_data.get('metadata', {})
                )
                content_relations.append(relation)
                
                # Add entity to participants if not already there
                if entity_name not in participants:
                    participants.append(entity_name)
        
        # Generate basic summary
        summary = f"Interaction of type {event_type} between {', '.join(participants)}"
        if actions:
            summary += f" involving {', '.join(actions[:3])}"
        
        if content_relations:
            summary += f". {content_relations[0].entity_name} {content_relations[0].relationship_type} {content_relations[0].content_type} with {content_relations[0].sentiment} sentiment"
        
        return EpisodicMemory(
            episode_id=episode_id or 'fallback_episode',
            timestamp=datetime.now(),
            event_type=event_type,
            participants=participants,
            actions=actions[:5],  # Limit to 5 actions
            outcomes=outcomes[:3],  # Limit to 3 outcomes
            emotional_context='neutral',
            episode_hash='',
            summary_text=summary,
            content_relations=content_relations,
            metadata=interaction_data.get('metadata', {})
        )
    
    def _add_to_cache(self, episode_hash: str, memory: EpisodicMemory):
        """Add episodic memory to cache with size management."""
        
        if len(self.episodic_cache) >= self.cache_size:
            # Remove oldest entry (simple FIFO)
            oldest_key = next(iter(self.episodic_cache))
            del self.episodic_cache[oldest_key]
        
        self.episodic_cache[episode_hash] = memory
    
    def get_episodic_summary(self, interaction_data: Dict[str, Any], episode_id: str = None) -> str:
        """Get a text summary of episodic memory."""
        memory = self.extract_episodic_memory(interaction_data, episode_id)
        return memory.summary_text
    
    def get_content_relations_summary(self, memory: EpisodicMemory) -> str:
        """Get a summary of content relations from episodic memory."""
        if not memory.content_relations:
            return "No content relations found"
        
        summaries = []
        for relation in memory.content_relations:
            summary = f"{relation.entity_type} '{relation.entity_name}' {relation.relationship_type} {relation.content_type} with {relation.sentiment} sentiment"
            if relation.content_summary:
                summary += f": {relation.content_summary}"
            summaries.append(summary)
        
        return "; ".join(summaries)
    
    def get_entity_summary(self, memory: EpisodicMemory, entity_name: str = None) -> str:
        """Get a summary of content relations for a specific entity."""
        if not memory.content_relations:
            return "No content relations found"
        
        filtered_relations = memory.content_relations
        if entity_name:
            filtered_relations = [rel for rel in memory.content_relations if rel.entity_name == entity_name]
        
        if not filtered_relations:
            return f"No content found for entity '{entity_name}'" if entity_name else "No content relations found"
        
        summaries = []
        for relation in filtered_relations:
            summary = f"{relation.content_type} with {relation.sentiment} sentiment"
            if relation.content_summary:
                summary += f": {relation.content_summary}"
            summaries.append(summary)
        
        entity_display = entity_name if entity_name else "entities"
        return f"{entity_display} have {len(filtered_relations)} contributions: " + "; ".join(summaries)
    
    def clear_cache(self):
        """Clear the episodic cache."""
        self.episodic_cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            'cache_size': len(self.episodic_cache),
            'max_cache_size': self.cache_size,
            'cache_usage_percentage': (len(self.episodic_cache) / self.cache_size) * 100
        }

# Global extractor instance
_episodic_extractor_instance = None

def get_episodic_extractor(llm_name: str = "gpt-4o-mini") -> EpisodicMemoryExtractor:
    """Get the global episodic memory extractor instance."""
    global _episodic_extractor_instance
    if _episodic_extractor_instance is None:
        try:
            _episodic_extractor_instance = EpisodicMemoryExtractor(llm_name)
        except ImportError:
            # Create a fallback extractor that only uses basic extraction
            _episodic_extractor_instance = FallbackEpisodicExtractor()
    return _episodic_extractor_instance

class FallbackEpisodicExtractor:
    """Fallback episodic extractor that doesn't require LLM."""
    
    def __init__(self):
        self.episodic_cache = {}
    
    def extract_episodic_memory(self, interaction_data: Dict[str, Any], episode_id: str = None) -> EpisodicMemory:
        """Extract episodic memory using basic methods."""
        interaction_str = json.dumps(interaction_data, sort_keys=True)
        if episode_id:
            interaction_str = f"{episode_id}: {interaction_str}"
        
        episode_hash = hashlib.md5(interaction_str.encode()).hexdigest()
        
        # Check cache first
        if episode_hash in self.episodic_cache:
            return self.episodic_cache[episode_hash]
        
        # Use basic extraction
        memory = self._fallback_extraction(interaction_data, episode_id)
        memory.episode_hash = episode_hash
        
        # Cache the result
        self.episodic_cache[episode_hash] = memory
        return memory
    
    def extract_content_relation_memory(self, 
                                      content: str, 
                                      entity_name: str, 
                                      entity_type: str = "user",
                                      content_type: str = "message",
                                      relationship_type: str = "created",
                                      episode_id: str = None,
                                      metadata: Dict[str, Any] = None) -> EpisodicMemory:
        """Extract episodic memory for content-entity relationships."""
        interaction_data = {
            'type': 'content_relation',
            'content': content,
            'entity_name': entity_name,
            'entity_type': entity_type,
            'content_type': content_type,
            'relationship_type': relationship_type,
            'participants': [entity_name, 'system'],
            'actions': [f'{entity_name} {relationship_type} {content_type}'],
            'outcomes': [f'{content_type} stored with {entity_type} attribution'],
            'metadata': metadata or {}
        }
        
        return self.extract_episodic_memory(interaction_data, episode_id)
    
    def extract_multi_entity_memory(self, 
                                  entities: List[Dict[str, Any]], 
                                  episode_id: str = None) -> EpisodicMemory:
        """Extract episodic memory for interactions involving multiple entities."""
        interaction_data = {
            'type': 'multi_entity_interaction',
            'entities': entities,
            'participants': [entity.get('entity_name', 'unknown') for entity in entities],
            'actions': [f"{entity.get('entity_name', 'unknown')} {entity.get('relationship_type', 'interacted')}" for entity in entities],
            'outcomes': ['Multi-entity interaction recorded']
        }
        
        return self.extract_episodic_memory(interaction_data, episode_id)
    
    def _fallback_extraction(self, interaction_data: Dict[str, Any], episode_id: str = None) -> EpisodicMemory:
        """Basic episodic extraction without LLM."""
        event_type = interaction_data.get('type', 'conversation')
        participants = interaction_data.get('participants', ['user', 'agent'])
        actions = interaction_data.get('actions', [])
        outcomes = interaction_data.get('outcomes', [])
        
        # Extract content relations if available
        content_relations = []
        if 'content' in interaction_data and 'entity_name' in interaction_data:
            entity_name = interaction_data['entity_name']
            entity_type = interaction_data.get('entity_type', 'user')
            content_type = interaction_data.get('content_type', 'message')
            content = interaction_data['content']
            relationship_type = interaction_data.get('relationship_type', 'created')
            
            # Basic sentiment analysis
            sentiment = 'neutral'
            if any(word in content.lower() for word in ['great', 'good', 'excellent', 'amazing', 'love']):
                sentiment = 'positive'
            elif any(word in content.lower() for word in ['bad', 'terrible', 'awful', 'hate', 'shit']):
                sentiment = 'negative'
            
            relation = ContentRelation(
                entity_id=entity_name,
                entity_name=entity_name,
                entity_type=entity_type,
                content_type=content_type,
                content_summary=content[:100] + "..." if len(content) > 100 else content,
                sentiment=sentiment,
                relationship_strength=0.9,
                relationship_type=relationship_type,
                timestamp=datetime.now(),
                metadata=interaction_data.get('metadata', {})
            )
            content_relations.append(relation)
            
            # Add entity to participants if not already there
            if entity_name not in participants:
                participants.append(entity_name)
        
        # Handle multi-entity interactions
        if 'entities' in interaction_data and isinstance(interaction_data['entities'], list):
            for entity_data in interaction_data['entities']:
                entity_name = entity_data.get('entity_name', 'unknown')
                entity_type = entity_data.get('entity_type', 'user')
                content_type = entity_data.get('content_type', 'message')
                content = entity_data.get('content', '')
                relationship_type = entity_data.get('relationship_type', 'interacted')
                
                # Basic sentiment analysis
                sentiment = 'neutral'
                if content and any(word in content.lower() for word in ['great', 'good', 'excellent', 'amazing', 'love']):
                    sentiment = 'positive'
                elif content and any(word in content.lower() for word in ['bad', 'terrible', 'awful', 'hate', 'shit']):
                    sentiment = 'negative'
                
                relation = ContentRelation(
                    entity_id=entity_name,
                    entity_name=entity_name,
                    entity_type=entity_type,
                    content_type=content_type,
                    content_summary=content[:100] + "..." if len(content) > 100 else content,
                    sentiment=sentiment,
                    relationship_strength=0.8,
                    relationship_type=relationship_type,
                    timestamp=datetime.now(),
                    metadata=entity_data.get('metadata', {})
                )
                content_relations.append(relation)
                
                # Add entity to participants if not already there
                if entity_name not in participants:
                    participants.append(entity_name)
        
        summary = f"Interaction of type {event_type} between {', '.join(participants)}"
        if actions:
            summary += f" involving {', '.join(actions[:3])}"
        
        if content_relations:
            summary += f". {content_relations[0].entity_name} {content_relations[0].relationship_type} {content_relations[0].content_type} with {content_relations[0].sentiment} sentiment"
        
        return EpisodicMemory(
            episode_id=episode_id or 'fallback_episode',
            timestamp=datetime.now(),
            event_type=event_type,
            participants=participants,
            actions=actions[:5],
            outcomes=outcomes[:3],
            emotional_context='neutral',
            episode_hash='',
            summary_text=summary,
            content_relations=content_relations,
            metadata=interaction_data.get('metadata', {})
        )
    
    def get_episodic_summary(self, interaction_data: Dict[str, Any], episode_id: str = None) -> str:
        """Get a text summary of episodic memory."""
        memory = self.extract_episodic_memory(interaction_data, episode_id)
        return memory.summary_text
    
    def get_content_relations_summary(self, memory: EpisodicMemory) -> str:
        """Get a summary of content relations from episodic memory."""
        if not memory.content_relations:
            return "No content relations found"
        
        summaries = []
        for relation in memory.content_relations:
            summary = f"{relation.entity_type} '{relation.entity_name}' {relation.relationship_type} {relation.content_type} with {relation.sentiment} sentiment"
            if relation.content_summary:
                summary += f": {relation.content_summary}"
            summaries.append(summary)
        
        return "; ".join(summaries)
    
    def get_entity_summary(self, memory: EpisodicMemory, entity_name: str = None) -> str:
        """Get a summary of content relations for a specific entity."""
        if not memory.content_relations:
            return "No content relations found"
        
        filtered_relations = memory.content_relations
        if entity_name:
            filtered_relations = [rel for rel in memory.content_relations if rel.entity_name == entity_name]
        
        if not filtered_relations:
            return f"No content found for entity '{entity_name}'" if entity_name else "No content relations found"
        
        summaries = []
        for relation in filtered_relations:
            summary = f"{relation.content_type} with {relation.sentiment} sentiment"
            if relation.content_summary:
                summary += f": {relation.content_summary}"
            summaries.append(summary)
        
        entity_display = entity_name if entity_name else "entities"
        return f"{entity_display} have {len(filtered_relations)} contributions: " + "; ".join(summaries)

# Convenience functions
def extract_episodic_memory(interaction_data: Dict[str, Any], episode_id: str = None) -> EpisodicMemory:
    """Convenience function to extract episodic memory."""
    extractor = get_episodic_extractor()
    return extractor.extract_episodic_memory(interaction_data, episode_id)

def extract_content_relation_memory(content: str, 
                                  entity_name: str, 
                                  entity_type: str = "user",
                                  content_type: str = "message",
                                  relationship_type: str = "created",
                                  episode_id: str = None,
                                  metadata: Dict[str, Any] = None) -> EpisodicMemory:
    """Convenience function to extract episodic memory for content-entity relationships."""
    extractor = get_episodic_extractor()
    return extractor.extract_content_relation_memory(
        content, entity_name, entity_type, content_type, relationship_type, episode_id, metadata
    )

def extract_multi_entity_memory(entities: List[Dict[str, Any]], episode_id: str = None) -> EpisodicMemory:
    """Convenience function to extract episodic memory for multi-entity interactions."""
    extractor = get_episodic_extractor()
    return extractor.extract_multi_entity_memory(entities, episode_id)

def extract_object_episodic_memory(obj: Any, episode_id: str = None) -> EpisodicMemory:
    """Convenience function to extract episodic memory directly from an object."""
    extractor = get_episodic_extractor()
    return extractor.extract_object_episodic_memory(obj, episode_id)

def extract_llm_communication_memory(source_llm: str, target_llm: str, communication_type: str, 
                                   message: str, context: Dict[str, Any] = None, 
                                   episode_id: str = None) -> EpisodicMemory:
    """Convenience function to extract episodic memory for LLM-to-LLM communication."""
    extractor = get_episodic_extractor()
    return extractor.extract_llm_communication_memory(source_llm, target_llm, communication_type, 
                                                    message, context, episode_id)



def get_episodic_summary(interaction_data: Dict[str, Any], episode_id: str = None) -> str:
    """Convenience function to get episodic summary."""
    extractor = get_episodic_extractor()
    return extractor.get_episodic_summary(interaction_data, episode_id)

def get_content_relations_summary(memory: EpisodicMemory) -> str:
    """Convenience function to get content relations summary."""
    extractor = get_episodic_extractor()
    return extractor.get_content_relations_summary(memory)

def get_entity_summary(memory: EpisodicMemory, entity_name: str = None) -> str:
    """Convenience function to get entity summary."""
    extractor = get_episodic_extractor()
    return extractor.get_entity_summary(memory, entity_name)

# Backward compatibility aliases
def extract_author_comment_memory(text: str, author: str, content_type: str = "comment", episode_id: str = None) -> EpisodicMemory:
    """Backward compatibility function for author-comment memory extraction."""
    return extract_content_relation_memory(
        content=text,
        entity_name=author,
        entity_type="author",
        content_type=content_type,
        relationship_type="created",
        episode_id=episode_id
    )

def get_author_relations_summary(memory: EpisodicMemory) -> str:
    """Backward compatibility function for author relations summary."""
    return get_content_relations_summary(memory)
