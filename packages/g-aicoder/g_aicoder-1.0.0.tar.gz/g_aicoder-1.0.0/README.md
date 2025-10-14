# gCoder - Advanced AI Development Assistant

[![PyPI version](https://img.shields.io/pypi/v/gcoder.svg)](https://pypi.org/project/gcoder/)
[![Python versions](https://img.shields.io/pypi/pyversions/gcoder.svg)](https://pypi.org/project/gcoder/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**gCoder** is an advanced AI-powered development assistant that supports multiple AI providers from local to cloud. It provides intelligent code editing, analysis, and development assistance through a clean command-line interface.

## 🚀 Quick Start

### Installation

```bash
pip install gcoder
```

### First Run Setup

```bash
gcoder chat
```

On first run, gCoder will guide you through:
1. **Permissions Setup** - Grant file operation permissions
2. **Provider Selection** - Choose your AI provider
3. **Model Selection** - Select specific model
4. **API Key Setup** - For cloud providers

## ✨ Features

- 🤖 **Multi-Provider AI Support** - Use any AI model (Ollama, OpenAI, Anthropic, Google, DeepSeek)
- 💻 **Code Intelligence** - Smart code editing, analysis, and improvements
- 📁 **File Operations** - Create, copy, move, delete files with AI assistance
- 🔍 **Advanced Search** - Regex pattern matching across codebases
- 🖼️ **Multi-modal Analysis** - Image analysis for screenshots and UI elements
- 💬 **Interactive Chat** - Natural conversation with conversation history
- ⚡ **Real-time Streaming** - Live response streaming for better UX
- 🔧 **Command-line Interface** - Intuitive CLI with multiple subcommands

## 🛠️ Usage

### Interactive Chat Session
```bash
gcoder chat
```

### Edit Files with AI Assistance
```bash
gcoder edit main.py --instruction "Add error handling"
```

### Search for Patterns
```bash
gcoder search "TODO" --path src/
```

### Analyze Codebase
```bash
gcoder analyze --path .
```

### Image Analysis
```bash
gcoder image screenshot.png --context code
```

### File Operations
```bash
gcoder file create new_file.py
gcoder file copy source.py destination.py
gcoder file move old.py new.py
gcoder file delete unwanted.py
```

## 🤖 AI Providers

gCoder supports multiple AI providers with a completely generic configuration system:

### Pre-configured Providers

1. **Ollama (Local)** - Free, private, offline
   - Models: qwen2.5-coder:7b, codellama:7b, deepseek-coder:6.7b, llava:7b

2. **OpenAI (Cloud)** - High-quality responses
   - Models: GPT-4, GPT-3.5-turbo

3. **Anthropic (Cloud)** - Excellent for coding tasks
   - Models: Claude-3-Sonnet, Claude-3-Haiku

4. **Google AI (Cloud)** - Fast and reliable
   - Models: Gemini Pro

5. **DeepSeek (Cloud)** - Specialized for coding
   - Models: DeepSeek Coder

### Configuration

All providers are configured through `~/.gcoder/config.json`:

```json
{
  "ai_provider": "ollama",
  "providers": {
    "ollama": {
      "name": "Ollama (Local)",
      "type": "local",
      "base_url": "http://localhost:11434",
      "api_endpoint": "/api/generate",
      "models": [
        {
          "name": "qwen2.5-coder:7b",
          "description": "Qwen2.5 Coder 7B - Recommended for coding"
        }
      ],
      "selected_model": "qwen2.5-coder:7b",
      "timeout": 600,
      "temperature": 0.7,
      "max_tokens": 4096
    }
  }
}
```

## 📋 Requirements

- **Python**: 3.8 or higher
- **Dependencies**: 
  - `aiohttp>=3.13.0`
  - `Pillow>=10.0.0`
- **Optional**: Ollama for local AI models

## 🔧 Development

### Installation from Source

```bash
git clone https://github.com/prdpspkt/gCoder.git
cd gCoder
pip install -e .
```

### Project Structure

```
gcoder/
├── main.py                 # CLI entry point
├── core/                   # Core AI functionality
│   ├── ai_assistant.py    # Main AI assistant
│   └── chat_manager.py    # Chat management
├── handlers/              # Request handlers
│   └── request_handlers.py
└── utils/                 # Utility modules
```

## 🐛 Troubleshooting

### Common Issues

1. **Ollama Connection Error**
   - Ensure Ollama is running: `ollama serve`
   - Check base URL in config: `http://localhost:11434`

2. **API Key Issues**
   - Verify API keys for cloud providers
   - Check provider configuration

3. **Permission Errors**
   - Grant permissions during first-run setup
   - Check file/directory permissions

### Getting Help

- **Issues**: [GitHub Issues](https://github.com/prdpspkt/gCoder/issues)
- **Documentation**: Check this README and inline help: `gcoder --help`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Support

If you encounter any problems or have questions:

1. Check the [troubleshooting](#troubleshooting) section
2. Search [existing issues](https://github.com/prdpspkt/gCoder/issues)
3. Create a [new issue](https://github.com/prdpspkt/gCoder/issues/new) with detailed information

---

**gCoder** - Making AI-assisted development accessible and powerful for everyone! 🚀
