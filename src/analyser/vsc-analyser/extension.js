// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
const vscode = require('vscode');
const path = require('path');
const fs = require('fs');

// this method is called when your extension is activated
// your extension is activated the very first time the command is executed
/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {

    // Use the console to output diagnostic information (console.log) and errors (console.error)
    // This line of code will only be executed once when your extension is activated
    const command_id = 'vsc-analyser.analyze';
    // The command has been defined in the package.json file
    // Now provide the implementation of the command with  registerCommand
    // The commandId parameter must match the command field in package.json
    let disposable = vscode.commands.registerCommand(command_id, function () {
        try {
            var file_name = vscode.window.activeTextEditor.document.fileName;
            var language_id = vscode.window.activeTextEditor.document.languageId;
            if (language_id !== "plaintext") {
                throw file_name;
            }
        } catch (e) {
            vscode.window.showInformationMessage(`${e} may not be a record file.`);
            return;
        }
        var content = vscode.window.activeTextEditor.document.getText();
        const panel = vscode.window.createWebviewPanel(
            "resultsWebview",
            `Record file ${file_name}`,
            vscode.ViewColumn.Active,
            {
                enableScripts: true,
                retainContextWhenHidden: false
            }
        );
        function getWebViewContent(context, templatePath) {
            const resourcePath = path.join(context.extensionPath, templatePath);
            const dirPath = path.dirname(resourcePath);
            let html = fs.readFileSync(resourcePath, 'utf-8');
            html = html.replace(/(<link.+?href="|<script.+?src="|<img.+?src=")(.+?)"/g, (m, $1, $2) => {
                return $1 + vscode.Uri.file(path.resolve(dirPath, $2)).with({ scheme: 'vscode-resource' }).toString() + '"';
            });
            return html;
        }
        panel.webview.html = getWebViewContent(context, "index.html");

        panel.webview.postMessage({
            command: "reload",
            record: content
        });
    });

    context.subscriptions.push(disposable);

    let status_bar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    status_bar.command = command_id;
    context.subscriptions.push(status_bar);
    status_bar.text = "2048 analysis";
    status_bar.show();

}
exports.activate = activate;

// this method is called when your extension is deactivated
function deactivate() { }

module.exports = {
    activate,
    deactivate
}
