from ..token import Token

class BaseBuilder():
    _input: list[Token]
    _index: int
    _output: str

    def consume(self) -> Token | None:
        try:
            index = self._index
            self._index += 1
            return self._input[index]
        except:
            pass

    def advance(self, after: int = 0) -> Token | None:
        try:
            return self._input[max(0, self._index + after)]
        except:
            pass
