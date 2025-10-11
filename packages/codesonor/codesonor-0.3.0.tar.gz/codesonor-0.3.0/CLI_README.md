# CodeSonor CLI 🔍

**AI-Powered GitHub Repository Analyzer with Multi-LLM Support**

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Analyze any GitHub repository with AI-powered insights. Choose from 5 different AI providers!

## 🚀 Installation

### Basic (includes Gemini)
```bash
pip install codesonor
```

### With Specific Provider
```bash
pip install codesonor[openai]      # OpenAI GPT
pip install codesonor[anthropic]   # Anthropic Claude
pip install codesonor[mistral]     # Mistral AI
pip install codesonor[groq]        # Groq (fastest)
pip install codesonor[all-llm]     # All providers
```

## 🤖 Supported AI Providers

| Provider | Free Tier | Speed | Get API Key |
|----------|-----------|-------|-------------|
| **Gemini** ⭐ | ✅ Yes | Fast | [Get Key](https://aistudio.google.com/app/apikey) |
| **OpenAI** | ❌ Paid | Medium | [Get Key](https://platform.openai.com/api-keys) |
| **Claude** | ❌ Paid | Fast | [Get Key](https://console.anthropic.com/settings/keys) |
| **Mistral** | ❌ Paid | Fast | [Get Key](https://console.mistral.ai/api-keys/) |
| **Groq** ⚡ | ✅ Yes | Ultra-fast | [Get Key](https://console.groq.com/keys) |

⭐ Default | ⚡ Fastest

## ⚙️ Configuration

### One-Time Setup (Recommended)
```bash
codesonor setup
```
This interactive wizard will:
- ✅ Let you choose your AI provider
- ✅ Guide you to get the API key  
- ✅ Save everything to `~/.codesonor/config.json`
- ✅ Never ask again!

### Check Your Configuration
```bash
codesonor config
```

### Alternative Methods

**Environment Variables** (if you prefer):
```bash
# Windows (PowerShell)
$env:GEMINI_API_KEY = "your_key"
$env:GITHUB_TOKEN = "your_token"

# Linux/Mac
export GEMINI_API_KEY="your_key"
export GITHUB_TOKEN="your_token"
```

**Per-Command** (override saved config):
```bash
codesonor analyze URL --gemini-key YOUR_KEY --github-token YOUR_TOKEN
```

## 📖 Usage

### Full Analysis with AI
```bash
codesonor analyze https://github.com/owner/repo
```

### Quick Summary (No AI)
```bash
codesonor summary https://github.com/owner/repo
```

### Advanced Options
```bash
# Skip AI analysis (faster)
codesonor analyze https://github.com/owner/repo --no-ai

# Limit number of files analyzed
codesonor analyze https://github.com/owner/repo --max-files 200

# Export results as JSON
codesonor analyze https://github.com/owner/repo --json-output results.json
```

## 📊 Example Output

```
╭─────────────────────────────────────────────────╮
│  CodeSonor Analysis: awesome-project            │
╰─────────────────────────────────────────────────╯

Repository Information
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Field      ┃ Value                          ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Owner      │ awesome-owner                  │
│ Repository │ awesome-project                │
│ Stars      │ 1,234                          │
│ Forks      │ 567                            │
│ Language   │ Python                         │
└────────────┴────────────────────────────────┘

Language Distribution
┏━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━┓
┃ Language   ┃ Files    ┃ %      ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━┩
│ Python     │ 45       │ 78.5%  │
│ JavaScript │ 8        │ 14.0%  │
│ CSS        │ 4        │ 7.0%   │
│ HTML       │ 1        │ 0.5%   │
└────────────┴──────────┴────────┘

🤖 AI-Generated Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This repository implements a modern web application
framework with clean architecture and comprehensive
testing. Key features include...
```

## 🎯 Features

- **🤖 AI Analysis**: Get intelligent insights about repository purpose, architecture, and key features
- **📊 Language Stats**: Detailed breakdown of programming languages used
- **📁 Smart Filtering**: Automatically skips common directories (node_modules, dist, build)
- **⚡ Performance**: File limits and optimizations for fast analysis
- **🎨 Beautiful Output**: Rich terminal formatting with colors and tables
- **💾 Export Options**: Save results as JSON for further processing

## 🛠️ Development

Install with development dependencies:
```bash
pip install codesonor[dev]
```

Run tests:
```bash
pytest
```

## 📦 Web App Version

CodeSonor also comes with a Flask web application. To use it:

```bash
# Install with web dependencies
pip install codesonor[web]

# Clone the repository for web app files
git clone https://github.com/farhanmir/CodeSonor.git
cd CodeSonor

# Run the web server
python app.py
```

Visit `http://localhost:5000` in your browser.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

**Farhan Mir**

- GitHub: [@farhanmir](https://github.com/farhanmir)

## 🙏 Acknowledgments

- Powered by Google Gemini AI
- Built with Python, Click, and Rich
- GitHub REST API v3

---

**Note**: This tool analyzes public repositories. Ensure you have appropriate permissions before analyzing private repositories.
