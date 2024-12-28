import pytest
import sys
import os
import argparse
from datetime import datetime

def run_tests(integration=False, unit=True, report=True):
	"""
	Run the test suite with specified options
	
	Args:
		integration (bool): Whether to run integration tests
		unit (bool): Whether to run unit tests
		report (bool): Whether to generate a test report
	"""
	# Ensure tests directory is in path
	tests_dir = os.path.join(os.path.dirname(__file__), 'tests')
	if tests_dir not in sys.path:
		sys.path.append(tests_dir)

	# Prepare pytest arguments
	pytest_args = ['-v']  # Verbose output
	
	if report:
		# Create reports directory if it doesn't exist
		reports_dir = os.path.join(os.path.dirname(__file__), 'test_reports')
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

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Run test suite')
	parser.add_argument('--integration', action='store_true',
					  help='Run integration tests')
	parser.add_argument('--no-unit', action='store_true',
					  help='Skip unit tests')
	parser.add_argument('--no-report', action='store_true',
					  help='Skip generating HTML report')
	
	args = parser.parse_args()
	
	# Run tests with parsed arguments
	exit_code = run_tests(
		integration=args.integration,
		unit=not args.no_unit,
		report=not args.no_report
	)
	
	sys.exit(exit_code)