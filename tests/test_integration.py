import pytest
import time
from submit_job import CompetitionClient, Job

pytestmark = pytest.mark.integration

class TestIntegration:
	@pytest.fixture(scope="class")
	def client(self):
		"""Create a real API client for integration tests"""
		api_key = "eyJsb2dpbiI6ICJraWxsYWxsdGhlaGlwcGllcyIsICJhcGlfa2V5IjogIjAyNzNhNmZlLTE3OWEtNDEyMi05ODk4LTI1YzE3OTNmN2EyMyJ9"
		return CompetitionClient(api_key)

	def test_create_and_get_job(self, client):
		"""Test creating a job and retrieving it"""
		job = client.create_job(
			scenario="level1a",
			subject="Integration Test",
			body="Testing real API integration"
		)
		
		assert job.job_id is not None
		assert job.scenario == "level1a"
		
		retrieved_job = client.get_job(job.job_id)
		assert retrieved_job.job_id == job.job_id
		assert retrieved_job.subject == "Integration Test"

	def test_list_jobs(self, client):
		"""Test listing all jobs"""
		jobs = client.list_jobs()
		assert isinstance(jobs, list)
		if len(jobs) > 0:
			assert isinstance(jobs[0], Job)
			assert jobs[0].job_id is not None

	def test_job_completion_flow(self, client):
		"""Test full job lifecycle including completion"""
		job = client.create_job(
			scenario="level1a",
			subject="Completion Test",
			body="Testing job completion flow"
		)
		
		start_time = time.time()
		timeout = 300  # 5 minutes
		
		while not job.is_completed and (time.time() - start_time) < timeout:
			time.sleep(30)
			job = client.get_job(job.job_id)
		
		if time.time() - start_time >= timeout:
			pytest.skip("Job did not complete within timeout period")
		
		assert job.is_completed
		assert job.completed_time is not None
		assert isinstance(job.objectives, dict)

if __name__ == '__main__':
	pytest.main(['-v', __file__])
