# VSCode Sync Tool

A cross-platform CLI tool to export, import, and share your VSCode settings and extensions across devices.

## Features

- **Export** VSCode configuration (extensions + settings) to JSON or ZIP files
- **Import** configurations to quickly set up VSCode on new machines
- **Interactive wizard** for setting up development environments
- **Cross-platform** support (Windows, macOS, Linux)
- **Backup** existing settings before importing
- **Preset management** for different development stacks

## Installation

### From Source

```bash
git clone https://github.com/rshidlov/VSCode-Sync-Tool-.git
cd vscode-sync
pip install -r requirements.txt
python -m vscode_sync.main --help
```

### Build Standalone Executable

```bash
python build.py
```

This will create a standalone executable in the `dist` folder.

## Usage

### Basic Commands

```bash
# Show current VSCode status
vscode-sync status

# Export configuration to JSON
vscode-sync export my-config.json

# Export configuration to ZIP (includes settings file)
vscode-sync export my-config.zip

# Import configuration
vscode-sync import my-config.json

# Interactive setup wizard
vscode-sync wizard
```

### Advanced Usage

```bash
# Export without settings (extensions only)
vscode-sync export --no-settings extensions-only.json

# Import without installing extensions
vscode-sync import --no-extensions my-config.json

# Import without updating settings
vscode-sync import --no-settings my-config.json

# Import without backing up current settings
vscode-sync import --no-backup my-config.json
```

## Configuration File Format

The tool exports configurations in the following JSON format:

```json
{
  "metadata": {
    "created_at": "2025-01-15T10:30:00",
    "system": "Darwin",
    "vscode_sync_version": "1.0.0"
  },
  "extensions": [
    "ms-python.python",
    "ms-vscode.vscode-typescript-next",
    "esbenp.prettier-vscode"
  ],
  "settings": {
    "editor.fontSize": 14,
    "workbench.colorTheme": "Dark+ (default dark)",
    "editor.formatOnSave": true
  }
}
```

## Development Presets

The wizard supports creating presets for different development environments:

- **Frontend**: React, Vue, Angular development
- **Backend**: Node.js, Python, API development
- **Full-stack**: Complete web development setup
- **Data Science**: Python, Jupyter, ML libraries
- **Mobile**: Flutter, React Native development

## Requirements

- Python 3.8 or higher
- VSCode with CLI tools installed (`code` command available)
- Internet connection for extension installation

## VSCode CLI Setup

Make sure the `code` command is available in your terminal:

### Windows
- Install VSCode
- During installation, check "Add to PATH" option
- Or manually add VSCode to your PATH

### macOS
- Install VSCode
- Open VSCode → Command Palette (Cmd+Shift+P)
- Type "Shell Command: Install 'code' command in PATH"

### Linux
- Install VSCode via package manager or snap
- The `code` command should be available automatically

## File Locations

The tool automatically detects VSCode settings based on your OS:

- **macOS**: `~/Library/Application Support/Code/User/settings.json`
- **Windows**: `%APPDATA%\\Code\\User\\settings.json`
- **Linux**: `~/.config/Code/User/settings.json`

## Troubleshooting

### "VSCode CLI not found" Error

This means the `code` command is not available in your terminal:

1. **Check if VSCode is installed**: Try running `code --version`
2. **Add to PATH**: Follow the VSCode CLI setup instructions above
3. **Restart terminal**: After adding to PATH, restart your terminal
4. **Alternative**: Use the full path to the VSCode executable

### "Permission denied" Error

On Unix systems, you might need to make the executable file executable:

```bash
chmod +x vscode-sync
```

### Extensions fail to install

1. **Check internet connection**: Extension installation requires internet
2. **VSCode marketplace access**: Ensure you can access the VSCode marketplace
3. **Extension already installed**: Some extensions might already be installed
4. **Retry**: Try running the import command again

### Settings not found

1. **Check VSCode installation**: Make sure VSCode is properly installed
2. **Create settings**: Open VSCode and change some settings to create the settings.json file
3. **Manual path**: Check if settings.json exists in the expected location

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Roadmap

### Phase 1 (Current) - MVP CLI Tool
- [x] Export/import functionality
- [x] Cross-platform support
- [x] Interactive wizard
- [x] Preset management
- [x] Settings backup

### Phase 2 - Web Interface
- [ ] Next.js web application
- [ ] Cloud storage integration
- [ ] User accounts and authentication
- [ ] Public preset sharing
- [ ] Team collaboration features

### Phase 3 - Advanced Features
- [ ] VSCode extension integration
- [ ] Automatic sync
- [ ] Git integration
- [ ] Advanced preset templates
- [ ] Analytics and insights

## License

MIT License - see LICENSE file for details

## Support

- Create an issue on GitHub for bug reports
- Feature requests are welcome
- Check existing issues before creating new ones

## Technical Details

### Architecture

```
vscode-sync/
├── vscode_sync/
│   ├── __init__.py
│   ├── main.py          # Main CLI application
│   ├── config.py        # Configuration management
│   └── presets.py       # Preset handling
├── requirements.txt     # Python dependencies
├── setup.py            # Package setup
├── build.py            # Build script
└── vscode-sync.spec    # PyInstaller spec
```

### Dependencies

- **typer**: Modern CLI framework with type hints
- **rich**: Beautiful terminal output and progress bars
- **pathlib**: Cross-platform path handling
- **subprocess**: VSCode CLI interaction
- **json**: Configuration file handling
- **zipfile**: Archive creation and extraction

### Build Process

The build script (`build.py`) handles:
1. Dependency installation
2. PyInstaller setup
3. Executable creation
4. Distribution packaging
5. Cross-platform compatibility

### Testing

Run tests with:

```bash
python -m pytest tests/
```

### Code Style

The project follows PEP 8 style guidelines:

```bash
# Format code
black vscode_sync/

# Check linting
flake8 vscode_sync/

# Type checking
mypy vscode_sync/
```

## FAQ

**Q: Can I sync across different operating systems?**
A: Yes! The tool works across Windows, macOS, and Linux. Extensions are cross-platform, though some OS-specific settings might need adjustment.

**Q: Are my settings stored in the cloud?**
A: In Phase 1, everything is local. Cloud sync will be added in Phase 2.

**Q: Can I share presets with my team?**
A: Currently, you can share the exported JSON/ZIP files manually. Team features will be added in Phase 2.

**Q: Does this work with VSCode forks (like Codium)?**
A: It should work with any VSCode-compatible editor that uses the same settings format and CLI commands.

**Q: How do I update the tool?**
A: For now, download the latest release. Auto-update functionality will be added in future versions.

**Q: Can I exclude certain extensions from export?**
A: This feature is planned for a future release. Currently, all extensions are included.

---

Made with ❤️ by Roei Shidlovsky