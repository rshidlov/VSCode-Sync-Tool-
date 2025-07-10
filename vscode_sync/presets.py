"""Presets for VSCode Sync Tool.

TODO: In the future, obtain these presets dynamically, maybe even using an AI query.
"""
from typing import Dict, Any

PRESETS: Dict[str, Dict[str, Any]] = {
    "Frontend": {
        "extensions": [
            "dbaeumer.vscode-eslint",
            "esbenp.prettier-vscode",
            "msjsdiag.debugger-for-chrome",
            "formulahendry.auto-close-tag",
            "formulahendry.auto-rename-tag",
            "eamodio.gitlens",
        ],
        "settings": {
            "editor.formatOnSave": True,
            "files.autoSave": "afterDelay",
        },
    },
    "Backend": {
        "extensions": [
            "ms-python.python",
            "ms-python.vscode-pylance",
            "ms-azuretools.vscode-docker",
            "ms-vscode.vscode-typescript-next",
            "eamodio.gitlens",
        ],
        "settings": {
            "editor.formatOnSave": True,
            "python.linting.enabled": True,
        },
    },
    "Full-stack": {
        "extensions": [
            "dbaeumer.vscode-eslint",
            "esbenp.prettier-vscode",
            "ms-python.python",
            "ms-python.vscode-pylance",
            "msjsdiag.debugger-for-chrome",
            "eamodio.gitlens",
        ],
        "settings": {
            "editor.formatOnSave": True,
        },
    },
    "Data Science": {
        "extensions": [
            "ms-python.python",
            "ms-toolsai.jupyter",
            "ms-toolsai.jupyter-keymap",
            "ms-toolsai.jupyter-renderers",
            "ms-toolsai.vscode-jupyter-cell-tags",
            "ms-toolsai.vscode-jupyter-slideshow",
        ],
        "settings": {
            "python.dataScience.sendSelectionToInteractiveWindow": True,
        },
    },
    "Mobile": {
        "extensions": [
            "Dart-Code.dart-code",
            "Dart-Code.flutter",
            "msjsdiag.debugger-for-chrome",
        ],
        "settings": {
            "editor.formatOnSave": True,
        },
    },
} 