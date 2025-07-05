# Temporal Python Project

A Python project following coding standards and best practices.

## Development Setup

### Prerequisites
- Python 3.8 or higher
- Poetry (for dependency management)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/kanzihuang/temporal-python.git
   cd temporal-python
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   # source .venv/bin/activate  # On macOS/Linux
   ```

3. Install dependencies:
   ```bash
   poetry install
   ```

4. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Coding Standards

This project follows PEP 8 style guide and uses the following tools to ensure code quality:
- **black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Static type checking

### Running Checks

To run all checks manually:
```bash
pre-commit run --all-files
```

To run tests:
```bash
pytest
```