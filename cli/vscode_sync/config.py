"""Configuration management for VSCode Sync Tool."""

import sys
import os
from pathlib import Path
from typing import Optional


def get_os() -> str:
    """Detect the current operating system (macos, windows, linux, or unknown)."""
    if sys.platform.startswith("darwin"):
        return "macos"
    if sys.platform.startswith("win"):
        return "windows"
    if sys.platform.startswith("linux"):
        return "linux"
    return "unknown"


def get_vscode_settings_path() -> Optional[Path]:
    """Get the path to the VSCode settings.json file for the current OS."""
    os_type = get_os()
    if os_type == "macos":
        return Path.home() / "Library/Application Support/Code/User/settings.json"
    if os_type == "windows":
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "Code/User/settings.json"
        return None
    if os_type == "linux":
        return Path.home() / ".config/Code/User/settings.json"
    return None
