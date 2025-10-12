"use strict";
/*
 * MIT License
 *
 * Copyright (c) 2025 Saleem Ahmad (Elite India Org Team)
 * Email: team@eliteindia.org
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */
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
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.deactivate = exports.activate = void 0;
const vscode = __importStar(require("vscode"));
let client;
function activate(context) {
    console.log('PowerScript extension is now active!');
    // Register commands
    registerCommands(context);
    // Start LSP client
    startLanguageServer(context);
    // Register diagnostics
    registerDiagnostics(context);
}
exports.activate = activate;
function registerCommands(context) {
    // Compile PowerScript file
    const compileCommand = vscode.commands.registerCommand('powerscript.compile', async (uri) => {
        var _a;
        const fileUri = uri || ((_a = vscode.window.activeTextEditor) === null || _a === void 0 ? void 0 : _a.document.uri);
        if (!fileUri) {
            vscode.window.showErrorMessage('No PowerScript file selected');
            return;
        }
        try {
            const terminal = vscode.window.createTerminal('PowerScript Compile');
            terminal.show();
            terminal.sendText(`powerscriptc "${fileUri.fsPath}"`);
            vscode.window.showInformationMessage('PowerScript compilation started');
        }
        catch (error) {
            vscode.window.showErrorMessage(`Compilation failed: ${error}`);
        }
    });
    // Run PowerScript file
    const runCommand = vscode.commands.registerCommand('powerscript.run', async (uri) => {
        var _a;
        const fileUri = uri || ((_a = vscode.window.activeTextEditor) === null || _a === void 0 ? void 0 : _a.document.uri);
        if (!fileUri) {
            vscode.window.showErrorMessage('No PowerScript file selected');
            return;
        }
        try {
            const terminal = vscode.window.createTerminal('PowerScript Run');
            terminal.show();
            terminal.sendText(`ps-run "${fileUri.fsPath}"`);
            vscode.window.showInformationMessage('PowerScript execution started');
        }
        catch (error) {
            vscode.window.showErrorMessage(`Execution failed: ${error}`);
        }
    });
    // Create PowerScript project
    const createProjectCommand = vscode.commands.registerCommand('powerscript.createProject', async () => {
        var _a;
        const projectName = await vscode.window.showInputBox({
            prompt: 'Enter project name',
            placeHolder: 'my-powerscript-project'
        });
        if (!projectName)
            return;
        const workspaceFolder = (_a = vscode.workspace.workspaceFolders) === null || _a === void 0 ? void 0 : _a[0];
        if (!workspaceFolder) {
            vscode.window.showErrorMessage('No workspace folder open');
            return;
        }
        try {
            const terminal = vscode.window.createTerminal('PowerScript Project');
            terminal.show();
            terminal.sendText(`cd "${workspaceFolder.uri.fsPath}" && ps-create "${projectName}"`);
            vscode.window.showInformationMessage(`Creating PowerScript project: ${projectName}`);
        }
        catch (error) {
            vscode.window.showErrorMessage(`Project creation failed: ${error}`);
        }
    });
    context.subscriptions.push(compileCommand, runCommand, createProjectCommand);
}
function startLanguageServer(context) {
    // For now, we'll use a basic implementation without the full LSP client
    // In a complete implementation, you would use vscode-languageclient
    console.log('Language server would start here');
}
function registerDiagnostics(context) {
    const diagnostics = vscode.languages.createDiagnosticCollection('powerscript');
    context.subscriptions.push(diagnostics);
    // Listen for document changes
    const onDidChangeDocument = vscode.workspace.onDidChangeTextDocument((event) => {
        if (event.document.languageId === 'powerscript') {
            validateDocument(event.document, diagnostics);
        }
    });
    // Listen for document opens
    const onDidOpenDocument = vscode.workspace.onDidOpenTextDocument((document) => {
        if (document.languageId === 'powerscript') {
            validateDocument(document, diagnostics);
        }
    });
    context.subscriptions.push(onDidChangeDocument, onDidOpenDocument);
}
async function validateDocument(document, diagnostics) {
    var _a;
    const diagnosticList = [];
    // Basic syntax validation
    const text = document.getText();
    const lines = text.split('\n');
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        // Check for common syntax errors
        if (line.includes('class ') && !line.includes('{') && !((_a = lines[i + 1]) === null || _a === void 0 ? void 0 : _a.includes('{'))) {
            const diagnostic = new vscode.Diagnostic(new vscode.Range(i, 0, i, line.length), 'Class declaration should be followed by opening brace', vscode.DiagnosticSeverity.Error);
            diagnosticList.push(diagnostic);
        }
        // Check for missing semicolons (optional but good practice)
        if (line.trim().match(/^(let|const|var)\s+\w+.*[^;{]$/) && !line.includes('//')) {
            const diagnostic = new vscode.Diagnostic(new vscode.Range(i, line.length - 1, i, line.length), 'Consider adding semicolon', vscode.DiagnosticSeverity.Information);
            diagnosticList.push(diagnostic);
        }
        // Check for undefined variables (basic check)
        const match = line.match(/let\s+(\w+):\s*(\w+)/);
        if (match) {
            const [, varName, typeName] = match;
            if (!['string', 'number', 'boolean', 'Hello'].includes(typeName)) {
                const typeIndex = line.indexOf(typeName);
                const diagnostic = new vscode.Diagnostic(new vscode.Range(i, typeIndex, i, typeIndex + typeName.length), `Unknown type: ${typeName}`, vscode.DiagnosticSeverity.Warning);
                diagnosticList.push(diagnostic);
            }
        }
    }
    diagnostics.set(document.uri, diagnosticList);
}
function deactivate() {
    if (!client) {
        return undefined;
    }
    return client.stop();
}
exports.deactivate = deactivate;
//# sourceMappingURL=extension.js.map