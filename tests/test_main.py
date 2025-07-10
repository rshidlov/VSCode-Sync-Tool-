import json
import builtins
import zipfile
from pathlib import Path
from typer.testing import CliRunner
from vscode_sync.main import app


def test_cli_commands_exist():
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "VSCode Sync Tool" in result.output
    for command in ["status", "export", "import", "wizard", "list-repos"]:
        assert command.replace("_", "-") in result.output or command in result.output


def test_export_and_import(tmp_path, monkeypatch):
    runner = CliRunner()
    monkeypatch.setattr("vscode_sync.main.check_cli_tools", lambda: True)
    monkeypatch.setattr("vscode_sync.main.IDE_CHOICE", "code")
    monkeypatch.setattr(
        "vscode_sync.main.subprocess.run",
        lambda *a, **kw: type(
            "Result", (), {"stdout": "ms-python.python\neamodio.gitlens", "returncode": 0, "stderr": ""}
        )(),
    )
    monkeypatch.setattr("vscode_sync.config.get_vscode_settings_path", lambda: tmp_path / "settings.json")
    settings = {"editor.fontSize": 14}
    with open(Path(tmp_path, "settings.json"), "w", encoding="utf-8") as f:
        json.dump(settings, f)
    export_zip = tmp_path / "export.zip"
    result = runner.invoke(app, ["export", str(export_zip), "--output-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "Exported configuration" in result.output
    with zipfile.ZipFile(export_zip, "r") as zipf:
        zipf.extractall(tmp_path)
    export_json = tmp_path / "vscode_sync_export.json"
    assert export_json.exists()
    result = runner.invoke(app, ["import", str(export_json)])
    assert result.exit_code == 0
    assert "Installing 2 extensions" in result.output
    assert "Updated settings" in result.output


def test_import_missing_file(monkeypatch):
    runner = CliRunner()
    monkeypatch.setattr(builtins, "input", lambda *a, **kw: "1")
    monkeypatch.setattr("vscode_sync.main.IDE_CHOICE", "code")
    monkeypatch.setattr("vscode_sync.main.check_cli_tools", lambda: True)
    result = runner.invoke(app, ["import", "nonexistent.json"])
    assert result.exit_code != 0
    assert "not found" in result.output or "No such file" in result.output


def test_import_invalid_json(tmp_path, monkeypatch):
    runner = CliRunner()
    monkeypatch.setattr(builtins, "input", lambda *a, **kw: "1")
    monkeypatch.setattr("vscode_sync.main.IDE_CHOICE", "code")
    monkeypatch.setattr("vscode_sync.main.check_cli_tools", lambda: True)
    bad_json = tmp_path / "bad.json"
    with open(bad_json, "w", encoding="utf-8") as f:
        f.write("not a json")
    result = runner.invoke(app, ["import", str(bad_json)])
    assert result.exit_code != 0
    assert "Failed to read input file" in result.output
