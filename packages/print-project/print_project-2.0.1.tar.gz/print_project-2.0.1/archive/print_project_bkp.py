#!/usr/bin/env python3
"""
Directory Content Analysis Tool

This script analyzes and extracts the contents of source code files across a project directory structure,
outputting them into a single organized document for easier review and analysis.

Usage:
    python print_project.py [options]

Options:
    -f, --folder PATH           Directory to process (default: current directory)
    -s, --skip DIRS             Comma-separated list of directories to exclude
    -e, --extensions EXTS       Comma-separated list of file extensions to include
    -x, --exclude-ext EXTS      Comma-separated list of file extensions to exclude
    -i, --ignore-files FILES    Comma-separated list of specific files to exclude
    --include-files FILES       Comma-separated list of specific files to include (overrides other filters)
    --max-size SIZE             Maximum file size in bytes to process
    --console                   Show console output (off by default)
    -o, --output FILENAME       Output filename (without extension)
    --duplicate                 Create duplicate output file with timestamp instead of overwriting
    --no-summary                Exclude summary from output file
    -h, --help                  Show this help message and exit
"""

import argparse
import configparser
import datetime
import os
import sys
import time
import chardet


def is_binary_file(file_path, sample_size=8192):
    """
    Check if a file is binary by examining its contents and encoding.

    Args:
        file_path: Path to the file to check.
        sample_size: Number of bytes to check at the beginning of the file.

    Returns:
        bool: True if the file appears to be binary, False otherwise.
    """
    try:
        with open(file_path, 'rb') as f:
            content = f.read(sample_size)

        # Use chardet to detect encoding
        result = chardet.detect(content)
        encoding = result['encoding']
        confidence = result['confidence']

        # If encoding is detected with low confidence, treat as binary
        if confidence < 0.7:
            return True

        # Check for common binary characteristics if encoding is likely text
        if encoding:
            try:
                text = content.decode(encoding)
                # If decoding succeeds, check for an unusually high proportion of non-ASCII characters
                non_ascii_count = sum(1 for char in text if ord(char) > 127)
                if non_ascii_count / len(text) > 0.3:  # Adjust threshold as needed
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
    Determine if a file should be processed based on exclusion rules.

    Args:
        file_path: Path to the file
        options: Dictionary of options including exclusion rules

    Returns:
        (bool, str): Tuple (should_process, reason_if_not)
    """
    # First check if we have specific files to include - this takes precedence
    if options['include_files']:
        file_name = os.path.basename(file_path)
        if file_name in options['include_files']:
            return True, ""
        else:
            return False, "Not in included files list"

    # Get file stats
    try:
        file_stats = os.stat(file_path)
        file_size = file_stats.st_size
    except:
        return False, "Permission denied or file error"

    # Check file size
    if options['max_size'] and file_size > options['max_size']:
        return False, f"Size exceeds limit ({get_human_readable_size(file_size)})"

    # Get file name and extension
    file_name = os.path.basename(file_path)
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

    # Check if binary
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
    skipped_files = {}
    skipped_dirs = []  # Track skipped directories
    total_files = 0

    start_time = time.time()

    # Create header for the output
    project_name = os.path.basename(os.path.abspath(root_dir))
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    header_content = [
        f"# Project: {project_name}",
        f"# Date: {current_time}",
        f"# Directory: {os.path.abspath(root_dir)}",
        f"# Excluded folders: {', '.join(options['skip_folders'])}",
        f"# Excluded extensions: {', '.join(options['exclude_ext'])}",
        f"# Excluded files: {', '.join(options['ignore_files'])}",
    ]

    # Add included files to header if specified
    if options['include_files']:
        header_content.append(f"# Included files: {', '.join(options['include_files'])}")

    header_content.extend(["", ""])
    output_content.extend(header_content)

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
                    # If it's a directory, check if we should process it
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

        # Print progress
        if options['console']:
            sys.stdout.write(f"\rProcessing file {file_idx + 1}/{total_files}: {rel_path}".ljust(80))
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

                # Print file content to console if enabled
                if options['console']:
                    # Clear the current progress line
                    sys.stdout.write("\r" + " " * 80 + "\r")
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
        sys.stdout.write("\r" + " " * 80 + "\r")
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
            f"Files skipped: {sum(len(files) for files in skipped_files.values())}"
        ]

        summary_content.extend(summary_section)

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
        summary_content.append("Processed files:")
        for file_path in processed_files:
            summary_content.append(f"  - {file_path}")

        # Print summary to console if enabled
        if options['console']:
            print("\n".join(summary_section))
            if skipped_dirs:
                print(f"Directories skipped: {len(skipped_dirs)}")
                print("\nSkipped directories:")
                for dir_path in skipped_dirs:
                    print(f"  - {dir_path}")

            print("\nSkip reasons:")
            for reason, files in skipped_files.items():
                print(f"  - {reason}: {len(files)}")

            print("\nProcessed files:")
            for file_path in processed_files:
                print(f"  - {file_path}")

    return output_content, summary_content, {
        'total_files': total_files,
        'processed_files': len(processed_files),
        'skipped_files': skipped_files,
        'skipped_dirs': skipped_dirs,
        'execution_time': time.time() - start_time
    }


def parse_arguments():
    """
    Parse command line arguments.

    Returns:
        argparse.Namespace: The parsed arguments
    """
    parser = argparse.ArgumentParser(description='Directory Content Analysis Tool')

    parser.add_argument('-f', '--folder', default=os.getcwd(),
                        help='Directory to process (default: current directory)')

    parser.add_argument('-s', '--skip', default='',
                        help='Comma-separated list of directories to exclude')

    parser.add_argument('-e', '--extensions', default='',
                        help='Comma-separated list of file extensions to include')

    parser.add_argument('-x', '--exclude-ext', default='',
                        help='Comma-separated list of file extensions to exclude')

    parser.add_argument('-i', '--ignore-files', default='',
                        help='Comma-separated list of specific files to exclude')

    parser.add_argument('--include-files', default='',
                        help='Comma-separated list of specific files to include (overrides other filters)')

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

    return parser.parse_args()


def get_script_directory():
    """
    Get the directory where the script is located.

    Returns:
        str: The script directory path
    """
    return os.path.dirname(os.path.abspath(__file__))


def load_config():
    """
    Load configuration from a config file located in the script directory.

    Returns:
        dict: Configuration options
    """
    config = configparser.ConfigParser()
    script_dir = get_script_directory()
    config_path = os.path.join(script_dir, 'config.ini')

    defaults = {
        'skip_folders': '',
        'extensions': '',
        'exclude_ext': '',
        'ignore_files': '',
        'include_files': '',
        'max_file_size': '0',
        'console': 'False',
        'no_summary': 'False'
    }

    if os.path.exists(config_path):
        config.read(config_path)
        if 'DEFAULT' in config:
            return {
                'skip_folders': config['DEFAULT'].get('skip_folders', defaults['skip_folders']),
                'extensions': config['DEFAULT'].get('extensions', defaults['extensions']),
                'exclude_ext': config['DEFAULT'].get('skip_extensions', defaults['exclude_ext']),
                'ignore_files': config['DEFAULT'].get('skip_files', defaults['ignore_files']),
                'include_files': config['DEFAULT'].get('include_files', defaults['include_files']),
                'max_file_size': config['DEFAULT'].get('max_file_size', defaults['max_file_size']),
                'console': config['DEFAULT'].get('console', defaults['console']),
                'no_summary': config['DEFAULT'].get('no_summary', defaults['no_summary'])
            }

    return defaults


def merge_options(args, config):
    """
    Merge command line arguments with configuration file options.
    Command line arguments take precedence.

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

    options['include_files'] = args.include_files.split(',') if args.include_files else config['include_files'].split(
        ',')
    options['include_files'] = [file.strip() for file in options['include_files'] if file.strip()]

    # Integer and boolean options
    options['max_size'] = args.max_size if args.max_size else int(config['max_file_size'])
    options['console'] = args.console if args.console else config['console'].lower() == 'true'
    options['no_summary'] = args.no_summary if args.no_summary else config['no_summary'].lower() == 'true'
    options['duplicate'] = args.duplicate
    options['output'] = args.output

    return options


def main():
    """Main function to run the script."""
    args = parse_arguments()
    config = load_config()
    options = merge_options(args, config)

    # Get and validate the root directory
    root_dir = os.path.abspath(args.folder)
    if not os.path.isdir(root_dir):
        print(f"Error: '{root_dir}' is not a valid directory")
        return 1

    # Process files
    print(f"Analyzing directory: {root_dir}")
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

    print(f"\nExecution time: {summary['execution_time']:.2f} seconds")
    print(f"Output file: {output_path} ({get_human_readable_size(output_size)})")

    return 0


if __name__ == "__main__":
    sys.exit(main())