import sys
import os
from pathlib import Path
from vscode_sync import config


def test_get_os(monkeypatch):
    monkeypatch.setattr(sys, "platform", "darwin")
    assert config.get_os() == "macos"
    monkeypatch.setattr(sys, "platform", "win32")
    assert config.get_os() == "windows"
    monkeypatch.setattr(sys, "platform", "linux")
    assert config.get_os() == "linux"
    monkeypatch.setattr(sys, "platform", "somerandomos")
    assert config.get_os() == "unknown"


def test_get_vscode_settings_path_macos(monkeypatch):
    monkeypatch.setattr(config, "get_os", lambda: "macos")
    path = config.get_vscode_settings_path()
    assert isinstance(path, Path)
    assert "Library/Application Support/Code/User/settings.json" in str(path)


def test_get_vscode_settings_path_windows(monkeypatch):
    monkeypatch.setattr(config, "get_os", lambda: "windows")
    monkeypatch.setitem(os.environ, "APPDATA", "C:/Users/test/AppData/Roaming")
    path = config.get_vscode_settings_path()
    assert isinstance(path, Path)
    assert "Code/User/settings.json" in str(path)


def test_get_vscode_settings_path_windows_no_appdata(monkeypatch):
    monkeypatch.setattr(config, "get_os", lambda: "windows")
    if "APPDATA" in os.environ:
        del os.environ["APPDATA"]
    path = config.get_vscode_settings_path()
    assert path is None


def test_get_vscode_settings_path_linux(monkeypatch):
    monkeypatch.setattr(config, "get_os", lambda: "linux")
    path = config.get_vscode_settings_path()
    assert isinstance(path, Path)
    assert ".config/Code/User/settings.json" in str(path)


def test_get_vscode_settings_path_unknown(monkeypatch):
    monkeypatch.setattr(config, "get_os", lambda: "unknown")
    path = config.get_vscode_settings_path()
    assert path is None
