#!/usr/bin/env python3
"""
VSCode Sync Tool - CLI Application
A cross-platform tool to export, import, and share VSCode settings and extensions.
"""

import os
import json
import platform
import subprocess
import zipfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich import print as rprint

app = typer.Typer(help="VSCode Sync Tool - Export, import, and share your VSCode setup")
console = Console()

class VSCodeSync:
    def __init__(self):
        self.system = platform.system()
        self.settings_path = self._get_settings_path()
        self.extensions_path = self._get_extensions_path()
        
    def _get_settings_path(self) -> Path:
        """Get the VSCode settings.json path for the current OS"""
        if self.system == "Darwin":  # macOS
            return Path.home() / "Library/Application Support/Code/User/settings.json"
        elif self.system == "Windows":
            return Path(os.getenv("APPDATA")) / "Code/User/settings.json"
        else:  # Linux
            return Path.home() / ".config/Code/User/settings.json"
    
    def _get_extensions_path(self) -> Path:
        """Get the VSCode extensions directory path"""
        if self.system == "Darwin":  # macOS
            return Path.home() / ".vscode/extensions"
        elif self.system == "Windows":
            return Path(os.getenv("USERPROFILE")) / ".vscode/extensions"
        else:  # Linux
            return Path.home() / ".vscode/extensions"
    
    def _check_vscode_installed(self) -> bool:
        """Check if VSCode CLI is available"""
        try:
            result = subprocess.run(["code", "--version"], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def get_installed_extensions(self) -> List[str]:
        """Get list of installed VSCode extensions"""
        if not self._check_vscode_installed():
            console.print("[red]VSCode CLI not found. Please install VSCode and ensure 'code' command is available.[/red]")
            return []
        
        try:
            result = subprocess.run(["code", "--list-extensions"], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return [ext.strip() for ext in result.stdout.strip().split('\n') if ext.strip()]
            else:
                console.print(f"[red]Error getting extensions: {result.stderr}[/red]")
                return []
        except subprocess.TimeoutExpired:
            console.print("[red]Timeout getting extensions list[/red]")
            return []
    
    def get_settings(self) -> Dict:
        """Read VSCode settings.json"""
        if not self.settings_path.exists():
            console.print(f"[yellow]Settings file not found at {self.settings_path}[/yellow]")
            return {}
        
        try:
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            console.print(f"[red]Error reading settings: {e}[/red]")
            return {}
        except Exception as e:
            console.print(f"[red]Error accessing settings: {e}[/red]")
            return {}
    
    def export_config(self, output_path: str, include_settings: bool = True) -> bool:
        """Export VSCode configuration to a file"""
        extensions = self.get_installed_extensions()
        if not extensions:
            console.print("[yellow]No extensions found to export[/yellow]")
        
        settings = self.get_settings() if include_settings else {}
        
        config = {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "system": self.system,
                "vscode_sync_version": "1.0.0"
            },
            "extensions": extensions,
            "settings": settings
        }
        
        try:
            output_file = Path(output_path)
            if output_file.suffix.lower() == '.zip':
                return self._export_to_zip(config, output_file)
            else:
                return self._export_to_json(config, output_file)
        except Exception as e:
            console.print(f"[red]Export failed: {e}[/red]")
            return False
    
    def _export_to_json(self, config: Dict, output_file: Path) -> bool:
        """Export configuration to JSON file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            console.print(f"[green]✓ Configuration exported to {output_file}[/green]")
            return True
        except Exception as e:
            console.print(f"[red]Failed to write JSON: {e}[/red]")
            return False
    
    def _export_to_zip(self, config: Dict, output_file: Path) -> bool:
        """Export configuration to ZIP file"""
        try:
            with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
                # Add config as JSON
                zf.writestr('vscode_config.json', json.dumps(config, indent=2))
                
                # Add settings file if it exists
                if self.settings_path.exists():
                    zf.write(self.settings_path, 'settings.json')
            
            console.print(f"[green]✓ Configuration exported to {output_file}[/green]")
            return True
        except Exception as e:
            console.print(f"[red]Failed to create ZIP: {e}[/red]")
            return False
    
    def import_config(self, input_path: str, install_extensions: bool = True, 
                     update_settings: bool = True, backup: bool = True) -> bool:
        """Import VSCode configuration from a file"""
        input_file = Path(input_path)
        
        if not input_file.exists():
            console.print(f"[red]Input file not found: {input_file}[/red]")
            return False
        
        try:
            if input_file.suffix.lower() == '.zip':
                config = self._import_from_zip(input_file)
            else:
                config = self._import_from_json(input_file)
            
            if not config:
                return False
            
            # Backup current settings if requested
            if backup and self.settings_path.exists():
                backup_path = self.settings_path.with_suffix('.backup.json')
                shutil.copy2(self.settings_path, backup_path)
                console.print(f"[blue]Settings backed up to {backup_path}[/blue]")
            
            success = True
            
            # Install extensions
            if install_extensions and config.get('extensions'):
                success &= self._install_extensions(config['extensions'])
            
            # Update settings
            if update_settings and config.get('settings'):
                success &= self._update_settings(config['settings'])
            
            return success
            
        except Exception as e:
            console.print(f"[red]Import failed: {e}[/red]")
            return False
    
    def _import_from_json(self, input_file: Path) -> Optional[Dict]:
        """Import configuration from JSON file"""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            console.print(f"[red]Invalid JSON file: {e}[/red]")
            return None
        except Exception as e:
            console.print(f"[red]Error reading file: {e}[/red]")
            return None
    
    def _import_from_zip(self, input_file: Path) -> Optional[Dict]:
        """Import configuration from ZIP file"""
        try:
            with zipfile.ZipFile(input_file, 'r') as zf:
                config_data = zf.read('vscode_config.json')
                return json.loads(config_data.decode('utf-8'))
        except Exception as e:
            console.print(f"[red]Error reading ZIP file: {e}[/red]")
            return None
    
    def _install_extensions(self, extensions: List[str]) -> bool:
        """Install VSCode extensions"""
        if not self._check_vscode_installed():
            console.print("[red]VSCode CLI not available for installing extensions[/red]")
            return False
        
        if not extensions:
            console.print("[yellow]No extensions to install[/yellow]")
            return True
        
        console.print(f"[blue]Installing {len(extensions)} extensions...[/blue]")
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Installing extensions...", total=len(extensions))
            
            failed = []
            for ext in extensions:
                progress.update(task, description=f"Installing {ext}...")
                try:
                    result = subprocess.run(["code", "--install-extension", ext], 
                                          capture_output=True, text=True, timeout=60)
                    if result.returncode != 0:
                        failed.append(ext)
                        console.print(f"[red]Failed to install {ext}: {result.stderr.strip()}[/red]")
                except subprocess.TimeoutExpired:
                    failed.append(ext)
                    console.print(f"[red]Timeout installing {ext}[/red]")
                
                progress.advance(task)
        
        if failed:
            console.print(f"[yellow]Failed to install {len(failed)} extensions[/yellow]")
            return False
        else:
            console.print(f"[green]✓ Successfully installed {len(extensions)} extensions[/green]")
            return True
    
    def _update_settings(self, settings: Dict) -> bool:
        """Update VSCode settings"""
        try:
            # Ensure the directory exists
            self.settings_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            
            console.print(f"[green]✓ Settings updated at {self.settings_path}[/green]")
            return True
        except Exception as e:
            console.print(f"[red]Failed to update settings: {e}[/red]")
            return False
    
    def show_status(self):
        """Show current VSCode configuration status"""
        table = Table(title="VSCode Configuration Status")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="magenta")
        table.add_column("Details", style="green")
        
        # VSCode CLI
        vscode_status = "✓ Available" if self._check_vscode_installed() else "✗ Not Available"
        table.add_row("VSCode CLI", vscode_status, "code --version")
        
        # Settings
        settings_status = "✓ Found" if self.settings_path.exists() else "✗ Not Found"
        table.add_row("Settings", settings_status, str(self.settings_path))
        
        # Extensions
        extensions = self.get_installed_extensions()
        ext_status = f"✓ {len(extensions)} installed" if extensions else "✗ None found"
        table.add_row("Extensions", ext_status, f"{len(extensions)} extensions")
        
        console.print(table)
        
        if extensions:
            console.print("\n[bold]Installed Extensions:[/bold]")
            for ext in extensions[:10]:  # Show first 10
                console.print(f"  • {ext}")
            if len(extensions) > 10:
                console.print(f"  ... and {len(extensions) - 10} more")


# CLI Commands
@app.command()
def export(
    output: str = typer.Argument(..., help="Output file path (.json or .zip)"),
    no_settings: bool = typer.Option(False, "--no-settings", help="Don't include settings"),
):
    """Export VSCode configuration to a file"""
    sync = VSCodeSync()
    
    include_settings = not no_settings
    if sync.export_config(output, include_settings):
        console.print("[green]✓ Export completed successfully![/green]")
    else:
        console.print("[red]✗ Export failed![/red]")
        raise typer.Exit(1)


@app.command()
def import_cmd(
    input_path: str = typer.Argument(..., help="Input file path"),
    no_extensions: bool = typer.Option(False, "--no-extensions", help="Don't install extensions"),
    no_settings: bool = typer.Option(False, "--no-settings", help="Don't update settings"),
    no_backup: bool = typer.Option(False, "--no-backup", help="Don't backup current settings"),
):
    """Import VSCode configuration from a file"""
    sync = VSCodeSync()
    
    install_extensions = not no_extensions
    update_settings = not no_settings
    backup = not no_backup
    
    if not no_backup and sync.settings_path.exists():
        if not Confirm.ask("This will modify your current VSCode settings. Continue?"):
            console.print("[yellow]Import cancelled[/yellow]")
            return
    
    if sync.import_config(input_path, install_extensions, update_settings, backup):
        console.print("[green]✓ Import completed successfully![/green]")
    else:
        console.print("[red]✗ Import failed![/red]")
        raise typer.Exit(1)


@app.command()
def status():
    """Show current VSCode configuration status"""
    sync = VSCodeSync()
    sync.show_status()


@app.command()
def wizard():
    """Interactive setup wizard"""
    console.print("[bold blue]VSCode Sync Setup Wizard[/bold blue]")
    console.print("This wizard will help you set up a VSCode configuration based on your development needs.\n")
    
    # Basic questions
    dev_type = Prompt.ask(
        "What type of development do you primarily do?",
        choices=["frontend", "backend", "fullstack", "data-science", "mobile", "other"],
        default="fullstack"
    )
    
    languages = Prompt.ask(
        "What programming languages do you use? (comma-separated)",
        default="javascript,python,typescript"
    ).split(",")
    
    # Generate recommended extensions based on answers
    recommendations = get_recommendations(dev_type, [lang.strip() for lang in languages])
    
    console.print(f"\n[bold]Recommended extensions for {dev_type} development:[/bold]")
    for ext in recommendations:
        console.print(f"  • {ext}")
    
    if Confirm.ask("\nWould you like to save this as a preset?"):
        preset_name = Prompt.ask("Enter preset name", default=f"{dev_type}-preset")
        save_preset(preset_name, dev_type, languages, recommendations)
        console.print(f"[green]✓ Preset '{preset_name}' saved![/green]")


def get_recommendations(dev_type: str, languages: List[str]) -> List[str]:
    """Get extension recommendations based on development type and languages"""
    base_extensions = [
        "ms-vscode.vscode-typescript-next",
        "esbenp.prettier-vscode",
        "bradlc.vscode-tailwindcss",
        "ms-python.python",
        "ms-vscode.powershell",
        "ms-vscode.vscode-json",
        "redhat.vscode-yaml",
        "ms-vscode.vscode-eslint"
    ]
    
    type_extensions = {
        "frontend": [
            "formulahendry.auto-rename-tag",
            "christian-kohler.npm-intellisense",
            "ms-vscode.vscode-css-peek",
            "ritwick.reactjs-code-snippets"
        ],
        "backend": [
            "ms-python.python",
            "ms-vscode.vscode-docker",
            "ms-vscode.vscode-restclient",
            "humao.rest-client"
        ],
        "data-science": [
            "ms-python.python",
            "ms-toolsai.jupyter",
            "ms-python.vscode-pylance",
            "ms-toolsai.vscode-jupyter-cell-tags"
        ],
        "mobile": [
            "dart-code.dart-code",
            "dart-code.flutter",
            "ms-vscode.vscode-react-native"
        ]
    }
    
    extensions = base_extensions.copy()
    extensions.extend(type_extensions.get(dev_type, []))
    
    return list(set(extensions))  # Remove duplicates


def save_preset(name: str, dev_type: str, languages: List[str], extensions: List[str]):
    """Save a preset configuration"""
    presets_dir = Path.home() / ".vscode-sync" / "presets"
    presets_dir.mkdir(parents=True, exist_ok=True)
    
    preset = {
        "name": name,
        "dev_type": dev_type,
        "languages": languages,
        "extensions": extensions,
        "created_at": datetime.now().isoformat()
    }
    
    preset_file = presets_dir / f"{name}.json"
    with open(preset_file, 'w', encoding='utf-8') as f:
        json.dump(preset, f, indent=2)


if __name__ == "__main__":
    app()
