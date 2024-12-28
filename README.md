# LLMailTest

A testing framework for evaluating LLM-based email systems.

## Setup

1. Create and activate a virtual environment:

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Unix/MacOS
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

### GUI Application
To run the main GUI application:

```bash
python submit_job_gui.py
```

This will launch the graphical interface where you can:
- Submit new jobs
- View job history
- Monitor job status
- Filter and sort results

### Running Tests

There are multiple ways to run the test suite:

1. Using the batch script (Windows):
```bash
run_tests.bat
```

2. Using the shell script (Unix/MacOS):
```bash
./run_tests.sh
```

3. Using Python directly:
```bash
# Run all tests
python run_tests.py

# Run only integration tests
python run_tests.py --integration

# Run without unit tests
python run_tests.py --no-unit

# Run without generating HTML report
python run_tests.py --no-report
```

Test reports will be generated in the `test_reports` directory.

## Project Structure

```
LLMAILTEST/
├── src/                    # Source code
│   └── llmailtest/        # Main package
│       ├── client/        # API client
│       └── ui/            # GUI components
├── tests/                 # Test files
├── scripts/              # Utility scripts
├── submit_job_gui.py     # Main GUI application
├── submit_job.py         # Core job submission logic
├── run_tests.py          # Test runner script
└── requirements.txt      # Dependencies
```

