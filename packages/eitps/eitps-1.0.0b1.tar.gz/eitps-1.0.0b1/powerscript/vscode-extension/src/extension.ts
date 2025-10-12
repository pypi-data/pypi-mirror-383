/** 
MIT License

Copyright (c) 2025 Saleem Ahmad (Elite India Org Team)
Email: team@eliteindia.org

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
**/
import * as vscode from 'vscode';
import { LanguageClient, LanguageClientOptions, ServerOptions } from 'vscode-languageclient/node';
import * as path from 'path';
import { spawn } from 'child_process';

let client: LanguageClient;

export function activate(context: vscode.ExtensionContext) {
    console.log('PowerScript extension is now active!');

    // Start LSP client
    startLanguageClient(context);

    // Register commands
    registerCommands(context);

    // Setup file associations
    setupFileAssociations();
}

function startLanguageClient(context: vscode.ExtensionContext) {
    const config = vscode.workspace.getConfiguration('powerscript');
    
    if (!config.get('lsp.enabled', true)) {
        return;
    }

    // Server options - start PowerScript LSP server
    const serverOptions: ServerOptions = {
        command: 'python',
        args: ['-m', 'powerscript.lsp.server'],
        options: {
            cwd: vscode.workspace.rootPath
        }
    };

    // Client options
    const clientOptions: LanguageClientOptions = {
        documentSelector: [
            { scheme: 'file', language: 'powerscript' },
            { pattern: '**/*.ps' }
        ],
        synchronize: {
            configurationSection: 'powerscript',
            fileEvents: vscode.workspace.createFileSystemWatcher('**/*.ps')
        },
        outputChannelName: 'PowerScript Language Server'
    };

    // Create and start the client
    client = new LanguageClient(
        'powerscript-lsp',
        'PowerScript Language Server',
        serverOptions,
        clientOptions
    );

    // Start the client and server
    client.start().then(() => {
        console.log('PowerScript LSP client started');
    }).catch(err => {
        console.error('Failed to start PowerScript LSP client:', err);
        vscode.window.showErrorMessage('Failed to start PowerScript Language Server');
    });

    context.subscriptions.push(client);
}

function registerCommands(context: vscode.ExtensionContext) {
    // Transpile command
    const transpileCommand = vscode.commands.registerCommand('powerscript.transpile', async (uri?: vscode.Uri) => {
        const targetUri = uri || vscode.window.activeTextEditor?.document.uri;
        if (!targetUri || !targetUri.fsPath.endsWith('.ps')) {
            vscode.window.showErrorMessage('Please select a PowerScript (.ps) file');
            return;
        }

        try {
            const result = await runPowerScriptCommand('powerscriptc', [targetUri.fsPath]);
            vscode.window.showInformationMessage('PowerScript file transpiled successfully!');
            
            // Open the transpiled Python file
            const pythonFile = targetUri.fsPath.replace('.ps', '.py');
            const doc = await vscode.workspace.openTextDocument(pythonFile);
            await vscode.window.showTextDocument(doc);
        } catch (error) {
            vscode.window.showErrorMessage(`Transpilation failed: ${error}`);
        }
    });

    // Run command
    const runCommand = vscode.commands.registerCommand('powerscript.run', async (uri?: vscode.Uri) => {
        const targetUri = uri || vscode.window.activeTextEditor?.document.uri;
        if (!targetUri || !targetUri.fsPath.endsWith('.ps')) {
            vscode.window.showErrorMessage('Please select a PowerScript (.ps) file');
            return;
        }

        try {
            const result = await runPowerScriptCommand('ps-run', [targetUri.fsPath]);
            vscode.window.showInformationMessage('PowerScript file executed successfully!');
        } catch (error) {
            vscode.window.showErrorMessage(`Execution failed: ${error}`);
        }
    });

    // Type check command
    const typeCheckCommand = vscode.commands.registerCommand('powerscript.typeCheck', async (uri?: vscode.Uri) => {
        const targetUri = uri || vscode.window.activeTextEditor?.document.uri;
        if (!targetUri || !targetUri.fsPath.endsWith('.ps')) {
            vscode.window.showErrorMessage('Please select a PowerScript (.ps) file');
            return;
        }

        try {
            const result = await runPowerScriptCommand('psc', [targetUri.fsPath]);
            vscode.window.showInformationMessage('Type checking completed!');
        } catch (error) {
            vscode.window.showErrorMessage(`Type checking failed: ${error}`);
        }
    });

    // Create project command
    const createProjectCommand = vscode.commands.registerCommand('powerscript.createProject', async () => {
        const projectName = await vscode.window.showInputBox({
            prompt: 'Enter project name',
            placeHolder: 'my-powerscript-project'
        });

        if (!projectName) {
            return;
        }

        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            vscode.window.showErrorMessage('Please open a workspace folder first');
            return;
        }

        try {
            const projectPath = path.join(workspaceFolder.uri.fsPath, projectName);
            await runPowerScriptCommand('ps-create', [projectName], workspaceFolder.uri.fsPath);
            
            vscode.window.showInformationMessage(`PowerScript project '${projectName}' created successfully!`);
            
            // Open the new project
            const projectUri = vscode.Uri.file(projectPath);
            await vscode.commands.executeCommand('vscode.openFolder', projectUri);
        } catch (error) {
            vscode.window.showErrorMessage(`Project creation failed: ${error}`);
        }
    });

    context.subscriptions.push(transpileCommand, runCommand, typeCheckCommand, createProjectCommand);
}

function setupFileAssociations() {
    // PowerScript files are handled by the language configuration
    // Additional setup can be done here if needed
}

async function runPowerScriptCommand(command: string, args: string[], cwd?: string): Promise<string> {
    return new Promise((resolve, reject) => {
        const process = spawn(command, args, { 
            cwd: cwd || vscode.workspace.rootPath,
            shell: true 
        });

        let output = '';
        let error = '';

        process.stdout.on('data', (data) => {
            output += data.toString();
        });

        process.stderr.on('data', (data) => {
            error += data.toString();
        });

        process.on('close', (code) => {
            if (code === 0) {
                resolve(output);
            } else {
                reject(error || `Command failed with exit code ${code}`);
            }
        });

        process.on('error', (err) => {
            reject(err.message);
        });
    });
}

export function deactivate(): Thenable<void> | undefined {
    if (!client) {
        return undefined;
    }
    return client.stop();
}