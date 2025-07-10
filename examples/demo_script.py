#!/usr/bin/env python3
"""
Demo script for VSCode Sync Tool
Shows basic usage and functionality
"""

import json
import tempfile
from pathlib import Path
from vscode_sync.main import VSCodeSync, get_recommendations

def demo_basic_functionality():
    """Demonstrate basic export/import functionality"""
    print("🔧 VSCode Sync Tool Demo")
    print("=" * 50)
    
    # Initialize the sync tool
    sync = VSCodeSync()
    
    # Show current status
    print("\n📊 Current VSCode Status:")
    sync.show_status()
    
    # Get current configuration
    print("\n📤 Getting current configuration...")
    extensions = sync.get_installed_extensions()
    settings = sync.get_settings()
    
    print(f"Found {len(extensions)} extensions")
    print(f"Found {len(settings)} settings")
    
    if extensions:
        print("\n📦 Sample Extensions:")
        for ext in extensions[:5]:  # Show first 5
            print(f"  • {ext}")
        if len(extensions) > 5:
            print(f"  ... and {len(extensions) - 5} more")
    
    if settings:
        print("\n⚙️ Sample Settings:")
        for key, value in list(settings.items())[:5]:  # Show first 5
            print(f"  • {key}: {value}")
        if len(settings) > 5:
            print(f"  ... and {len(settings) - 5} more")

def demo_export_import():
    """Demonstrate export/import functionality"""
    print("\n\n💾 Export/Import Demo")
    print("-" * 30)
    
    sync = VSCodeSync()
    
    # Create a temporary file for demo
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = Path(f.name)
    
    try:
        print(f"📤 Exporting configuration to {temp_path.name}...")
        
        # Export current configuration
        if sync.export_config(str(temp_path)):
            print("✅ Export successful!")
            
            # Show file contents
            with open(temp_path, 'r') as f:
                config = json.load(f)
            
            print(f"📄 Config file contains:")
            print(f"  • {len(config.get('extensions', []))} extensions")
            print(f"  • {len(config.get('settings', {}))} settings")
            print(f"  • Created: {config.get('metadata', {}).get('created_at', 'Unknown')}")
            
            # Demonstrate import (dry run)
            print(f"\n📥 Configuration ready for import to other machines")
            print(f"   Use: vscode-sync import {temp_path.name}")
            
        else:
            print("❌ Export failed!")
            
    finally:
        # Clean up
        if temp_path.exists():
            temp_path.unlink()

def demo_recommendations():
    """Demonstrate the recommendation system"""
    print("\n\n🧙 Recommendation System Demo")
    print("-" * 35)
    
    dev_types = ["frontend", "backend", "fullstack", "data-science", "mobile"]
    
    for dev_type in dev_types:
        print(f"\n🎯 {dev_type.capitalize()} Development:")
        
        # Get recommendations
        languages = {
            "frontend": ["javascript", "typescript", "css"],
            "backend": ["python", "nodejs", "go"],
            "fullstack": ["javascript", "python", "typescript"],
            "data-science": ["python", "r", "sql"],
            "mobile": ["dart", "swift", "kotlin"]
        }
        
        recommendations = get_recommendations(dev_type, languages[dev_type])
        
        print(f"   Recommended extensions ({len(recommendations)} total):")
        for ext in recommendations[:5]:  # Show first 5
            print(f"     • {ext}")
        if len(recommendations) > 5:
            print(f"     ... and {len(recommendations) - 5} more")

def demo_cli_commands():
    """Show CLI command examples"""
    print("\n\n⌨️ CLI Command Examples")
    print("-" * 25)
    
    commands = [
        ("Check Status", "vscode-sync status"),
        ("Export Config", "vscode-sync export my-setup.json"),
        ("Export to ZIP", "vscode-sync export my-setup.zip"),
        ("Import Config", "vscode-sync import my-setup.json"),
        ("Setup Wizard", "vscode-sync wizard"),
        ("Export Extensions Only", "vscode-sync export --no-settings extensions.json"),
        ("Import Without Backup", "vscode-sync import --no-backup config.json"),
        ("Dry Run Import", "vscode-sync import --no-extensions --no-settings config.json")
    ]
    
    for description, command in commands:
        print(f"  {description:20} → {command}")

def demo_file_format():
    """Show the configuration file format"""
    print("\n\n📋 Configuration File Format")
    print("-" * 30)
    
    example_config = {
        "metadata": {
            "created_at": "2025-01-15T10:30:00.000Z",
            "system": "Darwin",
            "vscode_sync_version": "1.0.0"
        },
        "extensions": [
            "ms-python.python",
            "ms-vscode.vscode-typescript-next",
            "esbenp.prettier-vscode",
            "bradlc.vscode-tailwindcss",
            "ms-vscode.vscode-eslint"
        ],
        "settings": {
            "editor.fontSize": 14,
            "editor.fontFamily": "Fira Code",
            "editor.formatOnSave": True,
            "workbench.colorTheme": "Dark+ (default dark)",
            "terminal.integrated.fontSize": 12,
            "python.defaultInterpreterPath": "/usr/local/bin/python3"
        }
    }
    
    print("📄 Example configuration file (JSON):")
    print(json.dumps(example_config, indent=2))

def main():
    """Run all demo functions"""
    try:
        demo_basic_functionality()
        demo_export_import()
        demo_recommendations()
        demo_cli_commands()
        demo_file_format()
        
        print("\n\n🎉 Demo Complete!")
        print("Try running 'python -m vscode_sync.main --help' to get started")
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo failed: {e}")
        print("Make sure VSCode is installed and the 'code' command is available")

if __name__ == "__main__":
    main()
