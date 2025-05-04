import os

from typing import Literal, overload

from ..lexer import Lexer
from ..lexer.Special import Keywords, Operators
from ..token import Token

from .BaseParser import BaseParser
from .ParserError import ParserError

from .CallMode import CallMode
from .MathOp import MathOp
from .SpecialFunction import SpecialFunction

from .types.PrimitiveType import PrimitiveType
from .types.BooleanType import BooleanType
from .types.StringLiType import StringLiType
from .types.Type import Type

class Parser(BaseParser):
    filepath: str | None
    _filedir: str | None

    def __init__(self, data: list[Token], filepath: str | None = None):
        self._input = data
        self._index = 0
        self._output = []

        self.filepath = filepath
        self._filedir = None if filepath == None else os.path.sep.join(filepath.replace('\\', '/').split('/')[:-1])

    def run(self) -> list[Token]:
        while self.advance():
            if tok := self.parseStatement():
                self.addToken(tok)
            else:
                raise ParserError("Unexpected %s" % self.consume())

        return self._output

    def parseCall(self) -> Token:
        name = self.consumeKind("literal").value
        self.consumeEq(kind="operator", meaning=Operators.parenOpen)

        args = {}

        while self.advance():
            if self.allow(kind="operator", meaning=Operators.parenClose):
                break

            key = self.consumeKind("literal").value
            self.consumeEq(kind="operator", meaning=Operators.semicolon)
            value = self.parseExpression()

            args[key] = value

        return Token("call", {
            "func": name,
            "args": args
        })

    def parseMode(self) -> Token:
        self.consumeEq(kind="keyword", meaning=Keywords.mode)

        if self.allow("keyword", meaning=Keywords.background):
            return Token("mode-change", {
                "value": CallMode.background
            })
        elif self.allow("keyword", meaning=Keywords.foreground):
            return Token("mode-change", {
                "value": CallMode.foreground
            })
        else:
            raise ParserError("Expected 'background' or 'foreground' after the 'mode' keyword")

    def parsePanic(self) -> Token:
        self.consumeEq(kind="keyword", meaning=Keywords.panic)

        return Token("panic")

    def parseRepeatTimes(self) -> Token:
        self.consumeEq(kind="keyword", meaning=Keywords.repeatTimes)
        times = self.consumeKind("number").value
        body = self.parseCode()

        parsed = Parser(body).run()

        return Token("repeat-times", {
            "times": times,
            "body": parsed
        })

    def parseWhile(self) -> Token:
        self.consumeEq(kind="keyword", meaning=Keywords.while_)
        expr = self.parseExpression()
        body = self.parseCode()

        parsed = Parser(body).run()

        return Token("while", {
            "expr": expr,
            "body": parsed
        })

    def parseIf(self) -> Token:
        self.consumeEq(kind="keyword", meaning=Keywords.if_)
        expr = self.parseExpression()
        body = self.parseCode()

        parsed = Parser(body).run()

        return Token("if", {
            "expr": expr,
            "body": parsed
        })

    def parseMath(self) -> Token:
        self.consumeEq(kind="operator", meaning=Operators.curlyOpen)

        a = self.consumeKind("number")

        if self.allow(kind="operator", meaning=Operators.plus):
            op = MathOp.add
        elif self.allow(kind="operator", meaning=Operators.minus):
            op = MathOp.subtract
        elif self.allow(kind="operator", meaning=Operators.star):
            op = MathOp.multiply
        elif self.allow(kind="operator", meaning=Operators.slash):
            op = MathOp.divide
        elif self.allow(kind="operator", meaning=Operators.dash):
            op = MathOp.exponentiate
        elif self.allow(kind="operator", meaning=Operators.xor):
            op = MathOp.xor
        elif self.allow(kind="operator", meaning=Operators.xand):
            op = MathOp.xand
        else:
            raise ParserError("Expected math operation")

        b = self.consumeKind("number")

        self.consumeEq(kind="operator", meaning=Operators.curlyClose)

        return Token("math-op", {
            "a": a,
            "b": b,
            "op": op
        })

    @overload
    def parseExpression(self, require: Literal[True] = True) -> Token: ...
    @overload
    def parseExpression(self, require: Literal[False]) -> Token: ...

    def parseExpression(self, require: bool = True) -> Token | None:
        if self.now("literal", {
            "kind": "operator",
            "meaning": Operators.parenOpen
        }):
            return self.parseCall()
        elif self.now({
            "kind": "keyword",
            "meaning": Keywords.foreground
        }):
            self.consumeEq(kind="keyword", meaning=Keywords.foreground)
            return Token("call-with-mode", {
                "mode": CallMode.foreground,
                "call": self.parseCall()
            })
        elif self.now({
            "kind": "keyword",
            "meaning": Keywords.background
        }):
            self.consumeEq(kind="keyword", meaning=Keywords.background)
            return Token("call-with-mode", {
                "mode": CallMode.background,
                "call": self.parseCall()
            })
        elif self.now("string") or self.now("number"):
            return self.consume()
        elif self.now({
            "kind": "operator",
            "meaning": Operators.curlyOpen
        }):
            return self.parseMath()
        elif self.now({
            "kind": "keyword",
            "meaning": Keywords.not_
        }):
            self.consumeEq(kind="keyword", meaning=Keywords.not_)
            return Token("inverted-value", {
                "expr": self.parseExpression()
            })
        elif require:
            raise ParserError("Expected expression")

    def parseStatement(self) -> Token | None:
        if output := self.parseExpression(False):
            pass
        elif self.now({
            "kind": "keyword",
            "meaning": Keywords.mode
        }):
            output = self.parseMode()
        elif self.now({
            "kind": "keyword",
            "meaning": Keywords.panic
        }):
            output = self.parsePanic()
        elif self.now({
            "kind": "keyword",
            "meaning": Keywords.repeatTimes
        }):
            output = self.parseRepeatTimes()
        elif self.now({
            "kind": "keyword",
            "meaning": Keywords.while_
        }):
            output = self.parseWhile()
        elif self.now({
            "kind": "keyword",
            "meaning": Keywords.if_
        }):
            output = self.parseIf()
        elif self.now({
            "kind": "keyword",
            "meaning": Keywords.function
        }):
            return self.parseFunctionDef()
        elif self.now({
            "kind": "keyword",
            "meaning": Keywords.include
        }):
            output = self.parseInclude()
        elif self.now({
            "kind": "keyword",
            "meaning": Keywords.staticInclude
        }):
            output = self.parseStaticInclude()
        elif self.now({
            "kind": "keyword",
            "meaning": Keywords.declare
        }):
            output = self.parseDeclare()
        elif self.now({
            "kind": "keyword",
            "meaning": Keywords.bind
        }):
            output = self.parseBind()
        elif self.now({
            "kind": "keyword",
            "meaning": Keywords.var
        }):
            output = self.parseVar()
        elif self.now({
            "kind": "keyword",
            "meaning": Keywords.const
        }):
            output = self.parseConst()
        else:
            return

        self.consumeEq(kind="operator", meaning=Operators.colon)
        return output

    def parseType(self) -> Type:
        if self.allow("keyword", meaning=Keywords.null):
            return PrimitiveType.NULL
        elif self.allow("keyword", meaning=Keywords.text):
            return PrimitiveType.TEXT
        elif self.allow("keyword", meaning=Keywords.integer):
            return PrimitiveType.INTEGER
        elif self.allow("keyword", meaning=Keywords.float):
            return PrimitiveType.FLOAT
        elif self.allow("keyword", meaning=Keywords.boolean):
            return PrimitiveType.BOOLEAN
        elif self.allow("keyword", meaning=Keywords.rgb):
            return PrimitiveType.RGB
        elif self.allow("keyword", meaning=Keywords.function_type):
            return PrimitiveType.FUNCTION
        elif self.allow("keyword", meaning=Keywords.true):
            return BooleanType.TRUE
        elif self.allow("keyword", meaning=Keywords.false):
            return BooleanType.FALSE
        elif self.allow("keyword", meaning=Keywords.any):
            return Type.ANY
        elif tok := self.allow("string"):
            value = tok.value
            if len(value) != 1 or value[0]['type'] != 'text':
                raise ParserError("String-literal types cannot include interpolation")
            return StringLiType(value)
        else:
            raise ParserError("Expected a type")

    def parseFunctionSignature(self, modifiersAvailable: list[Token] = []):
        modifiers = []

        while self.allow("operator", meaning=Operators.angleOpen):
            kw = self.consumeKind("keyword").value
            if kw in modifiers:
                raise ParserError("Modifier %r already used" % kw)
            elif kw not in modifiersAvailable:
                raise ParserError("Expected a function modifier keyword, got %r" % kw)
            modifiers.append(kw)
            self.consumeEq(kind="operator", meaning=Operators.angleClose)

        name = self.consumeKind("literal").value

        self.consumeEq(kind="operator", meaning=Operators.parenOpen)
        args = {}

        while self.advance():
            if self.allow(kind="operator", meaning=Operators.parenClose):
                break

            isOptional = bool(self.allow("keyword", meaning=Keywords.optional))

            key = self.consumeKind("literal").value
            self.consumeEq(kind="operator", meaning=Operators.semicolon)
            value = self.parseType()

            args[key] = {
                "type": value,
                "optional": isOptional
            }

        self.consumeEq(kind="operator", meaning=Operators.semicolon)
        retType = self.parseType()

        return name, args, retType, modifiers

    def parseCode(self) -> list[Token]:
        self.consumeEq(kind="operator", meaning=Operators.parenOpen)
        body = []
        parens = 1

        while tok := self.consume():
            if tok.eq(kind="operator", meaning=Operators.parenOpen):
                parens += 1
            elif tok.eq(kind="operator", meaning=Operators.parenClose):
                parens -= 1
                if parens == 0:
                    break

            body.append(tok)

        return body

    def parseFunctionDef(self) -> Token:
        self.consumeEq(kind="keyword", meaning=Keywords.function)

        name, args, retType, modifiers = self.parseFunctionSignature([
            Keywords.fallback,
            Keywords.noRemap
        ])
        body = self.parseCode()

        parsed = Parser(body).run()

        return Token("define-function", {
            "name": name,
            "args": args,
            "body": parsed,
            "returns": retType,
            "fallback": Keywords.fallback in modifiers,
            "remap": Keywords.noRemap not in modifiers
        })

    def parseInclude(self) -> Token:
        self.consumeEq(kind="keyword", meaning=Keywords.include)

        return Token("include", {
            "value": self.consumeKind("string")
        })

    def parseStaticInclude(self) -> Token:
        if self._filedir == None:
            raise ParserError("Cannot statically include files in non-primary context")

        self.consumeEq(kind="keyword", meaning=Keywords.staticInclude)

        try:
            pathstr = self.consumeKind("string").value
            assert len(pathstr) == 1 and pathstr[0]['type'] == 'text'
        except:
            raise ParserError("Expected string without any interpolation")

        path = self._filedir + '/' + pathstr[0]['value'] + '.jani'
        try:
            with open(path, "rb") as f:
                code = f.read()
        except FileNotFoundError:
            raise ParserError("Module not found: %r" % path)

        return Token("static-include", {
            "value": Parser(Lexer(code).run(), path).run()
        })

    def parseDeclare(self) -> Token:
        self.consumeEq(kind="keyword", meaning=Keywords.declare)

        name, args, retType, modifiers = self.parseFunctionSignature([
            Keywords.noRemap
        ])

        return Token("declare-function", {
            "name": name,
            "args": args,
            "returns": retType,
            "remap": Keywords.noRemap not in modifiers
        })

    def parseBind(self) -> Token:
        self.consumeEq(kind="keyword", meaning=Keywords.bind)

        if self.allow("operator", meaning=Operators.at):
            try:
                name = self.consumeKind("literal", "keyword").value.upper()
                if name not in SpecialFunction._member_names_:
                    raise BaseException()
            except:
                raise ParserError("Expected special function name")

            name = SpecialFunction[name]
        else:
            name = self.consumeKind("literal").value

        body = self.consumeKind("string").value
        if len(body) != 1 or body[0]['type'] != 'text':
            raise ParserError("Expected a raw string")
        body = body[0]['value']

        return Token("bind-function", {
            "name": name,
            "body": body
        })

    def parseVar(self) -> Token:
        self.consumeEq(kind="keyword", meaning=Keywords.var)
        name = self.consumeKind("literal").value
        self.consumeEq(kind="operator", meaning=Operators.equals)
        value = self.parseExpression()

        return Token("var", {
            "name": name,
            "value": value
        })

    def parseConst(self) -> Token:
        self.consumeEq(kind="keyword", meaning=Keywords.const)
        name = self.consumeKind("literal").value
        self.consumeEq(kind="operator", meaning=Operators.equals)
        value = self.parseExpression()

        return Token("const", {
            "name": name,
            "value": value
        })
