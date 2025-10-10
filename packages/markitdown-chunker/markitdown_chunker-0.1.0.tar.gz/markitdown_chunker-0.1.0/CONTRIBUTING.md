# Contributing to MarkitDown Chunker

Thank you for your interest in contributing to MarkitDown Chunker! This document provides guidelines and instructions for contributing.

## Getting Started

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/markitdown-chunker.git
   cd markitdown-chunker
   ```

2. **Set up development environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

3. **Create a new branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Code Style

We use several tools to maintain code quality:

- **Black** for code formatting
- **Flake8** for linting
- **MyPy** for type checking
- **isort** for import sorting

Run all checks before committing:

```bash
# Format code
black markitdown_chunker/ tests/ examples/

# Sort imports
isort markitdown_chunker/ tests/ examples/

# Lint code
flake8 markitdown_chunker/ tests/ examples/

# Type check
mypy markitdown_chunker/
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=markitdown_chunker --cov-report=html

# Run specific test file
pytest tests/test_converter.py

# Run specific test
pytest tests/test_converter.py::TestMarkdownConverter::test_initialization
```

### Adding New Features

1. **Write tests first** (TDD approach recommended)
2. **Implement the feature**
3. **Update documentation**
4. **Add examples if applicable**
5. **Run all tests and checks**
6. **Submit a pull request**

## Project Structure

```
markitdown-chunker/
├── markitdown_chunker/       # Main package
│   ├── __init__.py           # Package initialization
│   ├── converter.py          # Document to markdown conversion
│   ├── chunker.py            # Text chunking logic
│   ├── exporter.py           # JSON export functionality
│   ├── processor.py          # Main orchestrator
│   └── cli.py                # Command-line interface
├── tests/                    # Test suite
│   ├── test_converter.py
│   ├── test_chunker.py
│   └── ...
├── examples/                 # Usage examples
├── docs/                     # Documentation (if applicable)
└── setup.py                  # Package setup
```

## Pull Request Guidelines

### Before Submitting

- [ ] Code follows the project's style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] CHANGELOG.md updated (if applicable)
- [ ] No linter errors or warnings

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe the tests you ran

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Code formatted with black
- [ ] No linting errors
```

## Coding Standards

### Python Style

- Follow PEP 8
- Use type hints where possible
- Write docstrings for all public functions and classes
- Keep functions focused and small
- Use descriptive variable names

### Documentation

- Use Google-style docstrings
- Include examples in docstrings for complex functions
- Keep README.md up to date
- Add comments for complex logic

### Example Docstring

```python
def chunk_file(
    self, 
    markdown_path: str,
    include_images: bool = False
) -> List[Dict[str, Any]]:
    """
    Chunk a markdown file.
    
    Args:
        markdown_path: Path to the markdown file
        include_images: Whether to process images
        
    Returns:
        List of chunk dictionaries with text and metadata
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        
    Example:
        >>> chunker = DocumentChunker()
        >>> chunks = chunker.chunk_file("document.md")
        >>> print(len(chunks))
        10
    """
```

## Reporting Issues

### Bug Reports

Include:
- Python version
- Package version
- Operating system
- Steps to reproduce
- Expected behavior
- Actual behavior
- Error messages/stack traces

### Feature Requests

Include:
- Use case description
- Proposed API/interface
- Example usage
- Alternative solutions considered

## Community Guidelines

- Be respectful and inclusive
- Help others learn
- Accept constructive criticism
- Focus on what's best for the project

## Questions?

- Open an issue for general questions
- Tag maintainers for urgent matters
- Check existing issues before posting

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to MarkitDown Chunker! 🎉

