from abc import ABC, abstractmethod
from typing import Any

class Generator(ABC):
    _filename: str
    _command: str
    _input: bytes

    def __init__(self, dropName: str, command: str, input: bytes) -> None:
        self._filename = dropName
        self._command = command
        self._input = input
        self._lastLine = 0

    @abstractmethod
    def _run(self) -> str: ...

    def run(self) -> str:
        res = self._run()
        if self._lastLine:
            print()
        return res

    _lastLine: int

    def print(self, *text: Any, back: bool = False, paddingRight: int = 0) -> str:
        line = " ".join([str(e) for e in text])
        if back:
            spaces = self._lastLine - len(line) + paddingRight
            print("\r" + line + (" " * spaces) + ("\x08" * spaces), end="")
        else:
            print(line)
            self._lastLine = len(line)
        self._lastLine = len(line)
