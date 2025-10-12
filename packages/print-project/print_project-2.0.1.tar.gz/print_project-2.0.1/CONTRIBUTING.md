# Contributing to Directory Content Analysis Tool

Thank you for your interest in contributing to this project! This document provides guidelines and information for contributors.

## Getting Started

### Prerequisites
- Python 3.6 or higher
- Basic understanding of command-line tools
- Familiarity with Git and GitHub

### Setting Up Development Environment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/smaxiso/print-project.git
   cd print-project
   ```

2. **Test the current version:**
   ```bash
   python print_project.py --help
   python print_project.py --console  # Test with console output
   ```

3. **Review configuration:**
   - Examine `config.ini` for default settings
   - Test with different configuration options

## Development Guidelines

### Code Style
- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings for all functions and classes
- Include type hints where appropriate

### Testing Changes
- Test with various directory structures
- Verify both console and file output
- Test edge cases (empty directories, permission errors, large files)
- Ensure backward compatibility with existing configurations

### Configuration Changes
- Update `config.ini` template if adding new options
- Document new configuration options in README.md
- Maintain backward compatibility when possible

## Types of Contributions

### Bug Reports
When reporting bugs, please include:
- Operating system and Python version
- Command line arguments used
- Directory structure being analyzed
- Complete error message or unexpected output
- Steps to reproduce the issue

### Feature Requests
For new features, please describe:
- Use case and problem being solved
- Proposed solution or approach
- Any configuration options needed
- Impact on existing functionality

### Code Contributions

#### Before Starting
- Check existing issues and pull requests
- Discuss major changes in an issue first
- Ensure your contribution aligns with project goals

#### Making Changes
1. Create a feature branch from `master`
2. Make your changes with clear, atomic commits
3. Update documentation as needed
4. Add tests for new functionality
5. Ensure all existing functionality still works

#### Pull Request Process
1. Update CHANGELOG.md with your changes
2. Update version number if appropriate
3. Ensure README.md reflects any new features or options
4. Test thoroughly on different platforms if possible
5. Submit pull request with clear description

### Documentation Improvements
- README.md updates and clarifications
- Usage example additions
- Configuration documentation
- Code comments and docstrings

## Project Structure

```
print-project/
├── print_project.py          # Main application
├── config.ini               # Default configuration
├── README.md                # Primary documentation
├── CHANGELOG.md             # Version history
├── CONTRIBUTING.md          # This file
└── archive/                 # Archived versions
    ├── README.md            # Archive documentation
    └── print_project_bkp.py  # Previous version
```

## Release Process

### Version Numbering
- Follow [Semantic Versioning](https://semver.org/)
- Major: Breaking changes
- Minor: New features, backward compatible
- Patch: Bug fixes, backward compatible

### Release Checklist
1. Update version number in code
2. Update CHANGELOG.md with release notes
3. Test thoroughly
4. Update documentation
5. Create git tag
6. Update GitHub release

## Configuration Development

### Adding New Options
1. Add to `config.ini` with appropriate default
2. Add command-line argument in `parse_arguments()`
3. Update `merge_options()` function
4. Document in README.md
5. Add usage examples

### Configuration Best Practices
- Provide sensible defaults
- Allow command-line override of all options
- Validate configuration values
- Provide clear error messages for invalid configs

## Testing Scenarios

### Recommended Test Cases
- Empty directories
- Large projects (1000+ files)
- Binary-heavy projects
- Permission-restricted directories
- Various file encodings
- Different operating systems
- Edge cases (very long paths, special characters)

### Performance Testing
- Monitor memory usage with large projects
- Test processing time improvements
- Verify tree generation performance
- Check file size limit handling

## Common Development Tasks

### Adding File Extensions
Update `trusted_extensions` in `config.ini` and ensure binary detection works correctly.

### Modifying Tree Generation
The tree generation logic is in `generate_tree()` and `create_directory_tree()` functions.

### Enhancing Filtering
File filtering logic is centralized in `should_process_file()` function.

### Output Format Changes
Output formatting is handled in `process_files()` function.

## Questions and Support

- **Issues**: Use GitHub Issues for bugs and feature requests
- **Discussions**: Start a discussion for questions or ideas
- **Email**: Contact repository owner for private matters

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help maintain a welcoming environment
- Follow GitHub's community guidelines

## License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to making this tool better for everyone!