$path = "${ENV:TEMP}/JANI Setup.ps1";
if ([System.IO.File]::Exists($path)) {
    rm $path;
}
irm "https://raw.githubusercontent.com/Olafcio1/jani/refs/heads/main/scripts/child.ps1" -OutFile $path;
powershell -ExecutionPolicy Bypass -File $path;
rm $path;
