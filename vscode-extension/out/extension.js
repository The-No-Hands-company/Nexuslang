"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const path = __importStar(require("path"));
const vscode = __importStar(require("vscode"));
const node_1 = require("vscode-languageclient/node");
const debugAdapter_1 = require("./debugAdapter");
let client;
async function activate(context) {
    console.log('[NLPL] Extension activation started');
    vscode.window.showInformationMessage('NLPL extension is activating...');
    // Activate debug support
    (0, debugAdapter_1.activateDebugSupport)(context);
    // Get configuration
    const config = vscode.workspace.getConfiguration('nlpl');
    const enabled = config.get('languageServer.enabled', true);
    console.log('[NLPL] Language server enabled:', enabled);
    if (!enabled) {
        console.log('[NLPL] Language server is disabled');
        return;
    }
    // Determine server path
    let serverPath = config.get('languageServer.path', '');
    let args = [];
    if (!serverPath) {
        // Default: use Python to run LSP server from workspace
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (workspaceFolder) {
            const pythonPath = config.get('languageServer.pythonPath', 'python3');
            const lspServerPath = path.join(workspaceFolder.uri.fsPath, 'src', 'nlpl', 'lsp', 'server.py');
            serverPath = pythonPath;
            // Run server.py directly (simpler than -m)
            args = [lspServerPath, '--stdio'];
        }
        else {
            // Fallback to system installation
            serverPath = 'nlpl-lsp';
            args = config.get('languageServer.arguments', ['--stdio']);
        }
    }
    else {
        // Server path was manually configured
        args = config.get('languageServer.arguments', []);
    }
    if (config.get('languageServer.debug', false)) {
        args.push('--debug');
    }
    const logFile = config.get('languageServer.logFile', '');
    if (logFile) {
        args.push('--log-file', logFile);
    }
    console.log('[NLPL] Server command:', serverPath);
    console.log('[NLPL] Server args:', args);
    // Server options with PYTHONPATH for workspace
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    const pythonPath = workspaceFolder ? path.join(workspaceFolder.uri.fsPath, 'src') : process.env.PYTHONPATH;
    console.log('[NLPL] PYTHONPATH:', pythonPath);
    const serverOptions = {
        command: serverPath,
        args: args,
        transport: node_1.TransportKind.stdio,
        options: {
            env: {
                ...process.env,
                PYTHONPATH: pythonPath
            }
        }
    };
    // Client options
    const clientOptions = {
        documentSelector: [{ scheme: 'file', language: 'nlpl' }],
        synchronize: {
            fileEvents: vscode.workspace.createFileSystemWatcher('**/*.nlpl')
        }
    };
    // Create the language client
    console.log('[NLPL] Creating language client...');
    client = new node_1.LanguageClient('nlplLanguageServer', 'NLPL Language Server', serverOptions, clientOptions);
    // Start the client (async)
    console.log('[NLPL] Starting language client...');
    // Add timeout to prevent hanging forever
    const startPromise = client.start();
    const timeoutPromise = new Promise((_, reject) => setTimeout(() => reject(new Error('LSP server start timeout after 10 seconds')), 10000));
    try {
        await Promise.race([startPromise, timeoutPromise]);
        console.log('[NLPL] Language server started successfully!');
        vscode.window.showInformationMessage('NLPL Language Server started successfully!');
    }
    catch (error) {
        console.error('[NLPL] Failed to start language server:', error);
        vscode.window.showErrorMessage(`NLPL Language Server failed to start: ${error}`);
        // Show detailed diagnostic
        const diagnose = await vscode.window.showErrorMessage('NLPL LSP failed to start. Check if Python and src/nlpl/lsp/server.py exist?', 'Show Logs');
        if (diagnose === 'Show Logs') {
            vscode.commands.executeCommand('workbench.action.output.show');
        }
    }
}
function deactivate() {
    if (!client) {
        return undefined;
    }
    return client.stop();
}
//# sourceMappingURL=extension.js.map