#!/bin/bash
# Make script executable with: chmod +x run_tests.sh

# Change to script directory
cd "$(dirname "$0")"

# Color definitions for Unix
RED='\033[0;91m'
GREEN='\033[0;92m'
YELLOW='\033[0;93m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${YELLOW}=== Checking Virtual Environment ===${NC}"

# Check if .venv directory exists
if [ -d ".venv" ]; then
	echo -e "${GREEN}Found existing virtual environment${NC}"
else
	echo "Creating new virtual environment..."
	python3 -m venv .venv
	if [ $? -ne 0 ]; then
		echo -e "${RED}Virtual environment creation failed${NC}"
		exit 1
	fi
	echo "Installing pip in virtual environment..."
	python3 -m ensurepip --upgrade
	if [ $? -ne 0 ]; then
		echo -e "${RED}Pip installation failed${NC}"
		exit 1
	fi
fi

# Activate virtual environment
if [ -f ".venv/bin/activate" ]; then
	source .venv/bin/activate
else
	echo -e "${RED}Virtual environment activation script not found${NC}"
	exit 1
fi

echo -e "${YELLOW}=== Installing Dependencies ===${NC}"

# Check if uv is available
if command -v uv &> /dev/null; then
	echo "Using uv package installer..."
	uv pip install -r requirements.txt
else
	echo "Using pip package installer..."
	pip install -r requirements.txt
fi

if [ $? -ne 0 ]; then
	echo -e "${RED}Dependencies installation failed${NC}"
	exit 1
fi

# Create test reports directory
mkdir -p test_reports

TESTS_FAILED=0

echo -e "${YELLOW}=== Running Unit Tests ===${NC}"
python -m pytest tests/test_submit_job.py tests/test_submit_job_gui.py -v -m "not integration" --html "test_reports/unit_test_report.html"
if [ $? -ne 0 ]; then
	echo -e "${RED}Unit tests failed${NC}"
	TESTS_FAILED=1
fi

echo -e "${YELLOW}=== Running Integration Tests ===${NC}"
python -m pytest tests/test_integration.py -v --integration --html "test_reports/integration_test_report.html"
if [ $? -ne 0 ]; then
	echo -e "${RED}Integration tests failed${NC}"
	TESTS_FAILED=1
fi

echo -e "${YELLOW}=== Running End-to-End Tests ===${NC}"
python -m pytest tests/test_end_to_end.py -v --html "test_reports/e2e_test_report.html"
if [ $? -ne 0 ]; then
	echo -e "${RED}End-to-end tests failed${NC}"
	TESTS_FAILED=1
fi

# Deactivate virtual environment
deactivate

echo -e "${YELLOW}=== Test Summary ===${NC}"
echo -e "Test reports are available in the ${BOLD}test_reports${NC} directory:"
echo -e "- Unit Tests: ${BOLD}test_reports/unit_test_report.html${NC}"
echo -e "- Integration Tests: ${BOLD}test_reports/integration_test_report.html${NC}"
echo -e "- End-to-End Tests: ${BOLD}test_reports/e2e_test_report.html${NC}"

if [ $TESTS_FAILED -eq 1 ]; then
	exit 1
fi
exit 0