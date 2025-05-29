#!/bin/bash
#
# Vibe CLI Installer
# A simple bash script to install Vibe CLI on macOS and Linux
#

set -e

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Script variables
REPO_URL="https://github.com/yourusername/vibe-cli"
INSTALL_DIR="$HOME/.vibe-tools/cli/bin"
TEMP_DIR=$(mktemp -d)
FORCE_INSTALL=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --force)
      FORCE_INSTALL=true
      shift
      ;;
    *)
      echo -e "${RED}Unknown option: $1${NC}"
      exit 1
      ;;
  esac
done

# Print header
echo -e "\n${BOLD}🚀 Vibe CLI Installer${NC}\n"

# Function to detect shell and config file
detect_shell() {
  echo -e "${BLUE}==>${NC} ${BOLD}Detecting shell${NC}"
  
  if [[ -n "$ZSH_VERSION" ]]; then
    SHELL_NAME="zsh"
    CONFIG_FILE="$HOME/.zshrc"
  elif [[ -n "$BASH_VERSION" ]]; then
    SHELL_NAME="bash"
    if [[ "$OSTYPE" == "darwin"* ]]; then
      if [[ -f "$HOME/.bash_profile" ]]; then
        CONFIG_FILE="$HOME/.bash_profile"
      else
        CONFIG_FILE="$HOME/.bashrc"
      fi
    else
      CONFIG_FILE="$HOME/.bashrc"
    fi
  else
    SHELL_NAME="unknown"
    CONFIG_FILE="$HOME/.bashrc"
  fi
  
  echo -e "${GREEN}✓${NC} Detected shell: $SHELL_NAME"
  echo -e "${GREEN}✓${NC} Config file: $CONFIG_FILE"
}

# Function to create installation directory
create_install_dir() {
  echo -e "${BLUE}==>${NC} ${BOLD}Creating installation directory${NC}"
  
  if [[ -d "$INSTALL_DIR" ]] && [[ "$FORCE_INSTALL" != "true" ]]; then
    echo -e "${YELLOW}!${NC} Directory already exists: $INSTALL_DIR"
    echo -e "${YELLOW}!${NC} Use --force to reinstall"
    return 1
  fi
  
  mkdir -p "$INSTALL_DIR"
  echo -e "${GREEN}✓${NC} Created directory: $INSTALL_DIR"
  return 0
}

# Function to download and install Vibe CLI
download_and_install() {
  echo -e "${BLUE}==>${NC} ${BOLD}Downloading Vibe CLI${NC}"
  
  # For now, we'll copy from the local repository
  # In the future, this would download from GitHub releases
  
  # Get the script directory
  SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
  PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
  
  echo -e "${GREEN}✓${NC} Using local repository: $PROJECT_DIR"
  
  # Copy the CLI files
  cp -R "$PROJECT_DIR/cli" "$HOME/.vibe-tools/"
  
  # Make the binary executable
  chmod +x "$INSTALL_DIR/vibe"
  
  echo -e "${GREEN}✓${NC} Installed Vibe CLI to: $INSTALL_DIR"
  return 0
}

# Function to update shell configuration
update_shell_config() {
  echo -e "${BLUE}==>${NC} ${BOLD}Updating shell configuration${NC}"
  
  if grep -q "vibe-tools" "$CONFIG_FILE" && [[ "$FORCE_INSTALL" != "true" ]]; then
    echo -e "${YELLOW}!${NC} Vibe CLI is already configured in: $CONFIG_FILE"
    echo -e "${YELLOW}!${NC} Use --force to update"
    return 1
  fi
  
  echo -e "\n# Vibe CLI configuration - Added by installer" >> "$CONFIG_FILE"
  echo -e "export PATH=\"\$PATH:$INSTALL_DIR\"" >> "$CONFIG_FILE"
  echo -e "alias vibe='python \"$INSTALL_DIR/vibe\"'\n" >> "$CONFIG_FILE"
  
  echo -e "${GREEN}✓${NC} Updated shell config: $CONFIG_FILE"
  return 0
}

# Function to print post-installation instructions
print_instructions() {
  echo -e "\n${GREEN}${BOLD}🎉 Vibe CLI installation complete!${NC}\n"
  echo "To start using Vibe CLI, you need to:"
  echo -e "\n1. Reload your shell configuration:"
  echo -e "   source $CONFIG_FILE"
  echo -e "\n2. Try using a Vibe CLI command:"
  echo -e "   vibe status"
  echo -e "   vibe help"
  echo -e "\nFor more information:"
  echo -e "   vibe help"
  echo -e "\n${BOLD}Enjoy using Vibe CLI! 🚀${NC}\n"
}

# Main installation process
main() {
  detect_shell
  
  create_install_dir || true
  
  download_and_install || true
  
  update_shell_config || true
  
  print_instructions
}

# Run the installation
main
