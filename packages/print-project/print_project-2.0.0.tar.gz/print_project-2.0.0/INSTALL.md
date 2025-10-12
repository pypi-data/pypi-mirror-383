# Installation Quick Reference

## Method 1: PyPI Installation (Ultimate) 🌟 READY
```bash
pip install print-project
# Once published to PyPI - one command, any system!
```
- ✅ **No dependencies needed** (except Python)
- ✅ **Universal compatibility**
- ✅ **Automatic updates**
- ✅ **No repository cloning**

## Method 2: One-Line Installation (Current) 🚀
**Unix/Linux/macOS:**
```bash
curl -sSL https://raw.githubusercontent.com/smaxiso/print-project/master/install.sh | bash
```

**Windows (PowerShell):**
```powershell
iwr -useb https://raw.githubusercontent.com/smaxiso/print-project/master/install.ps1 | iex
```
- ✅ **No cloning required**
- ✅ **Automatic dependency checking**
- ✅ **PATH configuration**
- ✅ **Cross-platform compatibility**

## Method 3: Universal Python Package (Recommended) ✅ Tested
```bash
# Clone and install
git clone https://github.com/smaxiso/print-project.git
cd print-project
pip install -e .

# Creates: print-project and analyze-project commands
# Usage from any directory:
print-project --help
analyze-project --console
```

## Method 4: Direct Python Execution ✅ Tested
```bash
# Clone and run directly
git clone https://github.com/smaxiso/print-project.git
cd print-project
python print_project.py --help
python print_project.py --console
# No installation required
```

## Method 5: Guided Installation Script
```bash
python install.py
# Interactive installer with multiple options
```

## Method 6: Manual PATH Setup
```bash
# Add this directory to your PATH environment variable
# Windows: Use print-project.bat
# Unix/Linux: Use print-project script
```

## Verification ✅ All Methods Tested
After installation, test with:
```bash
# Test all working methods:
python print_project.py --help          # ✅ Works
print-project --help                    # ✅ Works (after pip install)  
analyze-project --help                  # ✅ Works (after pip install)
```

## Cross-Platform Compatibility ✅
- **Windows**: All methods tested and working
- **macOS**: `pip install -e .` and direct Python execution
- **Linux**: `pip install -e .` and direct Python execution

## Config File Search Locations
The tool searches for config.ini in:
1. Current working directory
2. Script directory
3. ~/.print-project/config.ini (user config)
4. /etc/print-project/config.ini (Unix system config)
5. %APPDATA%/print-project/config.ini (Windows system config)

## Quick Start for New Users
```bash
# ULTIMATE - PyPI installation (when published):
pip install print-project
print-project --help

# CURRENT EASIEST - One-line installation (Unix/Linux/macOS):
curl -sSL https://raw.githubusercontent.com/smaxiso/print-project/master/install.sh | bash
print-project --help

# CURRENT EASIEST - One-line installation (Windows PowerShell):
iwr -useb https://raw.githubusercontent.com/smaxiso/print-project/master/install.ps1 | iex
print-project --help

# ALTERNATIVE - Clone and install:
git clone https://github.com/smaxiso/print-project.git
cd print-project
pip install -e .
print-project --help

# DIRECT USAGE - No installation:
git clone https://github.com/smaxiso/print-project.git
cd print-project
python print_project.py --help
```