# Contributing to aiofiles-x

Thank you for your interest in contributing to **aiofiles-x**! We welcome contributions from the community.

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **C++23 compatible compiler** (GCC 12+, Clang 15+, or MSVC 19.30+)
- **CMake 3.20+**
- **Git**

### Development Setup

#### Quick Setup (Recommended)

1. **Fork and Clone**

   ```bash
   git clone https://github.com/YOUR_USERNAME/aiofiles-x.git
   cd aiofiles-x
   ```

1. **Automated Setup**

   ```bash
   # Linux/macOS
   ./scripts/setup-dev.sh

   # Windows
   scripts\setup-dev.bat
   ```

This will automatically:

- Create virtual environment
- Install dependencies
- Install pre-commit hooks
- Run initial checks

#### Manual Setup

1. **Create Virtual Environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

1. **Install Dependencies**

   ```bash
   pip install -e ".[dev]"
   ```

1. **Install Pre-commit Hooks**

   ```bash
   pre-commit install
   pre-commit install --hook-type commit-msg
   ```

1. **Build the C++ Extension**

   ```bash
   mkdir build && cd build
   cmake .. -DBUILD_TESTS=ON -DBUILD_BENCHMARKS=ON
   cmake --build . -j$(nproc)
   cd ..
   ```

## 📝 Contribution Guidelines

### Code Style

**Python:**

- Follow [PEP 8](https://pep8.org/)
- Use Black for formatting: `black src/python tests examples`
- Use Ruff for linting: `ruff check src/python tests examples`
- Type hints where appropriate

**C++:**

- Follow modern C++23 best practices
- Use meaningful variable names
- Keep functions focused and concise
- Add comments for complex logic

### Commit Messages

- Use clear, descriptive commit messages
- Start with a verb in imperative mood (e.g., "Add", "Fix", "Update")
- Reference issues when applicable: `Fix #123: Description`

Example:

```text
Add async truncate operation for file handles

- Implement truncate() method in AsyncFile class
- Add Python bindings for truncate
- Include unit tests for truncate functionality
- Update documentation

Fixes #42
```

### Pull Request Process

#### Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

#### Make Your Changes

- Write clean, well-documented code
- Add tests for new functionality
- Ensure all tests pass
- Update documentation as needed

#### Test Your Changes

   ```bash
   # Run unit tests
   pytest tests/unit -v

   # Run benchmarks (optional)
   pytest tests/benchmarks --benchmark-only

   # Type checking
   mypy src/python

   # Linting
   ruff check src/python tests examples
   black --check src/python tests examples
   ```

#### Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:

- Clear description of changes
- Reference to related issues
- Screenshots/benchmarks if applicable

## 🧪 Testing

### Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/unit/test_basic.py -v

# With coverage
pytest tests/ --cov=aiofiles --cov-report=html

# Benchmarks only
pytest tests/benchmarks --benchmark-only
```

### Writing Tests

- Place unit tests in `tests/unit/`
- Place integration tests in `tests/integration/`
- Place benchmarks in `tests/benchmarks/`
- Use descriptive test names: `test_<functionality>_<scenario>`
- Include docstrings explaining what the test verifies

Example:

```python
@pytest.mark.asyncio
async def test_read_returns_file_contents():
    """Test that read() returns the complete file contents."""
    # Test implementation
```

## 📚 Documentation

- Update relevant documentation for new features
- Add docstrings to all public functions/classes
- Include usage examples when appropriate
- Update README.md if adding major features

## 🐛 Bug Reports

When reporting bugs, please include:

- **Description**: Clear description of the bug
- **Steps to Reproduce**: Minimal code to reproduce the issue
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened
- **Environment**: OS, Python version, compiler version
- **Logs**: Any relevant error messages or logs

## 💡 Feature Requests

When proposing features:

- **Use Case**: Explain the problem you're trying to solve
- **Proposed Solution**: Describe your proposed implementation
- **Alternatives**: Any alternative solutions you've considered
- **API Design**: Proposed API if applicable
- **Performance Impact**: Expected performance implications

## 🔍 Code Review

All contributions go through code review. Reviewers will check for:

- **Correctness**: Does the code work as intended?
- **Tests**: Are there adequate tests?
- **Performance**: Any performance regressions?
- **Style**: Does it follow project conventions?
- **Documentation**: Is it well-documented?

## 📜 License

This project follows all licenses and terms from its original dependencies.

**Add license header to new files:**

```cpp
// Aiofiles-X
// Copyright (C) 2025 ohmyarthur
//
// Please read the GNU Affero General Public License in
// <https://github.com/ohmyarthur/aiofiles-x/blob/master/LICENSE/>.
```

## 🙏 Thank You

Thank you for contributing to aiofiles-x! Your efforts help make async file I/O faster and better for everyone.

---

If you have questions, feel free to:

- Open a [GitHub Discussion](https://github.com/ohmyarthur/aiofiles-x/discussions)
- Create an [Issue](https://github.com/ohmyarthur/aiofiles-x/issues)
- Contact the maintainers
