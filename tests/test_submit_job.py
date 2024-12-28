import pytest
from unittest.mock import Mock, patch
import requests
from submit_job import Job, CompetitionClient

# Fixtures
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
def client():
	return CompetitionClient("test_api_key")

class TestJob:
	def test_job_initialization(self):
		"""Test Job class initialization with default values"""
		job = Job()
		assert job.job_id is None
		assert job.team_id is None
		assert job.scenario is None
		assert job.subject is None
		assert job.body is None
		assert job.scheduled_time is None
		assert job.started_time is None
		assert job.completed_time is None
		assert job.output is None
		assert job.objectives == {}

	def test_job_initialization_with_values(self):
		"""Test Job class initialization with provided values"""
		job = Job(
			job_id='123',
			team_id='team1',
			scenario='level1a',
			subject='Test',
			body='Test Body',
			scheduled_time='2023-01-01',
			started_time='2023-01-01',
			completed_time='2023-01-02',
			output='Success',
			objectives={'obj1': True}
		)
		assert job.job_id == '123'
		assert job.team_id == 'team1'
		assert job.scenario == 'level1a'
		assert job.subject == 'Test'
		assert job.body == 'Test Body'
		assert job.scheduled_time == '2023-01-01'
		assert job.started_time == '2023-01-01'
		assert job.completed_time == '2023-01-02'
		assert job.output == 'Success'
		assert job.objectives == {'obj1': True}

	def test_is_completed_property(self):
		"""Test is_completed property behavior"""
		job = Job()
		assert not job.is_completed
		
		job.completed_time = '2023-01-01'
		assert job.is_completed

class TestCompetitionClient:
	def test_client_initialization(self):
		"""Test CompetitionClient initialization"""
		client = CompetitionClient("test_key", "http://test.com")
		assert client.api_key == "test_key"
		assert client.api_server == "http://test.com"

	def test_create_job_success(self, client, mock_response):
		"""Test successful job creation"""
		with patch('requests.post', return_value=mock_response):
			job = client.create_job("level1a", "Test Subject", "Test Body")
			assert job.job_id == '123'
			assert job.scenario == 'level1a'
			assert job.subject == 'Test Subject'
			assert job.body == 'Test Body'

	def test_create_job_failure(self, client):
		"""Test job creation with API error"""
		error_response = Mock(spec=requests.Response)
		error_response.ok = False
		error_response.json.return_value = {
			'message': 'Invalid scenario',
			'advice': 'Please check scenario name'
		}

		with patch('requests.post', return_value=error_response):
			with pytest.raises(Exception) as exc_info:
				client.create_job("invalid", "Test", "Test")
			assert "Invalid scenario" in str(exc_info.value)

	def test_get_job_success(self, client, mock_response):
		"""Test successful job retrieval"""
		with patch('requests.get', return_value=mock_response):
			job = client.get_job("123")
			assert job.job_id == '123'
			assert job.scenario == 'level1a'

	def test_get_job_failure(self, client):
		"""Test job retrieval with API error"""
		error_response = Mock(spec=requests.Response)
		error_response.ok = False
		error_response.json.return_value = {
			'message': 'Job not found',
			'advice': 'Check job ID'
		}

		with patch('requests.get', return_value=error_response):
			with pytest.raises(Exception) as exc_info:
				client.get_job("invalid_id")
			assert "Job not found" in str(exc_info.value)

	def test_list_jobs_success(self, client):
		"""Test successful jobs listing"""
		mock_response = Mock(spec=requests.Response)
		mock_response.ok = True
		mock_response.json.return_value = [
			{
				'job_id': '123',
				'scenario': 'level1a',
				'subject': 'Test 1',
				'body': 'Body 1'
			},
			{
				'job_id': '124',
				'scenario': 'level1b',
				'subject': 'Test 2',
				'body': 'Body 2'
			}
		]

		with patch('requests.get', return_value=mock_response):
			jobs = client.list_jobs()
			assert len(jobs) == 2
			assert jobs[0].job_id == '123'
			assert jobs[1].job_id == '124'

	def test_list_jobs_empty(self, client):
		"""Test listing jobs with empty response"""
		mock_response = Mock(spec=requests.Response)
		mock_response.ok = True
		mock_response.json.return_value = []

		with patch('requests.get', return_value=mock_response):
			jobs = client.list_jobs()
			assert len(jobs) == 0

if __name__ == '__main__':
	pytest.main(['-v', __file__])