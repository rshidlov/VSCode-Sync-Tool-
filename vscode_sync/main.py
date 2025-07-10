"""Main CLI application for VSCode Sync Tool."""

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

import tempfile
import zipfile
import typer


from . import config
from . import presets

app = typer.Typer(help="VSCode Sync Tool: Export, import, and share your VSCode settings and extensions.")

IDE_CHOICE: Optional[str] = None


def select_ide() -> None:
    """Prompt the user to select which IDE CLI to use (VSCode or Cursor)."""
    # pylint: disable=global-statement
    global IDE_CHOICE
    vscode_installed = shutil.which("code") is not None
    cursor_installed = shutil.which("cursor") is not None
    if not vscode_installed and not cursor_installed:
        typer.echo("Error: Neither VSCode ('code') nor Cursor ('cursor') CLI is installed.")
        raise typer.Exit(code=1)
    if vscode_installed and not cursor_installed:
        IDE_CHOICE = "code"
        typer.echo("Using VSCode (code CLI).")
    elif cursor_installed and not vscode_installed:
        IDE_CHOICE = "cursor"
        typer.echo("Using Cursor (cursor CLI).")
    else:
        typer.echo("Both VSCode ('code') and Cursor ('cursor') are installed.")
        typer.echo("Which IDE would you like to use?")
        typer.echo("1. VSCode (code)")
        typer.echo("2. Cursor (cursor)")
        while True:
            choice = input("Enter 1 or 2: ").strip()
            if choice == "1":
                IDE_CHOICE = "code"
                break
            if choice == "2":
                IDE_CHOICE = "cursor"
                break
            typer.echo("Invalid choice. Please enter 1 or 2.")


def check_cli_tools() -> bool:
    """Check if the selected IDE CLI tool is available in PATH."""
    if IDE_CHOICE is None:
        select_ide()
    if IDE_CHOICE is not None and shutil.which(IDE_CHOICE) is None:
        typer.echo(f"Required CLI tool '{IDE_CHOICE}' not found in PATH.")
        if IDE_CHOICE == "code":
            typer.echo("To install the 'code' command:")
            typer.echo("  1. Open VSCode.")
            typer.echo("  2. Press Cmd+Shift+P and type 'Shell Command: Install 'code' command in PATH'.")
        elif IDE_CHOICE == "cursor":
            typer.echo("To install the 'cursor' command, follow the instructions for your environment.")
        if IDE_CHOICE == "code" and config.get_os() == "macos":
            typer.echo("Would you like to run the VSCode command to install 'code' in PATH? [y/N]")
            response = input().strip().lower()
            if response == "y":
                try:
                    subprocess.run(
                        [
                            "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code",
                            "--install-shell-command",
                        ],
                        check=True,
                    )
                    typer.echo("'code' command installed. Please restart your terminal and try again.")
                except (OSError, subprocess.SubprocessError) as e:
                    typer.echo(f"Failed to run install command: {e}")
            raise typer.Exit(code=1)
        typer.echo(f"Please install '{IDE_CHOICE}' and try again.")
        raise typer.Exit(code=1)
    return True


@app.command()
def status() -> None:
    """Show current VSCode or Cursor status."""
    if not check_cli_tools():
        return
    cli_ok = False
    if IDE_CHOICE is not None:
        try:
            assert IDE_CHOICE is not None
            result = subprocess.run([IDE_CHOICE, "--version"], capture_output=True, text=True, check=False)
            cli_ok = result.returncode == 0
        except FileNotFoundError:
            cli_ok = False
    typer.echo(f"{IDE_CHOICE} CLI: {'Found' if cli_ok else 'Not found'}")
    extensions: List[str] = []
    if cli_ok:
        assert IDE_CHOICE is not None
        ext_result = subprocess.run(
            [IDE_CHOICE, "--list-extensions"],
            capture_output=True,
            text=True,
            check=False,
        )
        if ext_result.returncode == 0:
            extensions = ext_result.stdout.strip().splitlines()
    typer.echo(f"Extensions installed: {len(extensions)}")
    settings_path = config.get_vscode_settings_path()
    if settings_path and Path(settings_path).exists():
        typer.echo(f"Settings file: {settings_path} (Found)")
    else:
        typer.echo("Settings file: Not found")


@app.command()
def export(
    output: str = typer.Argument(..., help="Path to the output ZIP file."),
    output_dir: Optional[str] = typer.Option(
        None, help="Directory to save intermediate files (default: temp dir)."
    ),
) -> None:
    """Export configuration to a ZIP file (JSON only, assumes all extensions are from the Marketplace)."""
    if not check_cli_tools():
        return
    try:
        assert IDE_CHOICE is not None
        ext_result = subprocess.run(
            [IDE_CHOICE, "--list-extensions"],
            capture_output=True,
            text=True,
            check=False,
        )
        extensions = ext_result.stdout.strip().splitlines() if ext_result.returncode == 0 else []
    except FileNotFoundError:
        typer.echo(f"{IDE_CHOICE} CLI not found. Cannot export extensions.")
        return
    settings_path = config.get_vscode_settings_path()
    settings: Dict[str, Any] = {}
    if settings_path and Path(settings_path).exists():
        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                settings = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            typer.echo(f"Failed to read settings: {e}")
    if output_dir:
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
    else:
        out_dir = Path(tempfile.mkdtemp())
    data = {
        "metadata": {
            "created_at": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
            "system": config.get_os().capitalize(),
            "vscode_sync_version": "0.1.0",
        },
        "extensions": extensions,
        "settings": settings,
    }
    json_path = Path(out_dir, "vscode_sync_export.json")
    try:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except (OSError, json.JSONDecodeError) as e:
        typer.echo(f"Failed to write export file: {e}")
        return
    output_final = Path(out_dir, output)
    with zipfile.ZipFile(output_final, "w") as zipf:
        zipf.write(json_path, arcname="vscode_sync_export.json")
    typer.echo(f"Exported configuration to {output_final}")


@app.command(name="import")
def import_(
    input_file: str,
    no_extensions: bool = typer.Option(False, help="Do not install extensions."),
    no_settings: bool = typer.Option(False, help="Do not update settings."),
    no_backup: bool = typer.Option(False, help="Do not backup current settings."),
) -> None:
    """Import configuration from a file (JSON or ZIP)."""
    if not check_cli_tools():
        return
    if not os.path.exists(input_file):
        typer.echo(f"Input file '{input_file}' not found.")
        raise typer.Exit(code=1)
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        typer.echo(f"Failed to read input file: {e}")
        raise typer.Exit(code=1)
    if not no_extensions:
        extensions = data.get("extensions", [])
        if extensions:
            typer.echo(f"Installing {len(extensions)} extensions...")
            for ext in extensions:
                typer.echo(f"Installing {ext}...")
                assert IDE_CHOICE is not None
                result = subprocess.run(
                    [IDE_CHOICE, "--install-extension", ext],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode == 0:
                    typer.echo(f"  Installed {ext}")
                else:
                    typer.echo(f"  Failed to install {ext}: {result.stderr.strip()}")
        else:
            typer.echo("No extensions to install.")
    else:
        typer.echo("Skipping extension installation (--no-extensions).")
    if not no_settings:
        settings = data.get("settings", {})
        settings_path = config.get_vscode_settings_path()
        if not settings_path:
            typer.echo("Could not determine settings path for this OS.")
            raise typer.Exit(code=1)
        if not no_backup and settings_path.exists():
            backup_path = settings_path.parent / "settings.backup.json"
            shutil.copy2(settings_path, backup_path)
            typer.echo(f"Backed up current settings to {backup_path}")
        try:
            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)
            typer.echo(f"Updated settings at {settings_path}")
        except (OSError, json.JSONDecodeError) as e:
            typer.echo(f"Failed to update settings: {e}")
    else:
        typer.echo("Skipping settings update (--no-settings).")


@app.command()
def wizard() -> None:
    """Interactive setup wizard for environment presets and customization."""
    if not check_cli_tools():
        return
    typer.echo("Welcome to the VSCode Sync Tool Wizard!")
    preset_names = list(presets.PRESETS.keys()) + ["Custom"]
    typer.echo("Select a development preset:")
    for idx, name in enumerate(preset_names, 1):
        typer.echo(f"{idx}. {name}")
    while True:
        choice = input(f"Enter 1-{len(preset_names)}: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(preset_names):
            preset_choice = preset_names[int(choice) - 1]
            break
        typer.echo("Invalid choice. Please enter a valid number.")
    if preset_choice == "Custom":
        extensions: List[str] = []
        settings: Dict[str, Any] = {}
    else:
        extensions = list(presets.PRESETS[preset_choice]["extensions"])
        settings = dict(presets.PRESETS[preset_choice]["settings"])
    typer.echo("\nExtensions:")
    for ext in extensions:
        typer.echo(f"  - {ext}")
    if input("Would you like to add/remove extensions? [y/N]: ").strip().lower() == "y":
        while True:
            action = input("Type 'add', 'remove', or 'done': ").strip().lower()
            if action == "add":
                new_ext = input("Enter extension id to add: ").strip()
                if new_ext and new_ext not in extensions:
                    extensions.append(new_ext)
                    typer.echo(f"Added {new_ext}.")
            elif action == "remove":
                rem_ext = input("Enter extension id to remove: ").strip()
                if rem_ext in extensions:
                    extensions.remove(rem_ext)
                    typer.echo(f"Removed {rem_ext}.")
            elif action == "done":
                break
            else:
                typer.echo("Invalid action.")
    typer.echo("\nSettings:")
    for k, v in settings.items():
        typer.echo(f"  {k}: {v}")
    if input("Would you like to add/edit settings? [y/N]: ").strip().lower() == "y":
        while True:
            key = input("Enter setting key (or 'done'): ").strip()
            if key == "done":
                break
            value_str = input(f"Enter value for {key}: ").strip()
            if value_str.lower() in ["true", "false"]:
                value: Any = value_str.lower() == "true"
            else:
                try:
                    value = int(value_str)
                except ValueError:
                    try:
                        value = float(value_str)
                    except ValueError:
                        value = value_str
            settings[key] = value
            typer.echo(f"Set {key} = {value}")
    typer.echo("\nSummary:")
    typer.echo(f"Extensions: {extensions}")
    typer.echo(f"Settings: {settings}")
    if input("Apply this configuration? [Y/n]: ").strip().lower() in ["", "y", "yes"]:
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as tmp:
            json.dump({"extensions": extensions, "settings": settings}, tmp, indent=2)
            tmp_path = tmp.name
        import_(__file__, no_extensions=False, no_settings=False, no_backup=False)
        os.unlink(tmp_path)
    else:
        typer.echo("Aborted. No changes made.")


@app.command()
def list_repos() -> None:
    """List all git repositories in recent workspaces/folders of the selected IDE."""
    if not check_cli_tools():
        return
    os_type = config.get_os()
    recent_paths: List[str] = []
    if IDE_CHOICE == "code":
        if os_type == "macos":
            recent_json: Optional[Path] = (
                Path.home() / "Library/Application Support/Code/User/globalStorage/storage.json"
            )
            recent_workspaces: Optional[Path] = Path.home() / "Library/Application Support/Code/storage.json"
        elif os_type == "windows":
            appdata = os.environ.get("APPDATA")
            if appdata:
                recent_json = Path(appdata) / "Code/User/globalStorage/storage.json"
                recent_workspaces = Path(appdata) / "Code/storage.json"
            else:
                recent_json = None
                recent_workspaces = None
        elif os_type == "linux":
            recent_json = Path.home() / ".config/Code/User/globalStorage/storage.json"
            recent_workspaces = Path.home() / ".config/Code/storage.json"
        else:
            recent_json = None
            recent_workspaces = None
        found = False
        for f in [recent_json, recent_workspaces]:
            if f and f.exists():
                try:
                    with open(f, "r", encoding="utf-8") as file:
                        data = json.load(file)
                        paths = data.get("openedPathsList", {}).get("workspaces3", [])
                        paths += data.get("openedPathsList", {}).get("entries", [])
                        for p in paths:
                            if os.path.isdir(p) and os.path.isdir(os.path.join(p, ".git")):
                                recent_paths.append(p)
                        found = True
                except (OSError, json.JSONDecodeError) as e:
                    typer.echo(f"Failed to parse {f}: {e}")
        if not found:
            typer.echo("Could not find or parse recent workspaces/folders for VSCode.")
    elif IDE_CHOICE == "cursor":
        typer.echo("Listing recent repos for Cursor is not yet implemented.")
        return
    if recent_paths:
        typer.echo("Recent Git repositories:")
        for p in recent_paths:
            typer.echo(f"- {p}")
    else:
        typer.echo("No recent Git repositories found.")


if __name__ == "__main__":
    app()
