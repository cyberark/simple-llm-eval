# Debugging Simpleval 🐞

### vscode Debug settings

Example for configuring vscode to debug a run command overwriting existing results:

Filename: `launch.json`
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug simpleval",
      "type": "debugpy",
      "request": "launch",
      "program": "${workspaceFolder}/simpleval/main.py",
      "console": "integratedTerminal",
      "args": [
        "run",
        "-e",
        "simpleval/eval_sets/user-actions-by-events",
        "-t",
        "sonnet35",
        "-o",
      ]
    }
  ]
}
```

### JetBrains Debug settings
Download and install vscode: https://code.visualstudio.com/
<BR>Just kidding 😜, you got this! just run debug for the `simpleval/main.py` with the needed args.

<br>
