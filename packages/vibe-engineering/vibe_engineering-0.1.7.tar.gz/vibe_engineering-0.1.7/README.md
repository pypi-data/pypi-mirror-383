# 🚀 Vibe Engineering CLI

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **AI-powered specification and memory management CLI for modern development teams**

Vibe Engineering is a powerful command-line tool that helps development teams manage specifications, project knowledge, and development workflows using AI assistance. Built with VoyageAI embeddings and MongoDB vector search for intelligent document management.

## ✨ Features

- 🤖 **AI-Powered Specifications** - Generate detailed specs using advanced LLMs
- 🧠 **Memory Management** - Store and retrieve project knowledge with vector search
- 👥 **Team Collaboration** - Track team members and project ownership
- 📊 **Rich CLI Experience** - Beautiful, interactive command-line interface
- 🔍 **Vector Search** - Find relevant information using semantic similarity
- 📝 **Multiple Formats** - Export specifications in JSON, YAML, and Markdown

## 🚀 Quick Install

### PowerShell (Windows)
```powershell
PowerShell -ExecutionPolicy Bypass -Command "iwr -useb https://raw.githubusercontent.com/vibeengineering/vibe-engineering/main/install.ps1 | iex"
```

### Bash (Linux/macOS)
```bash
curl -sSL https://raw.githubusercontent.com/vibeengineering/vibe-engineering/main/install.sh | bash
```

### Manual Installation
```bash
# Clone the repository
git clone https://github.com/vibeengineering/vibe-engineering.git
cd vibe-engineering

# Install dependencies
pip install -r requirements.txt

# Install the CLI
pip install -e .

# Setup configuration
cp .env.dist .env
# Edit .env with your API keys
```

## ⚙️ Configuration

1. **Copy environment template:**
   ```bash
   cp .env.dist .env
   ```

2. **Configure your API keys in `.env`:**
   ```bash
   # VoyageAI Configuration
   VOYAGE_API_KEY=your_voyage_api_key_here
   VOYAGE_MODEL=voyage-2

   # MongoDB Configuration
   MONGODB_URI=your_mongodb_connection_string
   MONGO_DB=your_database_name
   MONGO_COLLECTION=memories

   # Fireworks AI Configuration
   FIREWORKS_API_KEY=your_fireworks_api_key_here
   FIREWORKS_MODEL=accounts/fireworks/models/llama-v3p1-70b-instruct
   ```

## 📖 Usage

### Basic Commands

```bash
# Show system status
vibe status

# Display team members
vibe team

# Generate AI specification
vibe specify "Create a user authentication system"

# Show version
vibe version

# Get help
vibe --help
```

### Advanced Usage

```bash
# Generate specification with options
vibe specify "Add payment processing" --format json --save --verbose

# Custom output formats
vibe specify "User dashboard" --format markdown

# Save specification to database
vibe specify "API rate limiting" --save
```

## 📋 Commands Reference

| Command | Description | Example |
|---------|-------------|---------|
| `vibe status` | 🔍 Show system status and configuration | `vibe status` |
| `vibe team` | 👥 Display team members from database | `vibe team` |
| `vibe specify` | ✨ Generate AI-powered specifications | `vibe specify "Add user auth"` |
| `vibe version` | 📦 Show version information | `vibe version` |

### Specify Command Options

```bash
vibe specify PROMPT [OPTIONS]

Options:
  -f, --format     Output format: json, yaml, markdown (default: json)
  -s, --save       Save specification to database
  -v, --verbose    Show detailed output
  --help           Show help message
```

## 🏗️ Architecture

```
├── src/
│   ├── cli/           # Command-line interface
│   ├── db/            # Database operations (MongoDB)
│   ├── llm/           # LLM clients (Fireworks, VoyageAI)
│   └── schemas/       # Data models and schemas
├── install.ps1        # PowerShell installer
├── install.sh         # Bash installer
├── setup.py          # Python package setup
└── requirements.txt   # Dependencies
```

## 🛠️ Development

### Prerequisites
- Python 3.10+
- MongoDB (Atlas or local)
- VoyageAI API key
- Fireworks AI API key

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/vibeengineering/vibe-engineering.git
cd vibe-engineering

# Install development dependencies
pip install -r requirements-dev.txt

# Install in development mode
pip install -e .

# Run tests
pytest

# Format code
black .

# Type checking
mypy src/
```

### Running Locally

```bash
# Run CLI directly
python -m src.cli --help

# Or use the installed command
vibe --help
```

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VOYAGE_API_KEY` | VoyageAI API key for embeddings | Required |
| `VOYAGE_MODEL` | VoyageAI model to use | `voyage-2` |
| `MONGODB_URI` | MongoDB connection string | Required |
| `MONGO_DB` | Database name | `master` |
| `MONGO_COLLECTION` | Collection name | `memories` |
| `FIREWORKS_API_KEY` | Fireworks AI API key | Required |
| `FIREWORKS_MODEL` | Fireworks model to use | `llama-v3p1-70b-instruct` |

## 🚦 System Requirements

- **Python**: 3.10 or higher
- **Memory**: 512MB RAM minimum
- **Storage**: 100MB free space
- **Network**: Internet connection for AI APIs
- **Database**: MongoDB Atlas or local MongoDB instance

## 📚 Documentation

- [Installation Guide](./docs/installation.md)
- [Configuration Reference](./docs/configuration.md)
- [API Documentation](./docs/api.md)
- [Contributing Guide](./CONTRIBUTING.md)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](./CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## 🆘 Support

- 📧 Email: support@vibeengineering.com
- 💬 GitHub Issues: [Create an issue](https://github.com/vibeengineering/vibe-engineering/issues)
- 📖 Documentation: [Read the docs](https://docs.vibeengineering.com)

## 🙏 Acknowledgments

- Built with [Typer](https://typer.tiangolo.com/) for the CLI framework
- Powered by [VoyageAI](https://www.voyageai.com/) for embeddings
- Uses [Fireworks AI](https://fireworks.ai/) for LLM capabilities
- Styled with [Rich](https://rich.readthedocs.io/) for beautiful terminal output

---

**Made with ❤️ by the Vibe Engineering Team**