"""
Test Runner Module

Provides functionality for running the test suite with various configurations.
"""

import pytest
import sys
import os
from datetime import datetime

def run_tests(integration=False, unit=True, report=True):
	"""
	Run the test suite with specified options
	
	Args:
		integration (bool): Whether to run integration tests
		unit (bool): Whether to run unit tests
		report (bool): Whether to generate a test report
	"""
	# Get the tests directory relative to this file
	tests_dir = os.path.dirname(os.path.abspath(__file__))
	
	# Prepare pytest arguments
	pytest_args = ['-v']  # Verbose output
	
	if report:
		# Create reports directory in project root
		reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(tests_dir))), 'test_reports')
		os.makedirs(reports_dir, exist_ok=True)
		
		# Generate report filename with timestamp
		timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
		report_file = os.path.join(reports_dir, f'test_report_{timestamp}.html')
		pytest_args.extend(['--html', report_file, '--self-contained-html'])

	# Add test selection arguments
	if not integration:
		pytest_args.append('-m not integration')
	if not unit:
		pytest_args.append('-m integration')

	# Add test discovery paths
	pytest_args.extend([
		os.path.join(tests_dir, 'test_submit_job.py'),
		os.path.join(tests_dir, 'test_submit_job_gui.py'),
		os.path.join(tests_dir, 'test_end_to_end.py')
	])

	# Run pytest
	return pytest.main(pytest_args)