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
const vscode = __importStar(require("vscode"));
const node_1 = require("vscode-languageclient/node");
let client;
function activate(context) {
    console.log('NLPL extension is now active');
    // Get configuration
    const config = vscode.workspace.getConfiguration('nlpl');
    const enabled = config.get('languageServer.enabled', true);
    if (!enabled) {
        console.log('NLPL language server is disabled');
        return;
    }
    // Determine server path
    let serverPath = config.get('languageServer.path', '');
    if (!serverPath) {
        // Use bundled server or system installation
        serverPath = 'nlpl-lsp'; // Assumes nlpl-lsp is in PATH
    }
    // Server arguments
    let args = config.get('languageServer.arguments', ['--stdio']);
    if (config.get('languageServer.debug', false)) {
        args.push('--debug');
    }
    const logFile = config.get('languageServer.logFile', '');
    if (logFile) {
        args.push('--log-file', logFile);
    }
    // Server options
    const serverOptions = {
        command: serverPath,
        args: args,
        transport: node_1.TransportKind.stdio
    };
    // Client options
    const clientOptions = {
        documentSelector: [{ scheme: 'file', language: 'nlpl' }],
        synchronize: {
            fileEvents: vscode.workspace.createFileSystemWatcher('**/*.nlpl')
        }
    };
    // Create the language client
    client = new node_1.LanguageClient('nlplLanguageServer', 'NLPL Language Server', serverOptions, clientOptions);
    // Start the client
    client.start();
    console.log('NLPL language server started');
}
function deactivate() {
    if (!client) {
        return undefined;
    }
    return client.stop();
}
//# sourceMappingURL=extension.js.map