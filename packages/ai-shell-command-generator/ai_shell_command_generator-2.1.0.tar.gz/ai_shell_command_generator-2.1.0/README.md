# AI Shell Command Generator

[![PyPI version](https://badge.fury.io/py/ai-shell-command-generator.svg)](https://badge.fury.io/py/ai-shell-command-generator)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Generate shell commands from natural language using AI. Supports OpenAI GPT-5, Anthropic Claude, and local Ollama models. Features intelligent risk assessment, teaching mode for learning, and cross-platform support (Windows/macOS/Linux).

## 📑 Table of Contents

- [Features](#-features)
- [AI-Assisted Getting Started](#-ai-assisted-getting-started--recommended)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [API Key Setup](#-api-key-setup)
- [Usage](#-usage)
  - [Interactive Mode](#interactive-mode)
  - [Non-Interactive Mode](#non-interactive-mode)
  - [Teaching Mode](#-teaching-mode)
- [Shell Support](#-shell-support)
- [Examples](#-examples)
- [Screenshots](#-screenshots)
- [Advanced Usage](#-advanced-usage)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### 🤖 Multi-Provider AI Support
- **OpenAI GPT-5 Family** - Latest GPT-5, GPT-5 Mini, and GPT-5 Nano models
- **Anthropic Claude** - Claude 4.1+, Sonnet 4.5, and Haiku 3.5
- **Ollama (Local AI)** - Privacy-focused, offline, free - use gpt-oss, Qwen, DeepSeek, Mistral, and more
- **Automatic model selection** - Or choose specific models for your needs

### 📚 Teaching Mode (NEW!)
- **Learn while you generate** - Understand commands before running them
- **Command breakdown** - Detailed explanation of each part
- **OS-specific notes** - BSD vs GNU differences, platform gotchas
- **Safer alternatives** - Preview steps before destructive operations
- **Interactive Q&A** - Ask clarifying questions, see examples
- **What-if scenarios** - Explore variations and alternatives

### 🖥️ Cross-Platform Support
- **Windows** - PowerShell and CMD support with native syntax
- **macOS** - BSD-compatible commands, zsh/bash support
- **Linux** - GNU tools with full feature support
- **WSL** - Works seamlessly in Windows Subsystem for Linux
- **Auto-detection** - Detects your shell and OS automatically

### ⚠️ Intelligent Risk Assessment
- **AI-powered safety analysis** - Every command checked for risks
- **Color-coded warnings** - HIGH/MEDIUM/LOW risk levels
- **Detailed explanations** - Understand what makes a command risky
- **Safer alternatives** - Suggested preview steps
- **Optional bypass** - Can disable with `--no-risk-check` for automation

### 💻 Flexible Usage Modes
- **Interactive Mode** - Guided experience with shell detection and confirmations
- **Teaching Mode** - Learn shell commands while generating them
- **Non-Interactive Mode** - Perfect for scripts, CI/CD, and automation
- **Auto-Copy** - Commands copied to clipboard automatically

## 🎓 AI-Assisted Getting Started (⭐ Recommended)

**The best way to learn this tool is with AI guidance!** Instead of reading documentation, let an AI assistant teach you interactively.

### Using Claude Code (Recommended)

If you're using [Claude Code](https://claude.com/claude-code), simply run:

```bash
/getting-started
```

This custom slash command will:
- ✅ Explain **what** the tool does and **why** it's different (teaching mode!)
- ✅ Show you cross-platform examples (Windows/macOS/Linux)
- ✅ Check if you have Ollama installed
- ✅ Check if ai-shell is installed
- ✅ Guide you through your first commands
- ✅ Teach you at your own pace with interactive Q&A

**No reading required** - just conversation!

### Using Any AI Coding Assistant

If you're using ChatGPT, Cursor, Windsurf, or any other AI assistant:

1. Copy the prompt from [.reference/AI_ASSISTANT_PROMPT.md](.reference/AI_ASSISTANT_PROMPT.md)
2. Paste it into your AI assistant
3. The AI will:
   - Read the knowledge base
   - Explain what makes this tool valuable
   - Check your system setup
   - Guide you through installation and usage
   - Answer your questions interactively

**Why this is better:**
- 🤖 **Personalized** to your platform and setup
- 💬 **Interactive** - ask questions as you go
- 🎯 **Focused** - only learn what you need right now
- ⚡ **Faster** - no searching through docs

---

## ⚡ Quick Start

**Prefer manual setup?** Here are the essential commands:

```bash
# Install with uv (recommended - fast, cross-platform, automatic PATH setup)
uv tool install ai-shell-command-generator

# Use with free local AI (no API key needed)
ai-shell -p ollama -q "find large files"

# Or use with cloud AI (interactive setup on first run)
ai-shell -p openai -q "find large files"

# Learn while you generate
ai-shell --teach -p ollama -q "backup my documents"
```

## 🚀 Installation

### Option 1: Using `uv` (⭐ Recommended)

[uv](https://github.com/astral-sh/uv) is the fastest, most reliable way to install Python CLI tools. It handles PATH setup automatically on all platforms.

```bash
# Install uv (one-time setup)
# macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell):
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Then install ai-shell (works immediately, no PATH configuration needed!)
uv tool install ai-shell-command-generator

# Update to latest version
uv tool upgrade ai-shell-command-generator

# Uninstall cleanly
uv tool uninstall ai-shell-command-generator
```

**Why uv?**
- ✅ **10-100x faster** than traditional package managers (written in Rust)
- ✅ **Automatic PATH setup** - works immediately on Windows/Mac/Linux
- ✅ **Isolated environments** - doesn't pollute your Python installation
- ✅ **Simple updates** - `uv tool upgrade` keeps you current
- ✅ **Clean uninstall** - removes everything cleanly


### From Source (Development)

```bash
git clone https://github.com/codingthefuturewithai/ai-shell-command-generator.git
cd ai-shell-command-generator

# Install with all development dependencies
uv pip install -e ".[dev]"
```

**Requirements:** Python 3.10 or higher, uv installed

### Development Setup
```bash
# Run tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/unit/test_main.py -v

# Run with coverage
uv run pytest tests/ --cov=ai_shell_command_generator --cov-report=html
```

## 🔑 API Key Setup

### Option 1: Automatic Setup (Easiest for Beginners)

Just run the tool! When you select OpenAI or Anthropic for the first time:

```bash
ai-shell -p openai -q "your query"
```

You'll be prompted:
```
🔑 OpenAI API Key Required

What would you like to do?
1. Enter my OpenAI API key now (I'll save it for you)
2. I'll set it manually via environment variable
3. Use Ollama instead (free, no API key needed)
```

**Select option 1**, paste your key, and it's saved to `~/.ai-shell-env` forever!

### Option 2: Manual Setup

#### Environment Variables (All Platforms)
```bash
# Linux/macOS
export OPENAI_API_KEY="your-key-here"
export ANTHROPIC_API_KEY="your-key-here"

# Windows PowerShell
$env:OPENAI_API_KEY="your-key-here"
$env:ANTHROPIC_API_KEY="your-key-here"
```

#### Project-Specific (.env file)
```bash
# Create .env in your project directory
echo "OPENAI_API_KEY=your-key-here" > .env
echo "ANTHROPIC_API_KEY=your-key-here" >> .env
```

#### Global Config (Persistent)
```bash
# Create ~/.ai-shell-env in your home directory
cat > ~/.ai-shell-env << EOF
OPENAI_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here
EOF
```

### Option 3: Ollama (No API Key Needed!)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull gpt-oss:latest

# Use immediately
ai-shell -p ollama -q "find large files"
```

**Recommended models:**
- `gpt-oss:latest` - OpenAI's GPT-OSS model
- `qwen2.5-coder:7b` - Excellent for coding tasks
- `deepseek-r1:8b` - Good reasoning capabilities
- `mistral-nemo:12b` - Balanced performance

### Where AI Shell Looks for API Keys

**Priority order:**
1. Environment variables (you set with `export`)
2. `./.env` file in current directory
3. `~/.ai-shell-env` file in your home directory
4. Prompts you to enter and saves to `~/.ai-shell-env`

**Simple and predictable!**

## 📖 Usage

### Interactive Mode

```bash
ai-shell
# or use the short alias
aisc
```

**Interactive flow:**
1. **Select AI Provider** - OpenAI GPT-5, Anthropic Claude, or Ollama
2. **Select Model** - Choose from available models with cost/feature info
3. **Confirm Shell** - Auto-detects your shell (bash/PowerShell/cmd), asks confirmation
4. **Enter Query** - Describe what you want in natural language
5. **Review Command** - See generated command with risk assessment
6. **Choose Action** - Use it, explain how it works, or try different approach

**Example session:**
```
Select AI Provider:
1. OpenAI GPT-5 - GPT-5 models
2. Anthropic Claude - Claude 4.1+ and 3.5 Haiku
3. Ollama (Local) - Privacy-focused, offline, free
Select your preferred AI provider: 3

Discovering available Ollama models...
1. gpt-oss:latest
2. qwen2.5-coder:7b
Select your preferred Ollama model: 1

🔍 Detected shell: bash (detected from $SHELL)
Is this correct?
1. Yes, use bash
2. No, let me choose
Select option [1]: 1

Enter your command query (or 'quit' to exit): find large files

Generated command:
find . -type f -size +100M

What would you like to do?
1. Use this command
2. Explain how it works
3. Try a different approach
Select option [1]:
```

### Non-Interactive Mode

**Perfect for scripts and automation:**

```bash
# Basic usage (shell required for safety)
ai-shell -p ollama -s bash -q "find all Python files modified today"

# With OpenAI
ai-shell -p openai -m gpt-5-nano -s bash -q "compress directory"

# With Anthropic
ai-shell -p anthropic -m claude-3-5-haiku-20241022 -s bash -q "backup documents"

# Auto-copy to clipboard
ai-shell -p ollama -s bash -q "show disk usage" --copy

# Disable risk check (for trusted automation)
ai-shell -p ollama -s bash -q "clean temp files" --no-risk-check

# Windows PowerShell
ai-shell -p ollama -s powershell -q "find large files"

# Windows CMD
ai-shell -p ollama -s cmd -q "list files"
```

**⚠️ Note:** Shell (`-s`) is required in non-interactive mode for safety. This prevents wrong commands in CI/CD pipelines.

### Utility Commands

```bash
# Check version
ai-shell --version

# List available models for a provider
ai-shell --list-models openai
ai-shell --list-models anthropic
ai-shell --list-models ollama
```

### 📚 Teaching Mode

**Learn shell commands while generating them:**

```bash
# Start in teaching mode
ai-shell --teach -p ollama -q "find files modified in last 24 hours"
```

**What you get:**
```
═══════════════════════════════════════════════════════════
📚 TEACHING MODE
═══════════════════════════════════════════════════════════

COMMAND:
  find . -type f -mtime -1

BREAKDOWN:
  find . - search from current directory
  -type f - only files (not directories)
  -mtime -1 - modified in last 24 hours

OS NOTES:
  macOS uses BSD find (no -printf option)
  -mtime uses 24-hour periods
  Use -mmin for minute-level precision

SAFER APPROACH:
  find . -type f -mtime -1 -ls
  (preview files before any action)

WHAT YOU LEARNED:
  ✓ find searches recursively by default
  ✓ -mtime uses days, -mmin uses minutes
  ✓ Negative numbers mean "less than"
  ✓ Always preview before destructive operations
```

**Interactive teaching features:**
- **Ask questions** - "What does -mtime mean?"
- **See examples** - Variations with different options
- **What-if scenarios** - "What if I only want .txt files?"
- **Alternative approaches** - Different ways to solve the same problem

### Command Line Options

```bash
Options:
  -p, --provider [openai|anthropic|ollama]
                                  AI provider to use
  -s, --shell [cmd|powershell|bash]
                                  Shell environment (required in non-interactive)
  -q, --query TEXT                Command query (enables non-interactive mode)
  -m, --model TEXT                Specific model to use
  --no-risk-check                 Disable risk assessment
  -c, --copy                      Auto-copy command to clipboard
  -t, --teach                     Enable teaching mode with explanations
  --list-models [openai|anthropic|ollama]
                                  List available models for provider
  --help                          Show help message
```

## 🐚 Shell Support

### Supported Shells

| Shell | Platforms | Command Syntax |
|-------|-----------|----------------|
| **bash** | macOS, Linux, WSL, Git Bash | Unix commands (`ls`, `find`, `grep`) |
| **powershell** | Windows, macOS, Linux | PowerShell cmdlets (`Get-ChildItem`, `Copy-Item`) |
| **cmd** | Windows | DOS commands (`dir`, `copy`, `del`) |

### Shell Detection

**Interactive mode:** Auto-detects your shell from `$SHELL` and asks for confirmation

**Non-interactive mode:** Shell must be specified with `-s` flag for safety

```bash
# Explicit shell selection (required for non-interactive)
ai-shell -s bash -q "your query"
ai-shell -s powershell -q "your query"
ai-shell -s cmd -q "your query"
```

### Platform Examples

```bash
# macOS (BSD commands)
ai-shell -s bash -q "find files" 
# → find . -name "*.txt" (no -printf, BSD-compatible)

# Linux (GNU commands)
ai-shell -s bash -q "find files with details"
# → find . -name "*.txt" -printf "%p %s\n" (GNU-specific)

# Windows PowerShell
ai-shell -s powershell -q "find files"
# → Get-ChildItem -Recurse -Filter "*.txt"

# Windows CMD
ai-shell -s cmd -q "list files"
# → dir /s *.txt
```

## 🎯 Examples

### Basic Commands
```bash
# List files
ai-shell -p ollama -s bash -q "list files in current directory"
# → ls -la

# Find files
ai-shell -p ollama -s bash -q "find PDF files larger than 10MB"
# → find . -name "*.pdf" -size +10M

# Disk usage
ai-shell -p ollama -s bash -q "show disk usage sorted by size"
# → du -sh * | sort -h
```

### Risky Commands (with warnings)
```bash
ai-shell -p ollama -s bash -q "delete all .log files"

# Output:
find . -type f -name "*.log" -delete

# WARNING: HIGH risk - Recursively deletes all log files without confirmation
```

### Teaching Mode Examples
```bash
# Learn about file operations
ai-shell --teach -p ollama -s bash -q "copy all PDFs to backup folder"

# Understand complex piping
ai-shell --teach -p anthropic -s bash -q "find largest 10 files"

# Learn PowerShell
ai-shell --teach -p ollama -s powershell -q "list running services"
```

### Cross-Platform Examples
```bash
# Same query, different shells
ai-shell -p ollama -s bash -q "find large files"
# → find . -type f -size +100M

ai-shell -p ollama -s powershell -q "find large files"
# → Get-ChildItem -Recurse | Where-Object {$_.Length -gt 100MB}

ai-shell -p ollama -s cmd -q "find large files"
# → forfiles /S /M *.* /C "cmd /c if @fsize GTR 104857600 echo @path"
```

### Advanced Examples
```bash
# Complex text processing
ai-shell -p openai -m gpt-5 -s bash -q "search all JavaScript files for TODO comments, show file and line number"

# System monitoring
ai-shell -p anthropic -s bash -q "show processes using more than 500MB RAM, sorted by memory usage"

# Backup with compression
ai-shell -p ollama -s bash -q "create dated backup archive of documents folder"
```

## 🖼️ Screenshots

### Interactive Mode with Risk Assessment
![Interactive mode showing risk warnings](images/anthropic-interactive-with-warning.png)

### Interactive Ollama Model Selection
![Interactive Ollama model selection](images/ollama-interactive-with-model-select.png)
*Interactive mode with Ollama model discovery and selection - users can choose from all available models*

### Non-Interactive Mode
![Non-interactive mode with warnings](images/anthropic-non-interactive-with-warning.png)

### Ollama Integration with Auto-Copy
![Ollama integration with copy functionality](images/ollama-non-interactive-with-copy.png)

## 🔧 Advanced Usage

### List Available Models

```bash
# See OpenAI models with costs
ai-shell --list-models openai

# Output:
# • GPT-5 Nano (Oct 2025)
#   Ultra cost-effective GPT-5 variant
#   Cost: $0.05/$0.05 per 1M tokens
#   Best for: quick, simple
#
# • GPT-5 Mini (Oct 2025)
#   Cost-effective GPT-5 variant  
#   Cost: $0.25/$0.25 per 1M tokens
#   Best for: general, teaching
#
# • GPT-5 (Oct 2025)
#   Flagship GPT-5 model
#   Cost: $1.25/$1.25 per 1M tokens
#   Best for: complex, teaching, critical

# See Anthropic models
ai-shell --list-models anthropic

# See your local Ollama models
ai-shell --list-models ollama
```

### Supported Models

**OpenAI:**
- `gpt-5` - Flagship model with advanced capabilities
- `gpt-5-mini` - Balanced performance and cost (default)
- `gpt-5-nano` - Ultra cost-effective for simple tasks

**Anthropic:**
- `claude-sonnet-4-5-20250929` - Latest balanced model (default)
- `claude-opus-4-1-20250805` - Most powerful for complex reasoning
- `claude-3-5-haiku-20241022` - Fast and cost-effective

**Ollama (dynamically detected):**
- `gpt-oss:latest` - OpenAI's open-source GPT-OSS
- `qwen2.5-coder:7b` - Excellent for coding tasks
- `deepseek-r1:8b` - Good reasoning capabilities
- `mistral-nemo:12b` - Balanced performance
- Any model you have pulled locally

### CI/CD and Automation

**For reliable automation, always specify shell:**

```bash
# In scripts or CI/CD pipelines
COMMAND=$(ai-shell -s bash -p ollama -q "cleanup old logs" --no-risk-check)
echo "Generated: $COMMAND"
eval "$COMMAND"

# With error handling
if COMMAND=$(ai-shell -s bash -p ollama -q "backup data" 2>/dev/null); then
    echo "Running: $COMMAND"
    eval "$COMMAND"
else
    echo "Failed to generate command"
    exit 1
fi
```

### Environment Variables

```bash
# API Keys (automatic or manual)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Ollama (optional)
OLLAMA_HOST=localhost:11434  # Custom Ollama host
```

## 🏗️ How It Works

1. **Shell Detection** - Auto-detects your shell and OS
2. **Query Analysis** - Understands your natural language request
3. **AI Generation** - Creates platform-specific command
4. **Risk Assessment** - Analyzes for potential dangers
5. **Teaching (Optional)** - Explains how the command works
6. **User Confirmation** - Review before execution
7. **Clipboard Copy** - Ready to paste and run

### Risk Assessment

Commands are analyzed for:
- **Data deletion** (`rm`, `dd`, destructive operations)
- **Permission changes** (`chmod`, `chown`, security risks)
- **System modifications** (network, system files)
- **Recursive operations** (widespread changes)
- **Network exposure** (security vulnerabilities)

## 🧪 Development

```bash
# Clone and setup
git clone https://github.com/codingthefuturewithai/ai-shell-command-generator.git
cd ai-shell-command-generator

# Install with development dependencies
uv pip install -e ".[dev]"

# Run tests
uv run pytest tests/ -v
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Commit your changes: `git commit -am 'Add feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔍 Troubleshooting

### API Key Issues

**"API key not found" error:**
- Check `~/.ai-shell-env` exists and has your key
- Or run interactively and let the tool prompt you
- Or set environment variable: `export OPENAI_API_KEY="..."`

**Can't save API key:**
- Check home directory is writable
- Manually create: `echo "OPENAI_API_KEY=your-key" > ~/.ai-shell-env`

### Ollama Issues

**"Could not connect to Ollama":**
```bash
# Start Ollama
ollama serve

# Pull a model if you don't have one
ollama pull gpt-oss:latest
```

**"No models found":**
```bash
# List available models
ollama list

# Pull a model
ollama pull gpt-oss:latest
```

### Shell Issues

**Wrong command syntax generated:**
- Make sure you specified the correct shell with `-s`
- In non-interactive mode, shell is REQUIRED
- Check: `ai-shell -s powershell -q "query"` for PowerShell
- Check: `ai-shell -s cmd -q "query"` for Windows CMD

**Shell not detected correctly:**
- Override in interactive mode when prompted
- Or specify explicitly with `-s bash` or `-s powershell`

### Platform-Specific

**Windows:**
- PowerShell and CMD both supported
- Git Bash works with `-s bash`
- WSL works with `-s bash`

**macOS:**
- Uses BSD-compatible commands automatically
- Both bash and zsh supported (zsh uses bash mode)

**Linux:**
- Full GNU tool support
- bash is default and recommended

## 🙏 Acknowledgments

- [OpenAI](https://openai.com/) for GPT-5 models and GPT-OSS
- [Anthropic](https://www.anthropic.com/) for Claude AI
- [Ollama](https://ollama.com/) for local AI infrastructure
- [Click](https://click.palletsprojects.com/) for CLI framework

---

**Made with ❤️ for everyone learning to master the command line.**