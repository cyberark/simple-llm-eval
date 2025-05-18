# Debugging Handlers 🐞

If you're using this library as a consumer and you want to debug your handler, you need to run the simpleval `main.py` file with the command line args.

This file resides in: 

` "${workspaceFolder}/.venv/lib/python3.11/site-packages/simpleval/main.py"`

!!! info
    * update the path to .venv according to your actual one.
    * `${workspaceFolder}` - is specific to vscode, so change it according to your IDE
    * replace `python3.11` with your version
    * add args as needed.


## vscode debug settings

Update args as you wish

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug simpleval",
      "type": "debugpy",
      "request": "launch",
      "program": "${workspaceFolder}/.venv/lib/python3.11/site-packages/simpleval/main.py",
      "console": "integratedTerminal",
      "args": [
        "run",
        "-e",
        "eval_set/user-actions-by-events",
        "-t",
        "sonnet35",
        "-o",
      ]
    }
  ]
}
```

## Other IDEs
Other IDEs are a little different, but the idea is the same, debug `main.py` in said path with the command line args.

<br>
