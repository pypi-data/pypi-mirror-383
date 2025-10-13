# Contributing to Scrava

Thank you for your interest in contributing to Scrava! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect differing viewpoints and experiences

## How to Contribute

### Reporting Bugs

1. **Check existing issues** first to avoid duplicates
2. **Provide detailed information:**
   - Scrava version
   - Python version
   - Operating system
   - Minimal reproducible example
   - Expected vs actual behavior
   - Error messages and tracebacks

### Suggesting Features

1. **Check existing issues and discussions**
2. **Describe the feature:**
   - Use case and motivation
   - Proposed API/interface
   - Alternative solutions considered
   - Implementation ideas (optional)

### Contributing Code

1. **Fork the repository**
2. **Create a branch:**
   ```bash
   git checkout -b feature/my-feature
   # or
   git checkout -b fix/my-bugfix
   ```

3. **Make your changes:**
   - Follow code style guidelines
   - Add/update tests
   - Update documentation
   - Add type hints

4. **Run tests:**
   ```bash
   pytest tests/
   ```

5. **Commit your changes:**
   ```bash
   git commit -m "feat: add amazing feature"
   # or
   git commit -m "fix: resolve issue with X"
   ```

   Use conventional commit messages:
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `style:` - Code style changes (formatting, etc.)
   - `refactor:` - Code refactoring
   - `test:` - Test additions or changes
   - `chore:` - Maintenance tasks

6. **Push and create Pull Request:**
   ```bash
   git push origin feature/my-feature
   ```

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/scrava.git
   cd scrava
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in development mode:**
   ```bash
   pip install -e ".[all]"
   pip install pytest black mypy ruff
   ```

4. **Run tests:**
   ```bash
   pytest tests/
   ```

## Code Style

### Python Style

- Follow **PEP 8**
- Use **type hints** for all functions
- Maximum line length: **100 characters**
- Use **async/await** for async code
- Prefer **composition over inheritance**

### Formatting

Use Black for formatting:
```bash
black scrava/
```

### Type Checking

Use mypy for type checking:
```bash
mypy scrava/
```

### Linting

Use ruff for linting:
```bash
ruff check scrava/
```

## Documentation

- **Docstrings:** Use Google style docstrings
- **Type hints:** Add type hints to all public APIs
- **Examples:** Include usage examples
- **README:** Update README.md for new features
- **API Docs:** Update docs/API.md for API changes

### Docstring Example

```python
async def fetch(self, request: Request) -> Response:
    """
    Execute an HTTP request and return a response.
    
    Args:
        request: The Request object to execute
        
    Returns:
        A Response object containing the fetched data
        
    Raises:
        HTTPError: If the request fails
        
    Example:
        ```python
        request = Request('https://example.com')
        response = await fetcher.fetch(request)
        ```
    """
    pass
```

## Testing

### Writing Tests

- Place tests in `tests/` directory
- Use descriptive test names
- Test edge cases and error conditions
- Use fixtures for common setup
- Mock external dependencies

### Test Example

```python
import pytest
from scrava import Request, Response

@pytest.mark.asyncio
async def test_request_creation():
    request = Request('https://example.com')
    assert request.url == 'https://example.com'
    assert request.method == 'GET'

@pytest.mark.asyncio
async def test_response_selector():
    html = '<html><h1>Title</h1></html>'
    response = Response(
        url='https://example.com',
        status=200,
        headers={},
        body=html.encode(),
        request=Request('https://example.com')
    )
    
    title = response.selector.css('h1::text').get()
    assert title == 'Title'
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_request.py

# Run with coverage
pytest --cov=scrava tests/

# Run with verbose output
pytest -v
```

## Adding New Features

### New Queue Backend

1. Inherit from `BaseQueue`
2. Implement all abstract methods
3. Add to `scrava/queue/`
4. Export in `scrava/queue/__init__.py`
5. Add tests in `tests/queue/`
6. Update documentation

### New Fetcher

1. Inherit from `BaseFetcher`
2. Implement `fetch()` method
3. Add to `scrava/fetchers/`
4. Export in `scrava/fetchers/__init__.py`
5. Add tests in `tests/fetchers/`
6. Update documentation

### New Hook

1. Inherit from `RequestHook` or `BotHook`
2. Implement hook methods
3. Add to `scrava/hooks/`
4. Export in `scrava/hooks/__init__.py`
5. Add tests and examples
6. Update documentation

### New Pipeline

1. Inherit from `BasePipeline`
2. Implement `process_rec()` method
3. Add to `scrava/pipelines/`
4. Export in `scrava/pipelines/__init__.py`
5. Add tests and examples
6. Update documentation

## Project Structure

```
scrava/
├── scrava/                 # Main package
│   ├── __init__.py
│   ├── bot.py             # Bot base class
│   ├── utils.py           # Utilities
│   ├── logging.py         # Logging setup
│   ├── http/              # Request/Response
│   ├── core/              # Core orchestrator
│   ├── queue/             # Queue implementations
│   ├── fetchers/          # Fetcher implementations
│   ├── hooks/             # Hook system
│   ├── pipelines/         # Pipeline implementations
│   ├── config/            # Configuration system
│   └── cli/               # CLI commands
├── tests/                 # Test suite
├── examples/              # Example bots
├── docs/                  # Documentation
├── setup.py              # Package setup
├── requirements.txt      # Dependencies
└── README.md            # Main documentation
```

## Release Process

1. Update version in `scrava/__init__.py`
2. Update CHANGELOG.md
3. Create git tag: `git tag v0.1.0`
4. Push tag: `git push origin v0.1.0`
5. GitHub Actions will build and publish to PyPI

## Getting Help

- **Documentation:** Read the docs at docs/
- **Examples:** Check examples/ directory
- **Issues:** Search existing issues
- **Discussions:** Start a GitHub discussion
- **Discord:** Join our Discord server (link)

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

Thank you for contributing to Scrava! 🎉



