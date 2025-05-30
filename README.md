# Vibe CLI

A natural language wrapper for development commands that makes common tasks simpler and more intuitive. Vibe CLI provides a unified interface for git, npm/yarn/pnpm, and Python operations.

## Features

- **Simple, memorable commands** - `vibe status` instead of `git status`
- **Dual-package distribution** - Install via npm or pip, your choice
- **Automatic shell integration** - Shell aliases are automatically installed
- **Consistent experience** - Same commands regardless of installation method
- **Cross-platform** - Works on macOS, Linux, and Windows (via WSL/Git Bash)

## Installation

### Via npm

```bash
npm install -g vibe-cli
install-alias  # Adds the vibe shell function to your .bashrc or .zshrc
```

### Via pip

```bash
pip install vibe-cli
install-alias  # Adds the vibe shell function to your .bashrc or .zshrc
```

## Usage

Once installed, you can use the `vibe` command directly in your terminal:

```bash
# Git commands
vibe status           # Check git status
vibe commit "Message" # Commit changes with a message
vibe push             # Push changes to remote

# NPM commands
vibe install lodash   # Install a package
vibe run start        # Run a script from package.json

# Python commands
vibe env              # Create a virtual environment
vibe install requests # Install a package via pip
```

## Command Reference

For a complete list of commands, run:

```bash
vibe help             # General help
vibe git help         # Git-specific commands
vibe npm help         # NPM-specific commands
vibe python help      # Python-specific commands
```

## Project Structure

The Vibe CLI project is structured to support both npm and pip packages:

```
vibe-cli/
├── shared/               # Shared code and assets used by both packages
│   ├── commands.yaml     # Command definitions
│   ├── utils.ts          # Shared utility functions (TypeScript version)
│   └── vibe_alias.sh     # Shell alias script
├── python-package/       # Python (pip) package
│   ├── vibe/             # Python module
│   │   ├── __init__.py
│   │   └── main.py       # Main Python entry point
│   └── pyproject.toml    # Python project config
├── node-package/         # Node.js (npm) package
│   ├── src/              # TypeScript source files
│   │   ├── main.ts       # Main TypeScript entry point
│   │   └── utils/        # TypeScript utilities
│   ├── dist/             # Compiled JavaScript output
│   ├── tests/            # Test files
│   ├── jest.config.ts    # Jest configuration
│   ├── tsconfig.json     # TypeScript configuration
│   └── package.json      # Node.js project config
├── .github/              # GitHub specific files
│   ├── workflows/        # GitHub Actions workflows
│   └── release-template.md # Release template
└── README.md             # Project documentation
```

## Development

### Architecture

The core principle of this project is to share command definitions and shell integration between both package implementations. Here's how it works:

1. Commands are defined in a single YAML file (`shared/commands.yaml`)
2. Each package implementation reads this file and handles command dispatch
3. The shell alias script (`vibe_alias.sh`) is identical for both packages
4. When installing either package, the alias script is added to the user's shell

This approach ensures a consistent user experience regardless of the installation method while minimizing code duplication.

### Using the Makefile

A Makefile is provided to simplify common development tasks:

```bash
# Build both packages
make build

# Run tests for both packages
make test

# Clean build artifacts
make clean

# Link Node.js package for local testing
make link-node

# Install packages for development
make install-node
make install-python

# Run in development mode
make dev-node
make dev-python

# See all available commands
make help
```

### Uninstalling

To completely remove Vibe CLI from your system:

```bash
# Using the CLI itself
vibe uninstall

# Or using the Makefile
make uninstall
```

### Building and Publishing

#### Python Package

```bash
cd python-package
poetry build
poetry publish
```

#### Node.js Package

```bash
cd node-package
npm publish
```

## License

MIT
