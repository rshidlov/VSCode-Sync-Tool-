# VSCode Sync Tool

Export, import, and share your VSCode (or Cursor) settings and extensions easily across machines and teams.

## Features
- Export your VSCode/Cursor extensions and settings to a file
- Import and apply settings/extensions from a file
- Interactive setup wizard for environment presets
- List recent Git repositories from your IDE

## Installation
1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd VSCode-Sync-Tool-
   ```
2. (Recommended) Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
Run the CLI tool using:
```bash
python -m vscode_sync.main [COMMAND]
```
Or, if installed as a package:
```bash
vscode-sync [COMMAND]
```

### Available Commands
- `status`         Show current VSCode or Cursor status
- `export`         Export configuration to a file (JSON or ZIP)
- `import`         Import configuration from a file
- `wizard`         Interactive setup wizard
- `list-repos`     List recent Git repositories

For help on a command:
```bash
vscode-sync [COMMAND] --help
```

## Development & Testing
- Install dev dependencies:
  ```bash
  pip install -r requirements-dev.txt
  ```
- Run tests:
  ```bash
  pytest
  ```
- Lint code:
  ```bash
  flake8 vscode_sync tests
  ```

## Contributing
Pull requests and issues are welcome! Please lint and test your code before submitting.

## License
MIT License 