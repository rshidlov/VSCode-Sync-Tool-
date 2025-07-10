from typer.testing import CliRunner
from vscode_sync.main import app


def test_cli_commands_exist():
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "VSCode Sync Tool" in result.output
    # Check for at least one command
    for command in ["status", "export", "import", "wizard", "list-repos"]:
        assert command.replace("_", "-") in result.output or command in result.output
