from enum import Enum
from .Type import Type

class PrimitiveType(Type, Enum):
    NULL = 0
    TEXT = 1
    INTEGER = 2
    FLOAT = 3
    BOOLEAN = 4
    RGB = 5
    FUNCTION = 6
