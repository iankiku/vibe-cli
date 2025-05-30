#!/usr/bin/env node
/**
 * Vibe CLI - Main entry point for Node.js package
 */
import * as fs from 'fs';
import * as path from 'path';
import * as yaml from 'js-yaml';
import { Command } from 'commander';
import { uninstallVibes } from './commands/uninstall';
import { execSync } from 'child_process';
import * as os from 'os';
import chalk from 'chalk';

// Import the logger
import { getLogger, info, error, debug, warning } from './utils/logger';

// Get a logger instance for this module
const logger = getLogger('cli');

// Define types for command configuration
interface CommandConfig {
  command?: string;
  description?: string;
  handler?: string;
  telemetry_event?: string;
  package_manager_sensitive?: boolean;
  aliases?: string[];
}

interface ToolCommands {
  [commandName: string]: CommandConfig;
}

interface AllCommands {
  [toolName: string]: ToolCommands;
}

interface CommandResult {
  type: string;
  success?: boolean;
  stdout?: string;
  stderr?: string;
  error?: string;
}

interface CommandInfo {
  tool: string;
  command: string;
  config: CommandConfig;
  args: string[];
}

const CLI_VERSION = '0.1.0';
const program = new Command();
program.version(CLI_VERSION);

// Get the path to the shared directory
export function getSharedDir(): string {
  // In development: Check for local shared directory (from /dist/main.js to ../shared)
  const localShared = path.resolve(__dirname, '..', '..', 'shared');
  if (fs.existsSync(localShared)) {
    logger.debug(`Found shared directory at ${localShared}`);
    return localShared;
  }

  // Check for project root shared directory (from /dist/main.js to ../../shared)
  const projectShared = path.resolve(__dirname, '..', '..', '..', 'shared');
  if (fs.existsSync(projectShared)) {
    logger.debug(`Found shared directory at ${projectShared}`);
    return projectShared;
  }

  // In installed package: Look in package directory
  const packageShared = path.resolve(__dirname, '..', 'shared');
  if (fs.existsSync(packageShared)) {
    logger.debug(`Found shared directory at ${packageShared}`);
    return packageShared;
  }

  // Check if we're in a test environment
  const isTestEnv = process.env.NODE_ENV === 'test' || process.env.JEST_WORKER_ID !== undefined;

  if (isTestEnv) {
    // Return a mock directory for tests to avoid error logs
    const mockDir = path.resolve(__dirname, '..', 'tests', 'mocks');
    // Create the directory if it doesn't exist to avoid errors
    if (!fs.existsSync(mockDir)) {
      try {
        fs.mkdirSync(mockDir, { recursive: true });
      } catch (e) {
        // Ignore errors in test environment
      }
    }
    return mockDir;
  }

  // Only log the error in non-test environments
  logger.error(`Could not find shared directory in: ${localShared}, ${projectShared}, ${packageShared}`);

  // Fallback to embedded files
  const embeddedDir = path.resolve(__dirname, '..', 'embedded');
  logger.debug(`Falling back to embedded directory: ${embeddedDir}`);
  return embeddedDir;
}

// Load command definitions from shared YAML file
export function loadCommands(): AllCommands {
  const sharedDir = getSharedDir();
  const commandsFile = path.join(sharedDir, 'commands.yaml');

  try {
    const fileContents = fs.readFileSync(commandsFile, 'utf8');
    return yaml.load(fileContents) as AllCommands || {};
  } catch (error) {
    logger.error(`Failed to load commands: ${(error as Error).message}`);
    return {};
  }
}

// Natural language command mapping interface
interface NaturalLanguageCommands {
  [toolName: string]: {
    [phrase: string]: string;
  };
}

// Load natural language command mappings
export function loadNaturalLanguageCommands(): NaturalLanguageCommands {
  const sharedDir = getSharedDir();
  const nlCommandsFile = path.join(sharedDir, 'vibe_language_commands.yaml');

  try {
    const fileContents = fs.readFileSync(nlCommandsFile, 'utf8');
    return yaml.load(fileContents) as NaturalLanguageCommands || {};
  } catch (error) {
    logger.error(`Failed to load natural language commands: ${(error as Error).message}`);
    return {};
  }
}

// Format a command template with argument values
export function formatCommand(template: string, args: string[]): string {
  let result = template;

  // Simple placeholder replacement
  if (template.includes('{')) {
    // Extract placeholder names from template
    const placeholders = template.match(/\{([^}]+)\}/g) || [];

    // Replace each placeholder with its value from args
    for (let i = 0; i < placeholders.length; i++) {
      const placeholder = placeholders[i];
      const placeholderName = placeholder.substring(1, placeholder.length - 1);

      // Replace with arg value if available
      if (i < args.length) {
        result = result.replace(placeholder, args[i]);
      }
    }
  }

  return result;
}

// Execute a shell command
export function executeShellCommand(command: string): CommandResult {
  try {
    const stdout = execSync(command, { encoding: 'utf8' });
    return {
      type: 'shell',
      success: true,
      stdout
    };
  } catch (error) {
    const err = error as { message: string; stdout?: string; stderr?: string };
    return {
      type: 'shell',
      success: false,
      error: err.message,
      stdout: err.stdout || '',
      stderr: err.stderr || ''
    };
  }
}

// Print general help
function printGeneralHelp(commands: AllCommands): void {
  console.log(chalk.bold('Vibe CLI') + ' - Natural language wrapper for development commands');
  console.log('Usage: vibe <tool> <command> [args]');
  console.log('       vibe <natural language command>');
  console.log('\nAvailable tools:');

  for (const toolName in commands) {
    console.log(`  ${toolName}`);
  }

  console.log('\nYou can use natural language commands like:');
  console.log("  'vibe check status'");
  console.log("  'vibe add everything'");
  console.log("  'vibe commit with message \"fix bug\"'");
  console.log("  'vibe pull latest'");

  console.log('\nRun \'vibe <tool> help\' for commands within a tool');
  console.log('Run \'vibe help\' to see this message');
}

// Print tool-specific help
function printToolHelp(toolName: string, toolCommands: ToolCommands): void {
  console.log(chalk.bold(`Vibe CLI - ${toolName} commands`));
  console.log(`Usage: vibe ${toolName} <command> [args]`);
  console.log('\nAvailable commands:');

  for (const cmdName in toolCommands) {
    const cmd = toolCommands[cmdName];
    console.log(`  ${cmdName.padEnd(20)} ${cmd.description || ''}`);
  }

  console.log(`\nRun 'vibe ${toolName} <command> help' for command details`);
}

// Print command-specific help
function printCommandHelp(toolName: string, commandName: string, config: CommandConfig): void {
  console.log(chalk.bold(`Vibe CLI - ${toolName} ${commandName}`));
  console.log(`Description: ${config.description || 'No description'}`);

  if (config.command) {
    console.log(`Executes: ${config.command}`);
  }
}

// Install alias command
program
  .command('install-alias')
  .description('Install Vibe CLI alias to shell configuration (.zshrc or .bashrc)')
  .action(() => {
        console.log(chalk.bold('🚀 Installing Vibe CLI alias...'));
        let step = 1;

        // Determine shell
        process.stdout.write(` ${chalk.blue(`[${step++}]`)} Determining shell environment... `);
        let shell = '';
        try {
          shell = path.basename(process.env.SHELL || '');
        } catch (e) { /* Ignore */ }
        if (shell !== 'zsh' && shell !== 'bash') {
          try {
            const userInfo = os.userInfo();
            if (userInfo.shell) shell = path.basename(userInfo.shell);
          } catch (e) { /* Ignore */ }
        }
        if (shell !== 'zsh' && shell !== 'bash') shell = 'bash';
        console.log(chalk.green('✅'));

        // Define paths
        const homeDir = os.homedir();
        const vibeCloudDir = path.join(homeDir, '.vibecloud');
        const targetCliDir = path.join(homeDir, '.vibecloud', 'cli');
        const sourceAliasScriptPath = path.join(getSharedDir(), 'vibe_cli.sh');
        const targetAliasScriptPath = path.join(targetCliDir, 'vibe_cli.sh');

        // Ensure target directory exists
        process.stdout.write(` ${chalk.blue(`[${step++}]`)} Ensuring Vibe CLI directory (${targetCliDir})... `);
        try {
          if (!fs.existsSync(vibeCloudDir)) fs.mkdirSync(vibeCloudDir, { recursive: true });
          if (!fs.existsSync(targetCliDir)) fs.mkdirSync(targetCliDir, { recursive: true });
          console.log(chalk.green('✅'));
        } catch (err) {
          console.log(chalk.red('❌'));
          logger.error(`Failed to create directory ${targetCliDir}: ${err}`);
          console.error(chalk.red(`Error: Failed to create Vibe CLI directory at ${targetCliDir}.`));
          process.exit(1);
        }

        // Copy the alias script
        process.stdout.write(` ${chalk.blue(`[${step++}]`)} Copying Vibe CLI script to ${targetAliasScriptPath}... `);
        try {
          fs.copyFileSync(sourceAliasScriptPath, targetAliasScriptPath);
          console.log(chalk.green('✅'));
        } catch (err) {
          console.log(chalk.red('❌'));
          logger.error(`Failed to copy alias script: ${err}`);
          console.error(chalk.red(`Error: Failed to copy alias script from ${sourceAliasScriptPath} to ${targetAliasScriptPath}.`));
          process.exit(1);
        }

        // Determine RC file path
        const rcFile = shell === 'zsh' ? path.join(homeDir, '.zshrc') : path.join(homeDir, '.bashrc');
        let backupFile: string | null = null;

        // Backup RC file
        process.stdout.write(` ${chalk.blue(`[${step++}]`)} Backing up shell configuration (${rcFile})... `);
        if (fs.existsSync(rcFile)) {
          try {
            backupFile = `${rcFile}.bak.${Date.now()}`;
            fs.copyFileSync(rcFile, backupFile);
            console.log(chalk.green('✅'));
          } catch (err) {
            console.log(chalk.red('❌'));
            logger.error(`Failed to backup ${rcFile}: ${err}`);
            console.error(chalk.red(`Error: Failed to backup ${rcFile} to ${backupFile}.`));
            process.exit(1);
          }
        } else {
          console.log(chalk.yellow('ℹ️ (File not found, will be created)'));
        }

        process.stdout.write(` ${chalk.blue(`[${step++}]`)} Updating shell configuration (${rcFile})... `);
        let lines: string[] = [];
        if (fs.existsSync(rcFile)) {
          const rcFileContent = fs.readFileSync(rcFile, 'utf-8');
          lines = rcFileContent.split('\n');
        } else {
          lines = [];
        }

        const brandingComment1 = "#===================================";
        const brandingComment2 = "# vibe-cli by www.vibcloud.dev 2025";
        const brandingComment3 = "# https://www.vibecloud.dev/cli";
        const brandingComment4 = "#===================================";
        const oldAliasMarkerComment = "# VibeCLI aliases";
        const anyVibeAliasSourcePattern = /source .*\/(vibe_alias\.sh|vibe_cli\.sh)/g;

        lines = lines.filter(line =>
          line.trim() !== brandingComment1 &&
          line.trim() !== brandingComment2 &&
          line.trim() !== brandingComment3 &&
          line.trim() !== brandingComment4 &&
          line.trim() !== oldAliasMarkerComment &&
          !anyVibeAliasSourcePattern.test(line)
        );

        let cleanedLines: string[] = [];
        if (lines.length > 0) {
          cleanedLines.push(lines[0]);
          for (let i = 1; i < lines.length; i++) {
            if (lines[i].trim() !== '' || lines[i - 1].trim() !== '') {
              cleanedLines.push(lines[i]);
            }
          }
        }
        lines = cleanedLines;

        while (lines.length > 0 && lines[lines.length - 1].trim() === '') lines.pop();

        if (lines.length > 0 && lines[lines.length - 1].trim() !== '') lines.push('');
        lines.push(brandingComment1);
        lines.push(brandingComment2);
        lines.push(brandingComment3);
        lines.push(brandingComment4);
        lines.push(`source ${targetAliasScriptPath}`);
        lines.push('');

        try {
          fs.writeFileSync(rcFile, lines.join('\n'));
          console.log(chalk.green('✅'));

          if (backupFile) {
            process.stdout.write(` ${chalk.blue(`[${step++}]`)} Cleaning up backup file (${backupFile})... `);
            try {
              fs.unlinkSync(backupFile);
              console.log(chalk.green('✅'));
            } catch (err) {
              console.log(chalk.red('❌'));
              logger.error(`Failed to remove backup file ${backupFile}: ${err}`);
              console.warn(chalk.yellow(`Warning: Could not remove backup file ${backupFile}. You may want to remove it manually.`));
            }
          }

          console.log(chalk.green.bold('\n Vibe CLI alias installed successfully!'));
          console.log(chalk.blue('Please restart your shell or run:'));
          console.log(chalk.yellow(`  source ${rcFile}`));
        } catch (err) {
          console.log(chalk.red('❌'));
          logger.error(`Failed to write to ${rcFile}: ${err}`);
          console.error(chalk.red(`Error: Failed to write to ${rcFile}.`));
          if (backupFile) {
            console.error(chalk.yellow(`Your original ${rcFile} is backed up at ${backupFile}. Please restore it if needed.`));
          }
          process.exit(1);
        }
      });


// Main function
function main(): void {
  // Check if the install-alias command was specified
  if (process.argv.length > 2 && process.argv[2] === 'install-alias') {
    program.parse(process.argv);
    return;
  }

  // Handle uninstall command before other parsing
  if (process.argv.length > 2 && process.argv[2] === 'uninstall') {
    uninstallVibes(process.argv.slice(3));
    return;
  }

  // Normal CLI execution
  const cliArgs = process.argv.slice(2);
  const commands = loadCommands();
  const nlCommands = loadNaturalLanguageCommands();

  if (Object.keys(commands).length === 0) {
    logger.error('Failed to load command definitions');
    console.error('Error: Failed to load command definitions');
    process.exit(1);
  }

  // Handle special cases
  if (cliArgs.length === 0 || cliArgs[0] === 'help' || cliArgs[0] === '--help') {
    printGeneralHelp(commands);
    return;
  }

  if (cliArgs[0] === '--version' || cliArgs[0] === '-v') {
    console.log(CLI_VERSION);
    return;
  }

  // Check for natural language command
  /*
  if (cliArgs.length >= 1) {
    const phrase = cliArgs.join(' ');
    const nlResult = checkNaturalLanguageCommand(phrase, commands, nlCommands);

    if (nlResult.matched && nlResult.toolName && nlResult.commandName && nlResult.config) {
      // Execute the mapped command
      if (nlResult.config.handler) {
        logger.info(`Executing handler: ${nlResult.config.handler}`);
        console.log(`Handler execution: ${nlResult.config.handler}`);
        console.log(`\n✨ Executed: vibe ${nlResult.toolName} ${nlResult.commandName}`);
        return;
      } else if (nlResult.config.command) {
        const cmdTemplate = nlResult.config.command;
        const finalCommand = formatCommand(cmdTemplate, []);

        const result = executeShellCommand(finalCommand);

        if (result.success) {
          if (result.stdout) {
            process.stdout.write(result.stdout);
          }
          logger.info(`Successfully executed natural language command: ${cliArgs.join(' ')}`);
          console.log(`\n✨ Executed: vibe ${nlResult.toolName} ${nlResult.commandName}`);
        } else {
          logger.error(`Failed to execute command: ${result.error}`);
          console.error(`Error executing command: ${result.error}`);
          if (result.stderr) {
            process.stderr.write(result.stderr);
          }
          process.exit(1);
        }
        return;
      }
    }
  }
  */

  // Standard command parsing
  const toolName = cliArgs[0];
  const toolCommands = commands[toolName];

  if (!toolCommands) {
    logger.error(`Unknown tool or command: ${cliArgs.join(' ')}`);
    console.error(`Error: Unknown tool or command: ${cliArgs.join(' ')}`);
    printGeneralHelp(commands);
    process.exit(1);
  }

  // Tool help
  if (cliArgs.length === 1 || (cliArgs.length > 1 && cliArgs[1] === 'help')) {
    printToolHelp(toolName, toolCommands);
    return;
  }

  const commandName = cliArgs[1];
  const command = toolCommands[commandName];

  if (!command) {
    logger.error(`Unknown command: ${toolName} ${commandName}`);
    console.error(`Error: Unknown command: ${toolName} ${commandName}`);
    printToolHelp(toolName, toolCommands);
    process.exit(1);
  }

  // Command help
  if (cliArgs.length > 2 && cliArgs[2] === 'help') {
    printCommandHelp(toolName, commandName, command);
    return;
  }

  // Execute command
  if (command.handler) {
    // This is a placeholder for handler implementation
    console.log(`Handler execution: ${command.handler}`);
  } else if (command.command) {
    const cmdTemplate = command.command;
    const args = cliArgs.slice(2);
    const finalCommand = formatCommand(cmdTemplate, args);

    const result = executeShellCommand(finalCommand);

    if (result.success) {
      if (result.stdout) {
        process.stdout.write(result.stdout);
      }
    } else {
      console.error(`Error executing command: ${result.error}`);
      if (result.stderr) {
        process.stderr.write(result.stderr);
      }
      process.exit(1);
    }
  } else {
    console.error('Error: Invalid command configuration');
    process.exit(1);
  }
}

// Run main function
main();
