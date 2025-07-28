import string

from ..token import Token

from .BaseLexer import BaseLexer
from .LexerError import LexerError
from .Special import *

class Lexer(BaseLexer):
    def __init__(self, data: bytes):
        self._input = data.decode("utf-8", "surrogateescape").replace("\r\n", "\n").replace("\r", "\n")
        self._index = 0
        self._output = []

    def run(self) -> list[Token]:
        while ch := self.consume():
            if cm := self.now(COMMENTS):
                self.handleComment(cm)
            elif op := self.now(OPERATORS):
                self.addToken("operator", value=op, meaning=OPERATORS[op])
            elif kw := self.now(KEYWORDS):
                self.addToken("keyword", value=kw, meaning=KEYWORDS[kw])
            elif kc := self.now(Keychars.string.value):
                self.handleString(kc, interpolation=True)
            elif kc := self.now(Keychars.no_escape_string.value):
                self.handleString(kc, escaping=False)
            elif ch in string.digits:
                self.handleNumber(ch)
            elif ch in (" ", "\n"):
                pass
            elif th := self.now(NONLITERAL):
                raise LexerError("Unexpected %r" % th)
            else:
                self.handleLiteral(ch)

        return self._output

    def handleLiteral(self, val: str) -> None:
        while ch := self.consume():
            if ch in NONLITERAL:
                self._index -= 1
                break
            else:
                val += ch

        self.addToken("literal", value=val)

    def handleString(self, surround: str, *, multiline: bool = True, escaping: bool = True, interpolation: bool = False) -> None:
        val = ""
        vals = []
        ended = False

        def finish():
            nonlocal val, vals
            if val != "":
                vals.append({
                    "type": "text",
                    "value": val
                })
                val = ""

        while ch := self.consume():
            if sur := self.now([surround]):
                if not escaping and self.now(Keychars.escape.value, before=-len(surround) - 1):
                    val += sur
                else:
                    ended = True
                    break
            elif (esc := self.now(Keychars.escape.value)) and escaping:
                nxt = self.consume()
                if nxt == "n":
                    val += "\n"
                elif nxt == "r":
                    val += "\r"
                elif nxt == "t":
                    val += "\t"
                elif nxt in (surround, "%"):
                    val += nxt
                else:
                    val += esc + nxt
            elif self.now(Keychars.interp.value) and interpolation:
                var = ""

                while ch := self.consume():
                    if self.now(Keychars.interp.value):
                        break
                    else:
                        var += ch

                finish()
                vals.append({
                    "type": "var",
                    "value": var
                })
            elif ch == "\n" and not multiline:
                raise LexerError("This string type doesn't support file newlines")
            else:
                val += ch

        if not ended:
            raise LexerError("Non-terminated string")

        finish()
        self.addToken("string", value=vals)

    def handleNumber(self, val: str) -> None:
        while ch := self.consume():
            if ch in string.digits or (
                ch == "." and
                "." not in val and
                self.advance(1) in string.digits
            ):
                val += ch
            else:
                self._index -= 1
                break

        self.addToken("number", value=val)

    def handleComment(self, start: str) -> None:
        end = COMMENTS[start]
        ended = False

        while self.consume():
            if self.now([end]):
                ended = True
                break

        if not ended:
            raise LexerError("A comment must have an end")
