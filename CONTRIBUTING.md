# Contributing to vibe-cli

Thank you for your interest in contributing to vibe-cli! This document provides guidelines and instructions for contributing to the project.

## Development Environment Setup

1. **Clone the repository**:
   ```bash
   git clone <repository_url>
   cd vibe-cli
   ```

2. **Install in development mode**:
   ```bash
   pip install -e .
   ```

3. **Install development dependencies**:
   ```bash
   pip install pytest
   ```

## Code Structure

- `vibe/cli.py`: Main CLI entry point and core logic
- `vibe/translators/`: Modules that define command mappings
  - `git.py`: Git command mappings
  - `npm.py`: npm command mappings
  - `python.py`: Python command mappings
- `tests/`: Test files

## Testing

### Known Testing Issue

We've identified an issue with pytest and Typer interaction that causes tests to exit with code 130 (SIGINT) when using Typer's CliRunner for testing.

### Testing Workaround

To run tests successfully:

```bash
# Run tests with PYTHONPATH set to the project root
PYTHONPATH=/path/to/vibe-cli python -m pytest -vv tests/
```

Our test suite is designed to test the core logic directly, avoiding Typer's CliRunner.

## Adding New Commands

To add support for a new command:

1. Identify the appropriate translator file in `vibe/translators/`
2. Add a new entry to the `commands` dictionary:
   
   ```python
   # For a simple command
   'natural language key': 'actual shell command',
   
   # For a command with arguments
   'command with arg': lambda args: ['command', 'subcommand', shlex.quote(args)],
   ```

3. Add tests for the new command in `tests/test_cli.py`
4. Update documentation in README.md to include the new command

## Adding a New Tool Translator

To add support for a new tool (e.g., Docker):

1. Create a new file `vibe/translators/docker.py` with a `commands` dictionary
2. Import and include the new commands dictionary in `vibe/cli.py`:
   ```python
   from .translators import git, npm, python, docker
   ALL_COMMANDS = {**git.commands, **npm.commands, **python.commands, **docker.commands}
   ```
3. Add appropriate tests
4. Update documentation

## Code Style

- Follow PEP 8 guidelines
- Use descriptive variable names
- Add docstrings to functions
- Keep functions small and focused

## Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for your changes
5. Ensure all tests pass
6. Update documentation if needed
7. Submit a pull request

## Security Considerations

When adding new commands:

- Always use `shlex.quote()` for sanitizing user input in command arguments
- Prefer `shell=False` when using `subprocess.run()` with a list of arguments
- Only use `shell=True` when shell features like redirections are required

Thank you for contributing to vibe-cli!
