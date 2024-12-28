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
def window(qapp, mock_client):
    with patch('submit_job_gui.CompetitionClient', return_value=mock_client):
        window = SubmitJobWindow()
        yield window
        window.close()

# Test initialization
def test_window_initialization(window):
    """Test that window initializes with correct default values"""
    assert window.sort_column == 0
    assert window.sort_order == Qt.AscendingOrder
    assert len(window.scenarios) == 40  # Based on the scenarios list in the code
    assert window.jobs_file == "jobs_data.csv"
    assert isinstance(window.job_check_timer, QTimer)
    assert isinstance(window.queue_timer, QTimer)
    assert isinstance(window.counter_timer, QTimer)

# Test scenario list
def test_scenarios_structure(window):
    """Test that scenarios are properly structured"""
    for display_name, value in window.scenarios:
        assert isinstance(display_name, str)
        assert isinstance(value, str)
        assert display_name.startswith("Level")
        assert value.startswith("level")

# Test job submission
@pytest.mark.parametrize("scenario,subject,body,expected_success", [
    ("level1a", "Test Subject", "Test Body", True),
    ("", "", "", False),
])
def test_submit_job(window, scenario, subject, body, expected_success):
    """Test job submission with various inputs"""
    window.scenario_input = MagicMock()
    window.subject_input = MagicMock()
    window.body_input = MagicMock()
    
    window.scenario_input.text.return_value = scenario
    window.subject_input.text.return_value = subject
    window.body_input.toPlainText.return_value = body
    
    with patch.object(window.job_processor, 'submit_job') as mock_submit:
        mock_submit.return_value = expected_success
        window.submit_job()
        mock_submit.assert_called_once_with(scenario, subject, body)

# Test rate limit updates
@pytest.mark.parametrize("input_value,expected_value", [
    ("5", 5),
    ("0", None),  # Should keep previous value
    ("invalid", None),  # Should keep previous value
])
def test_update_rate_limit(window, input_value, expected_value):
    """Test rate limit update with various inputs"""
    window.rate_limit_input = MagicMock()
    window.rate_limit_input.text.return_value = input_value
    original_limit = window.job_processor.submit_rate_limit
    
    window.update_rate_limit()
    
    if expected_value is not None:
        assert window.job_processor.submit_rate_limit == expected_value
    else:
        assert window.job_processor.submit_rate_limit == original_limit

# Test job loading
def test_load_jobs_with_empty_file(window, tmp_path):
    """Test loading jobs from an empty CSV file"""
    test_file = tmp_path / "test_jobs.csv"
    window.jobs_file = str(test_file)
    window.load_jobs()
    assert window.jobs_data == []
    assert window.objective_columns == set()

def test_load_jobs_with_data(window, tmp_path):
    """Test loading jobs from a CSV file with data"""
    test_file = tmp_path / "test_jobs.csv"
    test_data = [
        {
            'job_id': '1',
            'scenario': 'level1a',
            'subject': 'Test',
            'body': 'Test body',
            'scheduled_time': '2023-01-01',
            'started_time': '2023-01-01',
            'objectives': "{'email.retrieved': True}"
        }
    ]
    
    with open(test_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=test_data[0].keys())
        writer.writeheader()
        writer.writerows(test_data)
    
    window.jobs_file = str(test_file)
    window.load_jobs()
    assert len(window.jobs_data) == 1
    assert 'email.retrieved' in window.objective_columns

# Test template functionality
def test_use_as_template_no_selection(window):
    """Test using job as template when no job is selected"""
    window.selected_job = None
    with patch('PySide6.QtWidgets.QMessageBox.warning') as mock_warning:
        window.use_as_template()
        mock_warning.assert_called_once()

def test_use_as_template_with_selection(window):
    """Test using job as template with selected job"""
    test_job = {
        'scenario': 'level1a',
        'subject': 'Test Subject',
        'body': 'Test Body'
    }
    window.selected_job = test_job
    
    window.scenario_input = MagicMock()
    window.subject_input = MagicMock()
    window.body_input = MagicMock()
    
    window.use_as_template()
    
    window.scenario_input.setText.assert_called_with(test_job['scenario'])
    window.subject_input.setText.assert_called_with(test_job['subject'])
    window.body_input.setText.assert_called_with(test_job['body'])

# Test job details display
def test_show_job_details(window):
    """Test displaying job details"""
    test_job = {
        'job_id': '1',
        'scenario': 'level1a',
        'subject': 'Test Subject',
        'body': 'Test Body',
        'objectives': "{'email.retrieved': True}"
    }
    window.jobs_data = [test_job]
    window.response_text = MagicMock()
    
    mock_item = MagicMock()
    mock_item.row.return_value = 0
    
    window.jobs_table = MagicMock()
    window.jobs_table.item.return_value = MagicMock()
    window.jobs_table.item().data.return_value = '1'
    
    window.show_job_details(mock_item)
    
    assert window.selected_job == test_job
    window.response_text.setHtml.assert_called_once()

# Test sorting functionality
def test_sort_table(window):
    """Test table sorting"""
    window.jobs_table = MagicMock()
    window.sort_column = 0
    window.sort_order = Qt.AscendingOrder
    
    window.sort_table(1)
    
    assert window.sort_column == 1
    window.table_manager.apply_filters.assert_called_once()

if __name__ == '__main__':
    pytest.main(['-v', __file__])