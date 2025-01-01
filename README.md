# LLMailTest - LLM Email Testing Framework

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A comprehensive testing framework for evaluating LLM-based email systems across multiple scenarios and defense mechanisms.

## Features

- **GUI Interface**: Intuitive graphical interface for job submission and monitoring
- **Scenario Testing**: Test across multiple email scenarios and defense levels
- **Job Management**: Track job history, status, and results
- **Reporting**: Generate detailed test reports
- **Extensible**: Modular architecture for adding new test scenarios

## Quick Start

### Prerequisites
- Python 3.9+
- pip package manager

### Installation

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

## Usage

### GUI Application
To run the main GUI application:

```bash
python submit_job_gui.py
```

The interface provides:
- Job submission with scenario selection
- Real-time job status monitoring
- Job history with filtering and sorting
- Detailed job results analysis

### Command Line Interface
For automated testing:

```bash
python submit_job.py --scenario <scenario_name> --subject <email_subject> --body <email_body>
```

### Testing

Run the complete test suite:

```bash
# Windows
run_tests.bat

# Unix/MacOS
./run_tests.sh

# Direct Python execution
python run_tests.py [options]
```

Available options:
- `--integration`: Run only integration tests
- `--no-unit`: Skip unit tests
- `--no-report`: Skip HTML report generation

Test reports are generated in the `test_reports` directory.

## Project Structure

```
LLMAILTEST/
├── src/                    # Source code
│   └── llmailtest/        # Main package
│       ├── client/        # API client
│       └── ui/            # GUI components
├── tests/                 # Test files
├── scripts/              # Utility scripts
├── test_reports/         # Generated test reports
├── submit_job_gui.py     # Main GUI application
├── submit_job.py         # Core job submission logic
├── run_tests.py          # Test runner script
└── requirements.txt      # Dependencies
```

## Documentation

- [User Guide](INSTRUCTIONS.txt) - Detailed usage instructions
- [Developer Guide](DEVELOPERS.md) - Technical documentation for contributors
- [API Reference](docs/api.md) - API documentation

## Contributing

We welcome contributions! Please see our [Contribution Guidelines](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
