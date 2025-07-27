# Design Principles

## Core Philosophy
- **No Order Modification**: Never modify orders. Only validate and raise errors.
- **Pure Validation**: Check orders for POST_ONLY compliance but never alter them.
- **Fail Fast**: If an order doesn't meet POST_ONLY requirements, raise an exception immediately.

## POST_ONLY Enforcement Rules
1. **Only EXCHANGE LIMIT orders are allowed** - All other order types are rejected
2. **POST_ONLY flag (4096) must be present** - Orders without this flag are rejected  
3. **Validate but never modify** - Don't add flags, don't change parameters
4. **Raise exceptions for violations** - Use PostOnlyError for any non-compliant orders

## Implementation Guidelines
- Keep codebase lean and minimal
- Use simple validation wrapper approach
- Avoid complex decorator patterns or "contribution theater"
- Focus on the core requirement: enforce POST_ONLY behavior through validation

## Development Environment
- Python 3.13+ required
- Use virtual environment: `source venv/bin/activate`
- Run tests locally before committing: `pytest tests/`
- Unified linting with ruff (replaces black, isort, flake8)
- Type checking with mypy 1.17.0+
- Pre-commit hooks automatically run ruff and mypy checks