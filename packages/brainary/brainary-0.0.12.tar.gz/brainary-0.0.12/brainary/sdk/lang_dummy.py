from functools import wraps
import inspect
import logging
from typing import Any, Callable, Iterable, List, Dict, Union, Optional

def define_type(type_name, **fields: Dict[str, Dict[str, Any]]) -> type:
    """
    Dynamically defines a structured data type (class) with named fields and metadata, suitable for use in promptware workflows or schema definitions.

    Args:
        **fields: Each keyword argument defines a field, where:
            - The key is the field name (str).
            - The value is a dictionary containing:
                - "type": the expected Python type (or nested promptware type).
                - "desc": a human-readable description.
                - Optionally: "default" or other metadata.

    Returns:
        A new class with:
            - Strict field validation on initialization.
            - Field access via attributes.
            - `.to_dict()` method for serialization.
            - `.schema()` method to inspect field metadata.

    Example:
        >>> Review = promptware.define_type(
        ...     type_name="Review",
        ...     text={"type": str, "desc": "review content"},
        ...     author={"type": str, "desc": "reviewer name"}
        ... )
        >>> Movie = promptware.define_type(
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
    pass


def define_action(
    instruction: str,
    *params: str,
    executable: Optional[Callable[..., Any]] = None,
    contexts: Optional[List[Any]] = None,
    tools: Optional[List[Any]] = None,
    input_constraints: Optional[Dict[str, Any]] = None,
    output_constraints: Optional[Dict[str, Any]] = None,
    examples: Any = None,
    callbacks: Optional[List[Callable[[Any], Any]]] = None,
) -> Callable:
    """
    Creates an Action object with a natural language instruction, named parameters, and optional logic encapsulated via an executable hook, constraints, and post-processing.

    Args:
        instruction (str): A LLM-readable instruction describing the action.
        *params (str): Names of required input parameters.
        executable (callable, optional): A function implementing the action logic.
            If provided, it will be called with the given parameters during execution.
        contexts (list, optional): Additional context objects or data influencing the action.
        tools (list, optional): Additional tool objects possibly used in the action.
        input_constraints (dict, optional): Rules for validating input parameters (e.g., sentiment type, format).
        output_constraints (dict, optional): Rules for enforcing response criteria (e.g., word count limits, tone).
        examples (optional): Examples for referencing.
        callbacks (list of callable, optional): Functions to post-process the result.

    Returns:
        A callable Action object with a `.__call__(**kwargs)` method that executes the action. The provided **kwargs must align with the declared `*params` in both name and structure.

    Example:
        >>> Review = promptware.define_type(type_name="Review", text={"type": str, "desc": "review"}, author={"type": str, "desc": "reviewer"})
        >>> Movie = promptware.define_type(
        ...     type_name="Movie", 
        ...     title={"type": str, "desc": "movie title"},
        ...     year={"type": int, "desc": "release year"},
        ...     reviews={"type": list[Review], "desc": "list of reviews"}
        ... )
        >>> summarize = promptware.define_action("Summarize the review", "text", output_constraints={"tone": "sharp"}, contexts=[...], tools=[...])
        >>> summaries = [summarize(text=r.text) for r in movie.reviews]
    """
    pass
    

def examine(
    condition: str,
    contexts: Optional[List[Any]] = None,
    **kwargs,
) -> bool:
    """
    Examine a conditional logic unit for control flow in promptware.

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
        >>> if promptware.examine("The sentiment of the review is positive."):
        ...     print("Positive")
    """
    pass



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
        >>> def get_weather(city: str):
        ...     '''Retrieve current weather information for a given city.'''
        ...     # implementation logic
        ...
        >>> get_weather_tool = promptware.tool(get_weather)
        >>> recommend = promptware.define_action(
        ...     "Recommend a trip plan",
        ...     "city",
        ...     contexts=[...],
        ...     tools=[get_weather_tool]
        ... )
        >>> recommend(city="New York")
    """
    pass


def context(name: str, value: Union[str, Dict[str, Any]]) -> Any:
    """
    Defines a reusable context.

    Args:
        name (str): The name of the context.
        value (str or dict): A string (raw instruction) or dictionary (structured context) that represents reusable prompt metadata or guidance for an LLM.

    Returns:
        A context object or formatted string for internal use.

    Example:
        >>> cutoff = promptware.context(name="cutoff", value={"cutoff_year": "2023"})
        >>> language = promptware.context(name="lang", value="The given input is written in Chinese")
    """
    pass


def constraint(value: Union[str, Dict[str, Any]]) -> Any:
    """
    Defines a constraint.

    Args:
        value (str or dict): A string (raw instruction) or dictionary (structured context) that represents constraint for an action or object.

    Returns:
        A constraint object or formatted string for internal use.

    Example:
        >>> word_limit = promptware.constraint({"word number": 50})
        >>> language = promptware.constraint("The output should be in Chinese")
    """
    pass



def loop(iterable: Union[str, list, tuple]) -> Iterable:
    """
    Wraps an iterable or iterable description into a loop structure suitable for use in a promptware.

    Args:
        iterable (str | list | tuple): Either a string describing the iterable (e.g., "a list of API calls") or an actual iterable like a list or tuple.

    Returns:
        A loop wrapper object for promptware systems.

    Example:
        >>> m = Movie(
        ...     title='Matrix',
        ...     year=1999,
        ...     reviews=[Review(text="Amazing!", author="Bob")]
        ... )
        >>> for review in promptware.loop(m.reviews):
        >>>     print(item)
    """
    pass



def exception(desc: str) -> Exception:
    """
    Defines a structured exception block for representing a failure, warning,
    or recoverable error in a promptware execution flow.

    Args:
        desc (str): A natural language description of the error condition to handle.

    Returns:
        dict: A structured exception representation for downstream control flow.

    Example:
        >>> try:
        >>>     do_something()
        >>> except promptware.exception("API call fails") as e:
        >>>     retry(e)
    """
    pass


def roleplay(role: str):
    """
    Assigns a persona, identity, or behavioral context to the model.

    Args:
        role (str): A natural language description of the model's role or persona.

    Returns:
        dict: A structured role descriptor for use in prompt-based systems.

    Example:
        >>> promptware.roleplay("You are a legal advisor.")
    """
    pass


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
        >>> ex = promptware.examples([
        >>>     {"input": "2 + 2", "output": "4"},
        >>>     {"input": "3 * 5", "output": "15"}
        >>> ])
    """
    pass


import inspect
import sys

API_TABLE = {}
for name, func in inspect.getmembers(sys.modules[__name__], inspect.isfunction):
    signature = inspect.signature(func)
    docstring = inspect.getdoc(func)
    API_TABLE[name] = (f"{name}{signature}", docstring)

API_SPEC = "\n\n".join(f'- {func}:\n"""\n{doc}\n"""' for func, doc in API_TABLE.values())