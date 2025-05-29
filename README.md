# vibe-cli

🚀 Vibe: speak plain English, run dev commands.

Natural-language CLI for git, npm, python, and more! Simply type what you want to do in plain English, and vibe will translate it into the appropriate command.

## Installation

**Prerequisites:**
- Python 3.7+

**Steps:**

1. Clone this repository (if you haven't already):
   ```bash
   # If you have access to the repository
   # git clone <repository_url>
   # cd vibe-cli
   ```

2. Install the package locally (preferably in a virtual environment):
   ```bash
   pip install -e .
   ```
   The `-e` flag installs the package in editable mode, so changes to the source code will be immediately available.

## Usage

Once installed, you can use `vibe` from your terminal:

```bash
vibe your natural language command
```

**Examples:**

**Git:**
- `vibe start a new git repo`
- `vibe add everything`
- `vibe check status`
- `vibe commit with message Fix the main bug`
- `vibe push changes`
- `vibe pull latest changes`

**npm:**
- `vibe create a node project`
- `vibe add express`
- `vibe remove lodash`
- `vibe run build`
- `vibe check updates`

**Python:**
- `vibe run app.py`
- `vibe make env`
- `vibe activate env` (Handles OS-specific activation)
- `vibe install requests`
- `vibe freeze requirements`

## Supported Commands

**Git:**
- `start a new git repo`: Initializes a new Git repository (`git init`).
- `add everything`: Stages all changes (`git add .`).
- `check status`: Shows the working tree status (`git status`).
- `commit with message <message>`: Commits staged changes with a message (`git commit -m "<message>"`).
- `push changes`: Pushes commits to the remote repository (`git push`).
- `pull latest changes`: Fetches from and integrates with another repository or a local branch (`git pull`).

**npm:**
- `create a node project`: Initializes a new Node.js project (`npm init -y`).
- `add <package>`: Installs an npm package (`npm install <package>`).
- `remove <package>`: Uninstalls an npm package (`npm uninstall <package>`).
- `run <script>`: Runs an npm script defined in `package.json` (`npm run <script>`).
- `check updates`: Checks for outdated npm packages (`npm outdated`).

**Python:**
- `run <script.py>`: Executes a Python script (`python <script.py>`).
- `make env`: Creates a Python virtual environment named `venv` (`python -m venv venv`).
- `activate env`: Activates the `venv` virtual environment (OS-dependent command).
- `install <package>`: Installs a Python package using pip (`pip install <package>`).
- `freeze requirements`: Saves installed packages to `requirements.txt` (`pip freeze > requirements.txt`).

## Configuration

Vibe CLI uses a configuration file (`vibe.config.json`) that is automatically generated during installation. This file stores system information, package manager versions, MCP server configurations, and user preferences.

### Configuration File Location

The configuration file is stored at:
- macOS/Linux: `~/.vibe-cli/vibe.config.json`
- Windows: `%USERPROFILE%\.vibe-cli\vibe.config.json`

### Configuration Commands

Vibe CLI provides several commands to manage your configuration:

```bash
# View your entire configuration
vibe config show

# Get a specific configuration value
vibe config get system.python

# Set a configuration value
vibe config set preferences.theme=dark

# List configured MCP servers
vibe config mcp list

# Add a new MCP server
vibe config mcp add myserver npx -y server-package

# View a specific MCP server configuration
vibe config mcp show myserver

# Remove an MCP server
vibe config mcp remove myserver
```

### Configuration Structure

The configuration file has the following structure:

```json
{
  "version": "1.0.0",
  "created_at": "2025-05-26T10:46:34-05:00",
  "system": {
    "python": {
      "major": 3,
      "minor": 9,
      "full": "3.9.5"
    },
    "os": {
      "system": "Darwin",
      "release": "21.6.0"
    },
    "shell": "zsh"
  },
  "package_managers": {
    "npm": "8.19.3",
    "yarn": "1.22.19",
    "pnpm": null
  },
  "mcpServers": {
    "firecrawl": {
      "command": "npx",
      "args": ["-y", "firecrawl-mcp"],
      "env": {
        "FIRECRAWL_API_KEY": "abc-123-defghi"
      }
    }
  },
  "preferences": {
    "editor": "vscode",
    "theme": "dark"
  }
}
```

## Shell Auto-completion

`vibe` supports shell auto-completion for commands and arguments. To enable it:

1.  **Install completion script:**
    Find out which shell you are using (e.g., bash, zsh, fish, powershell).
    Then run the appropriate command:
    ```bash
    vibe --install-completion bash
    # or
    vibe --install-completion zsh
    # or
    vibe --install-completion fish
    # or
    vibe --install-completion powershell
    ```

2.  **Reload your shell:**
    You might need to restart your shell or source your shell's configuration file (e.g., `~/.bashrc`, `~/.zshrc`) for the changes to take effect.

    For example, for bash:
    ```bash
    source ~/.bashrc
    ```
    For zsh:
    ```bash
    source ~/.zshrc
    ```

Now, you should be able to use the `<Tab>` key to auto-complete `vibe` commands.

## Contributing

### Development Setup

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd vibe-cli
   ```

2. Install the package in development mode:
   ```bash
   pip install -e .
   ```

3. Install development dependencies:
   ```bash
   pip install pytest
   ```

### Testing

Due to a known issue with Typer and pytest interaction, use the following approach for testing:

```bash
# Set PYTHONPATH to include the project root and run tests
PYTHONPATH=/path/to/vibe-cli python -m pytest -vv tests/
```

For example, if you cloned to `/Users/username/vibe-cli`:

```bash
PYTHONPATH=/Users/username/vibe-cli python -m pytest -vv tests/
```

### Publishing to PyPI

## Installation

Vibe CLI can be installed in multiple ways, depending on your platform and preferences:

### Quick Install (All Platforms)

The easiest way to install is using our Python installer script:

```bash
# Clone the repository
git clone https://github.com/yourusername/vibe-cli.git
cd vibe-cli

# Run the installer
python scripts/install.py
```

### Platform-Specific Installation

#### macOS

**Using Homebrew:**
```bash
brew tap yourusername/vibe
brew install vibe-cli
```

**Using the Shell Script:**
```bash
curl -fsSL https://raw.githubusercontent.com/yourusername/vibe-cli/main/scripts/install.sh | bash
```

#### Linux

**Using the Shell Script:**
```bash
curl -fsSL https://raw.githubusercontent.com/yourusername/vibe-cli/main/scripts/install.sh | bash
```

**Using Python:**
```bash
pip install vibe-cli
```

#### Windows

**Using Scoop:**
```powershell
scoop bucket add vibe https://github.com/yourusername/vibe-cli.git
scoop install vibe-cli
```

**Using Python:**
```powershell
pip install vibe-cli
```

### Manual Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/vibe-cli.git
   ```

2. Install dependencies:
   ```bash
   cd vibe-cli
   pip install -e .
   ```

3. Add the bin directory to your PATH:
   ```bash
   # For bash/zsh
   echo 'export PATH="$PATH:$HOME/.vibe-tools/cli/bin"' >> ~/.bashrc
   # or
   echo 'export PATH="$PATH:$HOME/.vibe-tools/cli/bin"' >> ~/.zshrc
   ```

### Uninstallation

To uninstall Vibe CLI from your system:

```bash
# Using the Python uninstaller
python scripts/uninstall.py

# Or force uninstallation without prompts
python scripts/uninstall.py --force
```

**Using Shell Script (macOS/Linux):**
```bash
# Using the shell uninstaller
bash scripts/uninstall.sh

# Or force uninstallation without prompts
bash scripts/uninstall.sh --force
```

This will:
- Remove the Vibe CLI installation directory
- Remove Vibe CLI references from your shell configuration file
- Provide instructions for reloading your shell configuration

### For Developers

When ready to publish:

1. Update version in `pyproject.toml`

2. Build the package:
   ```bash
   pip install build
   python -m build
   ```

3. Upload to TestPyPI (for testing):
   ```bash
   pip install twine
   twine upload --repository-url https://test.pypi.org/legacy/ dist/*
   ```

4. Upload to PyPI (for production):
   ```bash
   twine upload dist/*
   ```

## License

MIT License

## Roadmap

Future enhancements planned for vibe:

- **LLM Integration**: Connect to language models to handle arbitrary commands beyond predefined mappings
- **Web GUI/Chat Interface**: Add a web-based interface for using vibe via browser
- **Additional Translators**: Support for Docker, Vercel, Terraform, and other tools
- **Interactive Mode**: Conversation-like CLI with history and suggestions
