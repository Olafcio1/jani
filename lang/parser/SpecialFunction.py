from enum import Enum

class SpecialFunction(Enum):
    HEADER = 0
    """Called at the start of the file."""

    PANIC = 1
    """Called at the `panic` keyword."""
