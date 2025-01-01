# Contributing to LLMailTest

We welcome contributions from the community! Here's how you can help improve LLMailTest.

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/LLMailTest.git
   ```
3. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```
3. Run tests:
   ```bash
   pytest
   ```

## Contribution Guidelines

### Code Style
- Follow PEP 8 guidelines
- Use type hints for all public methods
- Write docstrings for all public functions
- Keep lines under 100 characters

### Testing
- Write tests for new features
- Maintain 100% test coverage
- Include both unit and integration tests

### Documentation
- Update relevant documentation files
- Add docstrings for new functions/classes
- Include examples where appropriate

### Pull Requests
1. Ensure all tests pass
2. Update documentation
3. Write clear commit messages
4. Describe changes in the PR description
5. Reference related issues

## Reporting Issues
- Check existing issues before creating new ones
- Include steps to reproduce
- Provide error logs if available
- Describe expected vs actual behavior

## Code of Conduct
We follow the [Contributor Covenant](https://www.contributor-covenant.org/). Please be respectful and inclusive in all interactions.
