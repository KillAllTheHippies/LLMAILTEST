"""
Job Processor Module

Handles job submission queue and processing logic.
"""

import time
import csv
from typing import List, Dict, Optional
from ..client.submit_job import Job, CompetitionClient

class JobProcessor:
	def __init__(self, parent, client: CompetitionClient, jobs_file: str):
		self.parent = parent
		self.client = client
		self.jobs_file = jobs_file
		self.job_queue: List[Dict] = []
		self.current_job: Optional[Dict] = None
		self.last_submit_time = 0
		self.submit_rate_limit = 30  # seconds between submissions
		self.active_jobs = {}  # Track jobs that are being processed
		
	def check_job_status(self):
		"""Check status of submitted jobs and update display."""
		if not self.current_job or 'job_id' not in self.current_job:
			return

		try:
			response = self.client.get_job(self.current_job['job_id'])
			if response:
				# Update job with latest data
				self.current_job.update({
					'completed_time': response.completed_time if hasattr(response, 'completed_time') else None,
					'output': response.output if hasattr(response, 'output') else '',
					'objectives': str(response.objectives) if hasattr(response, 'objectives') else '{}'
				})
				
				# If job completed, remove from queue and update display
				if hasattr(response, 'completed_time'):
					self.job_queue.pop(0)
					self._save_job_to_csv(response)
					self.current_job = None
					
					# Update table display
					self.parent.table_manager.apply_filters()
		except Exception as e:
			print(f"Error checking job status: {str(e)}")

	def submit_job(self, scenario: str, subject: str, body: str) -> bool:
		"""Queue a new job for submission."""
		if not all([scenario, subject, body]):
			return False
			
		self.job_queue.append({
			'scenario': scenario,
			'subject': subject,
			'body': body,
			'retries': 0,
			'last_response': ''
		})
		return True
		
	def process_job_queue(self):
		"""Process the next job in the queue if ready."""
		if not self.job_queue:
			return

		current_time = time.time()
		time_since_last = current_time - self.last_submit_time
		
		# Check if we need to enforce rate limit
		if not self.parent.override_rate_limit.isChecked():
			if time_since_last < self.submit_rate_limit:
				return

		# Only process new jobs if we don't have a current job
		if not self.current_job:
			self.current_job = self.job_queue[0]
			try:
				response = self.client.create_job(
					self.current_job['scenario'],
					self.current_job['subject'],
					self.current_job['body']
				)
				
				if response:
					# Update job with response data
					self.current_job.update({
						'job_id': response.job_id,
						'scheduled_time': response.scheduled_time,
						'started_time': response.started_time
					})
					
					# Update table immediately
					self.parent.table_manager.apply_filters()
					
					# Update last submit time after successful submission
					self.last_submit_time = current_time
				
			except Exception as e:
				self.current_job['retries'] = self.current_job.get('retries', 0) + 1
				self.current_job['last_response'] = str(e)
				if self.current_job['retries'] >= 3:
					self.job_queue.pop(0)
					self.current_job = None
				
	def _save_job_to_csv(self, job: Job):
		"""Save job details to CSV storage."""
		job_data = {
			'job_id': job.job_id,
			'scenario': job.scenario,
			'subject': job.subject,
			'body': job.body,
			'scheduled_time': job.scheduled_time,
			'started_time': job.started_time,
			'completed_time': job.completed_time,
			'output': job.output,
			'objectives': str(job.objectives)
		}
		
		try:
			with open(self.jobs_file, mode='a', newline='', encoding='utf-8') as f:
				writer = csv.DictWriter(f, fieldnames=job_data.keys())
				if f.tell() == 0:
					writer.writeheader()
				writer.writerow(job_data)
		except Exception as e:
			print(f"Failed to save job to CSV: {e}")