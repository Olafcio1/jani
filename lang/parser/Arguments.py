from typing import TypedDict

from .types.Type import Type

class Argument(TypedDict):
    type: Type
    optional: bool

Arguments = dict[str, Argument]
