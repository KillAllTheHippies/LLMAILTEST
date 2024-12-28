import pytest
import requests
from unittest.mock import Mock
from submit_job import CompetitionClient

@pytest.fixture
def mock_response():
    response = Mock(spec=requests.Response)
    response.ok = True
    response.json.return_value = {
        'job_id': '123',
        'team_id': 'team1',
        'scenario': 'level1a',
        'subject': 'Test Subject',
        'body': 'Test Body',
        'scheduled_time': '2023-01-01T00:00:00Z',
        'started_time': '2023-01-01T00:00:01Z',
        'completed_time': None,
        'output': None,
        'objectives': {}
    }
    return response

@pytest.fixture
def mock_error_response():
    response = Mock(spec=requests.Response)
    response.ok = False
    response.json.return_value = {
        'message': 'Error occurred',
        'advice': 'Please check your input'
    }
    return response

@pytest.fixture
def test_client():
    return CompetitionClient("test_api_key", "http://test.com")

@pytest.fixture
def mock_jobs_list():
    return [
        {
            'job_id': '123',
            'team_id': 'team1',
            'scenario': 'level1a',
            'subject': 'Test 1',
            'body': 'Body 1',
            'scheduled_time': '2023-01-01T00:00:00Z',
            'started_time': '2023-01-01T00:00:01Z',
            'completed_time': None,
            'output': None,
            'objectives': {}
        },
        {
            'job_id': '124',
            'team_id': 'team1',
            'scenario': 'level1b',
            'subject': 'Test 2',
            'body': 'Body 2',
            'scheduled_time': '2023-01-01T00:00:00Z',
            'started_time': '2023-01-01T00:00:01Z',
            'completed_time': '2023-01-01T00:00:02Z',
            'output': 'Success',
            'objectives': {'score': 100}
        }
    ]

@pytest.fixture
def mock_completed_job():
    response = Mock(spec=requests.Response)
    response.ok = True
    response.json.return_value = {
        'job_id': '125',
        'team_id': 'team1',
        'scenario': 'level1a',
        'subject': 'Completed Test',
        'body': 'Test Body',
        'scheduled_time': '2023-01-01T00:00:00Z',
        'started_time': '2023-01-01T00:00:01Z',
        'completed_time': '2023-01-01T00:00:02Z',
        'output': 'Success output',
        'objectives': {'score': 95}
    }
    return response