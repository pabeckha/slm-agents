"""Pydantic models for function definitions and function call results."""

from typing import Any

from pydantic import BaseModel


class FunctionParameter(BaseModel):
    """A single parameter or return type descriptor.

    Attributes:
        type: The type string as declared in the function definition JSON
              (e.g. ``"number"``, ``"string"``, ``"boolean"``).
    """

    type: str


class FunctionDef(BaseModel):
    """A function definition loaded from ``functions_definition.json``.

    Attributes:
        name: The function identifier (e.g. ``"fn_add_numbers"``).
        description: Human-readable description of what the function does.
        parameters: Mapping from argument name to its parameter descriptor.
        returns: Descriptor for the function's return type.
    """

    name: str
    description: str
    parameters: dict[str, FunctionParameter]
    returns: FunctionParameter
    required: list[str] | None = None

    @property
    def arg_names(self) -> list[str]:
        """Return argument names in declaration order."""
        return list(self.parameters.keys())

    @property
    def arg_types(self) -> list[str]:
        """Return argument type strings in declaration order."""
        return [p.type for p in self.parameters.values()]


class FunctionCall(BaseModel):
    """One output record written to ``function_calling_results.json``.

    Attributes:
        prompt: The original natural-language request.
        fn_name: The name of the function to call.
        args: Mapping from argument name to its extracted value.
    """

    prompt: str
    fn_name: str
    args: dict[str, Any]
