# Vibe CLI (Node.js Package)

A natural language wrapper for git, npm, and python commands that allows developers to use simple English phrases to execute common development tasks.

## Installation

```bash
npm install -g vibe-cli
```

## Usage

### Basic Commands

```bash
# Using natural language
vibe check status
vibe add everything
vibe commit with message "fixed a bug"

# Traditional commands
vibe git status
vibe npm install
vibe python run app.py
```

### Configuration

The CLI supports environment variables for configuration:
- `VIBE_LOG_LEVEL`: Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `VIBE_LOG_TO_FILE`: Enable file logging (true/false)

## Features

- Natural language command recognition
- Support for git, npm, pip and other development tools
- Comprehensive logging system
- Command aliases for common operations

## Development

### Setup

```bash
cd node-package
npm install
```

### Testing

```bash
npm test
```

### Running Locally

```bash
npm run build
node dist/main.js
```

## License

GNU Affero General Public License v3.0 (AGPL-3.0)
