#!/usr/bin/env python3


import argparse
import sys
import time
import threading
import re
import os
import signal
from datetime import datetime
import colorama
from colorama import Back as bg, Fore, Style, init
init(autoreset=True)

try:
    from zoneinfo import ZoneInfo
    BERLIN = ZoneInfo("Europe/Berlin")
except Exception:
    BERLIN = None

# ─────────────────────────────────────────────
# Runtime save context (used by signal handlers)
_RUNTIME = {"filename": None, "md": ""}


def _write_md_atomic(filename: str | None, text: str) -> None:
    """Write the current Markdown to disk atomically.
    Why: prevents truncated files if the process is killed mid-write.
    """
    if not filename:
        return
    os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
    tmp = filename + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, filename)


def _flush_runtime():
    _write_md_atomic(_RUNTIME.get("filename"), _RUNTIME.get("md", ""))


def _install_signal_handlers():
    """Ensure we always save progress on interrupts/termination."""
    def _handler(signum, frame):
        try:
            print( "\n\n" + bg.BLACK+ Fore.WHITE + f"[WriteupBuilder] exited... Saving progress to: {_RUNTIME.get('filename')}" + Style.RESET_ALL)
            _flush_runtime()
        finally:
            # Exit immediately after flushing to avoid re-entrancy.
            os._exit(1)

    for sig in (getattr(signal, "SIGINT", None),
                getattr(signal, "SIGTERM", None),
                getattr(signal, "SIGHUP", None)):
        if sig is not None:
            try:
                signal.signal(sig, _handler)
            except Exception:
                pass


# ─────────────────────────────────────────────
# Spinner

def spinner(stop_event, message=""):
    symbols = ["|", "/", "–", "\\"]
    idx = 0
    while not stop_event.is_set():
        sys.stdout.write(f"\r{message} {symbols[idx]} ")
        sys.stdout.flush()
        idx = (idx + 1) % len(symbols)
        time.sleep(0.1)
    # Clear spinner line after stopping
    sys.stdout.write("\r" + " " * (len(message) + 4) + "\r")
    sys.stdout.flush()


def spinner_until_enter(message=""):
    """Show spinner with a message until user presses Enter."""
    sys.stdout.write("\n" + Fore.CYAN + "(Press Enter to continue)" + Style.RESET_ALL + "\n")
    sys.stdout.flush()
    sys.stdout.write("\033[F\033[F")  # Move up two lines
    sys.stdout.flush()

    stop_event = threading.Event()
    thread = threading.Thread(target=spinner, args=(stop_event, message))
    thread.start()

    try:
        input()  # Wait for Enter
    finally:
        stop_event.set()
        thread.join()


# ─────────────────────────────────────────────
# Utilities

def sanitize_filename(s: str) -> str:
    s = s.strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[-\s]+", "_", s)
    return s.lower() or "untitled"


def today_date_str():
    if BERLIN:
        return datetime.now(BERLIN).strftime("%Y-%m-%d")
    return datetime.now().strftime("%Y-%m-%d")


# ─────────────────────────────────────────────
# Input handlers

def prompt_normal(prompt_text: str, required: bool = False) -> str | None:
    while True:
        ans = input(Fore.WHITE + f"{prompt_text}: " + Style.RESET_ALL).strip()
        if ans:
            return ans
        if required:
            print(Fore.RED + "This field is required — please type a value." + Style.RESET_ALL)
            continue
        return None


def prompt_multiline(prompt_text: str) -> str | None:
    try:
        from prompt_toolkit import prompt
        from prompt_toolkit.key_binding import KeyBindings
        from prompt_toolkit.styles import Style as PromptStyle
    except ImportError:
        print(Fore.RED + "Error: prompt_toolkit is required for enhanced multi-line input. Install with: pip install prompt_toolkit" + Style.RESET_ALL)
        print(Fore.YELLOW + "Falling back to basic input mode..." + Style.RESET_ALL)
        return prompt_multiline_fallback(prompt_text)

    print(Fore.WHITE + prompt_text + Style.RESET_ALL)
    print(Fore.CYAN + "Instructions:")
    print(Fore.CYAN + "- Use arrow keys to navigate (↑↓←→)")
    print(Fore.CYAN + "- Press Ctrl+D to finish and accept")
    print(Fore.CYAN + "- Press Ctrl+C or Esc to cancel")
    print(Fore.CYAN + "- To skip, leave input empty and press Ctrl+D")
    print(Style.RESET_ALL)

    kb = KeyBindings()

    @kb.add('c-d')
    def _(event):
        event.app.exit(result=event.app.current_buffer.text)

    @kb.add('c-c')
    def _(event):
        event.app.exit(result=None)

    @kb.add('escape')
    def _(event):
        event.app.exit(result=None)

    style = PromptStyle.from_dict({'prompt': 'ansicyan'})

    try:
        text = prompt(message='> ', multiline=True, key_bindings=kb, style=style, wrap_lines=True)
    except KeyboardInterrupt:
        return None
    except Exception as e:
        print(f"Error during input: {e}")
        return None

    if text is None:
        return None
    text = text.rstrip()
    if not text:
        return None
    return text


def prompt_multiline_fallback(prompt_text: str) -> str | None:
    print(Fore.WHITE + prompt_text + Style.RESET_ALL)
    print(Fore.CYAN + "(Type `END` on a new line to finish. Press ENTER immediately (empty first line) to skip this question.)" + Style.RESET_ALL)
    first = input()
    if first == "":
        return None
    if first.strip() == "END":
        return None
    lines = [first]
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    content = "\n".join(lines).rstrip()
    return content if content else None


# ─────────────────────────────────────────────
# Markdown builders

def build_overview_md(challenge_name, platform, date_str, solver, category, difficulty, points):
    md = "#  📌 Challenge Overview\n\n"
    md += f"| 🧩 Platform & Name | {platform}/{challenge_name} |\n"
    md += "| ------------------- | ------------------------------- |\n"
    md += f"| 📅 Date             | {date_str} |\n"
    if solver:
        md += f"| 👾 Solver           | {solver} |\n"
    if category:
        md += f"| 🔰 Category         | {category} |\n"
    if difficulty:
        md += f"| ⭐ Difficulty        | {difficulty} |\n"
    if points:
        md += f"| 🎯 Points           | {points} |\n"
    md += "\n---\n\n"
    return md


def add_section(md, heading, content, inline_template=False):
    if not content:
        return md
    if inline_template:
        md += f"```markdown\n\n🚩 Flag -> `{content}`\n\n```\n\n---\n\n"
    else:
        # prefix every user input line with "### "
        formatted_content = "\n".join([f"### {line}" for line in content.splitlines() if line.strip()])
        md += f"{heading}\n\n{formatted_content}\n\n---\n\n"
    return md

# ─────────────────────────────────────────────
# Resume helpers

SECTION_HEADINGS = {
    "initial_info": "# 📋 Initial Info:",
    "initial_analysis": "# 🔍 Initial Analysis:",
    "solving": "# 🔓 Solving",
    
    "flag": "#  🚩 Flag ->",
    "takeaways": "# 📚 Takeaways",
}


SECTION_PROMPTS = {
    "initial_info": {
        "heading": "# 📋 Initial Info:",
        "prompt": "Paste the challenge description, any attached files, or screenshots here."
    },
    "initial_analysis": {
        "heading": "# 🔍 Initial Analysis:",
        "prompt": "What stood out during your first inspection? Mention suspicious URLs, strange files, unusual behavior, etc."
    },
    "solving": {
        "heading": "# 🔓 Solving",
        "prompt": "Describe the steps and tools/scripts used to exploit the challenge. Explain how each tool worked and how it helped you get the flag."
    },
    "flag": {
        "heading": "# 🚩 Flag ->",
        "prompt": "Enter The Flag"
    },
    "takeaways": {
        "heading": "# 📚 Takeaways",
        "prompt": "List the commands, tricks, or concepts you learned from this challenge."
    },
}

def detect_resume_point(filename: str) -> str | None:
    """Return last completed section key. Empty sections are ignored.
    Special-case flag which is inline with backticks.
    """
    if not os.path.exists(filename):
        return None
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    last_section = None
    for key, heading in SECTION_HEADINGS.items():
        if key == "flag":
            # match: "#  🚩 Flag -> `...`" followed by separator
            pat = rf"{re.escape(heading)}\s*`(.+?)`\s*\n\n---"
            m = re.search(pat, content, re.DOTALL)
            if m and m.group(1).strip():
                last_section = key
            continue
        # generic section: heading then body then separator or EOF
        pat = rf"{re.escape(heading)}\s*\n(.+?)(\n---|\Z)"
        m = re.search(pat, content, re.DOTALL)
        if m and m.group(1).strip():
            last_section = key
    return last_section


def upsert_section(md: str, heading: str, body: str, inline_template: bool = False) -> str:
    """Replace an existing section (even if empty) or append if missing."""
    if not body:
        return md
    if inline_template:
        block = f"#  🚩 Flag -> `{body}`\n\n---\n\n"
        # Replace any existing flag line
        pat = rf"{re.escape(heading)}.*?(\n\n---\n\n|\Z)"
        if re.search(pat, md, re.DOTALL):
            return re.sub(pat, block, md, count=1, flags=re.DOTALL)
        return md + block

    block = f"{heading}\n\n{body}\n\n---\n\n"
    pat = rf"{re.escape(heading)}\s*\n.*?(\n\n---\n\n|\n---\n\n|\Z)"
    if re.search(pat, md, re.DOTALL):
        return re.sub(pat, block, md, count=1, flags=re.DOTALL)
    return md + block


# ─────────────────────────────────────────────
# Main writeup builder

def writeup_builder(args):
    _install_signal_handlers()

    print(f"{Fore.CYAN}Tips for a clean writeup:")
    print(f"\n{bg.BLACK}{Fore.WHITE}- Screenshot as you go through the CTF for building a better writeup.")
    print(f"{bg.BLACK}{Fore.WHITE}- For multi-line sections, press Enter to add new lines, and type `END` on a new line to finish.")
    print(f"{bg.BLACK}{Fore.WHITE}- To insert an image: `![image](path/to/image.jpg)`")
    print(f"{bg.BLACK}{Fore.WHITE}- Skipping: If you press Enter without typing anything, that question will be skipped.")
    print(f"{bg.BLACK}{Fore.WHITE}- Sections with no answers will not be written to the file.{Style.RESET_ALL}\n")
    spinner_until_enter(f"{bg.BLACK}{Fore.GREEN}WriteupBuilder -> Starting")
    print()

    try:
        print("# 📌 Challenge Overview\n")
        challenge_name = prompt_normal("Name of the challenge", required=True)
        platform = prompt_normal("Platform / Event", required=True)
        solver = prompt_normal("Who are you (solver)", required=False)
        category = prompt_normal("Category of the challenge", required=False)
        difficulty = prompt_normal("Difficulty of the challenge", required=False)
        points = prompt_normal("Points for solving", required=False)
        date_str = today_date_str()

        # Determine filename now; create file immediately after Overview.
        if args.filename:
            filename = args.filename
        else:
            filename = f"{sanitize_filename(challenge_name)}.md"

        # Save filename globally for signal handlers
        _RUNTIME["filename"] = filename

        print(f"\n{bg.BLACK}{Fore.WHITE}Writing to file: {filename}{Style.RESET_ALL}\n")

        md = build_overview_md(challenge_name, platform, date_str, solver, category, difficulty, points)
        _RUNTIME["filename"] = filename
        _RUNTIME["md"] = md
        _flush_runtime()  # file created here

        print("\n# 📋 Initial Info:")
        initial_info = prompt_multiline(SECTION_PROMPTS["initial_info"]["prompt"])
        md = add_section(md, SECTION_PROMPTS["initial_info"]["heading"], initial_info)
        _RUNTIME["md"] = md
        _flush_runtime()

        print("\n# 🔍 Initial Analysis:")
        initial_analysis = prompt_multiline(SECTION_PROMPTS["initial_analysis"]["prompt"])
        md = add_section(md, SECTION_PROMPTS["initial_analysis"]["heading"], initial_analysis)
        _RUNTIME["md"] = md
        _flush_runtime()

        print("\n# 🔓 Solving")
        solving = prompt_multiline(SECTION_PROMPTS["solving"]["prompt"])
        md = add_section(md, SECTION_PROMPTS["solving"]["heading"], solving)
        _RUNTIME["md"] = md
        _flush_runtime()

        print("\n# 🚩 Flag ->")
        flag = prompt_normal(SECTION_PROMPTS["flag"]["prompt"], required=False)
        md = add_section(md, SECTION_PROMPTS["flag"]["heading"], flag, inline_template=True)
        _RUNTIME["md"] = md
        _flush_runtime()

        print("\n# 📚 Takeaways")
        takeaways = prompt_multiline(SECTION_PROMPTS["takeaways"]["prompt"])
        md = add_section(md, SECTION_PROMPTS["takeaways"]["heading"], takeaways)
        _RUNTIME["md"] = md.rstrip() + "\n"
        _flush_runtime()

        print(Fore.WHITE + f"Done. Saved {filename}" + Style.RESET_ALL)

    except KeyboardInterrupt:
        # Save whatever we have and exit.
        print(Fore.RED + "\nInterrupted. Progress saved." + Style.RESET_ALL)
        _RUNTIME["md"] = locals().get("md", _RUNTIME.get("md", ""))
        _flush_runtime()


# ─────────────────────────────────────────────
# Resume builder

def resume_builder(filename: str):
    _install_signal_handlers()

    if not os.path.exists(filename):
        print(Fore.RED + f"Resume file not found: {filename}" + Style.RESET_ALL)
        sys.exit(2)

    with open(filename, "r", encoding="utf-8") as f:
        md = f.read()

    _RUNTIME["filename"] = filename
    _RUNTIME["md"] = md

    last_section = detect_resume_point(filename)

    sections_order = [
        "initial_info",
        "initial_analysis",
        "solving",
        "flag",
        "takeaways",
    ]

    start_index = sections_order.index(last_section) + 1 if last_section in sections_order else 0
    print(Fore.GREEN + f"Resuming {filename} from: {sections_order[start_index] if start_index < len(sections_order) else 'completed'}" + Style.RESET_ALL)

    try:
        for sec in sections_order[start_index:]:

            prompt_text = SECTION_PROMPTS[sec]["prompt"]
            heading = SECTION_PROMPTS[sec]["heading"]

            print(f"\n{heading}")

            if sec == "flag":
                flag = prompt_normal(prompt_text, required=False)
                md = add_section(md, heading, flag, inline_template=True)
            else:
                content = prompt_multiline(prompt_text)
                md = add_section(md, heading, content)


            _RUNTIME["md"] = md
            _flush_runtime()  # write after every section

        # final tidy
        if not md.endswith("\n"):
            md += "\n"
        _RUNTIME["md"] = md
        _flush_runtime()
        print(Fore.WHITE + f"Done. Updated {filename}" + Style.RESET_ALL)

    except KeyboardInterrupt:
        print(Fore.RED + "\nInterrupted while resuming. Progress saved." + Style.RESET_ALL)
        _RUNTIME["md"] = md
        _flush_runtime()


# ─────────────────────────────────────────────
# Template builder

def template_builder(args):
    spinner_until_enter(f"{bg.BLACK}{Fore.GREEN} WriteupBuilder -> Writing the Advanced Writeup Template to {args.filename}")
    print()

    md = """# 1- Initial Reconnaissance

## Port Scanning  
We start with a full nmap scan to identify exposed services:  
# Quick initial scan
nmap -sS -O -sV -sC -p- --min-rate=1000 -oN initial_scan.txt

# Detailed scan of open ports  
nmap -sV -sC -A -p -oN detailed_scan.txt

# UDP scan (top ports)  
sudo nmap -sU --top-ports 1000 -oN udp_scan.txt

## Service Enumeration  
| Port | Service | Version | Notes |  
|------|---------|---------|-------|  
| 22 | SSH | OpenSSH 7.4 | Banner grabbing |  
| 80 | HTTP | Apache 2.4.6 | Web server |  
| 443 | HTTPS | Apache 2.4.6 | SSL/TLS enabled |

## Web Reconnaissance (if applicable)  
# Discover technologies  
whatweb

# Directory enumeration  
feroxbuster -u http:// -w /usr/share/wordlists/dirb/common.txt

# Alternative: Gobuster  
gobuster dir -u http:// -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt

Tools used: nmap, feroxbuster, gobuster, whatweb, nikto


# 2- Web Enumeration

## Initial Analysis  
- Detected technology: [Apache/Nginx/IIS version]  
- CMS/Framework: [WordPress/Drupal/Custom/etc]  
- Backend language: [PHP/Python/Node.js/etc]

## Directory Discovery  
# Main directories found  
feroxbuster -u http:// -w /usr/share/wordlists/dirb/common.txt -x php,html,txt,js

# Subdomains (if applicable)  
gobuster vhost -u -w /usr/share/wordlists/subdomains-top1million-5000.txt

### Interesting Directories:  
- /admin - Admin panel  
- /login - Login form  
- /uploads - Uploads directory  
- /config - Config files

## Vulnerability Analysis  
# Nikto scan  
nikto -h http://

# Burp Suite  
# - Set proxy to 127.0.0.1:8080  
# - Intercept and analyze requests/responses  
# - Look for vulnerable parameters

## Identified Attack Vectors  
- [ ] SQL Injection in login parameters  
- [ ] XSS Stored/Reflected  
- [ ] LFI/RFI in file inclusion  
- [ ] File Upload vulnerabilities  
- [ ] CSRF in critical forms  
- [ ] Directory Traversal

Tools: Burp Suite, Nikto, OWASP ZAP, SQLmap, XSSer


# 3- Exploitation

## Main Attack Vector  
Vulnerability exploited: [SQL Injection / RCE / File Upload / etc]  
Severity: [Critical/High/Medium/Low]  
CVE: [If applicable]

## Exploitation Steps

### 1. Vulnerability Identification  
[Describe how the vulnerability was found]

### 2. Exploit Development  
#!/usr/bin/env python3  
# Exploit for [VULNERABILITY]  
import requests  
import sys

target_url = 'http:///vulnerable_endpoint'  
payload =

def exploit():  
try:  
response = requests.post(target_url, data=payload)  
if 'success_indicator' in response.text:  
print('[+] Exploit successful!')  
print('[+] Response:', response.text)  
else:  
print('[-] Exploit failed')  
except Exception as e:  
print('[-] Error:', e)

if __name__ == '__main__':  
exploit()

### 3. Exploit Execution  
# Run exploit  
python3 exploit.py

# Set up reverse shell (example)  
nc -lvnp 4444 # Listener  
# Payload triggers reverse connection

## Initial Access Obtained  
- User: [www-data / apache / user]  
- Shell type: [bash/sh/cmd]  
- Initial directory: [/var/www/html / /home/user]

## Immediate Post-Exploitation  
# System info  
uname -a  
id  
whoami  
pwd

# Interesting files  
find / -name '*.txt' -type f 2>/dev/null | head -20  
find / -perm -4000 -type f 2>/dev/null # SUID binaries




# 4- Privilege Escalation

## System Enumeration  
# Basic system info  
uname -a  
cat /etc/os-release  
id  
sudo -l

# Running processes  
ps aux | grep root  
ps aux --forest

# Internal services and ports  
netstat -tulpn  
ss -tulpn

## Automated Enumeration Tools  
# LinPEAS (recommended)  
curl -L https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh | sh

# LinEnum  
./LinEnum.sh

# Linux Exploit Suggester  
./linux-exploit-suggester.sh

## Analyzed Escalation Vectors

### 1. SUID/SGID Binaries  
find / -perm -4000 -type f 2>/dev/null  
find / -perm -2000 -type f 2>/dev/null

# Interesting binaries found:  
# - /usr/bin/[binary_name]  
# - Check GTFOBins for exploitation

### 2. Sudo Misconfigurations  
sudo -l  
# Commands executable as root without password

### 3. Cron Jobs  
cat /etc/crontab  
ls -la /etc/cron.*  
crontab -l

### 4. Kernel Exploits  
# Kernel version  
uname -r

# Applicable exploits:  
# - CVE-XXXX-XXXX: [Description]  
# - Available at: [Exploit URL]

## Successful Escalation  
Method used: [SUID binary / Sudo misconfiguration / Kernel exploit / etc]

# Command/script used to escalate  
[command or specific script]

# Root verification  
id  
whoami  
cat /root/root.txt

Root obtained: ✅





# 5- User Flag

## Flag Location  
File: /home/[username]/user.txt  
Owner user: [username]

## Steps to Obtain the Flag  
# Navigate to user directory  
cd /home/[username]

# Read the flag  
cat user.txt

## User Flag  
[USER_FLAG_HERE]

## Additional Notes  
- The flag was found after [initial shell / partial escalation]  
- File permissions: [ls -la user.txt]  
- Verification hash (if applicable): [md5sum user.txt]

## Screenshot  
[Screenshot showing flag acquisition]




# 6- Root Flag

## Flag Location  
File: /root/root.txt  
Owner user: root  
Permissions: 600 (rw-------)

## Steps to Obtain the Flag  
# Verify root access  
id  
whoami

# Access root directory  
cd /root

# Read the root flag  
cat root.txt

## Root Flag  
[ROOT_FLAG_HERE]

## Full Compromise Verification  
# Verify full system access  
cat /etc/shadow | head -5  
ls -la /root/  
history

## Compromised System Info  
- Hostname: [hostname]  
- Kernel: [uname -r]  
- Distribution: [cat /etc/os-release]  
- Uptime: [uptime]

## Screenshot  
[Screenshot showing root flag acquisition]

---  
🎉 System fully compromised - Root obtained




# 7- Main Vulnerability

## Question  
What was the main vulnerability exploited to gain initial access to the system?

## Answer  
Vulnerability: [Specific vulnerability name]

### Technical Details  
- Type: [SQL Injection / RCE / File Upload / Buffer Overflow / etc]  
- Affected component: [Web app / Service / etc]  
- Vulnerable version: [Specific software version]  
- CVE (if applicable): CVE-XXXX-XXXX  
- CVSS Score: [Score if available]

### Vulnerability Description  
[Detailed explanation of what the vulnerability does and why it is exploitable]

### Impact  
- Confidentiality: [High/Medium/Low]  
- Integrity: [High/Medium/Low]  
- Availability: [High/Medium/Low]

### Attack Vector  
1. [Step 1 of the attack]  
2. [Step 2 of the attack]  
3. [Step 3 of the attack]

### Recommended Mitigation  
- [Mitigation step 1]  
- [Mitigation step 2]  
- [Mitigation step 3]

### References  
- [CVE URL if applicable]  
- [Public exploit URL if used]  
- [Additional documentation]






# 8- Lessons Learned

## CTF Reflections

### 🎯 Key Points  
- [Lesson 1]: [Description of what was learned]  
- [Lesson 2]: [Description of what was learned]  
- [Lesson 3]: [Description of what was learned]

### 💡 Important Techniques  
- Enumeration: [What worked well in recon phase]  
- Exploitation: [Key technique or tool]  
- Escalation: [Method that led to root]

### 🔧 Highlighted Tools  
| Tool | Use | Effectiveness |  
|------|-----|--------------|  
| [Tool 1] | [Purpose] | ⭐⭐⭐⭐⭐ |  
| [Tool 2] | [Purpose] | ⭐⭐⭐⭐ |  
| [Tool 3] | [Purpose] | ⭐⭐⭐ |

### ⚠️ Mistakes Made  
- [Mistake 1]: [What went wrong and how to avoid it]  
- [Mistake 2]: [What went wrong and how to avoid it]

### 📚 New Knowledge  
- [New concept learned 1]  
- [New concept learned 2]  
- [New command/technique discovered]

### 🚀 For Future CTFs  
- [ ] Remember to check [specific file/directory]  
- [ ] Always try [specific technique] in [context]  
- [ ] Never forget to enumerate [specific service/port]  
- [ ] Research more about [technology/concept]

### 📖 Useful Resources  
- [Useful documentation URL]  
- [Helpful blog post]  
- [Effective tool or wordlist]

### 🏆 Perceived Difficulty  
Personal rating: [1-10]/10

Total time: [X hours]

Most challenging aspects:  
1. [Challenge 1]  
2. [Challenge 2]

---  
Additional notes:  
[Any final observation or important reminder]


    """
    _RUNTIME["filename"] = args.filename
    _RUNTIME["md"] = md
    _flush_runtime()
    print(Fore.WHITE + f"Template saved as {args.filename}" + Style.RESET_ALL)


# ─────────────────────────────────────────────
# CLI main

def main():
    print(f"\n\n{bg.BLACK}{Fore.WHITE}In The Name of God {Style.RESET_ALL}\n\n")
    p = argparse.ArgumentParser(
        description="WriteupBuilder: creates a markdown write-up based on your inputs or creates a pre-written template."
    )
    p.add_argument(
        "-fn", "--filename",
        metavar="",
        help="Name of the output file"
    )
    p.add_argument(
        "-t", "--template",
        action="store_true",
        help="Generate an advanced pre-written template for you to fill out"
    )
    p.add_argument(
        "-rf", "--resumefile",
        metavar="",
        help="Resume writeup from an existing markdown file"
    )

    args = p.parse_args()

    if args.resumefile:
        resume_builder(args.resumefile)
    elif args.template:
        template_builder(args)
    else:
        writeup_builder(args)


if __name__ == "__main__":
    main()
