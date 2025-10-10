from typing import Any, Callable, List, Dict, Union, Optional
import logging

MAX_ENERGY = 100000


class PromptwareType:
    """
    Runtime class representing a promptware structured type with fields,
    type checking, and serialization.
    """

    __slots__: List[str]
    __schema__: Dict[str, Dict[str, Any]]

    def __init__(self, **kwargs):
        missing = [f for f in self.__slots__ if f not in kwargs]
        if missing:
            raise TypeError(f"Missing required field(s): {missing}")

        extra = [k for k in kwargs if k not in self.__slots__]
        if extra:
            raise TypeError(f"Unexpected field(s): {extra}")

        for field in self.__slots__:
            meta = self.__schema__[field]
            expected_type = meta.get("type")
            value = kwargs[field]

            # TODO: type ckecking
            # if expected_type and not isinstance(value, expected_type):
            #     raise TypeError(f"Field '{field}' expects type {expected_type.__name__}, got {type(value).__name__}")

            setattr(self, field, value)

    def __repr__(self):
        args = ', '.join(f"{f}={repr(getattr(self, f))}" for f in self.__slots__)
        return f"{self.__class__.__name__}({args})"
    
    def render(self):
        raise NotImplementedError

    def to_dict(self):
        return {f: getattr(self, f) for f in self.__slots__}

    @classmethod
    def schema(cls):
        return cls.__schema__



class PromptwareAction:
    # TODO: support Oracle definition and verification
    """
    
    """

    def __init__(
        self,
        instruction: str,
        *params: str,
        executable: Union[str, Callable],
        contexts: Optional[List[Any]] = None,
        constraints: Optional[List[Dict[str, Any]]] = None,
        callbacks: Optional[List[Callable[[Any], Any]]] = None,
        attentions: Optional[List[Dict[str, Any]]] = None,
        energy: Optional[int] = None,
    ):
        self.instruction = instruction
        self.executable = executable
        self.params = params
        self.contexts = contexts or []
        self.constraints = constraints or []
        self.callbacks = callbacks or []
        self.attentions = attentions or []
        self.energy = energy or MAX_ENERGY

    def _check_constraints(self, **kwargs):
        for constraint in self.constraints:
            # TODO: validate constraint
            pass

    def __call__(self, **kwargs):
        missing = [p for p in self.params if p not in kwargs]
        extra = [k for k in kwargs if k not in self.params]
        if missing:
            raise TypeError(f"Missing required parameter(s): {missing}")
        if extra:
            raise TypeError(f"Unexpected parameter(s): {extra}")

        self._check_constraints(**kwargs)

        logging.debug(f"[Instruction: {self.executable}] → Input: {kwargs}")
        # Use custom function hook if provided
        if self.executable and isinstance(self.executable, Callable):
            result = self.executable(**kwargs)
        else:
            from brainary.core.vm import __LLMVM__
            if __LLMVM__ is None:
                raise RuntimeError("VM is not started")
            result = __LLMVM__.execute(self, **kwargs)

        for cb in self.callbacks:
            result = cb(result)

        return result

    def __repr__(self):
        return f"Action(instruction={self.executable!r}, params={self.params})"


class Tool:
    """
    Defines a tool-like callable object and its required parameters. Useful for external tool or API calls in promptware workflows.

    Args:
        instruction (str): A natural language instruction representing the tool's behavior.
        *params (str): Required input parameter names for the tool.

    Returns:
         A callable Tool object with a `.__call__(**kwargs)` method that executes the action. The provided `**kwargs` must align with the declared `*params` in both name and structure.

    Example:
        >>> get_weather = promptware.Tool("Get the weather", "city")
        >>> response = get_weather(city="New York")
        >>> print(response)
    """

    def __init__(self, instruction: str, *params: str):
        self.instruction = instruction
        self.params = params

    def __call__(self, **kwargs):
        missing = [p for p in self.params if p not in kwargs]
        extra = [k for k in kwargs if k not in self.params]
        if missing:
            raise TypeError(f"Missing required parameter(s): {missing}")
        if extra:
            raise TypeError(f"Unexpected parameter(s): {extra}")

        return f"[Instruction: {self.instruction}] → Input: {kwargs}"

    def __repr__(self):
        return f"Tool(instruction={self.instruction!r}, params={self.params})"


class Context:
    """
    Defines a reusable context.

    Args:
        value (str or dict): A string (raw instruction) or dictionary (structured context) that represents reusable prompt metadata or guidance for an LLM.

    Returns:
        A context object or formatted string for internal use.

    Example:
        >>> cutoff = promptware.Context({"cutoff_year": "2023"})
        >>> language = promptware.Context("The given input is written in Chinese")
    """

    def __init__(self, value: Union[str, Dict[str, Any]]):
        self.type = "context"
        self.value = value

    def __repr__(self):
        return f"Context(type={self.type!r}, value={self.value!r})"

    def to_dict(self):
        return {"type": self.type, "value": self.value}


class Constraint:
    """
    Defines a constraint.

    Args:
        value (str or dict): A string (raw instruction) or dictionary (structured context) that represents constraint for an action or object.

    Returns:
        A constraint object or formatted string for internal use.

    Example:
        >>> word_limit = promptware.Constraint({"word number": 50})
        >>> language = promptware.Constraint("The output should be in Chinese")
    """

    def __init__(self, value: Union[str, Dict[str, Any]]):
        self.type = "constraint"
        self.value = value

    def __repr__(self):
        return f"Constraint(type={self.type!r}, value={self.value!r})"

    def to_dict(self):
        return {"type": self.type, "value": self.value}


class Loop:
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
        >>> for review in promptware.Loop(m.reviews):
        >>>     print(item)
    """

    def __init__(self, iterable: Union[str, list, tuple]):
        self.type = "loop"
        self.iterable = iterable

    def __repr__(self):
        return f"Loop(type={self.type!r}, iterable={self.iter}"
