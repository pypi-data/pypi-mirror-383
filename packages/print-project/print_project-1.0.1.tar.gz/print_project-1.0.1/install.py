#!/usr/bin/env python3
"""
Installation script for print-project command-line tool
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def install_via_pip():
    """Install using pip in development mode"""
    print("Installing print-project using pip...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."])
        print("✅ Installation successful!")
        print("\nYou can now use the following commands from anywhere:")
        print("  print-project --help")
        print("  analyze-project --help")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        return False

def install_manually():
    """Manual installation by copying to PATH"""
    print("Manual installation option:")
    print("1. Add this directory to your PATH environment variable")
    print("2. Or copy print_project.py to a directory in your PATH")
    print("3. Create a batch file or shell script wrapper")
    
    script_dir = Path(__file__).parent
    print(f"\nCurrent directory: {script_dir}")
    
    # Create a simple batch file for Windows
    if sys.platform == "win32":
        batch_content = f'''@echo off
python "{script_dir / 'print_project.py'}" %*
'''
        batch_file = script_dir / "print-project.bat"
        with open(batch_file, 'w') as f:
            f.write(batch_content)
        print(f"Created batch file: {batch_file}")
        print("Add this directory to your PATH to use 'print-project' command")
    
    # Create a shell script for Unix-like systems
    else:
        script_content = f'''#!/bin/bash
python3 "{script_dir / 'print_project.py'}" "$@"
'''
        script_file = script_dir / "print-project"
        with open(script_file, 'w') as f:
            f.write(script_content)
        os.chmod(script_file, 0o755)
        print(f"Created shell script: {script_file}")
        print("Add this directory to your PATH to use 'print-project' command")

def main():
    print("Print-Project Installation Script")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("print_project.py").exists():
        print("❌ Error: print_project.py not found in current directory")
        print("Please run this script from the print-project directory")
        sys.exit(1)
    
    print("Choose installation method:")
    print("1. Install as Python package (recommended)")
    print("2. Manual installation with PATH setup")
    print("3. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            if install_via_pip():
                break
            else:
                print("\nFalling back to manual installation...")
                install_manually()
                break
        elif choice == "2":
            install_manually()
            break
        elif choice == "3":
            print("Installation cancelled.")
            sys.exit(0)
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()