@echo off
REM print-project command wrapper for Windows
REM This batch file allows running print-project from anywhere

REM Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0

REM Run the Python script
python "%SCRIPT_DIR%print_project.py" %*