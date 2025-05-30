#!/usr/bin/env bash
# VibeCLI alias loader
# This script creates a 'vibe' shell function that forwards commands to the installed CLI

vibe() {
  local command_path
  
  # Determine which vibe executable to use (npm or pip)
  if command -v vibe-node > /dev/null 2>&1; then
    command_path=$(which vibe-node)
  elif command -v vibe-py > /dev/null 2>&1; then
    command_path=$(which vibe-py)
  else
    echo "Error: VibeCLI not found. Please install via 'npm install -g vibe-cli' or 'pip install vibe-cli'"
    return 1
  fi
  
  # Execute the command
  "$command_path" "$@"
}

# Export the function so it's available in subshells
export -f vibe

echo "VibeCLI aliases loaded. Use 'vibe' to access commands."
