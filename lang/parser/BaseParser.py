from typing import Any, overload

from ..token import Token, Undefined
from .ParserError import ParserError

class BaseParser():
    _input: list[Token]
    _index: int
    _output: list[Token]

    def consume(self) -> Token | None:
        try:
            index = self._index
            self._index += 1
            return self._input[index]
        except:
            pass

    def consumeKind(self, *kinds: str) -> Token:
        nxt = self.consume()
        if nxt == None:
            raise ParserError("Expected %s, got EOF" % "/".join(kinds))
        got = nxt.kind
        if got not in kinds:
            raise ParserError("Expected %s, got %s" % ("/".join(kinds), got))
        return nxt

    def consumeEq(self, **properties: Any) -> Token:
        nxt = self.consume()
        if nxt == None:
            raise ParserError("Expected a special token, got EOF")

        for k in properties:
            if getattr(nxt, k, Undefined) != properties[k]:
                raise ParserError("Expected a special token, got %s" % nxt.kind)

        return nxt

    def consumeEOF(self) -> None:
        nxt = self.consume()

        if nxt != None:
            raise ParserError("Expected EOF, got %s" % nxt.kind)

    def advance(self, after: int = 0) -> Token | None:
        try:
            return self._input[max(0, self._index + after)]
        except:
            pass

    def allow(self, kind: str, **properties: Any) -> Token | None:
        nxt = self.advance()
        if nxt == None:
            return None

        if nxt.kind != kind:
            return None

        for k in properties:
            if getattr(nxt, k, Undefined) != properties[k]:
                return None

        self.consume()

        return nxt

    def now(self, *tokens: str | dict[str, Any], before: int = 0) -> bool:
        for i, opt in enumerate(tokens):
            nxt = self.advance(i - before)
            if not nxt:
                return False

            if isinstance(opt, str):
                if nxt.kind != opt:
                    return False
            else:
                for k in opt:
                    if getattr(nxt, k, Undefined) != opt[k]:
                        return False

        return True

    @overload
    def addToken(self, token: Token) -> None: ...
    @overload
    def addToken(self, kind: str, properties: dict[str, Any] = {}, **kwproperties: Any) -> None: ...

    def addToken(self, kind: str | Token, properties: dict[str, Any] = {}, **kwproperties: Any) -> None:
        if isinstance(kind, Token):
            self._output.append(kind)
        else:
            self._output.append(Token(kind, {
                **properties,
                **kwproperties
            }))
