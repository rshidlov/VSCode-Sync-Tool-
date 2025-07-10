"""
Preset management for VSCode Sync Tool
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from .config import ConfigManager

class PresetManager:
    """Manages presets for VSCode Sync Tool"""
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        self.config = config_manager or ConfigManager()
        self.built_in_presets = self._load_built_in_presets()
    
    def _load_built_in_presets(self) -> Dict[str, Dict]:
        """Load built-in presets"""
        return {
            "frontend": {
                "name": "Frontend Development",
                "description": "Extensions for modern frontend development",
                "dev_type": "frontend",
                "languages": ["javascript", "typescript", "css", "html"],
                "extensions": [
                    "ms-vscode.vscode-typescript-next",
                    "esbenp.prettier-vscode",
                    "bradlc.vscode-tailwindcss",
                    "ms-vscode.vscode-eslint",
                    "formulahendry.auto-rename-tag",
                    "christian-kohler.npm-intellisense",
                    "ms-vscode.vscode-css-peek",
                    "ritwick.reactjs-code-snippets",
                    "ms-vscode.vscode-json",
                    "ms-vscode.vscode-html-css-support"
                ],
                "settings": {
                    "editor.formatOnSave": True,
                    "editor.codeActionsOnSave": {
                        "source.fixAll.eslint": True
                    },
                    "prettier.semi": True,
                    "prettier.singleQuote": True,
                    "emmet.includeLanguages": {
                        "javascript": "javascriptreact",
                        "typescript": "typescriptreact"
                    }
                }
            },
            "backend": {
                "name": "Backend Development",
                "description": "Extensions for server-side development",
                "dev_type": "backend",
                "languages": ["python", "javascript", "go", "rust"],
                "extensions": [
                    "ms-python.python",
                    "ms-python.vscode-pylance",
                    "ms-vscode.vscode-docker",
                    "ms-vscode.vscode-restclient",
                    "humao.rest-client",
                    "ms-vscode.vscode-json",
                    "redhat.vscode-yaml",
                    "ms-vscode.powershell",
                    "golang.go",
                    "rust-lang.rust-analyzer"
                ],
                "settings": {
                    "python.defaultInterpreterPath": "python3",
                    "python.linting.enabled": True,
                    "python.linting.pylintEnabled": True,
                    "python.formatting.provider": "black",
                    "editor.formatOnSave": True,
                    "files.associations": {
                        "*.env": "dotenv",
                        "Dockerfile*": "dockerfile"
                    }
                }
            },
            "fullstack": {
                "name": "Full-Stack Development",
                "description": "Complete setup for full-stack development",
                "dev_type": "fullstack",
                "languages": ["javascript", "typescript", "python", "html", "css"],
                "extensions": [
                    "ms-vscode.vscode-typescript-next",
                    "esbenp.prettier-vscode",
                    "ms-python.python",
                    "ms-python.vscode-pylance",
                    "bradlc.vscode-tailwindcss",
                    "ms-vscode.vscode-eslint",
                    "ms-vscode.vscode-docker",
                    "ms-vscode.vscode-restclient",
                    "formulahendry.auto-rename-tag",
                    "christian-kohler.npm-intellisense",
                    "ms-vscode.vscode-json",
                    "redhat.vscode-yaml",
                    "ritwick.reactjs-code-snippets"
                ],
                "settings": {
                    "editor.formatOnSave": True,
                    "editor.codeActionsOnSave": {
                        "source.fixAll.eslint": True
                    },
                    "python.defaultInterpreterPath": "python3",
                    "python.formatting.provider": "black",
                    "prettier.semi": True,
                    "prettier.singleQuote": True,
                    "emmet.includeLanguages": {
                        "javascript": "javascriptreact",
                        "typescript": "typescriptreact"
                    }
                }
            },
            "data-science": {
                "name": "Data Science",
                "description": "Extensions for data science and machine learning",
                "dev_type": "data-science",
                "languages": ["python", "r", "sql", "jupyter"],
                "extensions": [
                    "ms-python.python",
                    "ms-python.vscode-pylance",
                    "ms-toolsai.jupyter",
                    "ms-toolsai.jupyter-keymap",
                    "ms-toolsai.jupyter-renderers",
                    "ms-toolsai.vscode-jupyter-cell-tags",
                    "ms-toolsai.vscode-jupyter-slideshow",
                    "ikuyadeu.r",
                    "ms-mssql.mssql",
                    "ms-vscode.vscode-json",
                    "redhat.vscode-yaml"
                ],
                "settings": {
                    "python.defaultInterpreterPath": "python3",
                    "python.formatting.provider": "black",
                    "jupyter.askForKernelRestart": False,
                    "jupyter.interactiveWindowMode": "perFile",
                    "python.dataScience.askForKernelRestart": False,
                    "python.dataScience.sendSelectionToInteractiveWindow": True,
                    "editor.formatOnSave": True
                }
            },
            "mobile": {
                "name": "Mobile Development",
                "description": "Extensions for mobile app development",
                "dev_type": "mobile",
                "languages": ["dart", "kotlin", "swift", "javascript"],
                "extensions": [
                    "dart-code.dart-code",
                    "dart-code.flutter",
                    "ms-vscode.vscode-react-native",
                    "ms-vscode.vscode-typescript-next",
                    "mathiasfrohlich.kotlin",
                    "swift.swift-lang",
                    "ms-vscode.vscode-json",
                    "redhat.vscode-yaml"
                ],
                "settings": {
                    "dart.flutterSdkPath": "",
                    "dart.checkForSdkUpdates": True,
                    "dart.openDevTools": "flutter",
                    "editor.formatOnSave": True,
                    "editor.rulers": [80, 120],
                    "files.associations": {
                        "*.dart": "dart"
                    }
                }
            }
        }
    
    def get_preset(self, name: str) -> Optional[Dict]:
        """Get a preset by name"""
        # Check built-in presets first
        if name in self.built_in_presets:
            return self.built_in_presets[name]
        
        # Check user presets
        preset_path = self.config.get_preset_path(name)
        if preset_path.exists():
            try:
                with open(preset_path, 'r') as f:
                    return json.load(f)
            except Exception:
                return None
        
        return None
    
    def save_preset(self, name: str, preset: Dict):
        """Save a preset"""
        preset_path = self.config.get_preset_path(name)
        preset["created_at"] = datetime.now().isoformat()
        
        with open(preset_path, 'w') as f:
            json.dump(preset, f, indent=2)
    
    def list_presets(self) -> List[str]:
        """List all available presets"""
        presets = list(self.built_in_presets.keys())
        presets.extend(self.config.list_presets())
        return sorted(set(presets))
    
    def delete_preset(self, name: str) -> bool:
        """Delete a user preset"""
        if name in self.built_in_presets:
            return False  # Can't delete built-in presets
        
        preset_path = self.config.get_preset_path(name)
        if preset_path.exists():
            preset_path.unlink()
            return True
        return False
    
    def create_preset_from_current(self, name: str, description: str = "") -> Dict:
        """Create a preset from current VSCode setup"""
        from .main import VSCodeSync
        
        sync = VSCodeSync()
        extensions = sync.get_installed_extensions()
        settings = sync.get_settings()
        
        preset = {
            "name": name,
            "description": description,
            "dev_type": "custom",
            "languages": [],
            "extensions": extensions,
            "settings": settings,
            "created_at": datetime.now().isoformat()
        }
        
        self.save_preset(name, preset)
        return preset