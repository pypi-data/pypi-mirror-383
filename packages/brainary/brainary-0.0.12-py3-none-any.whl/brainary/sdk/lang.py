from functools import wraps
import inspect
import logging
from typing import Any, Callable, List, Dict, Union, Optional

from brainary.core.ops import *
from brainary.core.vm_bus import VMBus

def define_type(type_name, **fields: Dict[str, Dict[str, Any]]) -> TypeOp:
    """
    Dynamically defines a structured data type (class) with named fields and metadata, suitable for use in brainary workflows or schema definitions.

    Args:
        **fields: Each keyword argument defines a field, where:
            - The key is the field name (str).
            - The value is a dictionary containing:
                - "type": the expected Python type (or nested brainary type).
                - "desc": a human-readable description.
                - Optionally: "default" or other metadata.

    Returns:
        A new class with:
            - Strict field validation on initialization.
            - Field access via attributes.
            - `.to_dict()` method for serialization.
            - `.schema()` method to inspect field metadata.

    Example:
        >>> Review = brainary.define_type(
        ...     type_name="Review",
        ...     text={"type": str, "desc": "review content"},
        ...     author={"type": str, "desc": "reviewer name"}
        ... )
        >>> Movie = brainary.define_type(
        ...     type_name="Movie",
        ...     title={"type": str, "desc": "movie title"},
        ...     year={"type": int, "desc": "release year"},
        ...     reviews={"type": list[Review], "desc": "list of Review objects"}
        ... )
        >>> m = Movie(
        ...     title='Matrix',
        ...     year=1999,
        ...     reviews=[Review(text="Amazing!", author="Bob")]
        ... )
        >>> print(m.title)  # 'Matrix'
        >>> print(m.to_dict())  # {'title': 'Matrix', 'year': 1999, 'reviews': [...]}
    """
    
    field_names = list(fields.keys())
    field_meta = fields
    
    def wrapped_init(type_op, **kwargs):
        # Call original __init__
        TypeOp.__init__(type_op, **kwargs)
        VMBus.dispatch(type_op)

    # Create a new subclass of TypeOp with dynamic __slots__ and __schema__
    cls = type(
        type_name,
        (TypeOp,),
        {
            "__slots__": field_names,
            "__schema__": field_meta,
            "__init__": wrapped_init
        }
    )
    return cls


def define_action(
    instruction: str,
    *params: str,
    executable: Optional[Callable[..., Any]] = None,
    contexts: Optional[List[Any]] = None,
    tools: Optional[List[Any]] = None,
    input_constraints: Optional[Dict[str, Any]] = None,
    output_constraints: Optional[Dict[str, Any]] = None,
    callbacks: Optional[List[Callable[[Any], Any]]] = None,
    attentions: Optional[List[str]] = None,
    energy: Optional[int] = None,
    planning: Optional[str] = None,
    reasoning: Optional[str] = None,
    problem_solving: Optional[str] = None,
    critical_thinking: Optional[str] = None,
) -> Callable:
    """
    Creates an Action object with a natural language instruction, named parameters, and optional logic encapsulated via an executable hook, constraints, and post-processing.

    Args:
        instruction (str): A LLM-readable instruction describing the action.
        *params (str): Names of required input parameters.
        executable (callable, optional): A function implementing the action logic.
            If provided, it will be called with the given parameters during execution.
        contexts (list, optional): Additional context objects or data influencing the action.
        tools (list, optional): Available tools for executing the action.
        input_constraints (dict, optional): Rules for validating input parameters (e.g., sentiment type, format).
        output_constraints (dict, optional): Rules for enforcing response criteria (e.g., word count limits, tone).
        callbacks (list of callable, optional): Functions to post-process the result.
        attentions (list of callable, optional): Attention that the LLMs should focus on when executing the action.
        energy (int, optional): Energy (e.g., token budget) to execute the action.
        planning (str, optional): Planning strategy used to perform the action.
        reasoning (str, optional): Reasoning strategy used to perform the action.
        problem_solving (str, optional): Problem solving strategy used to perform the action.
        critical_thinking (str, optional): Critical thinking strategy used to perform the action.

    Returns:
        A callable Action object with a `.__call__(**kwargs)` method that executes the action. The provided **kwargs must align with the declared `*params` in both name and structure.

    Example:
        >>> Review = brainary.define_type(type_name="Review", text={"type": str, "desc": "review"}, author={"type": str, "desc": "reviewer"})
        >>> Movie = brainary.define_type(
        ...     type_name="Movie", 
        ...     title={"type": str, "desc": "movie title"},
        ...     year={"type": int, "desc": "release year"},
        ...     reviews={"type": list[Review], "desc": "list of reviews"}
        ... )
        >>> summarize = brainary.define_action("Summarize the review", "text", output_constraints={"tone": "sharp"}, thinking="critical")
        >>> summaries = [summarize(text=r.text) for r in movie.reviews]
    """
    logging.debug(f"[Instruction: {instruction}] → Input: {params}")

    contexts = contexts or []
    tools = tools or []
    input_constraints = input_constraints or {}
    output_constraints = output_constraints or {}
    attentions = attentions or []
    callbacks = callbacks or []

    class Action(Callable):
        def __call__(self, **kwargs):
            if executable and isinstance(executable, Callable):
                result = executable(**kwargs)
            else:
                action_op = ActionOp(
                    instruction,
                    *params,
                    contexts=contexts,
                    tools=tools,
                    input_constraints=input_constraints,
                    output_constraints=output_constraints,
                    callbacks=callbacks,
                    attentions=attentions,
                    energy=energy,
                    problem_solving=problem_solving,
                    critical_thinking=critical_thinking,
                )
                result = VMBus.dispatch(action_op, **kwargs)
            
            for cb in callbacks:
                result = cb(result)

            return result
    
    return Action()
    

def examine(
    condition: str,
    contexts: Optional[List[Any]] = None,
    attentions: Optional[List[str]] = None,
    thinking: Optional[str] = None,
    **kwargs,
) -> bool:
    """
    Examine a conditional logic unit for control flow in brainary.

    Args:
        condition (str): A natural language or logical condition that the LLM
                         or system will evaluate to True or False.
        contexts (list, optional): Additional context objects or data influencing the examination.
        attentions (list of callable, optional): Attention that the LLMs should focus on when executing the examination.
        thinking (str, optional): Strategy used to guide the examination.
        **kwargs: Arguments for executing the examination.

    Returns:
        A bool variable for decision-making in control flow.

    Example:
        Example:
        >>> if brainary.examine("The sentiment of the review is positive."):
        ...     print("Positive")
    """
    logging.debug(f"[Condition: {condition}] → Input: {kwargs}")
    examine_op = ExamineOp(
        condition, 
        *(kwargs.keys()),
        contexts=contexts,
        attentions=attentions,
        thinking=thinking
    )
    # frame = inspect.currentframe().f_back
    # print(f"LOCALS: {frame.f_locals}")
    return VMBus.dispatch(examine_op, **kwargs)



def tool(
    func: Callable,
) -> Any:
    """
    Wraps a function as a Tool object for use in promptware workflows.
    This is typically used to expose external tools or APIs to LLMs.

    Args:
        func (Callable): A Python function whose docstring describes the tool's behavior.

    Returns:
        Tool: An object that can be invoked by actions.

    Example:
        >>> @brainary.tool
        ... def get_weather(city: str):
        ...     '''Retrieve current weather information for a given city.'''
        ...     # implementation logic
        ...
        >>> recommend = promptware.define_action(
        ...     "Recommend a trip plan",
        ...     "city",
        ...     contexts=[...],
        ...     tools=[get_weather]
        ... )
        >>> recommend(city="New York")
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def context(name: str, value: Union[str, Dict[str, Any]]) -> Any:
    """
    Defines a reusable context.

    Args:
        name (str): The name of the context.
        value (str or dict): A string (raw instruction) or dictionary (structured context) that represents reusable prompt metadata or guidance for an LLM.

    Returns:
        A context object or formatted string for internal use.

    Example:
        >>> cutoff = brainary.context(name="cutoff", value={"cutoff_year": "2023"})
        >>> language = brainary.context(name="lang", value="The given input is written in Chinese")
    """
    ctx_op = CtxOp(name=name, value=value)
    VMBus.dispatch(ctx_op)


def constraint(value: Union[str, Dict[str, Any]]) -> Any:
    """
    Defines a constraint.

    Args:
        value (str or dict): A string (raw instruction) or dictionary (structured context) that represents constraint for an action or object.

    Returns:
        A constraint object or formatted string for internal use.

    Example:
        >>> word_limit = brainary.constraint({"word number": 50})
        >>> language = brainary.constraint("The output should be in Chinese")
    """
    return {"type": "constraint", "value": value}



def loop(iterable: Union[str, list, tuple]) -> Any:
    """
    Wraps an iterable or iterable description into a loop structure suitable for use in a brainary.

    Args:
        iterable (str | list | tuple): Either a string describing the iterable (e.g., "a list of API calls") or an actual iterable like a list or tuple.

    Returns:
        A loop wrapper object for brainary systems.

    Example:
        >>> m = Movie(
        ...     title='Matrix',
        ...     year=1999,
        ...     reviews=[Review(text="Amazing!", author="Bob")]
        ... )
        >>> for review in brainary.loop(m.reviews):
        >>>     print(item)
    """
    return {"type": "loop", "iterable": iterable}





def exception(desc: str) -> Any:
    """
    Defines a structured exception block for representing a failure, warning,
    or recoverable error in a brainary execution flow.

    Args:
        desc (str): A natural language description of the error condition to handle.

    Returns:
        dict: A structured exception representation for downstream control flow.

    Example:
        >>> try:
        >>>     do_something()
        >>> except brainary.exception("API call fails") as e:
        >>>     retry(e)
    """
    return {"type": "exception", "description": desc}


def roleplay(role: str) -> Dict[str, str]:
    """
    Assigns a persona, identity, or behavioral context to the model.

    Args:
        role (str): A natural language description of the model's role or persona.

    Returns:
        dict: A structured role descriptor for use in prompt-based systems.

    Example:
        >>> advisor = brainary.roleplay("You are a legal advisor.")
        >>> print(advisor)
        {'type': 'roleplay', 'role': 'You are a legal advisor.'}
    """
    return {"type": "roleplay", "role": role}


def examples(example_list: List[Dict[str, Any]]) -> Any:
    """
    Creates a structured set of few-shot examples for in-context learning,
    typically used to guide LLM behavior.

    Args:
        example_list (List[Dict[str, Any]]): 
            A list of example dictionaries, each containing 'input' and 'output' keys.

    Returns:
        dict: A structured object representing reusable few-shot examples.

    Example:
        >>> ex = brainary.examples([
        >>>     {"input": "2 + 2", "output": "4"},
        >>>     {"input": "3 * 5", "output": "15"}
        >>> ])
    """
    return {"type": "examples", "data": example_list}


__all__ = ["define_type", "define_action", "examine", "context", "tool"]
