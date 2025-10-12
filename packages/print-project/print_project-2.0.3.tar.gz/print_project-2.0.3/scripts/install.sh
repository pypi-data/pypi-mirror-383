#!/bin/bash
# Universal Print-Project Installer
# 
# RECOMMENDED: pip install print-project (PyPI - easiest method)
# ALTERNATIVE: curl -sSL https://raw.githubusercontent.com/smaxiso/print-project/master/scripts/install.sh | bash
# Or: wget -qO- https://raw.githubusercontent.com/smaxiso/print-project/master/scripts/install.sh | bash

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/smaxiso/print-project.git"
INSTALL_DIR="$HOME/.local/bin"
PROJECT_DIR="$HOME/.print-project"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# Function to install dependencies
install_dependencies() {
    print_status "Checking dependencies..."
    
    # Check Python
    if ! command_exists python3 && ! command_exists python; then
        print_error "Python is not installed. Please install Python 3.6+ first."
        exit 1
    fi
    
    # Check pip
    if ! command_exists pip3 && ! command_exists pip; then
        print_error "pip is not installed. Please install pip first."
        exit 1
    fi
    
    # Check git
    if ! command_exists git; then
        print_error "git is not installed. Please install git first."
        exit 1
    fi
    
    print_success "All dependencies found!"
}

# Function to create installation directory
create_install_dir() {
    print_status "Creating installation directory..."
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$PROJECT_DIR"
    print_success "Installation directory created: $PROJECT_DIR"
}

# Function to clone and install
install_print_project() {
    print_status "Cloning print-project repository..."
    
    # Remove existing installation if present
    if [ -d "$PROJECT_DIR" ]; then
        print_warning "Existing installation found. Updating..."
        rm -rf "$PROJECT_DIR"
        mkdir -p "$PROJECT_DIR"
    fi
    
    # Clone the repository
    git clone "$REPO_URL" "$PROJECT_DIR" --quiet
    cd "$PROJECT_DIR"
    
    print_status "Installing print-project..."
    
    # Determine Python and pip commands
    if command_exists python3; then
        PYTHON_CMD="python3"
        PIP_CMD="pip3"
    else
        PYTHON_CMD="python"
        PIP_CMD="pip"
    fi
    
    # Install the package
    $PIP_CMD install -e . --quiet
    
    print_success "print-project installed successfully!"
}

# Function to create shell wrapper (if pip install fails)
create_shell_wrapper() {
    print_status "Creating shell wrapper script..."
    
    cat > "$INSTALL_DIR/print-project" << EOF
#!/bin/bash
# Print-Project wrapper script
python3 "$PROJECT_DIR/print_project.py" "\$@"
EOF
    
    chmod +x "$INSTALL_DIR/print-project"
    
    print_success "Shell wrapper created: $INSTALL_DIR/print-project"
}

# Function to update PATH
update_path() {
    local shell_rc=""
    
    # Detect shell and appropriate rc file
    if [[ -n "$BASH_VERSION" ]]; then
        shell_rc="$HOME/.bashrc"
    elif [[ -n "$ZSH_VERSION" ]]; then
        shell_rc="$HOME/.zshrc"
    elif [ -f "$HOME/.profile" ]; then
        shell_rc="$HOME/.profile"
    fi
    
    # Add to PATH if not already present
    if [ -n "$shell_rc" ] && [ -f "$shell_rc" ]; then
        if ! grep -q "$INSTALL_DIR" "$shell_rc"; then
            echo "" >> "$shell_rc"
            echo "# Added by print-project installer" >> "$shell_rc"
            echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> "$shell_rc"
            print_success "Added $INSTALL_DIR to PATH in $shell_rc"
        fi
    fi
}

# Function to verify installation
verify_installation() {
    print_status "Verifying installation..."
    
    # Check if commands are available
    if command_exists print-project; then
        print_success "✅ print-project command is available"
        print_project --help > /dev/null 2>&1 && print_success "✅ print-project command works correctly"
    elif command_exists analyze-project; then
        print_success "✅ analyze-project command is available"
        analyze-project --help > /dev/null 2>&1 && print_success "✅ analyze-project command works correctly"
    elif [ -x "$INSTALL_DIR/print-project" ]; then
        print_success "✅ Shell wrapper is available at $INSTALL_DIR/print-project"
    else
        print_warning "Commands not found in PATH. You can run directly with:"
        echo "  $PROJECT_DIR/print_project.py --help"
    fi
}

# Function to show completion message
show_completion() {
    echo ""
    echo "🎉 Print-Project installation completed!"
    echo ""
    echo "📋 Usage:"
    if command_exists print-project; then
        echo "  print-project --help"
        echo "  print-project --console"
        echo "  analyze-project --help"
    elif [ -x "$INSTALL_DIR/print-project" ]; then
        echo "  print-project --help"
        echo "  Or directly: $PROJECT_DIR/print_project.py --help"
    else
        echo "  python3 $PROJECT_DIR/print_project.py --help"
    fi
    echo ""
    echo "📖 Documentation: https://github.com/smaxiso/print-project/blob/master/README.md"
    echo "🔧 Configuration: Copy $PROJECT_DIR/config.ini to customize settings"
    echo ""
    if [ -n "$shell_rc" ]; then
        echo "🔄 Restart your terminal or run: source $shell_rc"
    fi
    echo ""
}

# Main installation function
main() {
    echo "🚀 Print-Project Universal Installer"
    echo "======================================"
    echo ""
    
    OS=$(detect_os)
    print_status "Detected OS: $OS"
    
    # Check if running as root (not recommended)
    if [ "$EUID" -eq 0 ]; then
        print_warning "Running as root. Installing to /usr/local/bin instead."
        INSTALL_DIR="/usr/local/bin"
        PROJECT_DIR="/opt/print-project"
    fi
    
    print_status "Installation directory: $PROJECT_DIR"
    print_status "Binary directory: $INSTALL_DIR"
    echo ""
    
    # Run installation steps
    install_dependencies
    create_install_dir
    install_print_project
    
    # Try to update PATH
    if [ "$EUID" -ne 0 ]; then
        update_path
    fi
    
    verify_installation
    show_completion
}

# Handle script interruption
trap 'print_error "Installation interrupted."; exit 1' INT TERM

# Run main function
main "$@"