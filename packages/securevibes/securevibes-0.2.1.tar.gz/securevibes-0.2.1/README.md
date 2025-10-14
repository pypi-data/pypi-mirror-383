# 🛡️ SecureVibes

**AI-Native Security System for Vibecoded Applications**

SecureVibes uses **Claude's multi-agent architecture** to autonomously find security vulnerabilities in your codebase. Four specialized AI agents work together to deliver comprehensive, context-aware security analysis with concrete evidence.

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

---

## 🚀 Quick Start

```bash
# Install for the latest release on PyPi (might not have all the latest changes in the code)
pip install securevibes

# NOTE: the package uploaded on PyPi might not have all the latest changes. 
# I will try to release a new version of the package whenever there are significant changes/developments
# If you would rather use the version with the latest changes, you can do the following:

# Install for the latest version (might be buggy)
git clone https://github.com/anshumanbh/securevibes.git
cd securevibes
virtualenv env
. env/bin/activate
pip install -e packages/core

# Authenticate (choose one method)
# Method 1: Session-based (recommended)
# You could use your Claude subscription here, if you don't want to pay per API requests
claude  # Run interactive CLI, then type: /login

# Method 2: API key
export ANTHROPIC_API_KEY="your-api-key-here"

# Scan your project
securevibes scan /path/to/code --debug

# The most important part
# Sit back and relax. Please be patient as the scans might take some time, depending upon the model being used.
```

Get your API key from: https://console.anthropic.com/

---

## 🤖 Multi-Agent Architecture

SecureVibes orchestrates 4 specialized Claude agents:

1. **Assessment Agent** - Maps codebase architecture and technology stack
2. **Threat Modeling Agent** - Applies STRIDE methodology for realistic threats
3. **Code Review Agent** - Uses security thinking framework to find vulnerabilities
4. **Report Generator** - Compiles findings into actionable reports

**Key Difference:** Unlike traditional pattern-matching tools, SecureVibes agents *understand* your code's context, architecture, and business logic to find novel vulnerabilities that static analysis misses.

---

## 🎯 Common Use Cases

```bash
# Default: creates .securevibes/scan_report.md (markdown format)
securevibes scan .

# Real-time progress tracking (always enabled)
securevibes scan .

# Export JSON for CI/CD pipeline
securevibes scan . --format json --output security-report.json

# Custom markdown report (saved to .securevibes/custom_report.md)
securevibes scan . --format markdown --output custom_report.md

# Terminal table output (no file saved)
securevibes scan . --format table

# Focus on critical/high severity
securevibes scan . --severity high

# Fast scan with cheaper model
securevibes scan . --model haiku

# Quiet mode for automation
securevibes scan . --quiet
```

---

## ⚙️ Configuration

### Model Selection

SecureVibes uses a **three-tier priority system** for model selection:

**Priority Hierarchy:**
1. 🥇 **Per-agent environment variables** (highest)
2. 🥈 **CLI `--model` flag** (applies to all agents)
3. 🥉 **Default "sonnet"** (fallback)

**Examples:**

```bash
# All agents use haiku
securevibes scan . --model haiku

# All use haiku, except code-review uses opus
export SECUREVIBES_CODE_REVIEW_MODEL=opus
securevibes scan . --model haiku

# Fine-grained control per agent
export SECUREVIBES_ASSESSMENT_MODEL=haiku
export SECUREVIBES_CODE_REVIEW_MODEL=opus
securevibes scan .  # Others use default (sonnet)
```

**Available models:** `haiku` (fast/cheap), `sonnet` (balanced), `opus` (thorough/expensive)

### Per-Agent Model Override

Override specific agent models via environment variables:

```bash
# Authenticate first (see Quick Start above)

# Override specific agent models (overrides CLI --model flag)
export SECUREVIBES_CODE_REVIEW_MODEL="opus"  # Max accuracy
export SECUREVIBES_THREAT_MODELING_MODEL="sonnet"

# Control analysis depth (default: 50)
export SECUREVIBES_MAX_TURNS=75  # Deeper analysis
```

---

## 🐍 Python API

```python
import asyncio
from securevibes import Scanner

async def main():
    # Authentication is automatically handled by Claude Agent SDK via:
    # - ANTHROPIC_API_KEY environment variable, or
    # - Session token from `claude` CLI (run: claude, then /login)
    scanner = Scanner(
        model="sonnet",  # Use shorthand: sonnet, haiku, opus
        debug=True  # Show agent narration for verbose output
    )
    
    result = await scanner.scan("/path/to/repo")
    print(f"Found {len(result.issues)} vulnerabilities")
    print(f"Cost: ${result.total_cost_usd:.4f}")

asyncio.run(main())
```

---

## 📚 Full Documentation

This is a quick reference for PyPI users. For comprehensive documentation, visit:

**📖 [Full Documentation on GitHub](https://github.com/anshumanbh/securevibes)**

Including:
- 🏗️ [Architecture Deep Dive](https://github.com/anshumanbh/securevibes/blob/main/docs/ARCHITECTURE.md)
- 🌊 [Streaming Mode Guide](https://github.com/anshumanbh/securevibes/blob/main/docs/STREAMING_MODE.md) - Real-time progress tracking

---

## 👤 Author

Built by [@anshumanbh](https://github.com/anshumanbh)

🌟 **Star the repo** to follow development!

---

## 🙏 Acknowledgments

- Powered by [Claude](https://www.anthropic.com/claude) by Anthropic
- Built with [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python)
- Inspired by traditional SAST tools, reimagined with AI

---

**License:** AGPL-3.0 | **Requires:** Python 3.10+
