import * as vscode from 'vscode';

export async function activate(context: vscode.ExtensionContext) {
    console.log('[NLPL] SIMPLE TEST - Extension activation started');
    vscode.window.showInformationMessage('NLPL Test Extension Activated!');
    
    // Just register a simple command to prove extension works
    const disposable = vscode.commands.registerCommand('nlpl.test', () => {
        vscode.window.showInformationMessage('NLPL Test Command Works!');
    });
    
    context.subscriptions.push(disposable);
    
    console.log('[NLPL] SIMPLE TEST - Extension activation completed');
}

export function deactivate(): Thenable<void> | undefined {
    console.log('[NLPL] Extension deactivated');
    return undefined;
}
