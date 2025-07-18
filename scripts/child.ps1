function echo($line) {
    [Console]::WriteLine($line);
}

# Python Installation
try {
    $_ = gcm python;
    echo "[ 🐍 ] Python already installed.";
} catch {
    $out = "${ENV:TEMP}/JANI Setup - Python 3.13.5 Installer.exe";
    iwr "https://www.python.org/ftp/python/3.13.5/python-3.13.5-amd64.exe" -OutFile $out;
    echo "[ 🐍 ] Installing Python...";
    & $out /passive Include_test=0 PrependPath=1 Include_freethreaded=1;
}

# JANI Installation
cd "${ENV:TEMP}";
$out = "JANI Setup - Source Code.zip";
if ([System.IO.File]::Exists($out)) {
    del $out;
}
iwr https://github.com/Olafcio1/jani/archive/refs/heads/main.zip -OutFile $out;
echo "[ 🤐 ] Unpacking JANI...";
tar -xf $out;
del $out;

# Location
$installDir = "${ENV:LOCALAPPDATA}/JANI";
$firstInstall = -not [System.IO.Directory]::Exists($installDir);
if (-not $firstInstall) {
    $oldDir = "${ENV:LOCALAPPDATA}/JANI-old";
    if ([System.IO.Directory]::Exists($oldDir)) {
        #echo $oldDir;
        rm -Recurse -Force $oldDir;
    }
    move $installDir $oldDir;
}
move "jani-main" $installDir;

# Dependencies
echo "[ 📦 ] Installing dependencies...";
$raw = Get-Content "$installDir/requirements.txt";
$lines = $raw.Split("`n");
for ($i = 0; $i -lt $lines.Length; $i++) {
    $line = $lines[$i];
    if (($line -eq "") -or $line.StartsWith("#")) {
        continue;
    }

    $output = pip install -qq --no-input --disable-pip-version-check --no-color --no-python-version-warning $line;

    if (($output -ne $null) -and $output.Contains("ERROR: ")) {
        echo "[ ❌ ] Package $line installation failed.";
    } else {
        echo "[ ✅ ] Package $line installed.";
    }
}

# Aliases
if ($firstInstall) {
    echo "[ 💬 ] Adding as JANI to PowerShell config...";
    $_ = New-Item -Path ($profile | Split-Path) -ItemType Directory -ErrorAction Ignore;
    echo "`nfunction jani { python $installDir `$args }" >> $profile;
}

# Setup Finished
echo "[ 🤞 ] Setup finished. You should be able to run JANI like other commandlets in PowerShell.";
pause;
