class StringLiType():
    def __init__(self, value: str) -> None:
        self.literal = value

    literal: str
    """String-literal types do not support interpolation in the build-time — if a string that the type of should be this has it, it's checked only during runtime."""
