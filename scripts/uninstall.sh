#!/bin/bash
#
# Vibe CLI Uninstaller
# A simple bash script to uninstall Vibe CLI from macOS and Linux
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
INSTALL_DIR="$HOME/.vibe-tools"
FORCE_UNINSTALL=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --force)
      FORCE_UNINSTALL=true
      shift
      ;;
    *)
      echo -e "${RED}Unknown option: $1${NC}"
      exit 1
      ;;
  esac
done

# Print header
echo -e "\n${BOLD} 🚀 Vibe CLI Uninstaller${NC}\n"

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

# Function to confirm with user
confirm() {
  if [[ "$FORCE_UNINSTALL" == "true" ]]; then
    return 0
  fi
  
  read -p "$1 (y/N): " response
  if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    return 0
  else
    return 1
  fi
}

# Function to remove installation directory
remove_install_dir() {
  echo -e "${BLUE}==>${NC} ${BOLD}Removing installation directory${NC}"
  
  if [[ ! -d "$INSTALL_DIR" ]]; then
    echo -e "${YELLOW}!${NC} Directory not found: $INSTALL_DIR"
    return 0
  fi
  
  rm -rf "$INSTALL_DIR"
  echo -e "${GREEN}✓${NC} Removed directory: $INSTALL_DIR"
  return 0
}

# Function to update shell configuration
update_shell_config() {
  echo -e "${BLUE}==>${NC} ${BOLD}Updating shell configuration${NC}"
  
  if [[ ! -f "$CONFIG_FILE" ]]; then
    echo -e "${YELLOW}!${NC} Config file not found: $CONFIG_FILE"
    return 0
  fi
  
  # Check if vibe config exists
  if ! grep -q "vibe-tools\|vibe CLI" "$CONFIG_FILE"; then
    echo -e "${YELLOW}!${NC} No Vibe CLI configuration found in: $CONFIG_FILE"
    return 0
  fi
  
  # Create a temporary file
  TMP_FILE=$(mktemp)
  
  # Remove Vibe CLI related lines
  grep -v "vibe-tools\|vibe CLI\|alias vibe=" "$CONFIG_FILE" > "$TMP_FILE"
  
  # Replace the original file
  mv "$TMP_FILE" "$CONFIG_FILE"
  
  echo -e "${GREEN}✓${NC} Updated shell config: $CONFIG_FILE"
  return 0
}

# Function to print post-uninstallation instructions
print_instructions() {
  echo -e "\n${GREEN}${BOLD}🎉 Vibe CLI uninstallation complete!${NC}\n"
  echo "To finalize the uninstallation, you need to:"
  echo -e "\n1. Reload your shell configuration:"
  echo -e "   source $CONFIG_FILE"
  echo -e "\nThanks for trying Vibe CLI! If you had any issues, please let us know on GitHub."
  echo -e "\n${BOLD}Goodbye! 👋${NC}\n"
}

# Main uninstallation process
main() {
  # Confirm uninstallation
  if ! confirm "Are you sure you want to uninstall Vibe CLI?"; then
    echo -e "${YELLOW}!${NC} Uninstallation cancelled."
    exit 1
  fi
  
  detect_shell
  
  remove_install_dir
  
  update_shell_config
  
  print_instructions
}

# Run the uninstallation
main
