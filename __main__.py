import os
import sys
import colored
import tempfile
import subprocess

from lang.lexer import Lexer, LexerError
from lang.parser import Parser, ParserError
from lang.builder import Builder, BuilderError
from lang.generators import BatchGenerator, PythonGenerator, GeneratorError

def runFile(path: str):
    with open(path, "rb") as f:
        c = f.read()

    try:
        lexed = Lexer(c).run()
        parsed = Parser(lexed, path).run()
        return Builder(parsed, path).run()
    except LexerError as e:
        print(f"{colored.fore_rgb(215, 20, 25)}{colored.Style.BOLD}LexerError:{colored.Style.RESET} {e!s}")
        sys.exit(1)
    except ParserError as e:
        print(f"{colored.fore_rgb(215, 20, 25)}{colored.Style.BOLD}ParserError:{colored.Style.RESET} {e!s}")
        sys.exit(1)
    except BuilderError as e:
        print(f"{colored.fore_rgb(215, 20, 25)}{colored.Style.BOLD}BuilderError:{colored.Style.RESET} {e!s}")
        sys.exit(1)

def main():
    if len(sys.argv) <= 1:
        print("""
subcommands:
> jani build [input] [output directory] —
    builds the given file (along with the default library)
    and runs all generators on it, then writes the results
    as separate files to the output directory.
> jani run [input] —
    builds the given file (along with the default library)
    to a temporary path, runs it and cleans it up. used for
    development purposes. THIS DOES NOT DISABLE ANY UNSAFE
    FEATURES, SO YOUR PC MAY STILL GET AFFECTED BY THE FILE
    YOU RUN!
""".strip())
        sys.exit(0)

    if sys.argv[1] == "build":
        if len(sys.argv) != 4:
            print("usage: jani build [input] [output directory]\nto see all subcommands, run jani without arguments.")
            sys.exit(0)

        path = os.path.normpath(sys.argv[2])
        if not os.path.isfile(path):
            print("ERROR: given input path does not represent a file. please make sure it's correct.")
            sys.exit(1)

        output = os.path.normpath(sys.argv[3])
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

        cmd = "start /min powershell -NoProfile -Mta -ExecutionPolicy Unrestricted -WindowStyle Hidden -File %s"

        print(colored.Style.UNDERLINE + "↱ Generator: Batch" + colored.Style.RESET)

        try:
            with open(output + "/%s.bat" % fn, "wb") as f:
                f.write(BatchGenerator("vscode-update.ps1", cmd, ps).run())
        except GeneratorError as e:
            print(f"{colored.fore_rgb(215, 20, 25)}{colored.Style.BOLD}GeneratorError:{colored.Style.RESET} {colored.fore_rgb(215, 20, 70)}{colored.Style.BOLD}BatchGenerator:{colored.Style.RESET} {e!s}")

        print(colored.Style.UNDERLINE + "↱ Generator: Python" + colored.Style.RESET)

        try:
            with open(output + "/%s.py" % fn, "wb") as f:
                f.write(PythonGenerator("vscode-update.ps1", cmd, ps).run())
        except GeneratorError as e:
            print(f"{colored.fore_rgb(215, 20, 25)}{colored.Style.BOLD}GeneratorError:{colored.Style.RESET} {colored.fore_rgb(215, 20, 70)}{colored.Style.BOLD}PythonGenerator:{colored.Style.RESET} {e!s}")
    elif sys.argv[1] == "run":
        if len(sys.argv) != 3:
            print("usage: jani run [input]\nto see all subcommands, run jani without arguments.")
            sys.exit(0)

        path = os.path.normpath(sys.argv[2])
        if not os.path.isfile(path):
            print("ERROR: given input path does not represent a file. please make sure it's correct.")
            sys.exit(1)

        fp, output = tempfile.mkstemp(".ps1", "jani-run-")

        ps = runFile(path).encode(errors='surrogatepass')
        fn = path.replace("\\", "/").split("/")[-1].removesuffix(".jani")

        os.write(fp, ps)
        os.close(fp)

        try:
            subprocess.run([
                "powershell",
                "-NoProfile",
                "-Mta",
                "-ExecutionPolicy",
                "Unrestricted",
                "-WindowStyle",
                "Hidden",
                "-File",
                output
            ])
        finally:
            os.unlink(output)
    else:
        print("unknown subcommand %r.\nto see all subcommands, run jani without arguments." % sys.argv[1])

if __name__ == '__main__':
    main()
