from enum import Enum

class CallMode(Enum):
    background = 0
    """Processes operations such as function calls in separate threads."""

    foreground = 1
    """Processes operations such as function calls in the current thread."""
