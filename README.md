# 💥 JANI
JANI is a programming language dedicated to creating malware. It includes hundreds of built-in commands compatible with Windows, to exploit the victim whatever happens.

![Github Stars](https://img.shields.io/github/stars/Olafcio1/jani?style=for-the-badge&logo=github&labelColor=2b2b2b&color=2b2b2b)
![Downloads](https://img.shields.io/github/downloads/Olafcio1/jani/total?style=for-the-badge&logo=github&labelColor=2b2b2b&color=2b2b2b)

## ⏬ Installation
Create a file caled `Setup.ps1` with the following contents and run it:
```powershell
# Python Installation
$out = "${ENV:TEMP}/JANI Setup - Python 3.13.5 Installer.exe";
iwr "https://www.python.org/ftp/python/3.13.5/python-3.13.5-amd64.exe" -o $out;
echo "[ 🐍 ] Installing Python...";
& $out /passive Include_test=0 PrependPath=1 Include_freethreaded=1;

# JANI Installation
$out = "JANI Setup - Source Code.zip";
iwr https://github.com/Olafcio1/jani/archive/refs/heads/main.zip -o $out
echo "[ 🤐 ] Unpacking JANI...";
tar -xf $out
del $out

# Location
$installDir = "${ENV:LOCALAPPDATA}/JANI";
move "jani-main" $installDir;

# Dependencies
echo "[ 📦 ] Installing dependencies...";
$raw = Get-Content requirements.txt;
$lines = $raw.Split("`n");
for ($i = 0; $i -lt $lines.Length; $i++) {
    $line = $lines[$i];
    if (($line -eq "") -or $line.StartsWith("#"))
        continue;

    $output = pip install -qq --no-input --disable-pip-version-check --no-color --no-python-version-warning $line;

    if ($output.Contains("ERROR: ")) {
        echo "[ ❌ ] Package $line installation failed.";
    } else {
        echo "[ ✅ ] Package $line installed.";
    }
}

# Aliases
echo "[ 💬 ] Adding as JANI to PowerShell config...";
echo "`nfunction jani { python $installDir `$args }";

# Setup Finished
echo "[ 🤞 ] Setup finished. You should be able to run JANI like other commandlets in PowerShell.";
pause;
```

## 🧾 Syntax
The language mainly consists of things you can find in others.

**These are its types:**

Text (a.l.a. string) is a piece of text that you can do basically anything with.
```jani
cmd(line: "notepad");
```

**What are the notable differences?**

1. JANI doesn't have positional arguments. To specify an argument, you have to provide its name, then the value you want it to have.

2. Standard strings have Batch interpolation. To add an environment variable, you specify it like in Batch, e.g.: `"Welcome, %USERNAME%!"`

3. JANI's standard library isn't too big; it's a pain for writing typical programs. It's adjusted for writing malware, like the whole point of JANI.

## 💥 Intellisense
###### too lazy

##### Please don't ask about the name. It's `JANI Aggresive NAT Intrusivity`. It's a recursive acronym.
