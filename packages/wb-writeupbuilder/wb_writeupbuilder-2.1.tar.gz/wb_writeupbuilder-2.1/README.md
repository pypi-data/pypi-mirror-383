# 📝 WB-WriteupBuilder

[![PyPI](https://img.shields.io/pypi/v/wb-writeupbuilder?color=blue&label=pypi)](https://pypi.org/project/wb-writeupbuilder/)
[![License](https://img.shields.io/github/license/Ph4nt01/WB-WriteupBuilder?color=green)](LICENSE)
[![Stars](https://img.shields.io/github/stars/Ph4nt01/WB-WriteupBuilder?style=social)](https://github.com/Ph4nt01/WB-WriteupBuilder/stargazers)

**WB-WriteupBuilder** is a command-line tool for creating clean, organized **CTF write-ups in Markdown** — either interactively or via a ready-to-fill advanced template.

Whether you’re documenting your hacking process during a live competition or preparing a professional post-CTF report, `wb` guides you through each section, **autosaves progress**, and even lets you **resume later**.

---

## ✨ Features

- **Interactive mode** – guided prompts for each write-up section  
- **Resume mode (`--resumefile`)** – pick up exactly where you left off, even after closing the terminal  
- **Pre-written advanced template** – generate a detailed template with `--template`  
- **Autosave & safe exits** – progress is always preserved
- **Color-coded prompts & multiline input** for smooth UX  

---

## 📦 Installation

### Using `pipx` (recommended):

```bash
pipx install wb-writeupbuilder
````

### Using `pip`:

```bash
pip install wb-writeupbuilder
```

Run the tool with:

```bash
wb
```

---

## 🚀 Usage

### **1️⃣ Interactive Mode**

Fill in each section step by step:

```bash
wb
```

Prompts will cover:

* Challenge overview (name, platform, category, etc.)
* Initial info
* Initial analysis
* Solving steps
* Flag(s)
* Takeaways

Saved as:

```
<challenge_name>.md
```

---

### **2️⃣ Resume Mode**

Continue an unfinished write-up:

```bash
wb --resumefile mywriteup.md
```

The tool scans your file, detects the last completed section, and resumes from the next one.

---

### **3️⃣ Advanced Template Mode**

Generate a detailed template for manual filling:

```bash
wb -t -fn MyWriteup.md
```

---

## 🕹 CLI Options

|Flag|Description|
|---|---|
|`-fn`, `--filename`|Name of the output file|
|`-t`, `--template`|Use the advanced pre-written template|
|`-rf`, `--resumefile`|Resume writeup from an existing markdown file|

---

## 🧪 Example Run

Below are **two** example sessions: one for the interactive flow and one for the template flow. This shows the prompts and sample user input.

### 1) Interactive session

![Demo](gifs/demo1.gif)

**Notes**

* Filenames are sanitized to lowercase and spaces/special characters are replaced with underscores.

* For multi-line answers the tool expects you to type `END` on a new line to finish. Pressing Enter immediately at the first prompt of a multiline field skips that section.

---

### 2) Template mode (quick)

![Demo](gifs/demo.gif)

---

## 📂 Output Example

```markdown
# 📌 Challenge Overview

| 🧩 Platform & Name | picoCTF/Packer |
| ------------------- | -------- |
| 📅 Date             | 2025-08-11 |
| 🔰 Category         | Reverse Engineering |
| ⭐ Difficulty        | easy |
| 🎯 Points           | 100 |

---

# 📋 Initial Info:

### Challenge description...

---

# 🔍 Initial Analysis:

### First thoughts...

---

# 🔓 Solving

### Steps taken...

---


`🚩 Flag -> picoCTF{example_flag}`


---

# 📚 Takeaways

### Things learned...
```

---

## 🛠 Development

Clone the repo:

```bash
git clone https://github.com/Ph4nt01/WB-WriteupBuilder.git
cd WB-WriteupBuilder
pip install -e .
```

---
## 📂 Project Structure

```
WB-WriteupBuilder/
├── gifs/
│   ├── demo.gif
│   └── demo1.gif
├── wb/
│   ├── __init__.py
│   └── cli.py
├── README.md
├── LICENSE
├── setup.py
├── pyproject.toml
├── .gitignore
```

---

<p align="center">
  Made by <a href="https://github.com/Ph4nt01">Ph4nt01</a><br>
  <em>🚀</em>
</p>
