import time
import csv
import os
import html
from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import Qt

class JobProcessor:
    def __init__(self, parent, client, jobs_file):
        self.parent = parent
        self.client = client
        self.jobs_file = jobs_file
        self.current_job = None
        self.job_queue = []
        self.last_submit_time = 0
        self.submit_rate_limit = 33  # Initial rate limit of 33 seconds

    def submit_job(self, scenario, subject, body):
        """Submit a new job to the queue"""
        try:
            # Validate inputs
            if not scenario or not subject or not body:
                QMessageBox.warning(self.parent, "Validation Error", "Please fill in all fields")
                return False

            # Create job data dictionary with retries
            job_data = {
                'scenario': scenario,
                'subject': subject,
                'body': body,
                'retries': 0,
                'last_response': ''
            }

            # Add to queue
            self.job_queue.append(job_data)
            
            # Save queue to file
            if self.save_queue_to_csv():
                save_status = "and saved to queue"
            else:
                save_status = "but failed to save to queue"
            
            self.parent.statusBar().showMessage(f"Job queued {save_status}")
            return True

        except Exception as e:
            QMessageBox.critical(self.parent, "Error", f"Failed to queue job: {str(e)}")
            self.parent.statusBar().showMessage("Failed to queue job")
            return False

    def process_job_queue(self):
        """Process queued jobs respecting rate limit"""
        if not self.job_queue:
            return

        current_time = time.time()
        effective_rate_limit = int(self.parent.rate_limit_input.text()) if self.parent.override_rate_limit.isChecked() else self.submit_rate_limit
        
        if not self.parent.override_rate_limit.isChecked() and current_time - self.last_submit_time < effective_rate_limit:
            return

        try:
            # Get next job from queue
            job_data = self.job_queue[0]
            
            # Submit job using client
            try:
                job = self.client.create_job(
                    job_data['scenario'],
                    job_data['subject'], 
                    job_data['body']
                )
                # If successful, remove from queue
                self.job_queue.pop(0)
                self.save_queue_to_csv()
                
                self.current_job = job
                self.last_submit_time = current_time

                # Show initial job info
                self.parent.response_text.setText(f"Job submitted!\nJob ID: {job.job_id}\n\nWaiting for completion...")
                self.parent.statusBar().showMessage(f"Job {job.job_id} submitted, waiting for results...")

                # Start checking job status
                self.parent.job_check_timer.start(5000)  # Check every 5 seconds
                
            except Exception as api_error:
                # Check if it's a rate limit error
                error_str = str(api_error).lower()
                if 'rate limit' in error_str or 'too many requests' in error_str:
                    # Increment retry count and store error
                    job_data['retries'] = job_data.get('retries', 0) + 1
                    job_data['last_response'] = str(api_error)
                    
                    # Use the current effective rate limit for the next attempt
                    self.last_submit_time = current_time
                    
                    # Only increase rate limit if not overriding
                    if not self.parent.override_rate_limit.isChecked():
                        self.submit_rate_limit = 61  # Jump directly to 61s cap when rate limited
                        self.parent.rate_limit_input.setText(str(self.submit_rate_limit))
                        
                    self.parent.statusBar().showMessage(f"Rate limit hit (retry {job_data['retries']}). Next attempt in {effective_rate_limit}s")
                    return
                else:
                    # For other errors, remove job from queue and show error
                    self.job_queue.pop(0)
                    self.save_queue_to_csv()
                    raise

        except Exception as e:
            QMessageBox.critical(self.parent, "Error", f"Failed to submit job: {str(e)}")
            self.parent.statusBar().showMessage("Failed to submit job")

    def check_job_status(self):
        """Check status of current job"""
        try:
            if not self.current_job:
                self.parent.job_check_timer.stop()
                return

            # Get updated job status
            job = self.client.get_job(self.current_job.job_id)
            
            # Create job dictionary for current job
            job_dict = {
                'job_id': job.job_id,
                'scenario': job.scenario,
                'subject': job.subject,
                'body': job.body,
                'scheduled_time': job.scheduled_time,
                'started_time': job.started_time,
                'output': job.output if hasattr(job, 'output') else '',
                'objectives': str(job.objectives) if hasattr(job, 'objectives') else '{}'
            }

            # Update jobs_data with current job
            updated = False
            for i, existing_job in enumerate(self.parent.jobs_data):
                if existing_job['job_id'] == job.job_id:
                    self.parent.jobs_data[i] = job_dict
                    updated = True
                    break
            
            if not updated:
                self.parent.jobs_data.append(job_dict)

            # Store as selected_job for response window clicks
            self.parent.selected_job = job_dict

            # Update display
            self.parent.apply_filters()
            self.parent.highlight_job_in_table(job.job_id)
            
            # Format response text with HTML
            response_html = f"Job ID: {job.job_id}<br>"
            response_html += f"Scenario: {job.scenario}<br>"
            response_html += f"Subject: {job.subject}<br>"
            response_html += f"Body: {job.body}<br>"
            response_html += f"Output: {job.output if hasattr(job, 'output') else ''}<br><br>"
            
            if hasattr(job, 'objectives') and job.objectives:
                response_html += "Objectives:<br>"
                for objective, result in job.objectives.items():
                    status = "✓" if result else "✗"
                    color = "green" if result else "red"
                    response_html += f'<span style="color: {color}">{status} {objective}</span><br>'
            
            self.parent.response_text.setHtml(response_html)
            
            # If job is completed
            if job.is_completed:
                self.parent.job_check_timer.stop()
                self.current_job = None
                
                # If queue is empty, refresh all jobs from API
                if not self.job_queue:
                    try:
                        self.parent.fetch_and_update_jobs()
                        save_status = "and queue refreshed"
                    except Exception as e:
                        print(f"Error refreshing jobs: {str(e)}")
                        save_status = "but failed to refresh queue"
                else:
                    try:
                        self.save_queue_to_csv()
                        save_status = "and saved to file"
                    except Exception as e:
                        print(f"Error updating job in CSV: {str(e)}")
                        save_status = "but failed to save to file"

                self.parent.statusBar().showMessage(f"Job {job.job_id} completed {save_status}")

        except Exception as e:
            self.parent.job_check_timer.stop()
            self.parent.statusBar().showMessage(f"Error checking job status: {str(e)}")

    def save_queue_to_csv(self):
        """Save all jobs including queued ones to CSV file"""
        try:
            # Get all completed jobs (filter out any previous queued jobs)
            completed_jobs = [job for job in self.parent.jobs_data if job['job_id'] != 'queued']
            
            # Convert queued jobs to the same format
            queue_dicts = []
            for job in self.job_queue:
                queue_dict = {
                    'job_id': 'queued',
                    'scenario': job['scenario'],
                    'subject': job['subject'],
                    'body': job['body'],
                    'scheduled_time': '',
                    'started_time': '',
                    'output': '',
                    'objectives': '{}'
                }
                queue_dicts.append(queue_dict)
            
            # Combine completed jobs with queued jobs
            all_jobs = completed_jobs + queue_dicts
            
            # Save to CSV
            with open(self.jobs_file, mode='w', newline='', encoding='utf-8') as file:
                if all_jobs:
                    writer = csv.DictWriter(file, fieldnames=all_jobs[0].keys())
                    writer.writeheader()
                    writer.writerows(all_jobs)
            
            # Update jobs_data to include queued jobs
            self.parent.jobs_data = all_jobs
            
            # Refresh the table display
            self.parent.apply_filters()
            return True
        except Exception as e:
            print(f"Error saving queue to CSV: {str(e)}")
            return False
