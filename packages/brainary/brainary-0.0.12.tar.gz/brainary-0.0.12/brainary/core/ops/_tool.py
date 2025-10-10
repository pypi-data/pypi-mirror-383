from typing import Any, Callable, List, Dict, Union, Optional
import logging

class PromptwareTool:
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
        return f"PromptwareTool(instruction={self.instruction!r}, params={self.params})"