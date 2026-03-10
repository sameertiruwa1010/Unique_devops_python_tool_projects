# cmd-ai 🤖

**An AI-powered Linux command assistant. Describe what you want — get the exact shell command.**

```bash
$ cmd-ai "find large files"

  ╭─ 🤖 AI Suggested ──────────────────────────────────────────╮
  │   find / -size +100M -type f 2>/dev/null                   │
  ╰────────────────────────────────────────────────────────────╯
  Query:  find large files
  Run:    find / -size +100M -type f 2>/dev/null
```

---

## Table of Contents

- [What is cmd-ai?](#what-is-cmd-ai)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [API Key Setup](#api-key-setup)
- [Usage](#usage)
- [All Commands & Flags](#all-commands--flags)
- [Examples](#examples)
- [Using Ollama (Free & Offline)](#using-ollama-free--offline)
- [Using Claude API (Anthropic)](#using-claude-api-anthropic)
- [Project Structure](#project-structure)
- [Running Tests](#running-tests)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## What is cmd-ai?

`cmd-ai` is a command-line tool that converts plain English descriptions into Linux/Unix shell commands using AI. Instead of searching Stack Overflow or man pages, just describe what you want to do and get the right command instantly.

It works in three layers:

```
Your description (plain English)
        ↓
Local database lookup (instant, no API needed)
        ↓  (if not found)
AI Model — OpenAI / Claude / Ollama
        ↓
Suggested command
        ↓
Optional: explain the command
        ↓
Optional: execute with confirmation
```

---

## Features

- **Plain English → Shell command** using AI (OpenAI, Claude, or Ollama)
- **Local command database** with 80+ pre-mapped commands for instant offline results
- **Explain mode** — breaks down what each part of a command does
- **Execute mode** — runs the suggested command after your confirmation
- **Safety checks** — warns before running destructive commands like `rm -rf`
- **Interactive REPL** — back-and-forth session without retyping `cmd-ai` each time
- **Custom database** — add your own command shortcuts
- **Multiple AI backends** — OpenAI, Anthropic Claude, or local Ollama

---

## Requirements

- Python 3.8 or higher
- pip
- One of the following:
  - OpenAI API key (paid, from [platform.openai.com](https://platform.openai.com))
  - Anthropic API key (free tier, from [console.anthropic.com](https://console.anthropic.com))
  - Ollama installed locally (free, fully offline)

---

## Installation

### Step 1 — Clone the repository

```bash
git clone https://github.com/yourusername/cmd-ai.git
cd cmd-ai
```

### Step 2 — Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

> On Windows use: `venv\Scripts\activate`

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Install cmd-ai as a global command

```bash
pip install -e .
```

### Step 5 — Verify installation

```bash
cmd-ai --help
```

---

## API Key Setup

`cmd-ai` supports three AI backends. You only need one.

### Option A — OpenAI (GPT)

```bash
export OPENAI_API_KEY=sk-your_key_here
```

Get a key at: https://platform.openai.com/api-keys

To make it permanent, add it to your shell profile:

```bash
echo 'export OPENAI_API_KEY=sk-your_key_here' >> ~/.bashrc
source ~/.bashrc
```

### Option B — Anthropic Claude (recommended — has a free tier)

```bash
pip install anthropic
export ANTHROPIC_API_KEY=sk-ant-your_key_here
```

Get a free key at: https://console.anthropic.com

### Option C — Ollama (completely free, runs offline)

See [Using Ollama](#using-ollama-free--offline) section below.

---

## Usage

### Basic — get a command suggestion

```bash
cmd-ai "your description here"
```

```bash
cmd-ai "find large files"
cmd-ai "kill process on port 3000"
cmd-ai "check disk space"
cmd-ai "show top 10 memory consuming processes"
cmd-ai "compress the logs folder"
cmd-ai "find files modified in the last 7 days"
cmd-ai "watch cpu and memory usage live"
```

### Get an explanation of the suggested command

```bash
cmd-ai "find large files" --explain
cmd-ai "find large files" -e
```

Output:
```
╭─ Explanation ──────────────────────────────────────────────╮
│ find       → search for files in a directory tree          │
│ /          → start from the root directory                 │
│ -size +100M→ only files larger than 100 megabytes          │
│ -type f    → only regular files (not directories)          │
│ 2>/dev/null→ suppress permission error messages            │
╰────────────────────────────────────────────────────────────╯
```

### Suggest AND execute the command

```bash
cmd-ai "show disk usage" --run
cmd-ai "show disk usage" -r
```

You will always be asked to confirm before anything runs:

```
  Command to execute:  df -h

  Run this command? [y/N]: y
```

### Skip confirmation (use carefully)

```bash
cmd-ai "show disk usage" --run --yes
cmd-ai "show disk usage" -r -y
```

### Use local Ollama instead of OpenAI

```bash
cmd-ai "find large files" --ollama
```

### Interactive session

```bash
cmd-ai interactive
```

```
cmd-ai> find large files
cmd-ai> kill process on port 8080
cmd-ai> run show disk usage        ← prefix with 'run' to execute
cmd-ai> exit
```

### Explain a command directly

```bash
cmd-ai explain "find / -size +100M -type f 2>/dev/null"
```

### List all commands in the local database

```bash
cmd-ai list
cmd-ai list --search "disk"
cmd-ai list --search "find"
```

### Add a custom command to the local database

```bash
cmd-ai add "backup home folder" "tar -czf ~/backup.tar.gz ~/"
cmd-ai add "flush dns" "sudo systemd-resolve --flush-caches"
```

---

## All Commands & Flags

### Main command

```
cmd-ai "QUERY" [OPTIONS]
```

| Flag | Short | Description |
|------|-------|-------------|
| `--explain` | `-e` | Explain each part of the suggested command |
| `--run` | `-r` | Execute the command (asks for confirmation) |
| `--yes` | `-y` | Skip confirmation prompt when used with `--run` |
| `--ollama` | | Use local Ollama AI instead of OpenAI |
| `--model` | `-m` | Specify a model (e.g. `gpt-4o`, `mistral`) |
| `--no-db` | | Skip local database, query AI directly |
| `--help` | `-h` | Show help message |

### Subcommands

| Subcommand | Description |
|------------|-------------|
| `cmd-ai interactive` | Start an interactive REPL session |
| `cmd-ai list` | List all entries in the local database |
| `cmd-ai list --search KEYWORD` | Filter database entries by keyword |
| `cmd-ai add "DESC" "CMD"` | Add a custom entry to the database |
| `cmd-ai explain "COMMAND"` | Explain what a Linux command does |

---

## Examples

```bash
# Network
cmd-ai "show all open ports"
cmd-ai "check if port 80 is open"
cmd-ai "show my ip address"
cmd-ai "trace route to google.com"

# Files & Disk
cmd-ai "find all .log files older than 30 days"
cmd-ai "check which folder is using the most space"
cmd-ai "find duplicate files"
cmd-ai "show the 10 largest files"

# Processes
cmd-ai "kill all python processes"
cmd-ai "show what process is using port 5432"
cmd-ai "run a command every 5 seconds"

# System
cmd-ai "check system memory usage"
cmd-ai "show all running services"
cmd-ai "check when the system last rebooted"
cmd-ai "show cpu temperature"

# Users & Permissions
cmd-ai "add a new user called john"
cmd-ai "give a file execute permission"
cmd-ai "show who is logged in"

# With explanation
cmd-ai "sync two folders" --explain

# With execution
cmd-ai "show disk space" --run
```

---

## Using Ollama (Free & Offline)

Ollama lets you run AI models locally on your machine — no API key, no internet, no cost.

### Step 1 — Install Ollama

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Step 2 — Pull a model

```bash
ollama pull mistral        # recommended — fast and accurate
# or
ollama pull llama3         # more powerful but slower
# or
ollama pull phi3           # lightweight, good for low-spec machines
```

### Step 3 — Start Ollama

```bash
ollama serve
```

### Step 4 — Use cmd-ai with Ollama

```bash
cmd-ai "find large files" --ollama
cmd-ai "check disk space" --ollama --model llama3
```

---

## Using Claude API (Anthropic)

Anthropic offers a free tier for their Claude API, making it a great alternative if your OpenAI quota is exceeded.

### Step 1 — Install the Anthropic SDK

```bash
pip install anthropic
```

### Step 2 — Get your API key

Sign up at https://console.anthropic.com and create an API key.

### Step 3 — Set the key

```bash
export ANTHROPIC_API_KEY=sk-ant-your_key_here
```

### Step 4 — Update ai_engine.py

Open `cmd_ai/ai_engine.py` and replace the `ask_openai` function body with:

```python
def ask_openai(query: str, model: str = "claude-haiku-4-5-20251001") -> str:
    import anthropic
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY not set.")
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=model,
        max_tokens=200,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": query}],
    )
    return message.content[0].text.strip()
```

---

## Project Structure

```
cmd-ai/
├── cmd_ai/                     # Main Python package
│   ├── __init__.py             # Package marker + version
│   ├── main.py                 # CLI entry point (Click)
│   ├── ai_engine.py            # OpenAI / Ollama / Claude integration
│   ├── database.py             # Local command database with fuzzy lookup
│   └── commands_db.json        # 80+ pre-mapped Linux commands
├── tests/
│   ├── test_database.py        # Unit tests for database module
│   └── test_executor.py        # Unit tests for executor module
├── setup.py                    # Package config and entry points
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
└── README.md
```

---

## Running Tests

```bash
# Install pytest if you haven't already
pip install pytest

# Run all tests
pytest tests/ -v

# Run a specific test file
pytest tests/test_database.py -v
```

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'cmd_ai'`

Your package folder has the wrong name, or `pip install -e .` was not run inside the virtualenv.

```bash
# Check your folder is named exactly cmd_ai
ls

# Reinstall
pip install -e .
```

### `ModuleNotFoundError: No module named 'cmd_ai.executor'`

A file is missing from the `cmd_ai/` folder. Check all files exist:

```bash
ls cmd_ai/
# Should show: __init__.py  ai_engine.py  commands_db.json  database.py  executor.py  main.py
```

### `Error 429 — insufficient_quota`

Your OpenAI account has run out of credits.

- Add credits at https://platform.openai.com/settings/billing
- Or switch to Claude (free tier): see [Using Claude API](#using-claude-api-anthropic)
- Or switch to Ollama (fully free): see [Using Ollama](#using-ollama-free--offline)

### `Error 401 — invalid API key`

Your API key is wrong or not set. Check it with:

```bash
echo $OPENAI_API_KEY
```

If it is empty, set it:

```bash
export OPENAI_API_KEY=sk-your_key_here
```

### `cmd-ai: command not found`

The virtualenv is not active, or `pip install -e .` was not run.

```bash
source venv/bin/activate
pip install -e .
cmd-ai --help
```

---

## Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Run tests: `pytest tests/ -v`
5. Commit: `git commit -m "Add my feature"`
6. Push: `git push origin feature/my-feature`
7. Open a Pull Request

### Ideas for contributions

- Add more commands to `commands_db.json`
- Add support for more AI providers (Gemini, Cohere, etc.)
- Add a `--copy` flag to copy the command to clipboard
- Add shell completion (bash/zsh)
- Add a config file (`~/.cmd-ai.conf`) for persistent settings

---

## License

MIT License — free to use, modify, and distribute.

---

## Acknowledgements

- [Click](https://click.palletsprojects.com/) — CLI framework
- [Rich](https://github.com/Textualize/rich) — terminal formatting
- [OpenAI](https://openai.com) — GPT models
- [Anthropic](https://anthropic.com) — Claude models
- [Ollama](https://ollama.ai) — local AI models
