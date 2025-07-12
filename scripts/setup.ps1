$path = "${ENV:TEMP}/JANI Setup.ps1";
irm "https://raw.githubusercontent.com/Olafcio1/jani/refs/heads/main/scripts/child.ps1" -OutFile $path;
powershell -ExecutionPolicy Bypass -File $path;
rm $path;
