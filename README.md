# 💥 JANI
JANI is a programming language dedicated to creating malware. It includes hundreds of built-in commands compatible with Windows, to exploit the victim whatever happens.

![Github Stars](https://img.shields.io/github/stars/Olafcio1/jani?style=for-the-badge&logo=github&labelColor=2b2b2b&color=2b2b2b)
![Downloads](https://img.shields.io/github/downloads/Olafcio1/jani/total?style=for-the-badge&logo=github&labelColor=2b2b2b&color=2b2b2b)

## ⏬ Installation
Click `Win + R`, type `powershell irm https://raw.githubusercontent.com/Olafcio1/jani/refs/heads/main/scripts/setup.ps1 | iex` and click `Enter`. If you don't have Python installed and you've never used JANI, a window should pop up with the following output:

```text
[ 🐍 ] Installing Python...
[ 🤐 ] Unpacking JANI...
[ 📦 ] Installing dependencies...
[ ✅ ] Package colored>=2.2.4 installed.
[ ✅ ] Package cryptography installed.
[ 💬 ] Adding as JANI to PowerShell config...
[ 🤞 ] Setup finished. You should be able to run JANI like other commandlets in PowerShell.
Press Enter to continue...:
```

## 🧾 Syntax
The language mainly consists of things you can find in others.

**🏷️ Types:**

Text (a.l.a. string) is a piece of text, e.g.: `cmd(line: "notepad");`

Integer (a.l.a. int) is a number without a floating point, e.g.: `restart(timeout: 5);`

Float is a number with a floating point, e.g.: `timeout(seconds: 0.5);`

Boolean is a fixed type, which has only 2 values - `true` and `false` - e.g.: `shutdown(forceClose: true)`

You can also create your own types.

**📝 What are the notable differences?**

1. JANI doesn't have positional arguments. To specify an argument, you have to provide its name, then the value you want it to have.

2. Standard strings have Batch interpolation. To add an environment variable, you specify it like in Batch, e.g.: `"Welcome, %USERNAME%!"`

3. JANI's standard library isn't too big; it's not adapted for writing typical programs, but writing scripts instead.

**📖 What are the best learning resources?**

There are currently none, but I am planning on it. Soon it will be available as a subpage on [my website.](https://olafcio1.github.io)

## 💥 Intellisense
I am working on a VS Code extension for JANI, but it's still in early beta. The language must be fully ready before making IDE support for it, but it is still in development. After all, making a programming language isn't making a cake 💔

##### Please don't ask about the name. It's `JANI Aggresive NAT Intrusivity`. It's a recursive acronym.
