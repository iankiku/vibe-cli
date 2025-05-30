/**
 * Shared utilities for VibeCLI command parsing and execution
 * TypeScript implementation with strong typing
 */

// Types for command configuration
export interface CommandConfig {
  command?: string;
  description?: string;
  handler?: string;
  args?: string[];
}

export interface ToolCommands {
  [commandName: string]: CommandConfig;
}

export interface AllCommands {
  [toolName: string]: ToolCommands;
}

export interface CommandInfo {
  type?: string;
  tool?: string;
  command?: string;
  config?: CommandConfig;
  args?: string[];
  error?: string;
  showHelp?: boolean;
  toolHelp?: string;
  commands?: ToolCommands;
  commandHelp?: boolean;
  success?: boolean;
  result?: any;
}

// Load and parse commands from YAML
export function loadCommands(yamlPath: string): AllCommands {
  // Implementation will differ between Node and Python
  // Node will use fs and js-yaml
  // Python will use os and pyyaml
  // This is just a placeholder interface
  return {};
}

// Parse command arguments to determine which command to run
export function parseCommandArgs(args: string[], commands: AllCommands): CommandInfo {
  if (!args || args.length === 0) {
    return { error: "No command specified", showHelp: true };
  }

  // Handle special cases
  if (args[0] === "--version" || args[0] === "-v") {
    return { type: "system", command: "version", args: [] };
  }
  
  if (args[0] === "help" || args[0] === "--help" || args[0] === "-h") {
    return { showHelp: true };
  }

  // Extract tool and command
  const toolName = args[0];
  const toolCommands = commands[toolName];
  
  if (!toolCommands) {
    return { error: `Unknown tool: ${toolName}`, showHelp: true };
  }
  
  // If only tool specified, or explicit help for tool
  if (args.length === 1 || (args.length > 1 && args[1] === "help")) {
    return { toolHelp: toolName, commands: toolCommands };
  }
  
  const commandName = args[1];
  const command = toolCommands[commandName];
  
  if (!command) {
    return { error: `Unknown command: ${toolName} ${commandName}`, toolHelp: toolName, commands: toolCommands };
  }
  
  // Command-specific help
  if (args.length > 2 && args[2] === "help") {
    return { commandHelp: true, tool: toolName, command: commandName, config: command };
  }
  
  // Valid command found, return its config and remaining args
  return {
    tool: toolName,
    command: commandName,
    config: command,
    args: args.slice(2)
  };
}

// Execute a command based on its configuration
export function executeCommand(commandInfo: CommandInfo): CommandInfo {
  const { tool, command, config, args = [] } = commandInfo;
  
  if (!config) {
    return { error: "Invalid command configuration" };
  }
  
  if (config.handler) {
    // Handle execution via handler function
    return { type: "handler", success: true, result: `Handler executed: ${config.handler}` };
  } else if (config.command) {
    // Handle execution via shell command
    const cmdTemplate = config.command;
    const finalCommand = formatCommand(cmdTemplate, args);
    
    return { type: "shell", success: true, result: `Command executed: ${finalCommand}` };
  }
  
  return { error: "Command configuration is invalid" };
}

// Format a command template with argument values
export function formatCommand(template: string, args: string[]): string {
  let result = template;
  
  // Simple placeholder replacement
  if (template.includes("{")) {
    // Extract placeholder names from template
    const placeholders = template.match(/\{([^}]+)\}/g) || [];
    
    // Replace each placeholder with its value from args
    placeholders.forEach((placeholder, i) => {
      const clean = placeholder.replace(/[{}]/g, '');
      if (i < args.length) {
        result = result.replace(`{${clean}}`, args[i]);
      }
    });
  }
  
  return result;
}

// Display help information
export function printGeneralHelp(commands: AllCommands): void {
  console.log("Vibe CLI - Natural language wrapper for development commands");
  console.log("Usage: vibe <tool> <command> [args]");
  console.log("\nAvailable tools:");
  
  for (const toolName in commands) {
    console.log(`  ${toolName}`);
  }
  
  console.log("\nRun 'vibe <tool> help' for commands within a tool");
  console.log("Run 'vibe help' to see this message");
}

// Display help for a specific tool
export function printToolHelp(toolName: string, toolCommands: ToolCommands): void {
  console.log(`Vibe CLI - ${toolName} commands`);
  console.log(`Usage: vibe ${toolName} <command> [args]`);
  console.log("\nAvailable commands:");
  
  for (const cmdName in toolCommands) {
    const cmd = toolCommands[cmdName];
    console.log(`  ${cmdName.padEnd(20)} ${cmd.description || ''}`);
  }
  
  console.log(`\nRun 'vibe ${toolName} <command> help' for command details`);
}

// Display help for a specific command
export function printCommandHelp(toolName: string, commandName: string, config: CommandConfig): void {
  console.log(`Vibe CLI - ${toolName} ${commandName}`);
  console.log(`Description: ${config.description || 'No description'}`);
  
  if (config.command) {
    console.log(`Executes: ${config.command}`);
  }
  
  console.log("\nUsage examples:");
  console.log(`  vibe ${toolName} ${commandName} [args]`);
}
