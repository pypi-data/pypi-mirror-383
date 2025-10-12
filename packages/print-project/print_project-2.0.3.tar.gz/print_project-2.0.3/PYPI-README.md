# print-project

A comprehensive Python CLI tool for analyzing and extracting the contents of source code files across a project directory structure, outputting them into a single organized document for easier review and analysis.

## ⚡ Installation

```bash
pip install print-project
```

## 🚀 Quick Start

```bash
# Analyze current directory
print-project

# Analyze specific project
print-project -f /path/to/project

# Show progress during analysis
print-project --console

# Alternative command name
analyze-project --help
```

## ✨ Features

- **Recursive Directory Scanning**: Analyzes entire project structures including subdirectories
- **File Type Filtering**: Include/exclude files by extension or specific filenames
- **Smart Binary Detection**: Automatically skips binary files while allowing trusted text extensions
- **Directory Tree Generation**: Creates visual directory structure representation
- **Configurable Output**: Customizable output formatting with summary statistics
- **Size Limits**: Configurable maximum file size processing limits
- **Flexible Configuration**: INI-based configuration with command-line overrides

## 💡 Usage Examples

```bash
# Basic usage
print-project                                    # Analyze current directory
print-project -f /path/to/project               # Analyze specific directory
print-project --console                         # Show console output

# File filtering
print-project -e py,js,ts                       # Include only specific extensions
print-project -x log,tmp,bak                    # Exclude specific extensions
print-project -s "tests,docs,build"             # Skip directories

# Advanced options
print-project --include-files "config.py,.env"          # Force include files
print-project --only-include-files "main.py,README.md"  # Process only these files
print-project -o my_analysis                            # Custom output filename
print-project --duplicate                               # Timestamped output
print-project --no-tree                                 # Skip directory tree
```

## 📋 Command Line Options

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

## 🔧 Configuration

The tool uses a `config.ini` file for default settings. Config file locations:

- Current working directory
- `~/.print-project/config.ini` (user config)
- `/etc/print-project/config.ini` (system config - Unix/Linux)
- `%APPDATA%/print-project/config.ini` (system config - Windows)

## 📄 Output

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

## 🎯 Use Cases

- **Code Reviews**: Generate comprehensive project snapshots
- **Documentation**: Create detailed project overviews
- **Analysis**: Understand project structure and content
- **Migration**: Prepare project content for analysis or transfer
- **AI/LLM Input**: Generate context-rich project representations

## 🔄 Updates

```bash
# Upgrade to latest version
pip install --upgrade print-project

# Check current version
print-project --help  # Version shown in help text
```

## 🌐 Cross-Platform Compatibility

Works identically on:
- ✅ **Windows**
- ✅ **macOS** 
- ✅ **Linux**

## 📚 Links

- **Source Code**: [GitHub Repository](https://github.com/smaxiso/print-project)
- **Issues**: [Bug Reports & Feature Requests](https://github.com/smaxiso/print-project/issues)
- **Changelog**: [Version History](https://github.com/smaxiso/print-project/blob/master/docs/CHANGELOG.md)
- **Contributing**: [Development Guide](https://github.com/smaxiso/print-project/blob/master/docs/CONTRIBUTING.md)

## 📝 License

MIT License - see the [repository](https://github.com/smaxiso/print-project) for details.