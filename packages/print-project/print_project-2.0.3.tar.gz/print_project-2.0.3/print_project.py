"""
Directory Content Analysis Tool

This script analyzes and extracts the contents of source code files across a project directory structure,
outputting them into a single organized document for easier review and analysis.

Usage:
    print-project [options]
    analyze-project [options]
    python -m print_project [options]
    python print_project.py [options]

Options:
    -f, --folder PATH           Directory to process (default: current directory)
    -s, --skip DIRS             Comma-separated list of directories to exclude
    -e, --extensions EXTS       Comma-separated list of file extensions to include
    -x, --exclude-ext EXTS      Comma-separated list of file extensions to exclude
    -i, --ignore-files FILES    Comma-separated list of specific files to exclude
    --include-files FILES       Force include specific files (overrides skip/binary detection, scans other files too)
    --only-include-files FILES  Process ONLY these specific files, ignore everything else
    --max-size SIZE             Maximum file size in bytes to process
    --console                   Show console output (off by default)
    -o, --output FILENAME       Output filename (without extension)
    --duplicate                 Create duplicate output file with timestamp instead of overwriting
    --no-summary                Exclude summary from output file
    --no-tree                   Skip directory tree generation
    --tree-exclude DIRS         Override: Comma-separated list of directories to exclude from tree (if not specified, uses --skip)
    -h, --help                  Show this help message and exit

Examples:
    print-project
    print-project -s "tests,docs,build"
    print-project -f /path/to/project --console
    print-project --no-tree
    print-project --include-files "config.local.properties,secret.env,.env.production"
    print-project --only-include-files "main.py,config.py,README.md"
    print-project -o my_analysis --duplicate --console
"""

# Entry point for pip installable command-line tool
def main():
    return _main()

# Rename the original main() to _main()
def _main():
    args = parse_arguments()
    config = load_config()  # This now loads trusted extensions into global variable
    options = merge_options(args, config)

    # Validate include options (they're mutually exclusive)
    if options['include_files'] and options['only_include_files']:
        print("Error: --include-files and --only-include-files cannot be used together")
        print("  --include-files: Force include specific files while scanning others normally")
        print("  --only-include-files: Process ONLY the specified files, ignore everything else")
        return 1

    # Get and validate the root directory
    root_dir = os.path.abspath(args.folder)
    if not os.path.isdir(root_dir):
        print(f"Error: '{root_dir}' is not a valid directory")
        return 1

    # Process files
    print(f"Analyzing directory: {root_dir}")

    # Show processing mode
    if options['only_include_files']:
        print(f"Mode: ONLY processing {len(options['only_include_files'])} specific files")
        print(f"Files: {', '.join(options['only_include_files'])}")
    elif options['include_files']:
        print(f"Mode: Normal scanning + force including {len(options['include_files'])} specific files")
        print(f"Force included: {', '.join(options['include_files'])}")
    else:
        print("Mode: Normal scanning with configured filters")

    # Show tree mode
    if options['no_tree']:
        print("Tree generation: Disabled")
    else:
        tree_exclusions = determine_tree_exclusions(options)
        tree_source = "explicit tree config" if options.get('tree_exclude_explicit', False) else "file processing config"
        print(f"Tree generation: Enabled")
        print(f"Tree exclusions: {', '.join(tree_exclusions) if tree_exclusions else 'None'} (from {tree_source})")

    print("Starting analysis...")

    output_content, summary_content, summary = process_files(root_dir, options)

    # Determine the output file path
    current_dir = os.getcwd()  # Output file always goes to current directory
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    project_name = os.path.basename(root_dir)

    if options['output']:
        # Use custom filename if provided
        base_name = options['output']
    else:
        # Use project name by default
        base_name = f"{project_name}_project"

    if options['duplicate']:
        # Create duplicate with timestamp if requested
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{base_name}_{timestamp}.txt"
    else:
        # Default behavior is to overwrite
        output_filename = f"{base_name}.txt"

    output_path = os.path.join(current_dir, output_dir, output_filename)

    # Combine content and summary based on options
    final_content = output_content.copy()
    if not options['no_summary']:
        final_content.extend(summary_content)

    # Write output to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(final_content))

    output_size = os.path.getsize(output_path)

    # Always show detailed summary in console, regardless of console option
    print("\nAnalysis complete!")
    print(f"Processed {summary['processed_files']} of {summary['total_files']} files")
    print(f"Total code lines processed: {summary['total_lines']:,}")

    if summary['force_included_files']:
        print(f"Force-included files: {len(summary['force_included_files'])}")
        for file_path in summary['force_included_files']:
            line_count = summary['lines_per_file'].get(file_path, 0)
            print(f"  ✓ {file_path} ({line_count:,} lines)")

    print(f"Files skipped: {sum(len(files) for files in summary['skipped_files'].values())}")

    if summary['skipped_dirs']:
        print(f"Directories skipped: {len(summary['skipped_dirs'])}")
        print("\nSkipped directories:")
        for dir_path in summary['skipped_dirs']:
            print(f"  - {dir_path}")

    if summary['skipped_files']:
        print("\nSkip reasons:")
        for reason, files in summary['skipped_files'].items():
            print(f"  - {reason}: {len(files)}")

    print(f"\nTree exclusions: {', '.join(summary['tree_exclusions'])} (from {summary['tree_exclusion_source']})")
    print(f"Execution time: {summary['execution_time']:.2f} seconds")
    print(f"Output file: {output_path} ({get_human_readable_size(output_size)})")

    return 0

import argparse
import configparser
import datetime
import os
import sys
import time
import chardet
from pathlib import Path


# Global variable to store trusted extensions loaded from config
TRUSTED_EXTENSIONS = set()


def generate_tree(dir_path, exclude_list, prefix=""):
    """
    Recursively generates the tree structure for a directory, excluding specified folders.
    
    Args:
        dir_path: Path to the directory
        exclude_list: List of directory names to exclude
        prefix: String prefix for formatting the tree structure
        
    Returns:
        List of strings representing the tree structure
    """
    try:
        # Get directory contents and filter out excluded names
        if isinstance(dir_path, str):
            dir_path = Path(dir_path)
            
        contents = [p for p in dir_path.iterdir() if p.name not in exclude_list]
    except PermissionError:
        return [f"{prefix}└── [Error: Permission Denied]"]
    except Exception as e:
        return [f"{prefix}└── [Error: {str(e)}]"]

    # Sort contents, with directories first
    contents.sort(key=lambda p: (p.is_file(), p.name.lower()))
    
    tree_lines = []
    for i, path in enumerate(contents):
        is_last = i == (len(contents) - 1)
        connector = "└── " if is_last else "├── "
        
        # Add file/directory indicator
        if path.is_dir():
            tree_lines.append(f"{prefix}{connector}{path.name}/")
        else:
            tree_lines.append(f"{prefix}{connector}{path.name}")

        if path.is_dir():
            extension = "    " if is_last else "│   "
            # Pass the exclude_list down in the recursive call
            tree_lines.extend(generate_tree(path, exclude_list, prefix=prefix + extension))
            
    return tree_lines


def create_directory_tree(root_dir, exclude_list):
    """
    Create a complete directory tree structure.
    
    Args:
        root_dir: Root directory path
        exclude_list: List of directory names to exclude from tree
        
    Returns:
        String containing the formatted tree structure
    """
    root_path = Path(root_dir)
    
    # Generate the tree structure
    tree_output = [f"{root_path.resolve().name}/"]
    tree_output.extend(generate_tree(root_path, exclude_list=exclude_list))
    
    return "\n".join(tree_output)


def is_binary_file(file_path, sample_size=8192):
    """
    Check if a file is binary by examining its contents and encoding.
    Now with configurable trusted extensions and lower confidence threshold.

    Args:
        file_path: Path to the file to check.
        sample_size: Number of bytes to check at the beginning of the file.

    Returns:
        bool: True if the file appears to be binary, False otherwise.
    """
    try:
        # Use trusted extensions from config (loaded globally)
        _, ext = os.path.splitext(file_path)
        if ext.lower() in TRUSTED_EXTENSIONS:
            return False

        with open(file_path, 'rb') as f:
            content = f.read(sample_size)

        # Use chardet to detect encoding
        result = chardet.detect(content)
        encoding = result['encoding']
        confidence = result['confidence']

        if confidence < 0.5:
            return True

        # Check for common binary characteristics if encoding is likely text
        if encoding:
            try:
                text = content.decode(encoding)
                # If decoding succeeds, check for an unusually high proportion of non-ASCII characters
                non_ascii_count = sum(1 for char in text if ord(char) > 127)
                if non_ascii_count / len(text) > 0.3:
                    return True
                return False
            except UnicodeDecodeError:
                # If decoding fails, it's likely a binary file
                return True
        else:
            # If no encoding is detected, treat as binary
            return True
    except FileNotFoundError:
        print(f"File not found: {file_path}", file=sys.stderr)
        return True
    except Exception as e:
        # If there's an error reading the file, assume it's binary
        print(f"Error reading file {file_path}: {e}", file=sys.stderr)
        return True

def get_human_readable_size(size_in_bytes):
    """
    Convert a file size in bytes to a human-readable string.

    Args:
        size_in_bytes: File size in bytes

    Returns:
        str: Human-readable file size (e.g., "4.2 MB")
    """
    if size_in_bytes < 1024:
        return f"{size_in_bytes} bytes"
    elif size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.1f} KB"
    elif size_in_bytes < 1024 * 1024 * 1024:
        return f"{size_in_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_in_bytes / (1024 * 1024 * 1024):.1f} GB"


def should_process_file(file_path, options):
    """
    Determine if a file should be processed based on inclusion/exclusion rules.
    Updated with new include logic:
    1. --only-include-files: Process ONLY these files, ignore everything else
    2. --include-files: Force include these files, but also scan others normally
    3. Normal filtering: Apply all other rules

    Args:
        file_path: Path to the file
        options: Dictionary of options including exclusion rules

    Returns:
        (bool, str): Tuple (should_process, reason_if_not)
    """
    file_name = os.path.basename(file_path)

    # Priority 1: --only-include-files (most restrictive, overrides everything)
    if options['only_include_files']:
        if file_name in options['only_include_files']:
            return True, ""
        else:
            return False, "Not in only-include files list"

    # Priority 2: --include-files (force include, overrides other restrictions)
    if options['include_files'] and file_name in options['include_files']:
        return True, "Force included"

    # Priority 3: Normal filtering logic for all other files
    # Get file stats
    try:
        file_stats = os.stat(file_path)
        file_size = file_stats.st_size
    except Exception as e:
        print(f"Error accessing file {file_path}: {e}", file=sys.stderr)
        return False, "Permission denied or file error"

    # Check file size
    if options['max_size'] and file_size > options['max_size']:
        return False, f"Size exceeds limit ({get_human_readable_size(file_size)})"

    # Get file extension
    _, ext = os.path.splitext(file_name)
    ext = ext[1:] if ext.startswith('.') else ext  # Remove leading dot

    # Check specific files to exclude
    if file_name in options['ignore_files']:
        return False, f"Excluded file: {file_name}"

    # Check extension inclusions/exclusions
    if options['extensions'] and ext not in options['extensions']:
        return False, f"Extension not in inclusion list: .{ext}"

    if ext in options['exclude_ext']:
        return False, f"Excluded extension: .{ext}"

    # Check if binary (with improved detection using config-based trusted extensions)
    if is_binary_file(file_path):
        return False, "Binary file"

    return True, ""


def should_skip_directory(dir_name, skip_folders):
    """
    Check if a directory should be skipped based on its name.

    Args:
        dir_name: Name of the directory (not the full path)
        skip_folders: List of folder names to skip

    Returns:
        bool: True if the directory should be skipped, False otherwise
    """
    return dir_name in skip_folders


def determine_tree_exclusions(options):
    """
    Determine which directories to exclude from tree display.
    Uses file processing exclusions by default, but allows override.
    
    Args:
        options: Dictionary of options
        
    Returns:
        List of directory names to exclude from tree
    """
    # If tree_exclude is explicitly set (not empty), use it
    if options.get('tree_exclude_explicit', False):
        return options['tree_exclude']
    
    # Otherwise, use the same exclusions as file processing
    return options['skip_folders']


def process_files(root_dir, options):
    """
    Process all files in the directory tree that match the criteria.

    Args:
        root_dir: Root directory to start processing from
        options: Dictionary of options

    Returns:
        tuple: (output_content, summary)
    """
    output_content = []
    processed_files = []
    force_included_files = []  # Track files that were force included
    skipped_files = {}
    skipped_dirs = []  # Track skipped directories
    total_files = 0
    # Line counting variables
    lines_per_file = {}  # Track lines per processed file
    total_lines = 0  # Track total lines across all processed files

    start_time = time.time()

    # Create header for the output
    project_name = os.path.basename(os.path.abspath(root_dir))
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Determine tree exclusions
    tree_exclusions = determine_tree_exclusions(options)
    tree_exclusion_source = "explicit tree config" if options.get('tree_exclude_explicit', False) else "file processing config"

    header_content = [
        f"# Project: {project_name}",
        f"# Date: {current_time}",
        f"# Directory: {os.path.abspath(root_dir)}",
        f"# Excluded folders (file processing): {', '.join(options['skip_folders'])}",
        f"# Excluded folders (tree display): {', '.join(tree_exclusions)} (from {tree_exclusion_source})",
        f"# Excluded extensions: {', '.join(options['exclude_ext'])}",
        f"# Excluded files: {', '.join(options['ignore_files'])}",
        f"# Trusted extensions: {', '.join(sorted(TRUSTED_EXTENSIONS))}",
    ]

    # Add include information to header
    if options['only_include_files']:
        header_content.append(f"# ONLY processing files: {', '.join(options['only_include_files'])}")
    elif options['include_files']:
        header_content.append(f"# Force included files: {', '.join(options['include_files'])}")

    header_content.extend(["", ""])
    output_content.extend(header_content)

    # Generate and add directory tree structure if not disabled
    if not options['no_tree']:
        print("Generating directory tree structure...")
        tree_structure = create_directory_tree(root_dir, tree_exclusions)
        
        tree_section = [
            ""
            "DIRECTORY STRUCTURE",
            # f"# Tree exclusions: {', '.join(tree_exclusions)} (from {tree_exclusion_source})",
            "",
            tree_structure,
            "",
            "FILE CONTENTS",
            ""
        ]
        output_content.extend(tree_section)
        
        # Print the tree to console if console output is enabled
        if options['console']:
            print("\n" + "\n".join(tree_section))

    # Print header to console if console output is enabled
    if options['console']:
        print("\n" + "\n".join(header_content))

    # Build a list of all files to process in a breadth-first manner
    all_files = []
    dirs_to_process = [root_dir]

    while dirs_to_process:
        current_dir = dirs_to_process.pop(0)  # Process directories in order

        try:
            # Get all immediate contents of the current directory
            dir_contents = os.listdir(current_dir)

            # First, add all files in this directory to our list
            for item in sorted(dir_contents):  # Sort for consistent order
                item_path = os.path.join(current_dir, item)

                if os.path.isfile(item_path):
                    all_files.append(item_path)
                elif os.path.isdir(item_path):
                    # If it's a directory, check if we should process it (use file processing exclusions)
                    dir_name = os.path.basename(item_path)
                    if dir_name not in options['skip_folders']:
                        dirs_to_process.append(item_path)
                    else:
                        rel_path = os.path.relpath(item_path, root_dir)
                        skipped_dirs.append(rel_path)
                        if options['console']:
                            print(f"Skipping directory: {rel_path}")

        except PermissionError:
            if options['console']:
                print(f"Permission denied: {current_dir}")
        except Exception as e:
            if options['console']:
                print(f"Error accessing directory {current_dir}: {str(e)}")

    # Sort files by their relative path for consistent output
    all_files.sort(key=lambda f: os.path.relpath(f, root_dir))
    total_files = len(all_files)

    # Process each file
    for file_idx, filepath in enumerate(all_files):
        rel_path = os.path.relpath(filepath, root_dir)
        file_name = os.path.basename(filepath)

        # Print progress
        if options['console']:
            sys.stdout.write(f"\rProcessing file {file_idx + 1}/{total_files}: {rel_path}".ljust(100))
            sys.stdout.flush()

        # Check if we should process this file
        should_process, skip_reason = should_process_file(filepath, options)

        if should_process:
            try:
                # Read file content
                with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()

                # Format the file content with line numbers
                file_header = f"=== {rel_path} ==="
                output_content.append(file_header)
                output_content.append("```")

                lines = content.splitlines()
                formatted_lines = []
                for i, line in enumerate(lines, 1):
                    formatted_line = f"{i:4d} | {line}"
                    formatted_lines.append(formatted_line)
                    output_content.append(formatted_line)

                output_content.append("```")
                output_content.append("")
                processed_files.append(rel_path)

                # Track line counts
                file_line_count = len(lines)
                lines_per_file[rel_path] = file_line_count
                total_lines += file_line_count

                # Track if this was force included
                if skip_reason == "Force included":
                    force_included_files.append(rel_path)

                # Print file content to console if enabled
                if options['console']:
                    # Clear the current progress line
                    sys.stdout.write("\r" + " " * 100 + "\r")
                    sys.stdout.flush()

                    # Print file content
                    print(file_header)
                    print("```")
                    for line in formatted_lines:
                        print(line)
                    print("```")
                    print()

            except Exception as e:
                skip_reason = f"Error: {str(e)}"
                if skip_reason not in skipped_files:
                    skipped_files[skip_reason] = []
                skipped_files[skip_reason].append(rel_path)
        else:
            if skip_reason not in skipped_files:
                skipped_files[skip_reason] = []
            skipped_files[skip_reason].append(rel_path)

    # Clear the progress line
    if options['console']:
        sys.stdout.write("\r" + " " * 100 + "\r")
        sys.stdout.flush()

    # Only add summary if requested
    summary_content = []
    if not options['no_summary']:
        # Generate summary section
        total_time = time.time() - start_time
        summary_section = [
            "=" * 80,
            "SUMMARY",
            "=" * 80,
            "",
            f"Total scan time: {total_time:.2f} seconds",
            f"Total files found: {total_files}",
            f"Files processed: {len(processed_files)}",
            f"Files skipped: {sum(len(files) for files in skipped_files.values())}",
            f"Total code lines: {total_lines:,}"
        ]

        summary_content.extend(summary_section)

        # Add force included files info
        if force_included_files:
            summary_content.append(f"Files force-included: {len(force_included_files)}")
            summary_content.append("")
            summary_content.append("Force-included files:")
            for file_path in force_included_files:
                summary_content.append(f"  - {file_path}")

        if skipped_dirs:
            summary_content.append(f"Directories skipped: {len(skipped_dirs)}")
            summary_content.append("")
            summary_content.append("Skipped directories:")
            for dir_path in skipped_dirs:
                summary_content.append(f"  - {dir_path}")

        summary_content.append("")
        summary_content.append("Skip reasons:")
        for reason, files in skipped_files.items():
            summary_content.append(f"  - {reason}: {len(files)}")

        summary_content.append("")
        summary_content.append("Processed files with line counts:")
        for file_path in processed_files:
            line_count = lines_per_file.get(file_path, 0)
            summary_content.append(f"  - {file_path} ({line_count:,} lines)")

        # Print summary to console if enabled
        if options['console']:
            print("\n".join(summary_section))

            if force_included_files:
                print(f"Files force-included: {len(force_included_files)}")
                print("\nForce-included files:")
                for file_path in force_included_files:
                    print(f"  ✓ {file_path}")

            if skipped_dirs:
                print(f"Directories skipped: {len(skipped_dirs)}")
                print("\nSkipped directories:")
                for dir_path in skipped_dirs:
                    print(f"  - {dir_path}")

            print("\nSkip reasons:")
            for reason, files in skipped_files.items():
                print(f"  - {reason}: {len(files)}")

            print("\nProcessed files with line counts:")
            for file_path in processed_files:
                line_count = lines_per_file.get(file_path, 0)
                print(f"  - {file_path} ({line_count:,} lines)")
            
            print(f"\nTotal code lines: {total_lines:,}")

    return output_content, summary_content, {
        'total_files': total_files,
        'processed_files': len(processed_files),
        'force_included_files': force_included_files,
        'skipped_files': skipped_files,
        'skipped_dirs': skipped_dirs,
        'execution_time': time.time() - start_time,
        'tree_exclusion_source': tree_exclusion_source,
        'tree_exclusions': tree_exclusions,
        'lines_per_file': lines_per_file,
        'total_lines': total_lines
    }


def get_command_prefix():
    """
    Determine the appropriate command prefix based on how the script was invoked.
    
    Returns:
        str: Either 'python print_project.py' or 'print-project'
    """
    import sys
    # Check if script was called directly with python
    if sys.argv[0].endswith('print_project.py') or 'print_project.py' in sys.argv[0]:
        return 'python print_project.py'
    else:
        # Called as installed CLI tool
        return 'print-project'

def parse_arguments():
    """
    Parse command line arguments with updated include options and tree functionality.

    Returns:
        argparse.Namespace: The parsed arguments
    """
    cmd = get_command_prefix()
    
    parser = argparse.ArgumentParser(
        description='Directory Content Analysis Tool with Tree Structure',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  Basic usage - tree uses same exclusions as file processing:
    {cmd}
    {cmd} -f /path/to/project --console

  Tree follows file processing exclusions:
    {cmd} -s "tests,docs,build"

  Override tree exclusions specifically:
    {cmd} -s "tests,docs" --tree-exclude ".git,venv"

  Skip tree entirely:
    {cmd} --no-tree

  File filtering (tree follows same logic):
    {cmd} -e py,js,ts
    {cmd} -x log,tmp,bak
    {cmd} -s tests,build,node_modules

  Include options:
    {cmd} --include-files "config.local.py,secret.env"
    {cmd} --only-include-files "main.py,README.md"
    
  Combined usage:
    {cmd} -s tests --include-files "important-test.py" --console
    {cmd} -e py --tree-exclude "venv,.git" --console

  Alternative command:
    analyze-project --help
        """
    )

    parser.add_argument('-f', '--folder', default=os.getcwd(),
                        help='Directory to process (default: current directory)')

    parser.add_argument('-s', '--skip', default='',
                        help='Comma-separated list of directories to exclude from file processing (also used for tree unless --tree-exclude is specified)')

    parser.add_argument('-e', '--extensions', default='',
                        help='Comma-separated list of file extensions to include')

    parser.add_argument('-x', '--exclude-ext', default='',
                        help='Comma-separated list of file extensions to exclude')

    parser.add_argument('-i', '--ignore-files', default='',
                        help='Comma-separated list of specific files to exclude')

    parser.add_argument('--include-files', default='',
                        help='Force include specific files (overrides skip/binary detection, scans other files too)')

    parser.add_argument('--only-include-files', default='',
                        help='Process ONLY these specific files, ignore everything else')

    parser.add_argument('--max-size', type=int, default=0,
                        help='Maximum file size in bytes to process')

    parser.add_argument('--console', action='store_true',
                        help='Show console output (off by default)')

    parser.add_argument('-o', '--output', default='',
                        help='Output filename (without extension)')

    parser.add_argument('--duplicate', action='store_true',
                        help='Create duplicate output file with timestamp instead of overwriting')

    parser.add_argument('--no-summary', action='store_true',
                        help='Exclude summary from output file')

    # Tree-related arguments
    parser.add_argument('--no-tree', action='store_true',
                        help='Skip directory tree generation')

    parser.add_argument('--tree-exclude', default='',
                        help='Override: Comma-separated list of directories to exclude from tree display (if not specified, uses --skip folders)')

    return parser.parse_args()


def get_script_directory():
    """
    Get the directory where the script is located.

    Returns:
        str: The script directory path
    """
    return os.path.dirname(os.path.abspath(__file__))


def find_config_file():
    """
    Find the config.ini file in multiple possible locations.
    
    Returns:
        str: Path to config.ini file or None if not found
    """
    # Try multiple locations in order of preference
    search_paths = [
        # 1. Current working directory
        os.path.join(os.getcwd(), 'config.ini'),
        # 2. Script directory (for development/local install)
        os.path.join(get_script_directory(), 'config.ini'),
        # 3. Script directory config subdirectory (new organized structure)
        os.path.join(get_script_directory(), 'config', 'config.ini'),
        # 4. User home directory
        os.path.join(os.path.expanduser('~'), '.print-project', 'config.ini'),
        # 5. System config directory (Unix-like)
        '/etc/print-project/config.ini',
        # 6. Windows AppData
        os.path.join(os.environ.get('APPDATA', ''), 'print-project', 'config.ini') if os.name == 'nt' else None
    ]
    
    for path in search_paths:
        if path and os.path.exists(path):
            return path
    
    return None


def load_config():
    """
    Load configuration from a config file.
    Searches multiple locations for config.ini file.
    Now includes trusted_extensions configuration.

    Returns:
        dict: Configuration options
    """
    global TRUSTED_EXTENSIONS
    
    config = configparser.ConfigParser()
    config_path = find_config_file()

    # Default trusted extensions (fallback if not in config)
    default_trusted_extensions = [
        '.md', '.txt', '.sh', '.bash', '.zsh', '.fish', '.py', '.js', '.ts', '.jsx', '.tsx',
        '.java', '.c', '.cpp', '.cc', '.cxx', '.h', '.hpp', '.cs', '.go', '.rs', '.rb', '.php',
        '.css', '.scss', '.sass', '.less', '.html', '.htm', '.xml', '.xhtml', '.vue', '.svelte',
        '.yml', '.yaml', '.json', '.toml', '.ini', '.cfg', '.conf', '.config', '.properties',
        '.sql', '.pl', '.perl', '.r', '.R', '.m', '.mm', '.swift', '.kt', '.kts', '.scala',
        '.clj', '.cljs', '.hs', '.elm', '.ex', '.exs', '.erl', '.hrl', '.lua', '.vim', '.vimrc',
        '.ps1', '.psm1', '.bat', '.cmd', '.dockerfile', '.makefile', '.cmake', '.gradle',
        '.sbt', '.gemfile', '.rakefile', '.podfile', '.cartfile', '.nixos', '.nix'
    ]

    defaults = {
        'skip_folders': '',
        'extensions': '',
        'exclude_ext': '',
        'ignore_files': '',
        'include_files': '',
        'only_include_files': '',
        'trusted_extensions': ','.join(default_trusted_extensions),
        'tree_exclude': '',  # Empty by default - will use skip_folders
        'max_file_size': '0',
        'console': 'False',
        'no_summary': 'False',
        'no_tree': 'False'
    }

    if config_path and os.path.exists(config_path):
        config.read(config_path)
        print(f"Using config file: {config_path}")
        if 'DEFAULT' in config:
            config_dict = {
                'skip_folders': config['DEFAULT'].get('skip_folders', defaults['skip_folders']),
                'extensions': config['DEFAULT'].get('extensions', defaults['extensions']),
                'exclude_ext': config['DEFAULT'].get('skip_extensions', defaults['exclude_ext']),
                'ignore_files': config['DEFAULT'].get('skip_files', defaults['ignore_files']),
                'include_files': config['DEFAULT'].get('include_files', defaults['include_files']),
                'only_include_files': config['DEFAULT'].get('only_include_files', defaults['only_include_files']),
                'trusted_extensions': config['DEFAULT'].get('trusted_extensions', defaults['trusted_extensions']),
                'tree_exclude': config['DEFAULT'].get('tree_exclude', defaults['tree_exclude']),
                'max_file_size': config['DEFAULT'].get('max_file_size', defaults['max_file_size']),
                'console': config['DEFAULT'].get('console', defaults['console']),
                'no_summary': config['DEFAULT'].get('no_summary', defaults['no_summary']),
                'no_tree': config['DEFAULT'].get('no_tree', defaults['no_tree'])
            }
        else:
            config_dict = defaults
    else:
        # No config file found, use defaults
        if config_path is None:
            print("No config file found in standard locations, using built-in defaults")
        else:
            print(f"Config file not found: {config_path}, using built-in defaults")
        config_dict = defaults

    # Process trusted extensions and set global variable
    trusted_ext_list = [ext.strip() for ext in config_dict['trusted_extensions'].split(',') if ext.strip()]
    TRUSTED_EXTENSIONS = set(trusted_ext_list)
    
    # Print loaded trusted extensions for debugging
    print(f"Loaded {len(TRUSTED_EXTENSIONS)} trusted extensions from config")
    
    return config_dict


def merge_options(args, config):
    """
    Merge command line arguments with configuration file options.
    Command line arguments take precedence.
    Updated with new include options and smart tree exclusion logic.

    Args:
        args: Command line arguments
        config: Configuration from file

    Returns:
        dict: Combined options
    """
    options = {}

    # Convert string lists to actual lists
    options['skip_folders'] = args.skip.split(',') if args.skip else config['skip_folders'].split(',')
    options['skip_folders'] = [folder.strip() for folder in options['skip_folders'] if folder.strip()]

    options['extensions'] = args.extensions.split(',') if args.extensions else config['extensions'].split(',')
    options['extensions'] = [ext.strip() for ext in options['extensions'] if ext.strip()]

    options['exclude_ext'] = args.exclude_ext.split(',') if args.exclude_ext else config['exclude_ext'].split(',')
    options['exclude_ext'] = [ext.strip() for ext in options['exclude_ext'] if ext.strip()]

    options['ignore_files'] = args.ignore_files.split(',') if args.ignore_files else config['ignore_files'].split(',')
    options['ignore_files'] = [file.strip() for file in options['ignore_files'] if file.strip()]

    # Updated include options
    options['include_files'] = args.include_files.split(',') if args.include_files else config['include_files'].split(',')
    options['include_files'] = [file.strip() for file in options['include_files'] if file.strip()]

    options['only_include_files'] = args.only_include_files.split(',') if args.only_include_files else config['only_include_files'].split(',')
    options['only_include_files'] = [file.strip() for file in options['only_include_files'] if file.strip()]

    # Smart tree exclusion logic
    # Check if tree_exclude was explicitly specified
    tree_exclude_explicit = bool(args.tree_exclude) or bool(config['tree_exclude'])
    options['tree_exclude_explicit'] = tree_exclude_explicit
    
    if args.tree_exclude:
        # Command line tree_exclude takes precedence
        options['tree_exclude'] = [folder.strip() for folder in args.tree_exclude.split(',') if folder.strip()]
    elif config['tree_exclude']:
        # Config file tree_exclude
        options['tree_exclude'] = [folder.strip() for folder in config['tree_exclude'].split(',') if folder.strip()]
    else:
        # Default: empty (will use skip_folders)
        options['tree_exclude'] = []

    # Boolean and integer options
    options['max_size'] = args.max_size if args.max_size else int(config['max_file_size'])
    options['console'] = args.console if args.console else config['console'].lower() == 'true'
    options['no_summary'] = args.no_summary if args.no_summary else config['no_summary'].lower() == 'true'
    options['no_tree'] = args.no_tree if args.no_tree else config['no_tree'].lower() == 'true'
    options['duplicate'] = args.duplicate
    options['output'] = args.output

    return options





if __name__ == "__main__":
    sys.exit(main())


"""
## Usage Examples & Scenarios

### **Basic Usage with Tree Structure**
```bash
# Scan current directory with tree structure (tree uses same exclusions as file processing)
print-project

# Scan specific directory with console output
print-project -f /path/to/project --console

# Skip common directories - both file processing AND tree will exclude them
print-project -s "tests,docs,build,node_modules"
```

### **Tree Customization**
```bash
# Skip tree generation entirely
print-project --no-tree

# Tree uses different exclusions than file processing
print-project -s "tests,docs" --tree-exclude ".git,venv,__pycache__"
# Files: excludes tests,docs directories
# Tree: excludes .git,venv,__pycache__ directories

# Show full project structure but process limited files
print-project -s "tests,build,docs,logs,temp" --tree-exclude ".git,node_modules"
# Tree shows more structure, file processing is more selective
```

### **File Extension Filtering (Tree Shows All)**
```bash
# Only Python and JavaScript files (tree shows all directories)
print-project -e py,js,ts,jsx
# Files: only .py, .js, .ts, .jsx files processed
# Tree: shows complete directory structure

# Exclude log and temporary files
print-project -x log,tmp,bak,cache
# Files: excludes these extensions
# Tree: shows all directories
```

### **Force Include Scenarios**
```bash
# Include important config files that might be skipped
print-project --include-files "config.local.properties,.env.production,secret.yaml"

# Include specific test files while skipping test directories
print-project -s tests,test --include-files "critical-test.py,integration-test.js"
# File processing: skips test directories but includes specific test files
# Tree: also excludes test directories from structure

# Include README files that might be filtered out
python print_project.py -e py --include-files "README.md,CHANGELOG.md"
```

### **Only Include Scenarios**
```bash
# Process only core application files (tree still shows structure)
python print_project.py --only-include-files "main.py,config.py,utils.py"

# Quick documentation of specific files with no tree
python print_project.py --only-include-files "README.md,API.md,INSTALL.md" --no-tree

# Focus on configuration files only
python print_project.py --only-include-files "application.yml,database.properties,nginx.conf"
```

### **Advanced Tree + File Processing Combinations**
```bash
# Show clean tree but process more files
python print_project.py -s "tests" --tree-exclude ".git,venv,node_modules,build,dist"

# Minimal tree, comprehensive file processing
python print_project.py --tree-exclude ".git,venv,node_modules,build,dist,docs,temp,logs"

# Skip build directories but include important build files
python print_project.py -s build,dist,target --include-files "Dockerfile,docker-compose.yml"

# Only Python files + force include shell scripts + clean tree
python print_project.py -e py --include-files "deploy.sh,setup.sh,run.sh" --tree-exclude ".git,venv" --console

# Custom output with timestamp for archival
python print_project.py --include-files "CRITICAL.md" -o security_audit --duplicate
```

### **Project-Specific Scenarios**

#### **Python Project Analysis**
```bash
# Standard Python project
python print_project.py -s "__pycache__,venv,.pytest_cache" --tree-exclude ".git,venv,__pycache__"

# Django project
python print_project.py -e py,html,css,js --tree-exclude ".git,venv,static_collected,media"

# Data science project
python print_project.py -e py,ipynb,yml --include-files "requirements.txt,environment.yml"
```

#### **JavaScript/Node.js Projects**
```bash
# React/Vue project
python print_project.py -e js,jsx,ts,tsx,vue --tree-exclude ".git,node_modules,dist,build"

# Full-stack project
python print_project.py -s "node_modules,build" --tree-exclude ".git,node_modules,dist,coverage"

# Include package files
python print_project.py -e js,ts --include-files "package.json,package-lock.json,tsconfig.json"
```

#### **Java Enterprise Projects**
```bash
# Spring Boot project
python print_project.py -e java,xml,yml,properties --tree-exclude ".git,target,.idea,.gradle"

# Maven project
python print_project.py -s "target,.idea" --include-files "pom.xml" --tree-exclude ".git,target"

# Gradle project
python print_project.py -s "build,.gradle" --include-files "build.gradle,gradle.properties"
```

#### **Multi-language Projects**
```bash
# Backend + Frontend
python print_project.py -e py,js,ts,java,yml --tree-exclude ".git,node_modules,target,venv"

# Microservices architecture
python print_project.py -s "target,node_modules,venv" --tree-exclude ".git,build,dist"
```

### **Documentation and Analysis Workflows**

#### **Code Review Preparation**
```bash
# Comprehensive review with clean tree structure
python print_project.py -e py,js,ts,java --include-files "README.md,CHANGELOG.md" --tree-exclude ".git,node_modules,build"

# Security-focused review
python print_project.py --include-files ".env,.env.local,secrets.yml,config.properties" --tree-exclude ".git,node_modules"
```

#### **Documentation Generation**
```bash
# Only documentation files with minimal tree
python print_project.py --only-include-files "README.md,ARCHITECTURE.md,API.md,CHANGELOG.md" --tree-exclude ".git,node_modules,build,docs/build"

# Architecture documentation with structure focus
python print_project.py --only-include-files "ARCHITECTURE.md,README.md" --tree-exclude ".git"
```

#### **AI Code Analysis Preparation**
```bash
# Clean codebase without tests but with structure
python print_project.py -s tests,test --include-files "TestConfig.java,test-utils.py" --console

# Core logic only with minimal tree
python print_project.py -e py,js,java --tree-exclude ".git,tests,docs,examples,samples"

# Configuration and core files
python print_project.py -e py,yml,json --include-files "Dockerfile,docker-compose.yml"
```

#### **Project Migration/Archive**
```bash
# Complete project snapshot
python print_project.py --tree-exclude ".git" -o project_snapshot --duplicate

# Source code only
python print_project.py -s "tests,docs,examples" --tree-exclude ".git,build,dist,node_modules"

# Essential files for deployment
python print_project.py --include-files "Dockerfile,docker-compose.yml,requirements.txt,package.json" -o deployment_files
```

### **Configuration-based Usage**

#### **Using config.ini defaults**
```bash
# Uses all config.ini settings
python print_project.py

# Override only tree exclusions
python print_project.py --tree-exclude ".git,venv"

# Override only file processing exclusions
python print_project.py -s "tests,build"
```

#### **Environment-specific configs**
```bash
# Development environment (show more)
python print_project.py --tree-exclude ".git"

# Production analysis (show less)
python print_project.py -s "tests,docs,examples" --tree-exclude ".git,tests,docs,examples,temp,logs"
```

### **Debugging and Troubleshooting**
```bash
# See what's being excluded and why
python print_project.py --console

# Check tree vs file processing differences
python print_project.py -s "tests" --tree-exclude ".git" --console

# Minimal exclusions for debugging
python print_project.py --tree-exclude ".git" --console
```

### **Performance Optimization**
```bash
# Large projects - skip tree for faster processing
python print_project.py --no-tree -s "node_modules,build,dist"

# Small projects - full analysis
python print_project.py --tree-exclude ".git"

# Specific file analysis with structure context
python print_project.py --only-include-files "main.py,config.py" --tree-exclude ".git,venv"
```

## Error Handling & Validation
```bash
# This will show an error - conflicting include options
python print_project.py --include-files "a.py" --only-include-files "b.py"

# This works - different exclusions for tree vs files
python print_project.py -s "tests,docs" --tree-exclude ".git,venv"

# This works - tree follows file exclusions
python print_project.py -s "tests,docs,build"
```

## Pro Tips

### **Quick Project Assessment**
```bash
# See structure + key files only
python print_project.py --only-include-files "README.md,package.json,requirements.txt"

# Architecture overview
python print_project.py --tree-exclude ".git,node_modules,build" --no-summary
```

### **Team Collaboration**
```bash
# Standardized project documentation
python print_project.py -o team_review --duplicate --console

# Code review package
python print_project.py -e py,js,ts --include-files "CHANGELOG.md" -o code_review
```

### **Different Analysis Depths**
```bash
# Surface-level analysis
python print_project.py --tree-exclude ".git,tests,docs,examples" -e py,js

# Deep analysis
python print_project.py --tree-exclude ".git" --include-files "test_config.py,setup.cfg"

# Structure-focused
python print_project.py --only-include-files "README.md" --tree-exclude ".git"
```

"""