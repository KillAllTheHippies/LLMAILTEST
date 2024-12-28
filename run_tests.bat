@echo off
setlocal EnableDelayedExpansion

:: Change to script directory
cd /d "%~dp0"

:: Color definitions for Windows
set RED=[91m
set GREEN=[92m
set YELLOW=[93m
set NC=[0m
set BOLD=[1m

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
if exist .venv\Scripts\activate.bat (
	call .venv\Scripts\activate.bat
) else (
	echo %RED%Virtual environment activation script not found%NC%
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

:: Create test reports directory
mkdir test_reports 2>nul

echo %YELLOW%=== Running Unit Tests ===%NC%
python -m pytest tests/test_submit_job.py tests/test_submit_job_gui.py -v -m "not integration" --html "test_reports\unit_test_report.html"
if !ERRORLEVEL! neq 0 (
	echo %RED%Unit tests failed%NC%
	set TESTS_FAILED=1
)

echo %YELLOW%=== Running Integration Tests ===%NC%
python -m pytest tests/test_integration.py -v --integration --html "test_reports\integration_test_report.html"
if !ERRORLEVEL! neq 0 (
	echo %RED%Integration tests failed%NC%
	set TESTS_FAILED=1
)

echo %YELLOW%=== Running End-to-End Tests ===%NC%
python -m pytest tests/test_end_to_end.py -v --html "test_reports\e2e_test_report.html"
if !ERRORLEVEL! neq 0 (
	echo %RED%End-to-end tests failed%NC%
	set TESTS_FAILED=1
)

:: Deactivate virtual environment
if exist .venv\Scripts\deactivate.bat (
	call .venv\Scripts\deactivate.bat
)

echo %YELLOW%=== Test Summary ===%NC%
echo Test reports are available in the %BOLD%test_reports%NC% directory:
echo - Unit Tests: %BOLD%test_reports/unit_test_report.html%NC%
echo - Integration Tests: %BOLD%test_reports/integration_test_report.html%NC%
echo - End-to-End Tests: %BOLD%test_reports/e2e_test_report.html%NC%

if defined TESTS_FAILED (
	exit /b 1
)
exit /b 0
