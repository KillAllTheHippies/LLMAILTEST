"""
Main entry point for the LLMailTest package.
Provides command-line interface for running the GUI or tests.
"""

import sys
import os
import argparse

# Add package root to Python path
package_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if package_root not in sys.path:
	sys.path.insert(0, package_root)

from llmailtest.ui.main_window import main as gui_main
from llmailtest.tests.runner import run_tests

def main():
	# Ensure we're in the project root directory
	os.chdir(package_root)
	parser = argparse.ArgumentParser(description='LLMailTest - LLM Email Testing Framework')
	parser.add_argument('--gui', action='store_true', help='Launch the GUI application')
	parser.add_argument('--test', action='store_true', help='Run the test suite')
	parser.add_argument('--integration', action='store_true', help='Run integration tests')
	parser.add_argument('--no-unit', action='store_true', help='Skip unit tests')
	parser.add_argument('--no-report', action='store_true', help='Skip generating HTML report')
	
	args = parser.parse_args()
	
	if args.test:
		sys.exit(run_tests(
			integration=args.integration,
			unit=not args.no_unit,
			report=not args.no_report
		))
	else:
		# Default to GUI if no arguments provided
		sys.exit(gui_main())

if __name__ == '__main__':
	main()