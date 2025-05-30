/**
 * Tests for the Vibe CLI
 */

// Import Jest types
import { describe, beforeEach, test, expect, jest } from '@jest/globals';
import type { Mocked } from 'jest-mock';

// Import modules being tested
import { loadCommands, loadNaturalLanguageCommands, formatCommand } from '../src/main';

// Import modules for mocking
import * as fs from 'fs';
import * as path from 'path';

// Setup mocks
jest.mock('fs');
jest.mock('path');

const mockedFs = fs as unknown as Mocked<typeof fs>;
const mockedPath = path as unknown as Mocked<typeof path>;

describe('Command Loading', () => {
  beforeEach(() => {
    // Reset mocks
    jest.resetAllMocks();
    
    // Mock implementation for required functions
    mockedPath.resolve.mockImplementation((...args: string[]) => '/mock/path');
    mockedPath.join.mockImplementation((...args: string[]) => '/mock/path/commands.yaml');
    mockedFs.existsSync.mockReturnValue(true);
  });
  
  beforeEach(() => {
    // Reset mocks before each test
    jest.clearAllMocks();
  });

  test('loadCommands should load and parse YAML files', () => {
    // Mock successful file read
    mockedFs.readFileSync.mockReturnValue(`
git:
  status:
    command: git status
    description: Show the working tree status
`);
    
    // Mock file existence check
    mockedFs.existsSync.mockReturnValue(true);
    
    const commands = loadCommands();
    expect(commands).toBeDefined();
    expect(commands.git).toBeDefined();
    expect(commands.git.status).toBeDefined();
    expect(commands.git.status.command).toBe('git status');
  });
  
  test('loadNaturalLanguageCommands should load and parse YAML files', () => {
    // Mock successful file read
    mockedFs.readFileSync.mockReturnValue(`
git:
  check status: status
  add everything: add .
`);
    
    // Mock file existence check
    mockedFs.existsSync.mockReturnValue(true);
    
    const nlCommands = loadNaturalLanguageCommands();
    expect(nlCommands).toBeDefined();
    expect(nlCommands.git).toBeDefined();
    expect(nlCommands.git['check status']).toBe('status');
  });
  
  test('loadCommands should handle errors gracefully', () => {
    // Mock file existence check
    mockedFs.existsSync.mockReturnValue(true);
    
    // Mock file read error
    mockedFs.readFileSync.mockImplementation(() => {
      throw new Error('File not found');
    });
    
    // Silence the expected error logs during test
    jest.spyOn(console, 'error').mockImplementation(() => {});
    
    const commands = loadCommands();
    expect(commands).toEqual({});
  });
  
  test('loadNaturalLanguageCommands should handle errors gracefully', () => {
    // Mock file existence check
    mockedFs.existsSync.mockReturnValue(true);
    
    // Mock file read error
    mockedFs.readFileSync.mockImplementation(() => {
      throw new Error('File not found');
    });
    
    // Silence the expected error logs during test
    jest.spyOn(console, 'error').mockImplementation(() => {});
    
    const nlCommands = loadNaturalLanguageCommands();
    expect(nlCommands).toEqual({});
  });
});

describe('Command Formatting', () => {
  test('formatCommand should replace arguments in templates', () => {
    const template = 'git commit -m "{0}"';
    const args = ['Fixed a bug'];
    
    const result = formatCommand(template, args);
    expect(result).toBe('git commit -m "Fixed a bug"');
  });
  
  test('formatCommand should handle multiple arguments', () => {
    const template = 'git {0} {1}';
    const args = ['checkout', 'main'];
    
    const result = formatCommand(template, args);
    expect(result).toBe('git checkout main');
  });
  
  test('formatCommand should handle no arguments', () => {
    const template = 'git status';
    const args: string[] = [];
    
    const result = formatCommand(template, args);
    expect(result).toBe('git status');
  });
  
  test('formatCommand should handle missing argument references', () => {
    const template = 'git checkout {0} {1}';
    const args = ['main'];
    
    const result = formatCommand(template, args);
    expect(result).toBe('git checkout main {1}');
  });
});
