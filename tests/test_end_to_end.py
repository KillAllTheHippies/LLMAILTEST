import unittest
import time
from submit_job import CompetitionClient, Job

class TestEndToEnd(unittest.TestCase):
    def setUp(self):
        self.api_key = "eyJsb2dpbiI6ICJraWxsYWxsdGhlaGlwcGllcyIsICJhcGlfa2V5IjogIjAyNzNhNmZlLTE3OWEtNDEyMi05ODk4LTI1YzE3OTNmN2EyMyJ9"  # Replace with test API key
        self.client = CompetitionClient(self.api_key)
        
    def test_job_creation_and_completion(self):
        # Test creating a new job
        job = self.client.create_job(
            scenario="level2b",
            subject="Test Subject",
            body="Test Body Content"
        )
        
        # Verify job was created with correct initial state
        self.assertIsNotNone(job.job_id)
        self.assertEqual(job.scenario, "level2b")
        self.assertEqual(job.subject, "Test Subject")
        self.assertEqual(job.body, "Test Body Content")
        
        # Wait for job completion (with timeout)
        max_wait_time = 300  # 5 minutes timeout
        start_time = time.time()
        while not job.is_completed and (time.time() - start_time) < max_wait_time:
            time.sleep(30)
            job = self.client.get_job(job.job_id)
            
        # Verify job completed successfully
        self.assertTrue(job.is_completed)
        self.assertIsNotNone(job.completed_time)
        self.assertIsNotNone(job.output)
        
    def test_job_listing(self):
        # Test listing all jobs
        jobs = self.client.list_jobs()
        self.assertIsInstance(jobs, list)
        
        # Verify each job has required attributes
        for job in jobs:
            self.assertIsInstance(job, Job)
            self.assertIsNotNone(job.job_id)
            
    def test_invalid_scenario(self):
        # Test error handling for invalid scenario
        with self.assertRaises(Exception):
            self.client.create_job(
                scenario="invalid_scenario",
                subject="Test Subject",
                body="Test Body"
            )
            
    def test_job_status_retrieval(self):
        # Create a job first
        job = self.client.create_job(
            scenario="level2b",
            subject="Status Test",
            body="Testing status retrieval"
        )
        
        # Test getting job status
        retrieved_job = self.client.get_job(job.job_id)
        self.assertEqual(retrieved_job.job_id, job.job_id)
        self.assertEqual(retrieved_job.subject, "Status Test")
        
if __name__ == "__main__":
    unittest.main()