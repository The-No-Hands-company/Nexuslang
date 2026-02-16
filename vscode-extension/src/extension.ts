import * as path from 'path';
import * as vscode from 'vscode';
import {
    LanguageClient,
    LanguageClientOptions,
    ServerOptions,
    TransportKind
} from 'vscode-languageclient/node';
import { activateDebugSupport } from './debugAdapter';

let client: LanguageClient;

export function activate(context: vscode.ExtensionContext) {
    console.log('NLPL extension is now active');

    // Activate debug support
    activateDebugSupport(context);

    // Get configuration
    const config = vscode.workspace.getConfiguration('nlpl');
    const enabled = config.get<boolean>('languageServer.enabled', true);

    if (!enabled) {
        console.log('NLPL language server is disabled');
        return;
    }

    // Determine server path
    let serverPath = config.get<string>('languageServer.path', '');
    let args: string[] = [];
    
    if (!serverPath) {
        // Default: use Python to run LSP server from workspace
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (workspaceFolder) {
            const pythonPath = config.get<string>('languageServer.pythonPath', 'python3');
            const lspServerPath = path.join(workspaceFolder.uri.fsPath, 'src', 'nlpl', 'lsp', 'server.py');
            serverPath = pythonPath;
            args = [lspServerPath];
        } else {
            // Fallback to system installation
            serverPath = 'nlpl-lsp';
            args = config.get<string[]>('languageServer.arguments', []);
        }
    } else {
        // Server path was manually configured
        args = config.get<string[]>('languageServer.arguments', []);
    }
    
    if (config.get<boolean>('languageServer.debug', false)) {
        args.push('--debug');
    }

    const logFile = config.get<string>('languageServer.logFile', '');
    if (logFile) {
        args.push('--log-file', logFile);
    }

    // Server options
    const serverOptions: ServerOptions = {
        command: serverPath,
        args: args,
        transport: TransportKind.stdio
    };

    // Client options
    const clientOptions: LanguageClientOptions = {
        documentSelector: [{ scheme: 'file', language: 'nlpl' }],
        synchronize: {
            fileEvents: vscode.workspace.createFileSystemWatcher('**/*.nlpl')
        }
    };

    // Create the language client
    client = new LanguageClient(
        'nlplLanguageServer',
        'NLPL Language Server',
        serverOptions,
        clientOptions
    );

    // Start the client
    client.start();

    console.log('NLPL language server started');
}

export function deactivate(): Thenable<void> | undefined {
    if (!client) {
        return undefined;
    }
    return client.stop();
}
