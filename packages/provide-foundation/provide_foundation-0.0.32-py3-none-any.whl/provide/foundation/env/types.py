from __future__ import annotations


"""
Type definitions for environment utilities.
"""
from collections.abc import Callable
from typing import Any, TypeAlias





# Basic environment value types
EnvValue: TypeAlias = str | int | float | bool | None
EnvDict: TypeAlias = dict[str, EnvValue]

# Secret reference types
SecretRef: TypeAlias = str  # e.g., "file:///path/to/secret"

# Parser function type
EnvParser: TypeAlias = Callable[[str], Any]


__all__ = [
    "EnvDict",
    "EnvParser",
    "EnvValue",
    "SecretRef",
]