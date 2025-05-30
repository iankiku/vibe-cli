.PHONY: all clean build test link-node install-node install-python dev-node dev-python uninstall

# Default target
all: build

# Clean both packages
clean:
	@echo "🧹 Cleaning build artifacts..."
	cd node-package && npm run clean
	cd python-package && rm -rf dist/ build/ *.egg-info/

# Build both packages
build: build-node build-python

# Build Node.js package
build-node:
	@echo "🔨 Building and linking Node.js package..."
	cd node-package && npm run build
	@echo "🔗 Linking Node.js package for local development..."
	cd node-package && npm link

# Build Python package
build-python:
	@echo "🔨 Building and installing Python package (editable)..."
	cd python-package && poetry build
	cd python-package && poetry install

# Run tests for both packages
test: test-node test-python

# Test Node.js package
test-node:
	@echo "🧪 Testing Node.js package..."
	cd node-package && npm test

# Test Python package
test-python:
	@echo "🧪 Testing Python package..."
	cd python-package && poetry run pytest

# Create a symlink for the Node.js package for local development
link-node:
	@echo "🔗 Linking Node.js package for local development..."
	cd node-package && npm link

# Install the Node.js package globally
install-node: build-node
	@echo "📦 Installing Node.js package globally..."
	cd node-package && npm install -g

# Install the Python package in development mode
install-python: build-python
	@echo "📦 Installing Python package using Poetry (editable)..."
	cd python-package && poetry install

# Run Node.js package in development mode
dev-node:
	@echo "🚀 Running Node.js package in development mode..."
	cd node-package && npm run dev

# Run Python package in development mode
dev-python:
	@echo "🚀 Running Python package in development mode..."
	cd python-package && poetry run python -m vibe.main

# Complete uninstallation of Vibe CLI
uninstall:
	@echo "🗑️ Uninstalling Vibe CLI completely..."
	@echo "Removing Node.js package..."
	npm uninstall -g vibe-cli || true
	@echo "Removing Python package..."
	pip uninstall -y vibe-cli || true
	@echo "Removing shell aliases..."
	@grep -v "VibeCLI aliases" ~/.bashrc > ~/.bashrc.tmp || true
	@grep -v "source.*vibe_alias.sh" ~/.bashrc.tmp > ~/.bashrc.new || true
	@mv ~/.bashrc.new ~/.bashrc || true
	@grep -v "VibeCLI aliases" ~/.zshrc > ~/.zshrc.tmp || true
	@grep -v "source.*vibe_alias.sh" ~/.zshrc.tmp > ~/.zshrc.new || true
	@mv ~/.zshrc.new ~/.zshrc || true
	@echo "✅ Vibe CLI has been completely removed!"

# Helper message
help:
	@echo "🪄 Vibe CLI Development Commands"
	@echo "-------------------------------"
	@echo "make build        - Build both packages"
	@echo "make test         - Run tests for both packages"
	@echo "make clean        - Clean build artifacts"
	@echo "make link-node    - Create a symlink for Node.js package (for testing)"
	@echo "make install-node - Install Node.js package globally"
	@echo "make install-python - Install Python package in development mode"
	@echo "make dev-node     - Run Node.js package in development mode"
	@echo "make dev-python   - Run Python package in development mode"
	@echo "make uninstall    - Completely remove Vibe CLI (packages and shell aliases)"
