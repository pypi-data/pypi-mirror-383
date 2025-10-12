# Universal Print-Project Installer for Windows
# 
# RECOMMENDED: pip install print-project (PyPI - easiest method)
# ALTERNATIVE Usage: 
#   PowerShell: iwr -useb https://raw.githubusercontent.com/smaxiso/print-project/master/scripts/install.ps1 | iex
#   Or: Invoke-WebRequest -Uri "https://raw.githubusercontent.com/smaxiso/print-project/master/scripts/install.ps1" -UseBasicParsing | Invoke-Expression

param(
    [string]$InstallDir = "$env:USERPROFILE\.print-project",
    [string]$BinDir = "$env:USERPROFILE\.local\bin"
)

# Configuration
$RepoUrl = "https://github.com/smaxiso/print-project.git"
$ErrorActionPreference = "Stop"

# Colors for output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Function to check if command exists
function Test-Command {
    param([string]$Command)
    $null = Get-Command $Command -ErrorAction SilentlyContinue
    return $?
}

# Function to install dependencies
function Install-Dependencies {
    Write-Status "Checking dependencies..."
    
    # Check Python
    if (-not (Test-Command "python") -and -not (Test-Command "python3")) {
        Write-Error "Python is not installed. Please install Python 3.6+ first from https://python.org"
        exit 1
    }
    
    # Check pip
    if (-not (Test-Command "pip") -and -not (Test-Command "pip3")) {
        Write-Error "pip is not installed. Please install pip first."
        exit 1
    }
    
    # Check git
    if (-not (Test-Command "git")) {
        Write-Error "git is not installed. Please install git first from https://git-scm.com"
        exit 1
    }
    
    Write-Success "All dependencies found!"
}

# Function to create installation directory
function New-InstallDir {
    Write-Status "Creating installation directories..."
    
    if (-not (Test-Path $BinDir)) {
        New-Item -ItemType Directory -Path $BinDir -Force | Out-Null
    }
    
    if (Test-Path $InstallDir) {
        Write-Warning "Existing installation found. Updating..."
        Remove-Item -Path $InstallDir -Recurse -Force
    }
    
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
    Write-Success "Installation directory created: $InstallDir"
}

# Function to install print-project
function Install-PrintProject {
    Write-Status "Cloning print-project repository..."
    
    try {
        # Clone the repository
        git clone $RepoUrl $InstallDir --quiet
        Set-Location $InstallDir
        
        Write-Status "Installing print-project..."
        
        # Determine Python and pip commands
        $PythonCmd = if (Test-Command "python3") { "python3" } else { "python" }
        $PipCmd = if (Test-Command "pip3") { "pip3" } else { "pip" }
        
        # Install the package
        & $PipCmd install -e . --quiet
        
        Write-Success "print-project installed successfully!"
        
        return $true
    }
    catch {
        Write-Warning "pip install failed. Creating manual installation..."
        return $false
    }
}

# Function to create batch wrapper
function New-BatchWrapper {
    Write-Status "Creating batch wrapper..."
    
    $BatchContent = @"
@echo off
python "$InstallDir\print_project.py" %*
"@
    
    $BatchPath = "$BinDir\print-project.bat"
    $BatchContent | Out-File -FilePath $BatchPath -Encoding ASCII
    
    Write-Success "Batch wrapper created: $BatchPath"
}

# Function to update PATH
function Update-Path {
    Write-Status "Updating PATH environment variable..."
    
    $CurrentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    
    if ($CurrentPath -notlike "*$BinDir*") {
        $NewPath = "$BinDir;$CurrentPath"
        [Environment]::SetEnvironmentVariable("PATH", $NewPath, "User")
        
        # Update current session PATH
        $env:PATH = "$BinDir;$env:PATH"
        
        Write-Success "Added $BinDir to user PATH"
    }
    else {
        Write-Status "$BinDir already in PATH"
    }
}

# Function to verify installation
function Test-Installation {
    Write-Status "Verifying installation..."
    
    # Refresh PATH for current session
    $env:PATH = [Environment]::GetEnvironmentVariable("PATH", "User") + ";" + [Environment]::GetEnvironmentVariable("PATH", "Machine")
    
    try {
        if (Test-Command "print-project") {
            Write-Success "✅ print-project command is available"
            & print-project --help | Out-Null
            Write-Success "✅ print-project command works correctly"
        }
        elseif (Test-Command "analyze-project") {
            Write-Success "✅ analyze-project command is available"
            & analyze-project --help | Out-Null
            Write-Success "✅ analyze-project command works correctly"
        }
        elseif (Test-Path "$BinDir\print-project.bat") {
            Write-Success "✅ Batch wrapper is available"
        }
        else {
            Write-Warning "Commands not found in PATH. You can run directly with:"
            Write-Host "  python $InstallDir\print_project.py --help"
        }
    }
    catch {
        Write-Warning "Verification failed. Direct usage available:"
        Write-Host "  python $InstallDir\print_project.py --help"
    }
}

# Function to show completion message
function Show-Completion {
    Write-Host ""
    Write-Host "🎉 Print-Project installation completed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Usage:" -ForegroundColor Cyan
    
    if (Test-Command "print-project") {
        Write-Host "  print-project --help"
        Write-Host "  print-project --console" 
        Write-Host "  analyze-project --help"
    }
    elseif (Test-Path "$BinDir\print-project.bat") {
        Write-Host "  print-project --help"
        Write-Host "  Or directly: python $InstallDir\print_project.py --help"
    }
    else {
        Write-Host "  python $InstallDir\print_project.py --help"
    }
    
    Write-Host ""
    Write-Host "📖 Documentation: https://github.com/smaxiso/print-project/blob/master/README.md" -ForegroundColor Cyan
    Write-Host "🔧 Configuration: Copy $InstallDir\config.ini to customize settings" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🔄 Restart your terminal to use the commands from anywhere" -ForegroundColor Yellow
    Write-Host ""
}

# Main installation function
function Main {
    Write-Host "🚀 Print-Project Universal Installer (Windows)" -ForegroundColor Magenta
    Write-Host "==============================================" -ForegroundColor Magenta
    Write-Host ""
    
    Write-Status "Installation directory: $InstallDir"
    Write-Status "Binary directory: $BinDir"
    Write-Host ""
    
    try {
        # Run installation steps
        Install-Dependencies
        New-InstallDir
        
        $PipSuccess = Install-PrintProject
        
        if (-not $PipSuccess) {
            New-BatchWrapper
        }
        
        Update-Path
        Test-Installation
        Show-Completion
    }
    catch {
        Write-Error "Installation failed: $($_.Exception.Message)"
        exit 1
    }
}

# Handle script interruption
trap {
    Write-Error "Installation interrupted."
    exit 1
}

# Run main function
Main