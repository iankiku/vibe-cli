"""
Git command mappings for Vibe CLI

This module provides natural language mappings for Git commands.
All commands are prefixed with 'vibe' when used in the terminal.
Example: 'vibe status' instead of 'git status'
"""

import shlex
import os

# Git command mappings
COMMANDS = {
    # Repository status & information
    "status": ["git", "status"],
    "changes": ["git", "diff"],
    "staged changes": ["git", "diff", "--staged"],
    "history": ["git", "log", "--oneline", "-n", "10"],
    "log": ["git", "log", "--oneline", "-n", "10"],
    "full log": ["git", "log"],
    "recent commits": ["git", "log", "--oneline", "-n", "5"],
    "show remotes": ["git", "remote", "-v"],
    "remote": ["git", "remote", "-v"],
    "show": lambda ref: ["git", "show", ref],
    
    # Adding & committing changes
    "add everything": ["git", "add", "."],
    "add all": ["git", "add", "."],
    "stage all": ["git", "add", "."],
    "add": lambda args: ["git", "add"] + shlex.split(args),
    "stage": lambda args: ["git", "add"] + shlex.split(args),
    "commit": lambda msg: ["git", "commit", "-m", msg],
    "save": lambda msg: ["git", "commit", "-m", msg],
    "amend": ["git", "commit", "--amend"],
    "amend commit": ["git", "commit", "--amend"],
    
    # Syncing changes
    "push": ["git", "push"],
    "upload": ["git", "push"],
    "push all": ["git", "push", "--all"],
    "push tags": ["git", "push", "--tags"],
    "force push": ["git", "push", "--force"],
    "pull": ["git", "pull"],
    "update": ["git", "pull"],
    "download": ["git", "pull"],
    "fetch": ["git", "fetch"],
    "sync": ["git", "pull", "&&", "git", "push"],
    
    # Repository initialization
    "init": ["git", "init"],
    "start repo": ["git", "init"],
    "create repo": ["git", "init"],
    "clone": lambda url: ["git", "clone", url],
    "get repo": lambda url: ["git", "clone", url],
    "download repo": lambda url: ["git", "clone", url],
    
    # Branch operations
    "branches": ["git", "branch"],
    "show branches": ["git", "branch"],
    "all branches": ["git", "branch", "-a"],
    "list branches": ["git", "branch"],
    "create branch": lambda name: ["git", "checkout", "-b", name],
    "new branch": lambda name: ["git", "checkout", "-b", name],
    "branch": lambda name: ["git", "checkout", "-b", name] if name else ["git", "branch"],
    "switch": lambda branch: ["git", "checkout", branch],
    "checkout": lambda branch: ["git", "checkout", branch],
    "go to": lambda branch: ["git", "checkout", branch],
    "switch to": lambda branch: ["git", "checkout", branch],
    "rename branch": lambda args: ["git", "branch", "-m"] + shlex.split(args),
    "delete branch": lambda name: ["git", "branch", "-d", name],
    "remove branch": lambda name: ["git", "branch", "-d", name],
    
    # Merging & rebasing
    "merge": lambda branch: ["git", "merge", branch],
    "combine": lambda branch: ["git", "merge", branch],
    "rebase": lambda branch: ["git", "rebase", branch],
    "rebase onto": lambda branch: ["git", "rebase", branch],
    "continue rebase": ["git", "rebase", "--continue"],
    "abort rebase": ["git", "rebase", "--abort"],
    
    # Stashing
    "stash": ["git", "stash"],
    "save changes": ["git", "stash"],
    "stash save": ["git", "stash"],
    "stash list": ["git", "stash", "list"],
    "show stash": ["git", "stash", "list"],
    "stash changes": ["git", "stash"],
    "pop stash": ["git", "stash", "pop"],
    "apply stash": ["git", "stash", "apply"],
    "get stashed changes": ["git", "stash", "pop"],
    "drop stash": ["git", "stash", "drop"],
    "clear stash": ["git", "stash", "clear"],
    
    # Remote operations
    "add remote": lambda args: ["git", "remote", "add"] + shlex.split(args),
    "remove remote": lambda name: ["git", "remote", "remove", name],
    "update remote": lambda args: ["git", "remote", "set-url"] + shlex.split(args),
    
    # Undoing changes
    "reset": lambda file: ["git", "reset", file] if file else ["git", "reset"],
    "unstage": lambda file: ["git", "reset", file] if file else ["git", "reset"],
    "undo commit": ["git", "reset", "HEAD~1"],
    "undo last commit": ["git", "reset", "HEAD~1"],
    "undo": ["git", "reset", "HEAD~1"],
    "revert": lambda commit: ["git", "revert", commit],
    "revert commit": lambda commit: ["git", "revert", commit],
    "discard": ["git", "checkout", "--", "."],
    "discard changes": ["git", "checkout", "--", "."],
    "clean": ["git", "clean", "-fd"],
    "remove untracked": ["git", "clean", "-fd"],
    
    # Tags
    "tag": lambda args: ["git", "tag"] + (shlex.split(args) if args else []),
    "create tag": lambda tag: ["git", "tag", tag],
    "delete tag": lambda tag: ["git", "tag", "-d", tag],
    "list tags": ["git", "tag"],
    "show tags": ["git", "tag"],
    
    # Advanced operations
    "blame": lambda file: ["git", "blame", file],
    "who changed": lambda file: ["git", "blame", file],
    "bisect start": ["git", "bisect", "start"],
    "bisect good": ["git", "bisect", "good"],
    "bisect bad": ["git", "bisect", "bad"],
    "bisect reset": ["git", "bisect", "reset"],
    "check ignore": lambda file: ["git", "check-ignore", "-v", file],
    "is ignored": lambda file: ["git", "check-ignore", "-v", file],
    "gc": ["git", "gc"],
    "cleanup": ["git", "gc"],
    "compress": ["git", "gc"],
}
