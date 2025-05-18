const fs = require('fs');
const path = require('path');
const { parse } = require('@babel/parser');
const traverse = require('@babel/traverse').default;
const generate = require('@babel/generator').default;
const t = require('@babel/types'); // Babel types

function injectPlaceholders(htmlFilePath, outputFilePath, copyToDestination, placeholders) {
    let updateStatus = placeholders.reduce((acc, placeholder) => {
        acc[placeholder.name] = false;
        return acc;
    }, {});

    if (fs.existsSync(outputFilePath)) {
        fs.unlinkSync(outputFilePath);
    }

    // Read HTML file
    let htmlContent = fs.readFileSync(htmlFilePath, 'utf8');

    // Extract <script> blocks (assumes there is one module script)
    const scriptRegex = /<script type="module"[^>]*>([\s\S]*?)<\/script>/g;
    let match;
    let newHtmlContent = htmlContent;

    while ((match = scriptRegex.exec(htmlContent)) !== null) {
        let scriptContent = match[1]; // Extracted JavaScript
        const scriptStartIndex = match.index + match[0].indexOf(scriptContent);
        const scriptEndIndex = scriptStartIndex + scriptContent.length;

        // Parse JavaScript into an AST
        let ast = parse(scriptContent, { sourceType: 'module' });

        // Traverse the AST to find and update specific constants
        traverse(ast, {
            VariableDeclarator(path) {
                if (t.isIdentifier(path.node.id)) {
                    placeholders.forEach(placeholder => {
                        if (path.node.id.name === placeholder.name) {
                            path.node.init = t.valueToNode(placeholder.value);
                            updateStatus[placeholder.name] = true;
                        }
                    });
                }
            }
        });

        // Generate modified JavaScript
        let modifiedScript = generate(ast).code;

        // Replace the script in the original HTML
        newHtmlContent =
            newHtmlContent.substring(0, scriptStartIndex) +
            modifiedScript +
            newHtmlContent.substring(scriptEndIndex);
    }

    // Check if all updates were made
    const allUpdated = Object.values(updateStatus).every(status => status);
    if (!allUpdated) {
        throw new Error('Failed to update all placeholders: ' + JSON.stringify(updateStatus));
    }

    // Save the modified HTML file
    fs.writeFileSync(outputFilePath, newHtmlContent, 'utf8');

    console.log(`HTML file updated successfully, ${outputFilePath} template created.`);

    fs.copyFileSync(outputFilePath, path.join(copyToDestination, path.basename(outputFilePath)));
}

module.exports = injectPlaceholders;
