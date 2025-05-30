# Contributing to Vibe CLI

Thank you for your interest in contributing to Vibe CLI! This document provides guidelines and instructions for contributing to both the Python and TypeScript implementations of the CLI.

## Project Structure

The Vibe CLI project is structured with shared code between two package implementations:

```
vibe-cli/
├── shared/               # Shared code and assets used by both packages
│   ├── commands.yaml     # Command definitions
│   └── vibe_alias.sh     # Shell alias script
├── python-package/       # Python (pip) package
│   ├── vibe/             # Python module
│   ├── tests/            # Python tests
│   └── pyproject.toml    # Python project config
├── node-package/         # Node.js (npm) package
│   ├── src/              # TypeScript source files
│   ├── dist/             # Compiled JavaScript (generated)
│   ├── tests/            # TypeScript tests
│   └── package.json      # Node.js project config
└── README.md             # Project documentation
```

## Development Environment

### Prerequisites

- **Python**: Python 3.7+ with Poetry (for Python package)
- **Node.js**: Node.js 12+ with npm (for TypeScript package)
- **Git**: For version control

### Setting Up for Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/vibe-cli.git
   cd vibe-cli
   ```

2. **For Python package development**:
   ```bash
   cd python-package
   poetry install
   ```

3. **For TypeScript package development**:
   ```bash
   cd node-package
   npm install
   npm run build
   ```

## Development Workflow

### Shared Components

When modifying shared components (like `commands.yaml`), ensure your changes are compatible with both implementations.

#### Command Definitions

Commands are defined in `shared/commands.yaml` with the following structure:

```yaml
tool_name:
  command_name:
    command: "shell command {placeholder}"
    description: "Human-readable description"
    telemetry_event: "event_name_for_tracking"
    # Optional fields
    handler: "module.function_name"  # For complex commands
    package_manager_sensitive: true  # For npm/yarn/pnpm detection
    aliases: ["alias1", "alias2"]    # Command aliases
```

### Python Package Development

#### Running the Python CLI in Development

```bash
cd python-package
poetry run python -m vibe.main [arguments]
```

#### Testing the Python Package

```bash
cd python-package
poetry run pytest
```

#### Building the Python Package

```bash
cd python-package
poetry build
```

This creates both wheel and source distributions in the `dist/` directory.

#### Publishing to PyPI

```bash
cd python-package
poetry publish
```

### TypeScript Package Development

#### Running the TypeScript CLI in Development

```bash
cd node-package
npm run build  # Compile TypeScript to JavaScript
node dist/main.js [arguments]
```

For development with auto-recompilation:
```bash
npm run dev  # Watches for changes and recompiles
```

#### Testing the TypeScript Package

```bash
cd node-package
npm test
```

#### Building the TypeScript Package

```bash
cd node-package
npm run build
```

This compiles TypeScript files to JavaScript in the `dist/` directory.

#### Publishing to npm

```bash
cd node-package
npm publish
```

## Adding New Commands

To add a new command to the Vibe CLI:

1. **Identify the appropriate tool category** in `shared/commands.yaml`
2. **Add a new entry** to the tool's command dictionary:
   
   ```yaml
   git:
     # Existing commands...
     
     # New command
     my-new-command:
       command: "git some-command {arg}"
       description: "Description of my new command"
       telemetry_event: "git_my_new_command_executed"
   ```

3. **For complex commands requiring custom logic**:
   - Python: Add a handler function in the appropriate module
   - TypeScript: Add a handler function in the appropriate file
   
4. **Add tests** for your new command
5. **Update documentation** to include the new command

## Adding a New Tool Category

To add support for a new tool (e.g., Docker):

1. **Add a new section** to `shared/commands.yaml`:
   ```yaml
   docker:
     ps:
       command: "docker ps"
       description: "List running containers"
       telemetry_event: "docker_ps_executed"
     
     # Other docker commands...
   ```

2. **For complex commands**, add handler functions as needed
3. **Add tests** for the new commands
4. **Update documentation** to include the new tool category

## Code Style

### Python Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
- Use [Black](https://github.com/psf/black) for code formatting
- Add type hints to function signatures
- Add docstrings to all functions and classes

### TypeScript Code Style

- Follow the [TypeScript Style Guide](https://github.com/basarat/typescript-book/blob/master/docs/styleguide/styleguide.md)
- Use ESLint for code linting
- Add proper type annotations
- Document functions and interfaces

## Pull Request Process

1. **Fork the repository** to your GitHub account
2. **Create a feature branch** for your changes
3. **Make your changes** following the code style guidelines
4. **Add tests** for your changes
5. **Ensure all tests pass** in both Python and TypeScript implementations
6. **Update documentation** if needed
7. **Submit a pull request** with a clear description of the changes

## Release Process

### Python Package Release

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create a tagged release in Git
4. Build and publish to PyPI

### TypeScript Package Release

1. Update version in `package.json`
2. Update CHANGELOG.md
3. Create a tagged release in Git
4. Build and publish to npm

## License

By contributing to this project, you agree that your contributions will be licensed under the project's [MIT License](../vibe-cli/LICENSE).

## Questions?

If you have any questions or need further clarification, please open an issue on GitHub or reach out to the maintainers.
