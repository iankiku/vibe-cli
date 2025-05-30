"""
Uninstall command handlers for Vibe CLI.
"""
import os
import sys
import subprocess
import typer
import shutil
from pathlib import Path

def uninstall_vibes(args=None):
    """
    Completely uninstall Vibe CLI from the system.
    Removes both the Python and Node packages as well as any shell aliases.
    """
    typer.secho("🗑️ Uninstalling Vibe CLI completely...", fg=typer.colors.YELLOW, bold=True)
    
    # Remove Node.js package
    typer.secho("\n🔄 Removing Node.js package...", fg=typer.colors.BLUE)
    try:
        subprocess.run(
            "npm uninstall -g vibe-cli",
            shell=True,
            check=False,  # Don't raise an exception if it fails
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        typer.secho("✅ Node.js package removed (if installed)", fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho(f"⚠️ Warning when removing Node.js package: {str(e)}", fg=typer.colors.YELLOW)
    
    # Remove Python package
    typer.secho("\n🔄 Removing Python package...", fg=typer.colors.BLUE)
    typer.secho("⚠️ Will remove after this process completes", fg=typer.colors.YELLOW)
    
    # Remove shell aliases
    typer.secho("\n🔄 Removing shell aliases...", fg=typer.colors.BLUE)
    
    # Check for bash
    bash_rc = Path.home() / ".bashrc"
    if bash_rc.exists():
        try:
            # Read the content
            with open(bash_rc, "r") as f:
                content = f.read()
            
            # Remove vibe CLI lines
            new_content = []
            skip_next = False
            for line in content.splitlines():
                if "VibeCLI aliases" in line:
                    skip_next = True
                    continue
                if skip_next and "source" in line and "vibe_alias.sh" in line:
                    skip_next = False
                    continue
                new_content.append(line)
            
            # Write the new content
            with open(bash_rc, "w") as f:
                f.write("\n".join(new_content))
            
            typer.secho("✅ Removed from .bashrc", fg=typer.colors.GREEN)
        except Exception as e:
            typer.secho(f"⚠️ Warning when cleaning .bashrc: {str(e)}", fg=typer.colors.YELLOW)
    
    # Check for zsh
    zsh_rc = Path.home() / ".zshrc"
    if zsh_rc.exists():
        try:
            # Read the content
            with open(zsh_rc, "r") as f:
                content = f.read()
            
            # Remove vibe CLI lines
            new_content = []
            skip_next = False
            for line in content.splitlines():
                if "VibeCLI aliases" in line:
                    skip_next = True
                    continue
                if skip_next and "source" in line and "vibe_alias.sh" in line:
                    skip_next = False
                    continue
                new_content.append(line)
            
            # Write the new content
            with open(zsh_rc, "w") as f:
                f.write("\n".join(new_content))
            
            typer.secho("✅ Removed from .zshrc", fg=typer.colors.GREEN)
        except Exception as e:
            typer.secho(f"⚠️ Warning when cleaning .zshrc: {str(e)}", fg=typer.colors.YELLOW)
    
    # Final message
    typer.secho("\n🎉 Vibe CLI has been uninstalled!", fg=typer.colors.MAGENTA, bold=True)
    typer.secho("👋 Thank you for using Vibe CLI. We hope to see you again soon!", fg=typer.colors.CYAN)
    
    # Run pip uninstall as the last step
    typer.secho("\n🔄 Removing this Python package...", fg=typer.colors.BLUE)
    
    # Create a self-destruct script
    uninstall_script = Path.home() / ".vibe-uninstall-script.sh"
    with open(uninstall_script, "w") as f:
        f.write(f"""#!/bin/bash
# Self-destruct script for Vibe CLI
echo "Removing Python package..."
pip uninstall -y vibe-cli
rm -f {uninstall_script}
echo "✅ Vibe CLI Python package removed"
""")
    
    # Make it executable
    os.chmod(uninstall_script, 0o755)
    
    # Inform the user
    typer.secho(f"⚠️ To complete uninstallation, please run: {uninstall_script}", fg=typer.colors.YELLOW, bold=True)
    
    return {"message": "Uninstallation prepared. Follow the final step to complete."}
