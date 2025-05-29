# tests/test_cli.py
import pytest
from unittest.mock import patch, MagicMock
import subprocess

from vibe import cli

# Tests for find_command_key function
def test_find_command_key_success():
    # Test that it finds a known command
    key = cli.find_command_key("check status")
    assert key == "check status"

def test_find_command_key_partial_match():
    # Test that it matches the start of input
    key = cli.find_command_key("commit with message hello world")
    assert key == "commit with message"

def test_find_command_key_no_match():
    # Test that it returns None for unknown commands
    key = cli.find_command_key("nonexistent command")
    assert key is None

# Tests for process_command function
def test_process_command_empty():
    # Test empty command
    result = cli.process_command("")
    assert result['success'] is False
    assert "No command provided" in result['error_message']
    assert result['exit_code'] == 1

def test_process_command_unknown():
    # Test unknown command
    result = cli.process_command("unknown command")
    assert result['success'] is False
    assert "No matching vibe found" in result['error_message']
    assert result['command_found'] is False

def test_process_command_git_status():
    # Test 'check status' command (git status)
    result = cli.process_command("check status")
    assert result['success'] is True
    assert result['command_found'] is True
    assert result['exit_code'] == 0
    assert "Running" in result['display_message'] and "git status" in result['display_message']
    assert result['shell_cmd'] == ['git', 'status']
    assert result['use_shell'] is False

def test_process_command_with_args():
    # Test command with arguments
    result = cli.process_command("commit with message test commit")
    assert result['success'] is True
    assert result['command_found'] is True
    assert "Running: git commit -m" in result['display_message']
    assert isinstance(result['shell_cmd'], list)
    assert result['shell_cmd'][0:3] == ['git', 'commit', '-m']
    # The 4th item would be the quoted message

def test_process_command_shell_true():
    # Test command that requires shell=True
    result = cli.process_command("freeze requirements")
    assert result['success'] is True
    assert result['use_shell'] is True
    assert "Running (shell): pip freeze > requirements.txt" in result['display_message']

# Tests for execute_command function
@patch('vibe.cli.subprocess.run')
def test_execute_command_success(mock_subprocess_run):
    # Test successful command execution
    mock_subprocess_run.return_value = MagicMock(returncode=0)
    result = cli.execute_command(['git', 'status'], False)
    assert result['success'] is True
    assert result['exit_code'] == 0
    mock_subprocess_run.assert_called_once_with(['git', 'status'], shell=False, check=True)

@patch('vibe.cli.subprocess.run')
def test_execute_command_process_error(mock_subprocess_run):
    # Test CalledProcessError handling
    mock_subprocess_run.side_effect = subprocess.CalledProcessError(2, 'test cmd')
    result = cli.execute_command(['git', 'status'], False)
    assert result['success'] is False
    assert result['exit_code'] == 2
    assert "Error executing command" in result['error_message']

@patch('vibe.cli.subprocess.run')
def test_execute_command_file_not_found(mock_subprocess_run):
    # Test FileNotFoundError handling
    mock_subprocess_run.side_effect = FileNotFoundError()
    result = cli.execute_command(['nonexistent', 'cmd'], False)
    assert result['success'] is False
    assert result['exit_code'] == 1
    assert "Command not found" in result['error_message']
