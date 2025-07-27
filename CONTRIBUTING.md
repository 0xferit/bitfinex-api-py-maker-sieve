# Contributing to Bitfinex API Python POST-ONLY Wrapper

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

### Prerequisites

- Python 3.12 or higher
- Git
- A Bitfinex account with API access (for testing)

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/bitfinex-api-py-postonly-wrapper.git
   cd bitfinex-api-py-postonly-wrapper
   ```

2. **Set up development environment**
   ```bash
   python scripts/dev.py setup
   ```

3. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your API credentials (for testing)
   ```

4. **Verify installation**
   ```bash
   python scripts/dev.py test
   ```

## 🛠️ Development Workflow

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code following the project conventions
   - Add tests for new functionality
   - Update documentation as needed

3. **Run quality checks**
   ```bash
   python scripts/dev.py check
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add: your descriptive commit message"
   ```

### Code Style

We use several tools to maintain code quality:

- **Black** for code formatting
- **isort** for import sorting  
- **flake8** for linting
- **mypy** for type checking

Run all checks with:
```bash
python scripts/dev.py check
```

### Testing

- Write tests for all new functionality
- Ensure existing tests still pass
- Aim for high test coverage

```bash
# Run tests
python scripts/dev.py test

# Run tests with coverage
python scripts/dev.py test-cov
```

### Documentation

- Update README.md for user-facing changes
- Add docstrings to new functions and classes
- Update examples if relevant
- Keep documentation clear and concise

## 📋 Pull Request Process

1. **Ensure your branch is up to date**
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-feature-branch
   git rebase main
   ```

2. **Run all checks**
   ```bash
   python scripts/dev.py check
   ```

3. **Push your branch**
   ```bash
   git push origin your-feature-branch
   ```

4. **Create a Pull Request**
   - Use a descriptive title
   - Explain what changes you made and why
   - Reference any related issues
   - Include screenshots if relevant

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] All tests pass
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or properly documented)
```

## 🎯 Types of Contributions

### Bug Fixes
- Look for issues labeled `bug`
- Include reproduction steps in your PR
- Add regression tests

### New Features
- Discuss large features in an issue first
- Ensure features align with project goals
- Include comprehensive tests and documentation

### Documentation
- Fix typos and unclear explanations
- Add examples and usage guides
- Improve API documentation

### Code Quality
- Refactor complex code
- Improve test coverage
- Optimize performance

## 🔧 Project Structure

```
bitfinex-api-py-postonly-wrapper/
├── bfx_postonly/          # Main package
│   ├── client.py         # Main client wrapper
│   ├── decorators.py     # Decorator implementations
│   ├── exceptions.py     # Custom exceptions
│   └── utils.py         # Utility functions
├── examples/             # Usage examples
├── tests/               # Test suite
├── scripts/             # Development scripts
└── docs/               # Documentation
```

### Adding New Modules

1. Create the module in the appropriate directory
2. Add proper docstrings and type hints
3. Import and export in `__init__.py`
4. Add comprehensive tests
5. Update documentation

## 🔒 Security Considerations

- Never commit API keys or secrets
- Use environment variables for sensitive data
- Report security issues privately
- Follow secure coding practices

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Environment information**
   - Python version
   - Library version
   - Operating system

2. **Reproduction steps**
   - Minimal code example
   - Expected behavior
   - Actual behavior

3. **Additional context**
   - Error messages
   - Stack traces
   - Relevant logs

## 💡 Feature Requests

For feature requests:

1. Check if the feature already exists
2. Search existing issues and discussions
3. Clearly describe the use case
4. Explain why it would be valuable
5. Consider implementation complexity

## 📞 Getting Help

- **Issues**: For bugs and feature requests
- **Discussions**: For questions and general discussion
- **Email**: For security issues (privately)

## 🏆 Recognition

Contributors are recognized in:
- README.md contributors section
- Release notes for significant contributions
- Special thanks in documentation

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Thank You!

Every contribution helps make this project better. Whether you're fixing typos, reporting bugs, or adding features, your help is appreciated!
