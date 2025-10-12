<h1 align="center">
  ctf-dl
</h1>

<h4 align="center">Fast and flexible challenge downloader for all major CTF platforms</h4>

<p align="center">
  <a href="https://pypi.org/project/ctf-dl/"><img src="https://img.shields.io/pypi/v/ctf-dl" alt="PyPI"></a>
  <img src="https://img.shields.io/github/license/bjornmorten/ctf-dl" alt="License">
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-installation">Install</a> •
  <a href="#-quickstart">Quickstart</a> •
  <a href="#-examples">Examples</a> •
  <a href="#-license">License</a>
</p>


## 🔧 Features

- 🔽 **Download all challenges** from supported CTFs  
- 🗂️ **Organize challenges** with custom folder structures  
- 🧩 **Format outputs** using Jinja2 templates (Markdown, JSON, etc.)  
- 🎯 **Apply filters** by category, points, or solve status  
- 🌐 **Integrations:** Works with CTFd, rCTF, GZCTF, HTB, EPT, Berg, CryptoHack, pwnable.tw, pwnable.kr and pwnable.xyz via [ctfbridge](https://github.com/bjornmorten/ctfbridge)


## 📦 Installation

Run directly with [uv](https://github.com/astral-sh/uv):

```bash
uvx ctf-dl
```

Or install permanently with pip:

```bash
pip install ctf-dl
```

## 🚀 Quickstart

```bash
ctf-dl https://demo.ctfd.io -u user -p password
```

## 💡 Examples

If the CTF platform requires authentication, provide either:
- `--token YOUR_TOKEN`, or  
- `--username USERNAME --password PASSWORD`  

```bash
# Download all challenges
ctf-dl https://ctf.example.com

# Download to a custom directory
ctf-dl https://ctf.example.com --output /tmp/ctf

# Only download Web and Crypto challenges
ctf-dl https://ctf.example.com --categories Web Crypto

# Overwrite previously downloaded challenges
ctf-dl https://ctf.example.com --update

# Download and zip output
ctf-dl https://ctf.example.com --zip

# Save output as JSON
ctf-dl https://ctf.example.com --output-format json

# List available templates
ctf-dl --list-templates

```

## 📁 Default Output Structure

```
challenges/
├── README.md
├── crypto/
│   ├── rsa-beginner/
│   │   ├── README.md
│   │   └── files/
│   │       ├── chal.py
│   │       └── output.txt
├── web/
│   ├── sql-injection/
│   │   ├── README.md
│   │   └── files/
│   │       └── app.py
```

## 🤝 Contributing

Contributions are welcome! See [ctfbridge](https://github.com/bjornmorten/ctfbridge) regarding platform support, or open an issue or pull request to improve **ctf-dl** itself.

## 🪪 License

MIT License © 2025 [bjornmorten](https://github.com/bjornmorten)
