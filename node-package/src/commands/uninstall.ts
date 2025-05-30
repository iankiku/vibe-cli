/**
 * Uninstall command handlers for Vibe CLI.
 */
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';
import { execSync } from 'child_process';
import chalk from 'chalk';

/**
 * Completely uninstall Vibe CLI from the system.
 * Removes both the Python and Node packages as well as any shell aliases.
 */
export function uninstallVibes(args: string[] = []): any {
  console.log(chalk.yellow.bold('🗑️ Uninstalling Vibe CLI completely...'));
  
  // Remove Python package
  console.log(chalk.blue('\n🔄 Removing Python package...'));
  try {
    execSync('pip uninstall -y vibe-cli', { stdio: 'pipe' });
    console.log(chalk.green('✅ Python package removed (if installed)'));
  } catch (e) {
    console.log(chalk.yellow(`⚠️ Warning when removing Python package: ${e}`));
  }
  
  // Remove shell configuration
  console.log(chalk.blue('\n🔄 Removing shell configuration...'));

  const homeDir = os.homedir();
  let shell = '';
  try {
    shell = path.basename(process.env.SHELL || '');
  } catch (e) {
    // Ignore error, will default later
  }
  if (shell !== 'zsh' && shell !== 'bash') {
    try {
      const userInfo = os.userInfo(); // Attempt to get default shell for the user on Linux/macOS
      if (userInfo.shell) {
        shell = path.basename(userInfo.shell);
      }
    } catch (e) {
      // Fallback if os.userInfo() fails or no shell
    }
  }
  // If still not determined or not zsh/bash, default to bash
  if (shell !== 'zsh' && shell !== 'bash') {
    shell = 'bash'; 
  }

  const rcFile = shell === 'zsh'
    ? path.join(homeDir, '.zshrc')
    : path.join(homeDir, '.bashrc');

  const brandingComment1 = "#===================================";
  const brandingComment2 = "# vibe-cli by www.vibcloud.dev ©️2025";
  const brandingComment3 = "# https://www.vibecloud.dev/cli";
  const brandingComment4 = "#===================================";
  const oldAliasMarkerComment = "# VibeCLI aliases";
  const anyVibeAliasSourcePattern = /source .*\/(vibe_alias\.sh|vibe_cli\.sh)/g;

  if (fs.existsSync(rcFile)) {
    try {
      const rcFileContent = fs.readFileSync(rcFile, 'utf-8');
      let lines = rcFileContent.split('\n');

      const vibeCliBrandingPattern = /^# vibe-cli by .*vibcloud\.dev.*$/i;
      const vibeCliUrlPattern = /^# .*vibecloud\.dev\/cli.*$/i;

      lines = lines.filter(line => {
        const trimmedLine = line.trim();
        return (
          trimmedLine !== brandingComment1 && // Keep exact match for #===================================
          trimmedLine !== brandingComment4 && // Keep exact match for #===================================
          !vibeCliBrandingPattern.test(trimmedLine) &&
          !vibeCliUrlPattern.test(trimmedLine) &&
          trimmedLine !== oldAliasMarkerComment &&
          !anyVibeAliasSourcePattern.test(trimmedLine)
        );
      });

      // Remove consecutive blank lines that might be left after cleanup
      let cleanedLines: string[] = [];
      if (lines.length > 0) {
        cleanedLines.push(lines[0]); // Add first line unconditionally
        for (let i = 1; i < lines.length; i++) {
          // Add line if it's not a blank line following another blank line
          if (lines[i].trim() !== '' || lines[i-1].trim() !== '') {
            cleanedLines.push(lines[i]);
          }
        }
      }
      lines = cleanedLines;
      
      // Ensure the file doesn't end with multiple blank lines, but has one if content exists
      while (lines.length > 0 && lines[lines.length - 1].trim() === '') {
        lines.pop();
      }
      if (lines.length > 0) {
          lines.push(''); // Add a single blank line at the end for POSIX conformity
      }

      fs.writeFileSync(rcFile, lines.join('\n'));
      console.log(chalk.green(`✅ Cleaned Vibe CLI configuration from ${rcFile}`));
    } catch (e) {
      console.log(chalk.yellow(`⚠️ Warning when cleaning ${rcFile}: ${e}`));
    }
  } else {
    console.log(chalk.yellow(`ℹ️ Shell configuration file ${rcFile} not found. Skipping cleanup.`));
  }

  // Remove the alias script and directory
  console.log(chalk.blue('\n🔄 Removing Vibe CLI script files...'));
  const targetAliasScriptPath = path.join(homeDir, '.vibecloud', 'cli', 'vibe_cli.sh');
  const targetCliDir = path.join(homeDir, '.vibecloud', 'cli');
  const targetVibeCloudDir = path.join(homeDir, '.vibecloud');

  try {
    if (fs.existsSync(targetAliasScriptPath)) {
      fs.unlinkSync(targetAliasScriptPath);
      console.log(chalk.green(`✅ Removed script: ${targetAliasScriptPath}`));
    } else {
      // console.log(chalk.yellow(`ℹ️ Script not found: ${targetAliasScriptPath}. Skipping.`));
    }

    if (fs.existsSync(targetCliDir)) {
      const filesInCliDir = fs.readdirSync(targetCliDir);
      if (filesInCliDir.length === 0) {
        fs.rmdirSync(targetCliDir);
        console.log(chalk.green(`✅ Removed directory: ${targetCliDir}`));
        
        if (fs.existsSync(targetVibeCloudDir)) {
            const filesInVibeCloudDir = fs.readdirSync(targetVibeCloudDir);
            if (filesInVibeCloudDir.length === 0) {
                fs.rmdirSync(targetVibeCloudDir);
                console.log(chalk.green(`✅ Removed directory: ${targetVibeCloudDir}`));
            } else {
                // console.log(chalk.yellow(`ℹ️ Directory ${targetVibeCloudDir} is not empty. Skipping removal.`));
            }
        }
      } else {
        // console.log(chalk.yellow(`ℹ️ Directory ${targetCliDir} is not empty. Skipping removal.`));
      }
    } else {
      // console.log(chalk.yellow(`ℹ️ Directory not found: ${targetCliDir}. Skipping.`));
    }
  } catch (e) {
    console.log(chalk.yellow(`⚠️ Warning when removing script files/directories: ${e}`));
  }
  
  // Final message
  console.log(chalk.magenta.bold('\n🎉 Vibe CLI has been uninstalled!'));
  console.log(chalk.cyan('👋 Thank you for using Vibe CLI. We hope to see you again soon!'));
  
  // Note about npm uninstall
  console.log(chalk.blue('\n🔄 This package will be removed when you run:'));
  console.log(chalk.yellow.bold('npm uninstall -g vibe-cli'));
  
  return {
    type: 'handler',
    success: true,
    result: 'Vibe CLI has been uninstalled!'
  };
}
