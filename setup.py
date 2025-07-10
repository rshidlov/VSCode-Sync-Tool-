"""Setup script for VSCode Sync Tool."""
from setuptools import setup, find_packages

setup(
    name="vscode-sync",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "typer",
        "rich"
    ],
    entry_points={
        "console_scripts": [
            "vscode-sync = vscode_sync.main:app"
        ]
    },
    author="Shidlo",
    description="VSCode Sync Tool: Export, import, and share your VSCode settings and extensions.",
    license="MIT",
)
