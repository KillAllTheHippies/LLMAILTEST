#!/bin/bash
# Make script executable with: chmod +x run_tests.sh

# Change to project root directory
cd "$(dirname "$0")/.."

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

echo -e "${YELLOW}=== Running Tests ===${NC}"
python -m llmailtest --test "$@"
if [ $? -ne 0 ]; then
	echo -e "${RED}Tests failed${NC}"
	exit 1
fi

# Deactivate virtual environment
deactivate

exit 0
