from typing import Any, Iterable

from ..token import Token

class BaseLexer():
    _input: str
    _index: int
    _output: list[Token]

    def consume(self, length: int = 1) -> str:
        oldIndex = self._index
        newIndex = oldIndex + length
        self._index = newIndex
        return self._input[oldIndex:newIndex]

    def advance(self, after: int = 0, length: int = 1) -> str:
        index = self._index + after
        return self._input[index:index + length]

    def now(self, options: Iterable[str], *, before: int = 1) -> str | None:
        options = [*options]
        options.sort(key=lambda opt: opt, reverse=True)

        for opt in options:
            length = len(opt)

            if self.advance(-before, length) != opt:
                continue

            self.consume(max(0, length - before))
            return opt

    def addToken(self, kind: str, properties: dict[str, Any] = {}, **kwproperties: dict[str, Any]) -> None:
        self._output.append(Token(kind, {
            **properties,
            **kwproperties
        }))
