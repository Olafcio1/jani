$path = "${ENV:TEMP}/JANI Setup.ps1";
del $path;
irm "https://raw.githubusercontent.com/Olafcio1/jani/refs/heads/main/scripts/child.ps1" -OutFile $path;
& $path;
rm $path;
