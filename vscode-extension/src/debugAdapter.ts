/**
 * NLPL Debug Adapter for VS Code
 * 
 * Bridges VS Code's Debug Adapter Protocol to the NLPL Python DAP server.
 * Acts as a proxy that spawns the Python debugger and forwards messages.
 */

import * as vscode from 'vscode';
import * as path from 'path';
import { spawn, ChildProcess } from 'child_process';

export class NLPLDebugAdapterServerDescriptorFactory implements vscode.DebugAdapterDescriptorFactory {
    createDebugAdapterDescriptor(
        session: vscode.DebugSession,
        executable: vscode.DebugAdapterExecutable | undefined
    ): vscode.ProviderResult<vscode.DebugAdapterDescriptor> {
        
        const config = session.configuration;
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        
        // Get Python path from config or use default
        const pythonPath = config.pythonPath || 
                          vscode.workspace.getConfiguration('nlpl.debugger').get('pythonPath', 'python3');
        
        // Get debug server path
        let debugServerPath = config.debugServerPath || 
                             vscode.workspace.getConfiguration('nlpl.debugger').get('debugServerPath', '');
        
        // Auto-detect server path if not specified
        if (!debugServerPath && workspaceFolder) {
            debugServerPath = path.join(workspaceFolder.uri.fsPath, 'src', 'nlpl', 'debugger', 'dap_server.py');
        }
        
        // Get log file path
        const logFile = vscode.workspace.getConfiguration('nlpl.debugger').get('logFile', '/tmp/nlpl-dap.log');
        
        // Build command arguments
        const args = ['-m', 'nlpl.debugger', '--debug', '--log-file', logFile];
        
        console.log(`Starting NLPL debugger: ${pythonPath} ${args.join(' ')}`);
        
        // Return server descriptor that spawns Python DAP server
        return new vscode.DebugAdapterServer(0, '127.0.0.1');  // Will use stdio instead
        
        // Alternative: Use executable descriptor for stdio communication
        // return new vscode.DebugAdapterExecutable(pythonPath, args);
    }
}

export class NLPLDebugAdapterExecutableFactory implements vscode.DebugAdapterDescriptorFactory {
    createDebugAdapterDescriptor(
        session: vscode.DebugSession,
        executable: vscode.DebugAdapterExecutable | undefined
    ): vscode.ProviderResult<vscode.DebugAdapterDescriptor> {
        
        const config = session.configuration;
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        
        // Get Python path from config
        const pythonPath = config.pythonPath || 
                          vscode.workspace.getConfiguration('nlpl.debugger').get('pythonPath', 'python3');
        
        // Get log file path
        const logFile = vscode.workspace.getConfiguration('nlpl.debugger').get('logFile', '/tmp/nlpl-dap.log');
        
        // Build arguments
        const args = ['-m', 'nlpl.debugger', '--debug', '--log-file', logFile];
        
        console.log(`Launching NLPL debugger: ${pythonPath} ${args.join(' ')}`);
        
        // Return executable that runs Python DAP server via stdio
        return new vscode.DebugAdapterExecutable(pythonPath, args, {
            cwd: workspaceFolder?.uri.fsPath || process.cwd()
        });
    }
}

/**
 * Configuration provider for NLPL debug sessions.
 * Resolves launch configurations and provides initial setup.
 */
export class NLPLDebugConfigurationProvider implements vscode.DebugConfigurationProvider {
    
    /**
     * Massage a debug configuration just before a debug session is being launched.
     */
    resolveDebugConfiguration(
        folder: vscode.WorkspaceFolder | undefined,
        config: vscode.DebugConfiguration,
        token?: vscode.CancellationToken
    ): vscode.ProviderResult<vscode.DebugConfiguration> {
        
        // If launch.json is missing or empty
        if (!config.type && !config.request && !config.name) {
            const editor = vscode.window.activeTextEditor;
            
            if (editor && editor.document.languageId === 'nlpl') {
                config.type = 'nlpl';
                config.name = 'Debug NLPL Program';
                config.request = 'launch';
                config.program = editor.document.uri.fsPath;
                config.stopOnEntry = false;
            } else {
                vscode.window.showErrorMessage('No NLPL program to debug. Open a .nlpl file first.');
                return undefined;
            }
        }
        
        // Ensure program path is absolute
        if (config.program && !path.isAbsolute(config.program)) {
            const workspaceFolder = folder?.uri.fsPath || vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
            if (workspaceFolder) {
                config.program = path.join(workspaceFolder, config.program);
            }
        }
        
        // Resolve ${file} variable
        if (config.program === '${file}') {
            const editor = vscode.window.activeTextEditor;
            if (editor) {
                config.program = editor.document.uri.fsPath;
            } else {
                vscode.window.showErrorMessage('No active editor with NLPL file.');
                return undefined;
            }
        }
        
        // Resolve ${workspaceFolder} variable
        if (config.program && config.program.includes('${workspaceFolder}')) {
            const workspaceFolder = folder?.uri.fsPath || vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
            if (workspaceFolder) {
                config.program = config.program.replace('${workspaceFolder}', workspaceFolder);
            }
        }
        
        // Set default cwd if not specified
        if (!config.cwd) {
            config.cwd = folder?.uri.fsPath || path.dirname(config.program);
        }
        
        // Get Python path from settings if not in config
        if (!config.pythonPath) {
            config.pythonPath = vscode.workspace.getConfiguration('nlpl.debugger').get('pythonPath', 'python3');
        }
        
        console.log('Resolved debug configuration:', config);
        
        return config;
    }
    
    /**
     * Provide initial debug configurations for launch.json.
     */
    provideDebugConfigurations(
        folder: vscode.WorkspaceFolder | undefined,
        token?: vscode.CancellationToken
    ): vscode.ProviderResult<vscode.DebugConfiguration[]> {
        
        return [
            {
                type: 'nlpl',
                request: 'launch',
                name: 'Debug NLPL Program',
                program: '${file}',
                stopOnEntry: false
            },
            {
                type: 'nlpl',
                request: 'launch',
                name: 'Debug NLPL Program (Stop on Entry)',
                program: '${file}',
                stopOnEntry: true
            }
        ];
    }
}

/**
 * Register debug support for NLPL.
 */
export function activateDebugSupport(context: vscode.ExtensionContext) {
    // Register debug adapter factory
    context.subscriptions.push(
        vscode.debug.registerDebugAdapterDescriptorFactory(
            'nlpl',
            new NLPLDebugAdapterExecutableFactory()
        )
    );
    
    // Register debug configuration provider
    context.subscriptions.push(
        vscode.debug.registerDebugConfigurationProvider(
            'nlpl',
            new NLPLDebugConfigurationProvider()
        )
    );
    
    // Register command to run current file with debugger
    context.subscriptions.push(
        vscode.commands.registerCommand('nlpl.debug', () => {
            const editor = vscode.window.activeTextEditor;
            if (editor && editor.document.languageId === 'nlpl') {
                vscode.debug.startDebugging(undefined, {
                    type: 'nlpl',
                    name: 'Debug NLPL Program',
                    request: 'launch',
                    program: editor.document.uri.fsPath,
                    stopOnEntry: false
                });
            } else {
                vscode.window.showErrorMessage('No active NLPL file to debug.');
            }
        })
    );
    
    console.log('NLPL debug support activated');
}
