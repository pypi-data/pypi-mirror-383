# core/ops/type_op.py
from typing import Any, List, Dict, Union, Optional, Mapping, Iterable
import json  # For potential JSON handling

from brainary.core.ops.base_op import BaseOp

INDENT_UNIT = "  "

class TypeOp(BaseOp):
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

            if expected_type and not isinstance(value, expected_type):
                raise TypeError(f"Field '{field}' expects type {expected_type.__name__}, got {type(value).__name__}")

            setattr(self, field, value)

    def __repr__(self):
        return self.obj_repr(indent=0)

    @classmethod
    def type_repr(cls):
        param_info = "\n".join(f"   - field `{name} ({meta['type'].__name__})`: {meta['desc']}" for name, meta in cls.__schema__.items())
        return f"class `{cls.__name__}`:\n{param_info}"

    def obj_repr(self, indent=0):
        indent_str = INDENT_UNIT * indent
        next_indent_str = INDENT_UNIT * (indent + 1)
        cls_name = self.__class__.__name__

        lines = [f"{cls_name}("]
        for key in self.__slots__:
            value = getattr(self, key)
            desc = self.__schema__[key]["desc"].strip()
            if desc:
                lines.append(f"{next_indent_str}# {desc}")
            formatted_value = self._format_value(value, indent + 1)
            lines.append(f"{next_indent_str}{key}={formatted_value},")
        lines.append(f"{indent_str})")
        return '\n'.join(lines)

    def _format_value(self, value, indent, max_depth=5):
        if max_depth <= 0:
            return "<truncated>"

        indent_str = INDENT_UNIT * indent

        # If value is a nested instance of this mixin, recurse
        if isinstance(value, TypeOp):
            return value.obj_repr(indent=indent)

        # Don't treat strings/bytes as iterables
        if isinstance(value, (str, bytes)):
            return repr(value)

        # Handle mappings (dict)
        if isinstance(value, Mapping):
            if not value:
                return "{}"
            items = []
            for k, v in value.items():
                k_repr = repr(k)
                v_repr = self._format_value(v, indent + 1, max_depth - 1)
                items.append(f"\n{indent_str}{INDENT_UNIT}{k_repr}: {v_repr}")
            return f"{{{''.join(items)}\n{indent_str}}}"

        # Handle other iterables (list, set, tuple, etc.)
        if isinstance(value, Iterable):
            if not value:
                return repr(value)
            open_char = "[" if isinstance(value, list) else "(" if isinstance(value, tuple) else "{" if isinstance(value, set) else "<"
            close_char = "]" if isinstance(value, list) else ")" if isinstance(value, tuple) else "}" if isinstance(value, set) else ">"
            items = [
                f"\n{indent_str}{INDENT_UNIT}{self._format_value(item, indent + 1, max_depth - 1)}"
                for item in value
            ]
            return f"{open_char}{''.join(items)}\n{indent_str}{close_char}"

        # Fallback for non-iterables
        return repr(value)

    def render(self, **kwargs):
        prompt = (
            f"{self.__class__.type_repr()}\n\n"
            f"An `{self.__class__.__name__}` instance:\n"
            f"{self.obj_repr()}\n\n"
        )
        return prompt

    def to_dict(self):
        return {f: getattr(self, f) for f in self.__slots__}

    @classmethod
    def schema(cls):
        return cls.__schema__