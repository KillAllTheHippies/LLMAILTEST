import pytest
import os
import csv
from unittest.mock import MagicMock, patch
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication, QTableWidgetItem, QMessageBox

from submit_job_gui import SubmitJobWindow
from submit_job import CompetitionClient

# Fixture for QApplication instance
@pytest.fixture(scope="session")
def qapp():
	app = QApplication([])
	yield app
	app.quit()

# Fixture for mocked CompetitionClient
@pytest.fixture
def mock_client():
	client = MagicMock(spec=CompetitionClient)
	client.list_jobs.return_value = []
	return client

# Fixture for SubmitJobWindow instance
@pytest.fixture
def window(qapp, mock_client, tmp_path):
	with patch('submit_job_gui.CompetitionClient', return_value=mock_client):
		jobs_file = tmp_path / "test_jobs.csv"
		window = SubmitJobWindow()
		window.jobs_file = str(jobs_file)
		yield window
		window.close()

class TestSubmitJobWindow:
	def test_init(self, window):
		"""Test initialization of SubmitJobWindow"""
		assert window.sort_column == 0
		assert window.sort_order == Qt.AscendingOrder
		assert len(window.scenarios) == 40
		assert isinstance(window.job_check_timer, QTimer)
		assert isinstance(window.queue_timer, QTimer)
		assert isinstance(window.counter_timer, QTimer)

	def test_submit_job(self, window, mock_client):
		"""Test job submission functionality"""
		# Setup test data
		window.scenario_input = MagicMock()
		window.subject_input = MagicMock()
		window.body_input = MagicMock()
		
		window.scenario_input.text.return_value = "level1a"
		window.subject_input.text.return_value = "Test Subject"
		window.body_input.toPlainText.return_value = "Test Body"
		
		# Test submission
		window.submit_job()
		
		# Verify job was added to queue
		assert len(window.job_processor.job_queue) == 1
		job = window.job_processor.job_queue[0]
		assert job['scenario'] == "level1a"
		assert job['subject'] == "Test Subject"
		assert job['body'] == "Test Body"

	def test_load_jobs(self, window, tmp_path):
		"""Test loading jobs from CSV file"""
		test_jobs = [
			{
				'job_id': '1',
				'scenario': 'level1a',
				'subject': 'Test 1',
				'body': 'Body 1',
				'scheduled_time': '2023-01-01',
				'started_time': '2023-01-01',
				'objectives': "{'email.retrieved': True}"
			}
		]
		
		with open(window.jobs_file, 'w', newline='', encoding='utf-8') as f:
			writer = csv.DictWriter(f, fieldnames=test_jobs[0].keys())
			writer.writeheader()
			writer.writerows(test_jobs)
		
		window.load_jobs()
		
		assert len(window.jobs_data) == 1
		assert window.jobs_data[0]['job_id'] == '1'
		assert 'email.retrieved' in window.objective_columns

	def test_update_rate_limit(self, window):
		"""Test rate limit update functionality"""
		window.rate_limit_input = MagicMock()
		original_limit = window.job_processor.submit_rate_limit
		
		# Test valid input
		window.rate_limit_input.text.return_value = "5"
		window.update_rate_limit()
		assert window.job_processor.submit_rate_limit == 5
		
		# Test invalid input
		window.rate_limit_input.text.return_value = "invalid"
		window.update_rate_limit()
		window.rate_limit_input.setText.assert_called_with(str(5))

	def test_use_as_template(self, window):
		"""Test using existing job as template"""
		test_job = {
			'scenario': 'level1a',
			'subject': 'Template Subject',
			'body': 'Template Body'
		}
		window.selected_job = test_job
		
		window.scenario_input = MagicMock()
		window.subject_input = MagicMock()
		window.body_input = MagicMock()
		
		window.use_as_template()
		
		window.scenario_input.setText.assert_called_with('level1a')
		window.subject_input.setText.assert_called_with('Template Subject')
		window.body_input.setText.assert_called_with('Template Body')

	def test_show_job_details(self, window):
		"""Test job details display"""
		test_job = {
			'job_id': '1',
			'scenario': 'level1a',
			'subject': 'Test Subject',
			'body': 'Test Body',
			'objectives': "{'email.retrieved': True}"
		}
		window.jobs_data = [test_job]
		
		mock_item = MagicMock()
		mock_item.row.return_value = 0
		
		window.jobs_table = MagicMock()
		window.jobs_table.item.return_value = MagicMock()
		window.jobs_table.item().data.return_value = '1'
		
		window.response_text = MagicMock()
		
		window.show_job_details(mock_item)
		
		assert window.selected_job == test_job
		window.response_text.setHtml.assert_called_once()

	def test_fetch_and_update_jobs(self, window, mock_client):
		"""Test fetching and updating jobs from API"""
		mock_job = MagicMock()
		mock_job.job_id = '1'
		mock_job.scenario = 'level1a'
		mock_job.subject = 'Test'
		mock_job.body = 'Test Body'
		mock_job.scheduled_time = '2023-01-01'
		mock_job.started_time = '2023-01-01'
		mock_job.objectives = {'email.retrieved': True}
		
		mock_client.list_jobs.return_value = [mock_job]
		
		window.fetch_and_update_jobs()
		
		assert os.path.exists(window.jobs_file)
		window.load_jobs()
		assert len(window.jobs_data) == 1
		assert window.jobs_data[0]['job_id'] == '1'

	def test_update_submit_counter(self, window):
		"""Test submit counter update"""
		window.jobs_data = [{'id': 1}, {'id': 2}]
		window.jobs_table = MagicMock()
		window.jobs_table.rowCount.return_value = 2
		window.statusBar = MagicMock()
		window.job_processor.job_queue = []
		window.job_processor.last_submit_time = 0
		
		window.update_submit_counter()
		
		assert window.statusBar().showMessage.called

if __name__ == '__main__':
	pytest.main(['-v', __file__])