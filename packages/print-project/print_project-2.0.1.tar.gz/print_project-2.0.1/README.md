# Directory Content Analysis Tool

A comprehensive Python utility for analyzing and extracting the contents of source code files across a project directory structure, outputting them into a single organized document for easier review and analysis.

## Features

- **Recursive Directory Scanning**: Analyzes entire project structures including subdirectories
- **File Type Filtering**: Include/exclude files by extension or specific filenames
- **Smart Binary Detection**: Automatically skips binary files while allowing trusted text extensions
- **Directory Tree Generation**: Creates visual directory structure representation
- **Configurable Output**: Customizable output formatting with summary statistics
- **Size Limits**: Configurable maximum file size processing limits
- **Flexible Configuration**: INI-based configuration with command-line overrides

## Installation

### 🚀 Option 1: PyPI Installation (Recommended)

Install directly from PyPI - works on **any system** with Python:

```bash
pip install print-project
```

**✅ After installation, use from any directory:**
```bash
print-project --help                    # Main command
analyze-project /path/to/project        # Alternative command
print-project --console -f ~/myproject  # Example usage
```

### 📦 Option 2: One-Line Installation Scripts

Install without cloning - alternative method for any system:

**Unix/Linux/macOS:**
```bash
curl -sSL https://raw.githubusercontent.com/smaxiso/print-project/master/install.sh | bash
```

**Windows (PowerShell):**
```powershell
iwr -useb https://raw.githubusercontent.com/smaxiso/print-project/master/install.ps1 | iex
```### 🔧 Option 3: Development Installation  

For development or latest features from source:

```bash
# Clone the repository
git clone https://github.com/smaxiso/print-project.git
cd print-project

# Install as Python package (creates 'print-project' and 'analyze-project' commands)
pip install -e .
```

### 🎯 Option 4: Guided Installation Script

For interactive setup with multiple installation options:

```bash
git clone https://github.com/smaxiso/print-project.git
cd print-project
python install.py
# Provides guided installation with choices for different setups
```

### 📁 Option 5: Direct Usage (No Installation)

Run directly without any installation:

```bash
git clone https://github.com/smaxiso/print-project.git
cd print-project
python print_project.py --help          # Works immediately
python print_project.py --console       # Example usage
```

### 📋 Requirements

- **Python 3.6+** (required)
- **chardet library** (automatically installed with pip methods)

### ✅ Verification

After installation, test that everything works:

```bash
# Test the commands work:
print-project --help
analyze-project --help
python print_project.py --help

# Test basic functionality:
print-project --console --only-include-files "README.md"
```

### 🔧 Cross-Platform Compatibility

This tool works identically on:
- ✅ **Windows** (tested)
- ✅ **macOS** (clone and `pip install -e .`)  
- ✅ **Linux** (clone and `pip install -e .`)

### 📂 Config File Search Locations

The tool automatically searches for `config.ini` in:
1. Current working directory
2. Script directory (for development)
3. `~/.print-project/config.ini` (user config)
4. `/etc/print-project/config.ini` (system config - Unix/Linux)
5. `%APPDATA%/print-project/config.ini` (system config - Windows)

## Usage

### Basic Usage

```bash
# If installed as command-line tool:
print-project                    # Analyze current directory
print-project -f /path/to/project # Analyze specific directory
print-project --console          # Show console output during processing

# Alternative command name:
analyze-project --help

# Direct usage (without installation):
python print_project.py
python print_project.py -f /path/to/project
python print_project.py --console
```

### Advanced Options

```bash
# Using installed command (recommended):
print-project -s "tests,docs,build"              # Skip specific directories
print-project -e py,js,ts                        # Include only specific file extensions
print-project -x txt,log,tmp                     # Exclude specific file extensions
print-project --include-files "config.local.properties,.env.production"  # Force include specific files
print-project --only-include-files "main.py,config.py,README.md"          # Process only specific files
print-project -o my_project_analysis             # Custom output filename
print-project --duplicate                        # Create timestamped output
print-project --no-tree                          # Skip directory tree generation
print-project --tree-exclude ".git,venv,node_modules"  # Custom tree exclusions

# Direct usage (replace 'print-project' with 'python print_project.py'):
python print_project.py -s "tests,docs,build"
python print_project.py -e py,js,ts
# ... etc
```

## Command Line Options

| Option | Description |
|--------|-------------|
| `-f, --folder` | Directory to process (default: current directory) |
| `-s, --skip` | Comma-separated list of directories to exclude |
| `-e, --extensions` | Comma-separated list of file extensions to include |
| `-x, --exclude-ext` | Comma-separated list of file extensions to exclude |
| `-i, --ignore-files` | Comma-separated list of specific files to exclude |
| `--include-files` | Force include specific files (overrides filters) |
| `--only-include-files` | Process ONLY these specific files |
| `--max-size` | Maximum file size in bytes to process |
| `--console` | Show console output during processing |
| `-o, --output` | Output filename (without extension) |
| `--duplicate` | Create timestamped output instead of overwriting |
| `--no-summary` | Exclude summary from output file |
| `--no-tree` | Skip directory tree generation |
| `--tree-exclude` | Override directory exclusions for tree generation |
| `-h, --help` | Show help message |

## Configuration

The tool uses a `config.ini` file for default settings. You can customize:

- Default directories to skip
- File extensions to exclude
- Trusted text file extensions
- Maximum file size limits
- Default output behavior

## Output

The tool generates a `.txt` file containing:

1. **Directory Tree**: Visual representation of the project structure
2. **File Analysis**: Content of each processed file with:
   - File path and metadata
   - Line numbers
   - Syntax highlighting markers
3. **Summary Statistics**: 
   - Total files processed
   - Files skipped (with reasons)
   - Processing time and performance metrics

## Files

- `print_project.py` - Main application (current version)
- `config.ini` - Configuration file with default settings
- `VERSION` - Current version number
- `CHANGELOG.md` - Version history and release notes
- `CONTRIBUTING.md` - Guidelines for contributors
- `archive/` - Archived versions and backup files
  - `print_project_bkp.py` - Previous version (v1.0.0)
  - `README.md` - Archive documentation

## Use Cases

- **Code Reviews**: Generate comprehensive project snapshots
- **Documentation**: Create detailed project overviews
- **Analysis**: Understand project structure and content
- **Migration**: Prepare project content for analysis or transfer
- **AI/LLM Input**: Generate context-rich project representations

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on:

- Setting up the development environment
- Code style and testing requirements
- Submitting bug reports and feature requests
- Pull request process and release guidelines

For version history and recent changes, see [CHANGELOG.md](CHANGELOG.md).

## License

This project is open source. See the repository for license details.