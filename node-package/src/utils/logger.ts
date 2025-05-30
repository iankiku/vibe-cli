/**
 * Vibe CLI Logger Module
 * 
 * A consistent logging interface for the Vibe CLI application.
 */
// Use require instead of import to avoid TypeScript issues
const fs = require('fs');
const path = require('path');
const os = require('os');
const process = require('process');

// Define log levels
export enum LogLevel {
  TRACE = 5,
  DEBUG = 10,
  INFO = 20,
  WARNING = 30,
  ERROR = 40,
  CRITICAL = 50
}

// ANSI color codes for terminal output
const COLORS = {
  reset: '\x1b[0m',
  black: '\x1b[30m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  white: '\x1b[37m',
  bold: '\x1b[1m'
};

// Define log level colors
const LEVEL_COLORS = {
  [LogLevel.CRITICAL]: COLORS.red + COLORS.bold,
  [LogLevel.ERROR]: COLORS.red,
  [LogLevel.WARNING]: COLORS.yellow,
  [LogLevel.INFO]: COLORS.green,
  [LogLevel.DEBUG]: COLORS.blue,
  [LogLevel.TRACE]: COLORS.magenta
};

// Log level names
const LEVEL_NAMES = {
  [LogLevel.CRITICAL]: 'CRITICAL',
  [LogLevel.ERROR]: 'ERROR',
  [LogLevel.WARNING]: 'WARNING',
  [LogLevel.INFO]: 'INFO',
  [LogLevel.DEBUG]: 'DEBUG',
  [LogLevel.TRACE]: 'TRACE'
};

interface LogOptions {
  /** Enable/disable colorized output for terminal */
  useColors: boolean;
  /** Enable/disable file logging */
  logToFile: boolean;
  /** Directory to store log files */
  logDir?: string;
  /** Minimum log level to display */
  logLevel: LogLevel;
}

/**
 * Main logger class for Vibe CLI
 */
export class Logger {
  private static instance: Logger;
  private loggers: Map<string, Logger> = new Map();
  private options: LogOptions;
  private logFile?: string;
  private name: string;
  private fileStream?: any; // File stream for logging
  
  /**
   * Create a new logger instance
   * 
   * @param name Logger name (typically module name)
   * @param options Logging options
   */
  private constructor(name: string, options?: Partial<LogOptions>) {
    this.name = name;
    
    // Default options
    this.options = {
      useColors: process.stdout.isTTY,
      logToFile: process.env.VIBE_LOG_TO_FILE === 'true',
      logLevel: this.getLogLevelFromEnv(),
      ...options
    };
    
    // Set up file logging if enabled
    if (this.options.logToFile) {
      this.setupFileLogging();
    }
  }
  
  /**
   * Get log level from environment variable
   */
  private getLogLevelFromEnv(): LogLevel {
    const envLevel = process.env.VIBE_LOG_LEVEL?.toUpperCase();
    switch (envLevel) {
      case 'TRACE': return LogLevel.TRACE;
      case 'DEBUG': return LogLevel.DEBUG;
      case 'INFO': return LogLevel.INFO;
      case 'WARNING': return LogLevel.WARNING;
      case 'ERROR': return LogLevel.ERROR;
      case 'CRITICAL': return LogLevel.CRITICAL;
      default: return LogLevel.INFO;
    }
  }
  
  /**
   * Set up file logging
   */
  private setupFileLogging(): void {
    try {
      // Determine log directory
      const homeDir = os.homedir();
      const logDir = this.options.logDir || path.join(homeDir, '.vibe-cloud', 'logs');
      
      // Create log directory if it doesn't exist
      if (!fs.existsSync(logDir)) {
        fs.mkdirSync(logDir, { recursive: true });
      }
      
      // Create log file with timestamp
      const timestamp = new Date().toISOString().replace(/[:.]/g, '').replace('T', '_').slice(0, 15);
      this.logFile = path.join(logDir, `vibe_cli_${timestamp}.log`);
      
      // Create file stream
      this.fileStream = fs.createWriteStream(this.logFile, { flags: 'a' });
    } catch (error) {
      console.error(`Failed to set up file logging: ${(error as Error).message}`);
    }
  }
  
  /**
   * Get a singleton instance of the logger
   */
  public static getInstance(name: string = 'vibe'): Logger {
    if (!Logger.instance) {
      Logger.instance = new Logger(name);
    }
    return Logger.instance;
  }
  
  /**
   * Get a logger with a specific name
   */
  public getLogger(name: string): Logger {
    if (!this.loggers.has(name)) {
      const logger = new Logger(name, {
        useColors: this.options.useColors,
        logToFile: this.options.logToFile,
        logDir: this.options.logDir,
        logLevel: this.options.logLevel
      });
      this.loggers.set(name, logger);
    }
    return this.loggers.get(name)!;
  }
  
  /**
   * Format a log message
   */
  private formatLogMessage(level: LogLevel, message: string): string {
    const timestamp = new Date().toISOString();
    const levelName = LEVEL_NAMES[level];
    
    if (this.options.useColors) {
      const color = LEVEL_COLORS[level];
      return `${timestamp} - ${color}${levelName}${COLORS.reset} - ${this.name} - ${message}`;
    } else {
      return `${timestamp} - ${levelName} - ${this.name} - ${message}`;
    }
  }
  
  /**
   * Write a log message
   */
  private log(level: LogLevel, message: string, ...args: any[]): void {
    // Check if this log level should be displayed
    if (level < this.options.logLevel) {
      return;
    }
    
    // Format message with arguments
    let formattedMessage = message;
    if (args.length > 0) {
      // Simple printf-style formatting (replace %s, %d, etc.)
      let i = 0;
      formattedMessage = message.replace(/%[sdj%]/g, (match) => {
        if (match === '%%') return '%';
        return String(args[i++]);
      });
    }
    
    const logMessage = this.formatLogMessage(level, formattedMessage);
    
    // Log to console
    switch (level) {
      case LogLevel.CRITICAL:
      case LogLevel.ERROR:
        console.error(logMessage);
        break;
      case LogLevel.WARNING:
        console.warn(logMessage);
        break;
      case LogLevel.INFO:
        console.info(logMessage);
        break;
      case LogLevel.DEBUG:
      case LogLevel.TRACE:
        console.debug(logMessage);
        break;
    }
    
    // Log to file if enabled
    if (this.fileStream) {
      // Remove color codes for file logging
      const plainMessage = logMessage.replace(/\x1b\[\d+m/g, '');
      this.fileStream.write(plainMessage + '\n');
    }
  }
  
  /**
   * Set the log level
   */
  public setLevel(level: LogLevel): void {
    this.options.logLevel = level;
  }
  
  /**
   * Log methods for different levels
   */
  public trace(message: string, ...args: any[]): void {
    this.log(LogLevel.TRACE, message, ...args);
  }
  
  public debug(message: string, ...args: any[]): void {
    this.log(LogLevel.DEBUG, message, ...args);
  }
  
  public info(message: string, ...args: any[]): void {
    this.log(LogLevel.INFO, message, ...args);
  }
  
  public warning(message: string, ...args: any[]): void {
    this.log(LogLevel.WARNING, message, ...args);
  }
  
  public error(message: string, ...args: any[]): void {
    this.log(LogLevel.ERROR, message, ...args);
  }
  
  public critical(message: string, ...args: any[]): void {
    this.log(LogLevel.CRITICAL, message, ...args);
  }
}

// Create default logger instance
const defaultLogger = Logger.getInstance();

// Export convenience functions
export function getLogger(name?: string): Logger {
  return name ? defaultLogger.getLogger(name) : defaultLogger;
}

export const trace = (message: string, ...args: any[]): void => defaultLogger.trace(message, ...args);
export const debug = (message: string, ...args: any[]): void => defaultLogger.debug(message, ...args);
export const info = (message: string, ...args: any[]): void => defaultLogger.info(message, ...args);
export const warning = (message: string, ...args: any[]): void => defaultLogger.warning(message, ...args);
export const error = (message: string, ...args: any[]): void => defaultLogger.error(message, ...args);
export const critical = (message: string, ...args: any[]): void => defaultLogger.critical(message, ...args);

// Export default logger
export default defaultLogger;
