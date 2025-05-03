import random

from ..lexer import Lexer
from ..parser import Parser
from ..parser.Arguments import Arguments
from ..parser.CallMode import CallMode
from ..parser.MathOp import MathOp
from ..parser.SpecialFunction import SpecialFunction
from ..parser.types.Type import Type
from ..token import Token

from .BaseBuilder import BaseBuilder
from .Function import Function

class BuilderError(BaseException):
    pass

Functions = dict[str, Function]
Constants = dict[str, Token]

class Builder(BaseBuilder):
    filepath: str
    callMode: CallMode

    functions: Functions
    constants: Constants

    def __init__(self, input: list[Token], filepath: str, *, primaryContext: bool = True, copy: "Builder | None" = None):
        """
        Initializes the builder.

        Arguments:
            input: The parser tokens to build PowerShell from.
            filepath: The path of the parsed file. Used for `include` statements.
            primaryContext: Refer to the full Jani documentation. This is a complex term.
        """

        self._input = input
        self.filepath = filepath
        self._index = 0
        self._output = ""

        self.functions = copy.functions if copy != None else {}
        self.constants = copy.constants if copy != None else {}

        self.callMode = CallMode.foreground

        if primaryContext:
            stdlib = "/".join(__file__.replace("\\", "/").split("/")[:-3]) + "/stdlib/stdlib.jani"
            if self.filepath != stdlib:
                with open(stdlib, "rb") as f:
                    code = f.read()

                self._input.insert(0, Token("static-include", {
                    "value": Parser(Lexer(code).run(), stdlib).run()
                }))

    def run(self, *, context: "Builder | None" = None) -> str:
        self.assignFunctions()
        self.assignConstants()

        while tok := self.consume():
            if tok.kind == "call":
                self.callWithMode(self.callMode, tok)
            elif tok.kind == "call-with-mode":
                self.callWithMode(tok.mode, tok.call)
            elif tok.kind == "define-function":
                self.defineFunction(tok.name, tok.args, tok.body, tok.returns, tok.fallback)
            elif tok.kind == "mode-change":
                self.callMode = tok.value
            elif tok.kind == "var":
                self.setVar(tok.name, tok.value)
            elif tok.kind == "while":
                self.while_(tok.expr, tok.body)
            elif tok.kind == "panic":
                self.panic()
            else:
                raise BuilderError("Unrecognized token %r" % tok.kind)

        if context != None:
            context.functions.update(self.functions)

        return self._output

    def assignFunctions(self) -> None:
        funs = 0
        i = 0

        while i < len(self._input):
            tok = self._input[i]
            if tok.kind == "define-function":
                name = tok.name

                if name not in self.functions:
                    self.functions[name] = {
                        "name": "j[$%d]+inv" % funs,
                        "body": tok.body,
                        "args": tok.args,
                        "fallback": tok.fallback,
                        "ret": tok.returns,
                        "defined": True,
                        "bound": False
                    }
                    funs += 1
                elif tok.fallback:
                    pass
                else:
                    raise BuilderError("Already existing function: %r" % name)

                self._input.pop(i)
            elif tok.kind == "declare-function":
                name = tok.name
                if name in self.functions:
                    raise BuilderError("Already existing function: %r" % name)

                self.functions[name] = {
                    "name": "j[$%d]+inv" % funs,
                    "args": tok.args,
                    "ret": tok.returns,
                    "defined": False,
                    "bound": False
                }
                funs += 1

                self._input.pop(i)
            elif tok.kind == "bind-function":
                name = tok.name

                if name in self.functions:
                    f = self.functions[name]
                    if f['defined']:
                        raise BuilderError("This function is already defined")
                    f['defined'] = True
                    f['body'] = tok.body
                    f['bound'] = True
                elif isinstance(name, SpecialFunction):
                    pass
                else:
                    raise BuilderError("Cannot bind nonexistent function: %r" % name)

                self._input.pop(i)
            elif tok.kind == "static-include":
                self._input = [
                    *self._input[:i],
                    *tok.value,
                    *self._input[i + 1:]
                ]
            else:
                i += 1

        for n in self.functions:
            f = self.functions[n]

            if not f['defined']:
                raise BuilderError("Unbound function: %r" % f)
            elif f['bound']:
                self._output += "function %s($params){%s}" % (f['name'], f['body'])
            else:
                self._output += "function %s($params){%s}" % (f['name'], Builder(f['body'], self.filepath, primaryContext=False, copy=self).run())

    def assignConstants(self) -> None:
        consts = 0
        i = 0

        code = ''
        func = 'ą'
        equal = '\uD83C'

        while i < len(self._input):
            tok = self._input[i]
            if tok.kind == "const":
                name = "%s%d" % (random.choice('JANI'), consts)
                self.constants[tok.name] = name
                code += '%s{%s%s%s};' % (func, name, equal + chr((127 + i * 10) % 15000), self.translate(tok.value))
                consts += 1
                self._input.pop(i)
            else:
                i += 1

        fun = "$__=[System.Collections.ArrayList]::new();function %s($_){$_=$_.tostring().split('%s',2);$Global:__.add(@($_[0],$_[1].substring(1)))}" % (func, equal)

        self._output += fun + code

    def translate(self, token: Token) -> str:
        if token.kind == "string":
            val = '"'
            special = {
                "\n": "n",
                "\r": "r",
                "\t": "t",
                '"': '"',
                "$": "$"
            }

            for frag in token.value:
                if frag['type'] == "var":
                    val += "${ENV:"
                for ch in frag['value']:
                    if ch in special:
                        val += "`" + special[ch]
                    else:
                        val += ch
                if frag['type'] == "var":
                    val += "}"

            val += '"'
            return val
        elif token.kind == "math-op":
            a = self.translate(token.a)
            b = self.translate(token.b)

            if token.op == MathOp.add:
                op = "+"
            elif token.op == MathOp.subtract:
                op = "-"
            elif token.op == MathOp.multiply:
                op = "*"
            elif token.op == MathOp.divide:
                op = "/"
            elif token.op == MathOp.exponentiate:
                return f"[bigint]::Pow({a},{b})"
            elif token.op == MathOp.xor:
                op = "-bxor"
            elif token.op == MathOp.xand:
                op = "-band"
            else:
                raise BuilderError("Unsupported math operation %r" % token.op)

            return a + op + b
        elif token.kind == "number":
            return token.value if "." in token.value else hex(int(token.value))
        elif token.kind == "inverted-value":
            return "!(%s)" % self.translate(token.expr)
        elif token.kind == "call":
            return self.callWithMode(self.callMode, token, append=False)
        else:
            raise BuilderError("Cannot translate token %r" % token)

    def callWithMode(self, mode: CallMode, token: Token, *, append: bool = True) -> str:
        bindFunc = self.functions.get(token.func)
        if bindFunc == None:
            raise BuilderError("No such function: %r" % token.func)
        bindName = bindFunc['name']

        data = ""

        if mode == CallMode.background:
            data += "^ "

        data += bindName + " "
        data += "@{"

        args = token.args
        for arg in args:
            name = self.translate(Token("string", {
                "value": [{
                    "type": "text",
                    "value": arg
                }]
            }))
            value = self.translate(args[arg])

            data += name + "=" + value + ";"

        data += "};"

        if append:
            self._output += data
        return data

    def defineFunction(self, name: str, args: Arguments, body: list[Token], returns: Type, fallback: bool) -> None:
        self._output += "function %s($params){%s}" % (self.functions[name], Builder(body, self.filepath, primaryContext=False).run())

    def setVar(self, name: str, value: Token) -> None:
        self._output += "$%s=%s;" % (name, self.translate(value))

    def while_(self, expr: Token, body: list[Token]) -> None:
        self._output += "while(%s){" % self.translate(expr)
        self._output += Builder(body, self.filepath, primaryContext=False, functions=self.functions).run(context=self)
        self._output += "}"

    def panic(self) -> None:
        self._output += "*;"

    def include(self, path: str) -> None:
        with open(path, "rb") as f:
            code = f.read()
        sub = Builder(Parser(Lexer(code).run(), path).run(), path, primaryContext=False, functions=self.functions)
        sub.run(context=self)
