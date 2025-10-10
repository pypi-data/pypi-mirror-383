# Installation Guide

This guide covers different ways to install and set up MarkitDown Chunker.

## Quick Install (PyPI)

**Note**: Package needs to be published to PyPI first.

```bash
pip install markitdown-chunker
```

## Install from Source

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/markitdown-chunker.git
cd markitdown-chunker
```

### 2. Create Virtual Environment (Recommended)

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Package

**For users:**
```bash
pip install -e .
```

**For developers:**
```bash
pip install -e ".[dev]"
```

Or using Make:
```bash
make install-dev
```

## Verify Installation

### 1. Check Package Installation

```bash
pip show markitdown-chunker
```

### 2. Check CLI

```bash
markitdown-chunker --version
markitdown-chunker --list-formats
```

### 3. Test in Python

```python
from markitdown_chunker import MarkitDownProcessor

processor = MarkitDownProcessor()
print("✓ Installation successful!")
```

## Run Tests

```bash
# Run all tests
pytest

# With coverage
pytest --cov=markitdown_chunker --cov-report=html

# Or using Make
make test
make test-cov
```

## Dependencies

### Core Dependencies

- **markitdown** (>=0.0.1): Document conversion
- **langchain** (>=0.1.0): Text processing
- **langchain-text-splitters** (>=0.0.1): Text splitting utilities

### Development Dependencies

- pytest: Testing framework
- black: Code formatter
- flake8: Linter
- mypy: Type checker
- pytest-cov: Coverage reporting

## System Requirements

- **Python**: 3.8 or higher
- **OS**: Linux, macOS, Windows
- **Memory**: 512MB minimum (more for large documents)
- **Disk**: 50MB for package + space for output files

## Troubleshooting

### Issue: ImportError for markitdown

```bash
pip install markitdown --upgrade
```

### Issue: ImportError for langchain

```bash
pip install langchain langchain-text-splitters --upgrade
```

### Issue: CLI command not found

Make sure your Python scripts directory is in PATH:

**macOS/Linux:**
```bash
export PATH="$PATH:$HOME/.local/bin"
```

**Windows:**
Add `%USERPROFILE%\AppData\Local\Programs\Python\Python3X\Scripts` to PATH

### Issue: Permission errors

Use `--user` flag:
```bash
pip install --user markitdown-chunker
```

## Uninstallation

```bash
pip uninstall markitdown-chunker
```

## Upgrading

```bash
pip install --upgrade markitdown-chunker
```

## Building from Source

### Create Distribution

```bash
# Install build tools
pip install build twine

# Build package
python -m build

# Or using Make
make build
```

This creates:
- `dist/markitdown_chunker-0.1.0-py3-none-any.whl` (wheel)
- `dist/markitdown-chunker-0.1.0.tar.gz` (source)

### Install from Distribution

```bash
pip install dist/markitdown_chunker-0.1.0-py3-none-any.whl
```

## Publishing to PyPI

**First time:**
1. Create account at https://pypi.org
2. Create API token
3. Configure `~/.pypirc`

**Publish:**
```bash
# Test PyPI (recommended first)
make upload-test

# Production PyPI
make upload
```

## Docker (Optional)

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY markitdown_chunker/ ./markitdown_chunker/
COPY setup.py .

RUN pip install -e .

ENTRYPOINT ["markitdown-chunker"]
```

Build and run:

```bash
docker build -t markitdown-chunker .
docker run -v $(pwd)/data:/data markitdown-chunker /data/input.pdf /data/output/
```

## Development Setup

For contributing to the project:

```bash
# Clone and setup
git clone https://github.com/yourusername/markitdown-chunker.git
cd markitdown-chunker

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks (optional)
pip install pre-commit
pre-commit install

# Verify setup
make test
make lint
```

## Need Help?

- 📖 [Quick Start Guide](QUICKSTART.md)
- 📚 [Full Documentation](README.md)
- 🐛 [Report Issues](https://github.com/yourusername/markitdown-chunker/issues)
- 💬 [Discussions](https://github.com/yourusername/markitdown-chunker/discussions)

---

For questions about installation, please open an issue on GitHub.

