const vscode = require('vscode');
const path = require('path');
const { LanguageClient, TransportKind } = require('vscode-languageclient/node');

let client;

function activate(context) {
    console.log('NLPL Language Extension activating...');

    // Get configuration
    const config = vscode.workspace.getConfiguration('nlpl');
    let serverPath = config.get('languageServer.path');

    // Auto-detect server path if not configured
    if (!serverPath) {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (workspaceFolder) {
            serverPath = path.join(workspaceFolder.uri.fsPath, 'src', 'nlpl_lsp.py');
        } else {
            vscode.window.showErrorMessage('NLPL: No workspace folder found');
            return;
        }
    }

    console.log('NLPL Language Server path:', serverPath);

    // Server options
    const serverOptions = {
        command: 'python3',
        args: [serverPath],
        transport: TransportKind.stdio
    };

    // Client options
    const clientOptions = {
        documentSelector: [{ scheme: 'file', language: 'nlpl' }],
        synchronize: {
            fileEvents: vscode.workspace.createFileSystemWatcher('**/*.nlpl')
        }
    };

    // Create and start client
    client = new LanguageClient(
        'nlplLanguageServer',
        'NLPL Language Server',
        serverOptions,
        clientOptions
    );

    client.start();
    console.log('NLPL Language Server started');

    vscode.window.showInformationMessage('NLPL Language Server activated!');
}

function deactivate() {
    if (!client) {
        return undefined;
    }
    return client.stop();
}

module.exports = {
    activate,
    deactivate
};
