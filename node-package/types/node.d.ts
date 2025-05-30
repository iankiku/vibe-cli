// Basic Node.js modules type definitions

// Buffer definition
interface Buffer extends Uint8Array {
  write(string: string, offset?: number, length?: number, encoding?: string): number;
  toString(encoding?: string, start?: number, end?: number): string;
  toJSON(): { type: 'Buffer'; data: number[] };
  equals(otherBuffer: Uint8Array): boolean;
  compare(otherBuffer: Uint8Array, targetStart?: number, targetEnd?: number, sourceStart?: number, sourceEnd?: number): number;
  copy(targetBuffer: Uint8Array, targetStart?: number, sourceStart?: number, sourceEnd?: number): number;
  slice(start?: number, end?: number): Buffer;
  byteLength: number;
  length: number;
}

declare var Buffer: {
  new(str: string, encoding?: string): Buffer;
  new(size: number): Buffer;
  new(array: Uint8Array): Buffer;
  new(arrayBuffer: ArrayBuffer): Buffer;
  new(array: any[]): Buffer;
  alloc(size: number, fill?: string | Buffer | number, encoding?: string): Buffer;
  allocUnsafe(size: number): Buffer;
  from(array: any[]): Buffer;
  from(arrayBuffer: ArrayBuffer, byteOffset?: number, length?: number): Buffer;
  from(str: string, encoding?: string): Buffer;
  isBuffer(obj: any): boolean;
  concat(list: Buffer[], totalLength?: number): Buffer;
};
declare module 'fs' {
  export function readFileSync(path: string, options: { encoding: string }): string;
  export function readFileSync(path: string, options?: string): Buffer;
  export function existsSync(path: string): boolean;
  export function appendFileSync(file: string, data: string): void;
  export function writeFileSync(file: string, data: string | Buffer): void;
  export function mkdirSync(path: string, options?: { recursive?: boolean }): void;
  export function copyFileSync(src: string, dest: string): void;
}

declare module 'path' {
  export function join(...paths: string[]): string;
  export function resolve(...paths: string[]): string;
  export function dirname(path: string): string;
  export function basename(path: string, ext?: string): string;
  export function extname(path: string): string;
}

declare module 'os' {
  export function homedir(): string;
  export function platform(): string;
  export function tmpdir(): string;
  export function hostname(): string;
  export const EOL: string;
}

declare module 'process' {
  global {
    namespace NodeJS {
      interface Process {
        env: { [key: string]: string | undefined };
        argv: string[];
        exit(code?: number): never;
        stdout: {
          write(data: string | Buffer): boolean;
        };
        stderr: {
          write(data: string | Buffer): boolean;
        };
      }
    }
    var process: NodeJS.Process;
    var __dirname: string;
    var __filename: string;
  }
}

declare module 'js-yaml' {
  export function load(input: string, options?: any): any;
  export function dump(object: any, options?: any): string;
}

declare module 'commander' {
  export class Command {
    constructor(name?: string);
    version(str: string, flags?: string, description?: string): this;
    description(str: string): this;
    option(flags: string, description?: string, defaultValue?: any): this;
    command(name: string): Command;
    action(fn: (...args: any[]) => void): this;
    parse(argv?: string[]): this;
    help(): void;
  }
}

declare module 'child_process' {
  export interface ExecSyncOptions {
    encoding?: string | null;
    stdio?: 'pipe' | 'ignore' | 'inherit' | Array<any>;
    shell?: string;
    cwd?: string;
    env?: { [key: string]: string | undefined };
    timeout?: number;
    maxBuffer?: number;
    killSignal?: string;
  }
  
  export function execSync(command: string, options?: ExecSyncOptions): Buffer | string;
}

declare module 'chalk' {
  interface ChalkFunction {
    (text: string): string;
    red: ChalkFunction;
    green: ChalkFunction;
    yellow: ChalkFunction;
    blue: ChalkFunction;
    magenta: ChalkFunction;
    cyan: ChalkFunction;
    white: ChalkFunction;
    gray: ChalkFunction;
    grey: ChalkFunction;
    black: ChalkFunction;
    bold: ChalkFunction;
    italic: ChalkFunction;
    underline: ChalkFunction;
    dim: ChalkFunction;
    bgRed: ChalkFunction;
    bgGreen: ChalkFunction;
    bgYellow: ChalkFunction;
    bgBlue: ChalkFunction;
    bgMagenta: ChalkFunction;
    bgCyan: ChalkFunction;
    bgWhite: ChalkFunction;
    bgBlack: ChalkFunction;
  }
  
  const chalk: ChalkFunction;
  export default chalk;
}
