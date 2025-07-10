"""
Configuration management for VSCode Sync Tool
"""

import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class SyncConfig:
    """Configuration class for VSCode Sync Tool"""

    # Paths
    config_dir: Path = Path.home() / ".vscode-sync"
    presets_dir: Path = config_dir / "presets"
    backup_dir: Path = config_dir / "backups"

    # Settings
    auto_backup: bool = True
    backup_retention_days: int = 30
    default_export_format: str = "json"  # json or zip

    # CLI settings
    confirm_destructive_actions: bool = True
    show_progress: bool = True
    verbose: bool = False

    def __post_init__(self):
        """Ensure directories exist"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.presets_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> 'SyncConfig':
        """Load configuration from file"""
        if config_path is None:
            config_path = cls().config_dir / "config.json"

        if not config_path.exists():
            return cls()

        try:
            with open(config_path, 'r') as f:
                data = json.load(f)

            # Convert path strings back to Path objects
            for key in ['config_dir', 'presets_dir', 'backup_dir']:
                if key in data:
                    data[key] = Path(data[key])

            return cls(**data)
        except Exception:
            return cls()

    def save(self, config_path: Optional[Path] = None):
        """Save configuration to file"""
        if config_path is None:
            config_path = self.config_dir / "config.json"

        # Convert Path objects to strings for JSON serialization
        data = asdict(self)
        for key in ['config_dir', 'presets_dir', 'backup_dir']:
            if key in data:
                data[key] = str(data[key])

        with open(config_path, 'w') as f:
            json.dump(data, f, indent=2)


class ConfigManager:
    """Manages configuration for VSCode Sync Tool"""

    def __init__(self, config_path: Optional[Path] = None):
        self.config = SyncConfig.load(config_path)

    def get_preset_path(self, name: str) -> Path:
        """Get path for a preset file"""
        return self.config.presets_dir / f"{name}.json"

    def get_backup_path(self, timestamp: Optional[str] = None) -> Path:
        """Get path for a backup file"""
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.config.backup_dir / f"backup_{timestamp}.json"

    def list_presets(self) -> list[str]:
        """List available presets"""
        return [f.stem for f in self.config.presets_dir.glob("*.json")]

    def list_backups(self) -> list[str]:
        """List available backups"""
        return [f.stem for f in self.config.backup_dir.glob("backup_*.json")]

    def cleanup_old_backups(self):
        """Remove old backup files"""
        cutoff_date = datetime.now().timestamp() - (self.config.backup_retention_days * 86400)

        for backup_file in self.config.backup_dir.glob("backup_*.json"):
            if backup_file.stat().st_mtime < cutoff_date:
                backup_file.unlink()
