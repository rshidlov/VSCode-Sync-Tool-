"""
VSCode Sync Tool

A cross-platform CLI tool to export, import, and share VSCode settings and extensions.
"""

__version__ = "1.0.0"
__author__ = "Roei Shidlovsky"
__email__ = "your.email@example.com"

from .main import VSCodeSync, app

__all__ = ["VSCodeSync", "app"]
