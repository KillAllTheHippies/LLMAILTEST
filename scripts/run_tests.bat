@echo off
setlocal EnableDelayedExpansion

:: Change to project root directory
cd /d "%~dp0\.."

:: Color definitions
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "NC=[0m"

:: Check Python installation
python --version >nul 2>&1
if !ERRORLEVEL! neq 0 (
	echo %RED%Python is not installed or not in PATH%NC%
	exit /b 1
)

echo %YELLOW%=== Checking Virtual Environment ===%NC%

:: Check if .venv directory exists
if exist .venv (
	echo %GREEN%Found existing virtual environment%NC%
) else (
	echo Creating new virtual environment...
	python -m venv .venv
	if !ERRORLEVEL! neq 0 (
		echo %RED%Virtual environment creation failed%NC%
		exit /b 1
	)
	echo Installing pip in virtual environment...
	python -m ensurepip --upgrade
	if !ERRORLEVEL! neq 0 (
		echo %RED%Pip installation failed%NC%
		exit /b 1
	)
)

:: Activate virtual environment
call .venv\Scripts\activate.bat
if !ERRORLEVEL! neq 0 (
	echo %RED%Virtual environment activation failed%NC%
	exit /b 1
)

echo %YELLOW%=== Installing Dependencies ===%NC%

:: Check if uv is available
where uv >nul 2>&1
if !ERRORLEVEL! equ 0 (
	echo Using uv package installer...
	uv pip install -r requirements.txt
) else (
	echo Using pip package installer...
	pip install -r requirements.txt
)
if !ERRORLEVEL! neq 0 (
	echo %RED%Dependencies installation failed%NC%
	exit /b 1
)

echo %YELLOW%=== Running Tests ===%NC%
python -m llmailtest --test %*
if !ERRORLEVEL! neq 0 (
    echo %RED%Tests failed%NC%
    exit /b 1
)

:: Deactivate virtual environment
if exist .venv\Scripts\deactivate.bat (
    call .venv\Scripts\deactivate.bat
)

exit /b 0
