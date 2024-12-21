import sys
import time
import csv
import os
import html
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
							  QHBoxLayout, QLabel, QLineEdit, QTextEdit, 
							  QPushButton, QMessageBox, QTableWidget, 
							  QTableWidgetItem, QComboBox, QCheckBox, QDialog,
							  QMenu, QSplitter, QSizePolicy)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction

from submit_job import CompetitionClient, Job
from job_analyzer import JobAnalyzer
from defense_filters import load_defense_levels, filter_by_model, filter_by_defense



class JobQueueWindow(QDialog):
		def __init__(self, parent=None):
			super().__init__(parent)
			self.setWindowTitle("Job Queue")
			self.resize(1000, 600)  # Make window larger to accommodate new columns
			self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)
			self.parent = parent  # Store parent reference
			
			layout = QVBoxLayout(self)
			
			# Queue table
			self.queue_table = QTableWidget()
			self.queue_table.setColumnCount(7)  # Add columns for retries and response
			self.queue_table.setHorizontalHeaderLabels(["Scenario", "Subject", "Body", "Status", "Position", "Retries", "Last Response"])
			self.queue_table.horizontalHeader().setStretchLastSection(True)
			self.queue_table.setContextMenuPolicy(Qt.CustomContextMenu)  # Enable custom context menu
			self.queue_table.customContextMenuRequested.connect(self.show_context_menu)  # Connect context menu handler
			layout.addWidget(self.queue_table)
			
			# Close button
			close_button = QPushButton("Close")
			close_button.clicked.connect(self.close)
			layout.addWidget(close_button)

		def update_queue(self, job_queue, current_job):
			"""Update the queue display"""
			self.queue_table.setRowCount(len(job_queue) + (1 if current_job else 0))
			row = 0
			
			# Show current job if exists
			if current_job:
				self.queue_table.setItem(row, 0, QTableWidgetItem(current_job.scenario))
				
				# Add subject with tooltip
				subject_item = QTableWidgetItem(current_job.subject)
				subject_item.setToolTip(current_job.subject)
				self.queue_table.setItem(row, 1, subject_item)
				
				# Add body with tooltip
				body_item = QTableWidgetItem(current_job.body)
				body_item.setToolTip(current_job.body)
				self.queue_table.setItem(row, 2, body_item)
				
				self.queue_table.setItem(row, 3, QTableWidgetItem("Processing"))
				self.queue_table.setItem(row, 4, QTableWidgetItem("Current"))
				# Add retry count and last response if available
				retries = current_job.retries if hasattr(current_job, 'retries') else 0
				last_response = current_job.last_response if hasattr(current_job, 'last_response') else ''
				self.queue_table.setItem(row, 5, QTableWidgetItem(str(retries)))
				self.queue_table.setItem(row, 6, QTableWidgetItem(last_response))
				row += 1
			
			# Show queued jobs
			for i, job in enumerate(job_queue):
				self.queue_table.setItem(row, 0, QTableWidgetItem(job['scenario']))
				
				# Add subject with tooltip
				subject_item = QTableWidgetItem(job['subject'])
				subject_item.setToolTip(job['subject'])
				self.queue_table.setItem(row, 1, subject_item)
				
				# Add body with tooltip
				body_item = QTableWidgetItem(job['body'])
				body_item.setToolTip(job['body'])
				self.queue_table.setItem(row, 2, body_item)
				
				self.queue_table.setItem(row, 3, QTableWidgetItem("Queued"))
				self.queue_table.setItem(row, 4, QTableWidgetItem(str(i + 1)))
				# Add retry count and last response if available
				retries = job.get('retries', 0)
				last_response = job.get('last_response', '')
				self.queue_table.setItem(row, 5, QTableWidgetItem(str(retries)))
				self.queue_table.setItem(row, 6, QTableWidgetItem(last_response))
				row += 1

		def show_context_menu(self, position):
			"""Show context menu for queue table"""
			menu = QMenu()
			
			# Add copy actions
			copy_info_action = QAction("Copy Job Info", self)
			copy_subject_action = QAction("Copy Subject", self)
			copy_body_action = QAction("Copy Body", self)
			copy_subject_body_action = QAction("Copy Subject and Body", self)
			
			# Connect actions to handlers
			copy_info_action.triggered.connect(self.copy_job_info)
			copy_subject_action.triggered.connect(self.copy_subject)
			copy_body_action.triggered.connect(self.copy_body)
			copy_subject_body_action.triggered.connect(self.copy_subject_and_body)
			
			# Add actions to menu
			menu.addAction(copy_info_action)
			menu.addAction(copy_subject_action)
			menu.addAction(copy_body_action)
			menu.addAction(copy_subject_body_action)
			
			# Show menu at cursor position
			menu.exec_(self.queue_table.viewport().mapToGlobal(position))

		def get_selected_jobs(self):
			"""Get list of selected jobs from queue table"""
			selected_rows = set(item.row() for item in self.queue_table.selectedItems())
			selected_jobs = []
			
			for row in selected_rows:
				job_data = {
					'scenario': self.queue_table.item(row, 0).text(),
					'subject': self.queue_table.item(row, 1).text(),
					'body': self.queue_table.item(row, 2).text(),
					'status': self.queue_table.item(row, 3).text()
				}
				selected_jobs.append(job_data)
			
			return selected_jobs

		def copy_job_info(self):
			"""Copy complete job info to clipboard"""
			selected_jobs = self.get_selected_jobs()
			if not selected_jobs:
				return
				
			text = []
			for job in selected_jobs:
				job_text = f"Scenario: {job['scenario']}\n"
				job_text += f"Subject: {job['subject']}\n"
				job_text += f"Body: {job['body']}\n"
				job_text += f"Status: {job['status']}"
				text.append(job_text)
			
			QApplication.clipboard().setText("\n---\n".join(text))

		def copy_subject(self):
			"""Copy just the subject(s) to clipboard"""
			selected_jobs = self.get_selected_jobs()
			if not selected_jobs:
				return
				
			subjects = [job['subject'] for job in selected_jobs]
			QApplication.clipboard().setText("\n".join(subjects))

		def copy_body(self):
			"""Copy just the body/bodies to clipboard"""
			selected_jobs = self.get_selected_jobs()
			if not selected_jobs:
				return
				
			bodies = [job['body'] for job in selected_jobs]
			QApplication.clipboard().setText("\n".join(bodies))

		def copy_subject_and_body(self):
			"""Copy subject and body together to clipboard"""
			selected_jobs = self.get_selected_jobs()
			if not selected_jobs:
				return
				
			text = []
			for job in selected_jobs:
				text.append(f"Subject: {job['subject']}\nBody: {job['body']}")
			
			QApplication.clipboard().setText("\n---\n".join(text))

class SubmitJobWindow(QMainWindow):
	def __init__(self):
		super().__init__()

		# Add scenarios list with display names and filter values
		self.scenarios = [
			("Level 1A: Phi3 with prompt_shield", "level1a"),
			("Level 1B: GPT4-o-mini with prompt_shield", "level1b"),
			("Level 1C: Phi3 with task_tracker", "level1c"),
			("Level 1D: GPT4-o-mini with task_tracker", "level1d"),
			("Level 1E: Phi3 with spotlight", "level1e"),
			("Level 1F: GPT4-o-mini with spotlight", "level1f"),
			("Level 1G: Phi3 with llm_judge", "level1g"),
			("Level 1H: GPT4-o-mini with llm_judge", "level1h"),
			("Level 1I: Phi3 with all", "level1i"),
			("Level 1J: GPT4-o-mini with all", "level1j"),
			("Level 2A: Phi3 with prompt_shield", "level2a"),
			("Level 2B: GPT4-o-mini with prompt_shield", "level2b"),
			("Level 2C: Phi3 with task_tracker", "level2c"),
			("Level 2D: GPT4-o-mini with task_tracker", "level2d"),
			("Level 2E: Phi3 with spotlight", "level2e"),
			("Level 2F: GPT4-o-mini with spotlight", "level2f"),
			("Level 2G: Phi3 with llm_judge", "level2g"),
			("Level 2H: GPT4-o-mini with llm_judge", "level2h"),
			("Level 2I: Phi3 with all", "level2i"),
			("Level 2J: GPT4-o-mini with all", "level2j"),
			("Level 3A: Phi3 with prompt_shield", "level3a"),
			("Level 3B: GPT4-o-mini with prompt_shield", "level3b"),
			("Level 3C: Phi3 with task_tracker", "level3c"),
			("Level 3D: GPT4-o-mini with task_tracker", "level3d"),
			("Level 3E: Phi3 with spotlight", "level3e"),
			("Level 3F: GPT4-o-mini with spotlight", "level3f"),
			("Level 3G: Phi3 with llm_judge", "level3g"),
			("Level 3H: GPT4-o-mini with llm_judge", "level3h"),
			("Level 3I: Phi3 with all", "level3i"),
			("Level 3J: GPT4-o-mini with all", "level3j"),
			("Level 4A: Phi3 with prompt_shield", "level4a"),
			("Level 4B: GPT4-o-mini with prompt_shield", "level4b"),
			("Level 4C: Phi3 with task_tracker", "level4c"),
			("Level 4D: GPT4-o-mini with task_tracker", "level4d"),
			("Level 4E: Phi3 with spotlight", "level4e"),
			("Level 4F: GPT4-o-mini with spotlight", "level4f"),
			("Level 4G: Phi3 with llm_judge", "level4g"),
			("Level 4H: GPT4-o-mini with llm_judge", "level4h"),
			("Level 4I: Phi3 with all", "level4i"),
			("Level 4J: GPT4-o-mini with all", "level4j")
		]

		self.client = CompetitionClient("eyJsb2dpbiI6ICJraWxsYWxsdGhlaGlwcGllcyIsICJhcGlfa2V5IjogIjAyNzNhNmZlLTE3OWEtNDEyMi05ODk4LTI1YzE3OTNmN2EyMyJ9")
		self.jobs_file = "jobs_data.csv"
		self.job_analyzer = JobAnalyzer(csv_path=self.jobs_file)  # Create JobAnalyzer instance
		self.setWindowTitle("Submit Job")
		self.resize(1800, 800)  # Wider window to accommodate the jobs panel
		self.current_job = None
		self.job_check_timer = QTimer()
		self.job_check_timer.timeout.connect(self.check_job_status)
		self.jobs_data = []
		self.job_queue = []  # Queue for pending job submissions
		self.last_submit_time = 0  # Track last submission time
		self.submit_rate_limit = 33  # Initial rate limit of 33 seconds
		self.queue_timer = QTimer()  # Timer for processing queue
		self.queue_timer.timeout.connect(self.process_job_queue)
		self.queue_timer.start(1000)  # Check queue every second
		
		# Add counter timer
		self.counter_timer = QTimer()
		self.counter_timer.timeout.connect(self.update_submit_counter)
		self.counter_timer.start(1000)  # Update every second
		
		self.queue_window = None  # Initialize queue window reference
		self.objective_columns = set()  # Track unique objective names
		self.objective_order = [
			"email.retrieved",
			"defense.undetected",
			"exfil.sent",
			"exfil.destination",
			"exfil.content"
		]
		self.setup_ui()
		self.load_jobs()

	def handle_table_click(self, item):
		"""Handle clicks on table items"""
		self.show_job_details(item)


	def show_job_details(self, item):
		"""Show selected job details in the response panel"""
		row = item.row()
		job_id = self.jobs_table.item(row, 0).data(Qt.UserRole)
		
		# Find matching job in jobs_data
		for job in self.jobs_data:
			if job['job_id'] == job_id:
				# Store current job details for template use
				self.selected_job = job
				
				response_html = f"Job ID: {job['job_id']}<br>"
				response_html += f"Scenario: {job['scenario']}<br>"
				response_html += f"Subject: {job['subject']}<br>"
				response_html += f"Body: <pre style=\"white-space: pre-wrap;\">{html.escape(job['body'])}</pre><br>"
				
				if job['objectives']:
					response_html += "Objectives:<br>"
					objectives = eval(job['objectives'])
					for objective, result in objectives.items():
						status = "✓" if result else "✗"
						color = "green" if result else "red"
						response_html += f'<span style="color: {color}">{status} {objective}</span><br>'
				
				self.response_text.setHtml(response_html)
				break



	def setup_ui(self):
		# Create menu bar
		menubar = self.menuBar()
		file_menu = menubar.addMenu("File")
		view_menu = menubar.addMenu("View")
		
		# Add menu actions
		refresh_action = file_menu.addAction("Refresh")
		refresh_action.triggered.connect(self.fetch_and_update_jobs)
		
		show_queue_action = view_menu.addAction("Show Queue")
		show_queue_action.triggered.connect(self.show_queue_window)

		# Create central widget
		central_widget = QWidget()
		self.setCentralWidget(central_widget)
		main_layout = QVBoxLayout(central_widget)
		
		# Create horizontal splitter
		splitter = QSplitter(Qt.Horizontal)
		splitter.setChildrenCollapsible(True)  # Allow panels to be collapsed
		splitter.setHandleWidth(5)  # Make handles easier to grab
		splitter.setStyleSheet("""
			QSplitter::handle {
				background-color: #CCCCCC;
				border: 1px solid #999999;
				width: 4px;
				margin: 2px;
			}
			QSplitter::handle:hover {
				background-color: #666666;
			}
		""")
		
		# Setup panels
		input_panel = self.setup_input_panel()
		response_panel = self.setup_response_panel()
		self.jobs_panel = self.setup_jobs_panel()
		
		# Set size policies to allow shrinking
		input_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		response_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.jobs_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		
		# Remove any minimum sizes
		input_panel.setMinimumWidth(0)
		response_panel.setMinimumWidth(0)
		self.jobs_panel.setMinimumWidth(0)
		
		# Add panels to splitter
		splitter.addWidget(input_panel)
		splitter.addWidget(response_panel)
		splitter.addWidget(self.jobs_panel)
		
		# Set initial sizes (adjust these values as needed)
		splitter.setSizes([300, 400, 500])
		
		# Add splitter to main layout
		main_layout.addWidget(splitter)
		
		# Add status bar
		self.statusBar().showMessage("Ready")

	def setup_input_panel(self):
		"""Setup the input panel with job submission controls"""
		input_panel = QWidget()
		layout = QVBoxLayout(input_panel)
		
		# Scenario input
		scenario_layout = QHBoxLayout()
		scenario_label = QLabel("Scenario:")
		self.scenario_input = QLineEdit()
		scenario_layout.addWidget(scenario_label)
		scenario_layout.addWidget(self.scenario_input)
		layout.addLayout(scenario_layout)
		
		# Subject input
		subject_layout = QHBoxLayout()
		subject_label = QLabel("Subject:")
		self.subject_input = QLineEdit()
		subject_layout.addWidget(subject_label)
		subject_layout.addWidget(self.subject_input)
		layout.addLayout(subject_layout)
		
		# Body input
		body_label = QLabel("Body:")
		self.body_input = QTextEdit()
		layout.addWidget(body_label)
		layout.addWidget(self.body_input)
		
		# Rate limit input
		rate_layout = QHBoxLayout()
		rate_label = QLabel("Rate Limit (seconds):")
		self.rate_limit_input = QLineEdit(str(self.submit_rate_limit))
		self.rate_limit_input.setFixedWidth(50)
		self.rate_limit_input.editingFinished.connect(self.update_rate_limit)
		
		# Add override checkbox
		self.override_rate_limit = QCheckBox("Override (Testing)")
		self.override_rate_limit.setToolTip("Disable rate limit for testing")
		self.override_rate_limit.stateChanged.connect(self.update_submit_button_state)
		
		rate_layout.addWidget(rate_label)
		rate_layout.addWidget(self.rate_limit_input)
		rate_layout.addWidget(self.override_rate_limit)
		rate_layout.addStretch()
		layout.addLayout(rate_layout)
		
		# Submit button
		self.submit_button = QPushButton("Submit Job")  # Store reference
		self.submit_button.setStyleSheet("""
			QPushButton {
				color: #000000;
				border: 1px solid #000000;
				border-radius: 3px;
				padding: 5px;
				background-color: #228B22;
			}
			QPushButton:hover {
				background-color: #228B22;
			}
		""")  # Initial Forest Green color
		self.submit_button.clicked.connect(self.submit_job)
		layout.addWidget(self.submit_button)
		
		# Add job count label with big font and box
		self.job_count_label = QLabel()
		font = self.job_count_label.font()
		font.setPointSize(18)  # Make font even bigger
		font.setBold(True)     # Make it bold
		self.job_count_label.setFont(font)
		self.job_count_label.setAlignment(Qt.AlignCenter)
		self.job_count_label.setStyleSheet("""
			QLabel {
				border: 2px solid black;
				border-radius: 5px;
				padding: 5px;
				background: transparent;
			}
		""")
		layout.addWidget(self.job_count_label)

		# Add queue table
		self.queue_table = QTableWidget()
		self.queue_table.setColumnCount(7)  # Add columns for retries and response
		self.queue_table.setHorizontalHeaderLabels(["Scenario", "Subject", "Body", "Status", "Position", "Retries", "Last Response"])
		self.queue_table.horizontalHeader().setStretchLastSection(True)
		self.queue_table.setContextMenuPolicy(Qt.CustomContextMenu)  # Enable custom context menu
		self.queue_table.customContextMenuRequested.connect(self.show_context_menu)  # Connect context menu handler
		self.queue_table.setMaximumHeight(200)  # Limit height to keep it compact
		layout.addWidget(self.queue_table)

		# Add stretch to push controls to top
		layout.addStretch() 
		
		return input_panel

	def setup_response_panel(self):
		"""Setup the response panel with text display area"""
		response_panel = QWidget()
		layout = QVBoxLayout(response_panel)
		
		# Template button at top
		template_button = QPushButton("Use as Template")
		template_button.clicked.connect(self.use_as_template)
		layout.addWidget(template_button)
		
		# Response text area
		self.response_text = QTextEdit()
		self.response_text.setReadOnly(True)
		self.response_text.mousePressEvent = self.response_text_clicked
		layout.addWidget(self.response_text)
		
		return response_panel

	def save_job_to_csv(self, job):
		"""Save job details to CSV file"""
		is_new_file = not os.path.exists(self.jobs_file)
		
		job_dict = {
			'job_id': job.job_id,
			'scenario': job.scenario,
			'subject': job.subject,
			'body': job.body,
			'scheduled_time': job.scheduled_time,
			'started_time': job.started_time,
			'output': job.output if hasattr(job, 'output') else '',
			'objectives': str(job.objectives)
		}

		try:
			with open(self.jobs_file, mode='a', newline='', encoding='utf-8') as file:
				writer = csv.DictWriter(file, fieldnames=job_dict.keys())
				if is_new_file:
					writer.writeheader()
				writer.writerow(job_dict)
			self.load_jobs()  # Reload jobs after saving
			return True
		except Exception as e:
			print(f"Error saving job to CSV: {str(e)}")
			return False

	def save_queue_to_csv(self):
		"""Save all jobs including queued ones to CSV file"""
		try:
			# Get all completed jobs (filter out any previous queued jobs)
			completed_jobs = [job for job in self.jobs_data if job['job_id'] != 'queued']
			
			# Convert queued jobs to the same format as completed jobs
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
			self.jobs_data = all_jobs
			
			# Refresh the table display
			self.apply_filters()
			return True
		except Exception as e:
			print(f"Error saving queue to CSV: {str(e)}")
			return False




	def update_rate_limit(self):
		"""Update the submission rate limit based on user input"""
		try:
			new_limit = int(self.rate_limit_input.text())
			if new_limit > 0:
				self.submit_rate_limit = new_limit
			else:
				self.rate_limit_input.setText(str(self.submit_rate_limit))
		except ValueError:
			self.rate_limit_input.setText(str(self.submit_rate_limit))

	def submit_job(self):
		try:
			# Get values from inputs
			scenario = self.scenario_input.text()
			subject = self.subject_input.text()
			body = self.body_input.toPlainText()

			# Validate inputs
			if not scenario or not subject or not body:
				QMessageBox.warning(self, "Validation Error", "Please fill in all fields")
				return

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
			queue_pos = len(self.job_queue)
			
			# Save queue to file and update UI
			if self.save_queue_to_csv():
				save_status = "and saved to queue"
			else:
				save_status = "but failed to save to queue"
			
			# Show and focus queue window
			self.show_queue_window()
			if self.queue_window:
				self.queue_window.raise_()
				self.queue_window.activateWindow()
			
			# Update status immediately
			self.update_submit_counter()


		except Exception as e:
			QMessageBox.critical(self, "Error", f"Failed to queue job: {str(e)}")
			self.statusBar().showMessage("Failed to queue job")

	def process_job_queue(self):
		"""Process queued jobs respecting rate limit"""
		if not self.job_queue:
			return

		current_time = time.time()
		effective_rate_limit = int(self.rate_limit_input.text()) if self.override_rate_limit.isChecked() else self.submit_rate_limit
		
		# Only check rate limit if we're not overriding and have submitted recently
		if not self.override_rate_limit.isChecked() and current_time - self.last_submit_time < effective_rate_limit:
			return

		try:
			# Get next job from queue
			job_data = self.job_queue[0]  # Don't pop yet, wait for successful submission
			
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
				self.response_text.setText(f"Job submitted!\nJob ID: {job.job_id}\n\nWaiting for completion...")
				self.statusBar().showMessage(f"Job {job.job_id} submitted, waiting for results...")

				# Start checking job status
				self.job_check_timer.start(5000)  # Check every 5 seconds
				
			except Exception as api_error:
				# Check if it's a rate limit error
				error_str = str(api_error).lower()
				if 'rate limit' in error_str or 'too many requests' in error_str:
					# Increment retry count and store error
					job_data['retries'] = job_data.get('retries', 0) + 1
					job_data['last_response'] = str(api_error)
					
					# Use the current effective rate limit for the next attempt
					self.last_submit_time = current_time  # Update last attempt time
					
					# Only increase rate limit if not overriding
					if not self.override_rate_limit.isChecked():
						self.submit_rate_limit = 61  # Jump directly to 61s cap when rate limited
						self.rate_limit_input.setText(str(self.submit_rate_limit))
						
					self.statusBar().showMessage(f"Rate limit hit (retry {job_data['retries']}). Next attempt in {effective_rate_limit}s")
					return
				else:
					# For other errors, remove job from queue and show error
					self.job_queue.pop(0)
					self.save_queue_to_csv()
					raise  # Re-raise the error to be caught by outer try-except
			
			# Update queue window and counter after processing
			self.update_queue_window()
			self.update_submit_counter()

		except Exception as e:
			QMessageBox.critical(self, "Error", f"Failed to submit job: {str(e)}")
			self.statusBar().showMessage("Failed to submit job")

	def check_job_status(self):
		try:
			if not self.current_job:
				self.job_check_timer.stop()
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
			for i, existing_job in enumerate(self.jobs_data):
				if existing_job['job_id'] == job.job_id:
					self.jobs_data[i] = job_dict
					updated = True
					break
			
			if not updated:
				self.jobs_data.append(job_dict)

			# Store as selected_job for response window clicks
			self.selected_job = job_dict

			# Update display
			self.apply_filters()
			self.highlight_job_in_table(job.job_id)
			
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
			
			self.response_text.setHtml(response_html)
			
			# If job is completed
			if job.is_completed:
				self.job_check_timer.stop()
				self.current_job = None
				
				# If queue is empty, refresh all jobs from API
				if not self.job_queue:
					try:
						self.fetch_and_update_jobs()
						save_status = "and queue refreshed"
					except Exception as e:
						print(f"Error refreshing jobs: {str(e)}")
						save_status = "but failed to refresh queue"
				else:
					try:
						# Get all completed jobs (filter out any previous queued jobs)
						completed_jobs = [j for j in self.jobs_data if j['job_id'] != 'queued']
						
						# Convert queued jobs to the same format
						queue_dicts = []
						for queued_job in self.job_queue:
							queue_dict = {
								'job_id': 'queued',
								'scenario': queued_job['scenario'],
								'subject': queued_job['subject'],
								'body': queued_job['body'],
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
						save_status = "and saved to file"
					except Exception as e:
						print(f"Error updating job in CSV: {str(e)}")
						save_status = "but failed to save to file"

				self.statusBar().showMessage(f"Job {job.job_id} completed {save_status}")

		except Exception as e:
			self.job_check_timer.stop()
			self.statusBar().showMessage(f"Error checking job status: {str(e)}")



	def load_jobs(self):
		"""Load all jobs from CSV file and update objective columns"""
		self.jobs_data = []
		self.objective_columns = set()
		
		if not os.path.exists(self.jobs_file):
			return

		try:
			with open(self.jobs_file, mode='r', encoding='utf-8') as file:
				reader = csv.DictReader(file)
				jobs = list(reader)
				# Sort jobs by started_time in descending order (most recent first)
				jobs.sort(key=lambda x: x['started_time'] if x['started_time'] else '', reverse=True)
				for row in jobs:
					self.jobs_data.append(row)
					# Extract objective names from the objectives string
					if row['objectives']:
						objectives = eval(row['objectives'])
						self.objective_columns.update(objectives.keys())
			
			# Sort objective columns according to predefined order
			sorted_objectives = [obj for obj in self.objective_order if obj in self.objective_columns]
			remaining_objectives = sorted(obj for obj in self.objective_columns if obj not in self.objective_order)
			self.objective_columns = sorted_objectives + remaining_objectives
			
			# Update table structure with all columns
			total_columns = len(self.base_columns) + len(self.objective_columns) + len(self.time_columns)
			self.jobs_table.setColumnCount(total_columns)
			
			# Set headers in the correct order: scenario, objectives, remaining base columns, time columns
			headers = self.base_columns + list(self.objective_columns) + self.base_columns_after + self.time_columns
			self.jobs_table.setHorizontalHeaderLabels(headers)
			
			# Populate sort combo box
			self.sort_combo.clear()
			self.sort_combo.addItems(headers)
			
			# Find the index of "Started Time" column
			started_time_index = headers.index("Started Time")
			self.sort_column = started_time_index
			self.sort_order = Qt.DescendingOrder
			self.sort_order_btn.setText("↓")
			
			# Set the combo box and sort the table
			self.sort_combo.setCurrentText("Started Time")
			self.sort_combo.currentTextChanged.connect(self.handle_sort_change)
			self.jobs_table.sortItems(self.sort_column, self.sort_order)
			
			self.apply_filters()
		except Exception as e:
			QMessageBox.warning(self, "Error", f"Failed to load jobs: {str(e)}")

	def apply_filters(self):
		"""Apply filters to jobs data and update table"""
		current_index = self.scenario_filter.currentIndex()
		selected_scenario_value = self.scenario_filter.itemData(current_index)
		selected_model = self.model_filter.currentText()
		selected_defense = self.defense_filter.currentText()
		
		# Load defense levels data
		defense_data = load_defense_levels('defense_levels.txt')

		# Get checked objectives
		include_objectives = [obj for obj, cbs in self.objective_checkboxes.items() if cbs['include'].isChecked()]
		exclude_objectives = [obj for obj, cbs in self.objective_checkboxes.items() if cbs['exclude'].isChecked()]
		
		filtered_jobs = []
		for job in self.jobs_data:
			# Apply scenario filter
			if selected_scenario_value != "all" and selected_scenario_value != job['scenario'].lower():
				continue

			# Apply defense filters
			scenario_level = job['scenario'].lower()
			
			if selected_model != "All":
				if selected_model == "Phi3":
					if scenario_level not in defense_data['Phi3']:
						continue
				elif selected_model == "GPT4-o-mini":
					if scenario_level not in defense_data['GPT4-o-mini']:
						continue
						
			if selected_defense != "All":
				if scenario_level not in defense_data[selected_defense]:
					continue
				
			# Apply objectives filter
			if include_objectives or exclude_objectives:
				if not job['objectives']:
					continue
				objectives = eval(job['objectives'])
				
				# Check included objectives
				if include_objectives and not all(objectives.get(obj, False) for obj in include_objectives):
					continue
					
				# Check excluded objectives
				if exclude_objectives and any(objectives.get(obj, False) for obj in exclude_objectives):
					continue
					
			filtered_jobs.append(job)

		# Update table
		self.jobs_table.setRowCount(len(filtered_jobs))
		
		# Update job count label
		total_jobs = len(self.jobs_data)
		filtered_count = len(filtered_jobs)
		if total_jobs == filtered_count:
			self.job_count_label.setText(f"Total Jobs: {total_jobs}")
		else:
			self.job_count_label.setText(f"Showing {filtered_count} of {total_jobs} jobs")
		
		# Calculate total columns and set them
		total_columns = len(self.base_columns) + len(self.objective_columns) + len(self.base_columns_after) + len(self.time_columns)
		self.jobs_table.setColumnCount(total_columns)
		
		# Set headers in correct order
		headers = self.base_columns + list(self.objective_columns) + self.base_columns_after + self.time_columns
		self.jobs_table.setHorizontalHeaderLabels(headers)

		for row, job in enumerate(filtered_jobs):
			col = 0
			
			# Set scenario (first column)
			item = QTableWidgetItem(job['scenario'])
			item.setData(Qt.UserRole, job['job_id'])
			self.jobs_table.setItem(row, col, item)
			col += 1
			
			# Set objective columns
			if job['objectives']:
				objectives = eval(job['objectives'])
				for objective_name in self.objective_columns:
					result = objectives.get(objective_name, False)
					item = QTableWidgetItem('✓' if result else '✗')
					item.setTextAlignment(Qt.AlignCenter)
					item.setForeground(Qt.green if result else Qt.red)
					self.jobs_table.setItem(row, col, item)
					col += 1
			else:
				# Skip objective columns if no objectives
				col += len(self.objective_columns)
			
			# Set remaining base columns
			for base_col in self.base_columns_after:
				key = base_col.lower().replace(' ', '_')
				item = QTableWidgetItem(job[key])
				item.setToolTip(job[key])  # Add tooltip for subject and body
				self.jobs_table.setItem(row, col, item)
				col += 1
			
			# Set time columns
			for time_col in self.time_columns:
				key = time_col.lower().replace(' ', '_')
				timestamp = job[key]
				if timestamp:
					# Store original timestamp as data for sorting
					item = QTableWidgetItem()
					item.setData(Qt.UserRole, timestamp)
					
					if time_col == "Scheduled Time":
						# Calculate relative time for Scheduled Time
						try:
							# Remove fractional seconds and convert T to space
							clean_timestamp = timestamp.split('.')[0].replace('T', ' ')
							timestamp_time = time.strptime(clean_timestamp, "%Y-%m-%d %H:%M:%S")
							timestamp_seconds = time.mktime(timestamp_time)
							current_time = time.time()
							diff_seconds = current_time - timestamp_seconds
							
							# Format relative time
							if diff_seconds < 60:
								display_text = "just now"
							elif diff_seconds < 3600:
								minutes = int(diff_seconds / 60)
								seconds = int(diff_seconds % 60)
								display_text = f"{minutes}m {seconds}s ago"
							elif diff_seconds < 86400:
								hours = int(diff_seconds / 3600)
								minutes = int((diff_seconds % 3600) / 60)
								display_text = f"{hours}h {minutes}m ago"
							else:
								days = int(diff_seconds / 86400)
								hours = int((diff_seconds % 86400) / 3600)
								minutes = int((diff_seconds % 3600) / 60)
								if hours == 0:
									display_text = f"{days}d ago"
								else:
									display_text = f"{days}d {hours}h {minutes}m ago"
							
							item.setText(display_text)
						except:
							item.setText(timestamp)  # Fallback to original if parsing fails
					else:
						# For Started Time, just show the timestamp
						item.setText(timestamp)
					
					item.setToolTip(timestamp)  # Show full timestamp on hover
				else:
					item = QTableWidgetItem('')
				
				self.jobs_table.setItem(row, col, item)
				col += 1

			# Set column widths based on content
			font_metrics = self.jobs_table.fontMetrics()
			for col in range(self.jobs_table.columnCount()):
				header_text = self.jobs_table.horizontalHeaderItem(col).text()
				if header_text == "Scenario":
					width = font_metrics.horizontalAdvance("1234567") + 20  # 7 chars + padding
				elif col < len(self.base_columns) + len(self.objective_columns):
					width = font_metrics.horizontalAdvance("Objective") + 20
				elif header_text in ["Subject", "Body"]:
					width = font_metrics.horizontalAdvance(header_text * 3) + 20
				else:
					width = font_metrics.horizontalAdvance("YYYY-MM-DD HH:MM:SS") + 20
				self.jobs_table.setColumnWidth(col, width)

	def fetch_and_update_jobs(self):
		"""Fetch all jobs from API and update the CSV file"""
		try:
			# Create backup of existing CSV if it exists
			if os.path.exists(self.jobs_file):
				backup_file = f"{self.jobs_file}.bak"
				try:
					os.replace(self.jobs_file, backup_file)
				except Exception as e:
					QMessageBox.warning(self, "Backup Warning", f"Failed to create backup: {str(e)}")
					return

			# Use JobAnalyzer to fetch and save jobs
			self.job_analyzer.fetch_and_save_jobs()
			self.statusBar().showMessage("Successfully updated jobs from API")
			self.load_jobs()  # Reload the table with new data
			
		except Exception as e:
			# Restore backup if operation failed
			if os.path.exists(f"{self.jobs_file}.bak"):
				try:
					os.replace(f"{self.jobs_file}.bak", self.jobs_file)
				except Exception as restore_err:
					QMessageBox.critical(self, "Critical Error", 
						f"Failed to restore backup after error: {str(restore_err)}")
			QMessageBox.critical(self, "Error", f"Failed to fetch jobs from API: {str(e)}")
			self.statusBar().showMessage("Failed to update jobs from API")




	def use_as_template(self):
		"""Populate input fields with selected job details"""
		if hasattr(self, 'selected_job'):
			self.scenario_input.setText(self.selected_job['scenario'])
			self.subject_input.setText(self.selected_job['subject']) 
			self.body_input.setText(self.selected_job['body'])

	def handle_checkbox_change(self, objective, checkbox_type, state):
		"""Handle mutually exclusive checkbox changes"""
		if state == Qt.Checked:
			# Only uncheck the opposite checkbox for this objective
			other_type = 'exclude' if checkbox_type == 'include' else 'include'
			self.objective_checkboxes[objective][other_type].setChecked(False)
		self.apply_filters()

	def handle_sort_change(self, column_name):
		"""Handle sort column selection change"""
		# Find column index
		for i in range(self.jobs_table.columnCount()):
			if self.jobs_table.horizontalHeaderItem(i).text() == column_name:
				self.sort_column = i
				self.jobs_table.sortItems(i, self.sort_order)
				break


	def toggle_sort_order(self):
		"""Toggle between ascending and descending sort order"""
		self.sort_order = Qt.DescendingOrder if self.sort_order == Qt.AscendingOrder else Qt.AscendingOrder
		self.sort_order_btn.setText("↑" if self.sort_order == Qt.AscendingOrder else "↓")
		self.jobs_table.sortItems(self.sort_column, self.sort_order)

	def sort_table(self, column):
		"""Sort table by clicked column header"""
		if self.sort_column == column:
			# Toggle sort order if clicking the same column
			self.sort_order = Qt.DescendingOrder if self.sort_order == Qt.AscendingOrder else Qt.AscendingOrder
			self.sort_order_btn.setText("↑" if self.sort_order == Qt.AscendingOrder else "↓")
		else:
			# Default to ascending order for new column
			self.sort_order = Qt.AscendingOrder
			self.sort_order_btn.setText("↓")
		
		self.sort_column = column
		self.sort_combo.setCurrentText(self.jobs_table.horizontalHeaderItem(column).text())
		
		# Custom sorting for timestamp columns
		header_text = self.jobs_table.horizontalHeaderItem(column).text()
		if header_text in self.time_columns:
			# Sort by the stored timestamp data
			rows = []
			for row in range(self.jobs_table.rowCount()):
				item = self.jobs_table.item(row, column)
				timestamp = item.data(Qt.UserRole) if item else ''
				rows.append((timestamp, row))
			
			# Sort rows based on timestamp
			rows.sort(key=lambda x: x[0] if x[0] else '', reverse=(self.sort_order == Qt.DescendingOrder))
			
			# Reorder table rows
			for new_row, (_, old_row) in enumerate(rows):
				# Take all items from old row
				items = []
				for col in range(self.jobs_table.columnCount()):
					items.append(self.jobs_table.takeItem(old_row, col))
				
				# Put items in new row
				for col, item in enumerate(items):
					if item:
						self.jobs_table.setItem(new_row, col, item)
		else:
			# Use default sorting for other columns
			self.jobs_table.sortItems(column, self.sort_order)

	def update_submit_button_state(self):
		"""Update submit button color based on current state"""
		button_style = """
			QPushButton {
				color: #000000;
				border: 1px solid #000000;
				border-radius: 3px;
				padding: 5px;
				background-color: %s;
			}
			QPushButton:hover {
				background-color: %s;
			}
		"""
		
		if self.override_rate_limit.isChecked():
			self.submit_button.setStyleSheet(button_style % ('#228B22', '#228B22'))  # Forest Green
			return
			
		current_time = time.time()
		time_since_last = current_time - self.last_submit_time
		
		if time_since_last < self.submit_rate_limit:
			# Check if it's rate limited or just counting down
			if any(job.get('retries', 0) > 0 for job in self.job_queue):
				self.submit_button.setStyleSheet(button_style % ('#DC143C', '#DC143C'))  # Bright Crimson
			else:
				self.submit_button.setStyleSheet(button_style % ('#FFA500', '#FFA500'))  # Buddhist Orange
		else:
			self.submit_button.setStyleSheet(button_style % ('#228B22', '#228B22'))  # Forest Green

	def update_submit_counter(self):
		"""Update the submission counter in status bar"""
		total_jobs = len(self.jobs_data)
		filtered_count = self.jobs_table.rowCount()
		jobs_count = f"[{filtered_count} of {total_jobs} jobs] - "
		
		self.update_submit_button_state()  # Update button color
		
		if not self.job_queue:
			self.statusBar().showMessage(f"{jobs_count}Ready - Next submission available")
			return
			
		current_time = time.time()
		time_since_last = current_time - self.last_submit_time
		if time_since_last < self.submit_rate_limit:
			remaining = int(self.submit_rate_limit - time_since_last)
			queue_status = f"{jobs_count}Queue: {len(self.job_queue)} job(s) - Next submission in {remaining}s"
			if self.current_job:
				queue_status = f"{jobs_count}Processing job {self.current_job.job_id} - Queue: {len(self.job_queue)} job(s) - Next submission in {remaining}s"
			self.statusBar().showMessage(queue_status)
		else:
			queue_msg = f"{jobs_count}Queue: {len(self.job_queue)} job(s) - Ready to submit"
			if self.current_job:
				queue_msg = f"{jobs_count}Processing job {self.current_job.job_id} - {queue_msg}"
			self.statusBar().showMessage(queue_msg)

	def highlight_job_in_table(self, job_id):
		"""Highlight the job row in the table"""
		for row in range(self.jobs_table.rowCount()):
			item = self.jobs_table.item(row, 0)
			if item and item.data(Qt.UserRole) == job_id:
				self.jobs_table.selectRow(row)
				break

	def response_text_clicked(self, event):
		"""Handle clicks in the response text area"""
		if hasattr(self, 'selected_job'):
			self.highlight_job_in_table(self.selected_job['job_id'])
		super(QTextEdit, self.response_text).mousePressEvent(event)



			
	def setup_jobs_panel(self):
		jobs_panel = QWidget()
		jobs_layout = QVBoxLayout(jobs_panel)

		# Create vertical layout for controls
		controls_layout = QVBoxLayout()
		controls_layout.setSpacing(5)  # Add some spacing between elements
		
		# Sort controls in their own row
		sort_widget = QWidget()
		sort_layout = QHBoxLayout(sort_widget)
		sort_layout.setContentsMargins(0, 0, 0, 0)
		
		sort_label = QLabel("Sort by:")
		self.sort_combo = QComboBox()
		self.sort_order_btn = QPushButton("↓")
		self.sort_order_btn.setFixedWidth(30)
		self.sort_order_btn.clicked.connect(self.toggle_sort_order)
		
		sort_layout.addWidget(sort_label)
		sort_layout.addWidget(self.sort_combo)
		sort_layout.addWidget(self.sort_order_btn)
		sort_layout.addStretch()  # Push controls to the left
		
		controls_layout.addWidget(sort_widget)

		# Defense filters
		defense_widget = QWidget()
		defense_layout = QHBoxLayout(defense_widget)
		defense_layout.setContentsMargins(0, 0, 0, 0)
		
		# Model filter
		model_label = QLabel("Model:")
		self.model_filter = QComboBox()
		self.model_filter.addItems(["All", "Phi3", "GPT4-o-mini"])
		self.model_filter.currentTextChanged.connect(self.apply_filters)
		
		# Defense type filter  
		defense_label = QLabel("Defense:")
		self.defense_filter = QComboBox()
		self.defense_filter.addItems(["All", "prompt_shield", "task_tracker", "spotlight", "llm_judge", "all defenses"])
		self.defense_filter.currentTextChanged.connect(self.apply_filters)
		
		defense_layout.addWidget(model_label)
		defense_layout.addWidget(self.model_filter)
		defense_layout.addWidget(defense_label)
		defense_layout.addWidget(self.defense_filter)
		defense_layout.addStretch()
		
		controls_layout.addWidget(defense_widget)

		
		# Scenario filter in its own row
		scenario_widget = QWidget()
		scenario_layout = QHBoxLayout(scenario_widget)
		scenario_layout.setContentsMargins(0, 0, 0, 0)
		
		scenario_label = QLabel("Scenario:")
		self.scenario_filter = QComboBox()
		self.scenario_filter.addItem("All Scenarios", "all")
		for display_name, filter_value in self.scenarios:
			self.scenario_filter.addItem(display_name, filter_value)
		self.scenario_filter.currentTextChanged.connect(self.apply_filters)
		
		scenario_layout.addWidget(scenario_label)
		scenario_layout.addWidget(self.scenario_filter)
		scenario_layout.addStretch()  # Push controls to the left
		
		controls_layout.addWidget(scenario_widget)
		
		# Objectives filter
		objectives_widget = QWidget()
		objectives_layout = QVBoxLayout(objectives_widget)
		objectives_layout.setContentsMargins(0, 0, 0, 0)
		objectives_layout.setSpacing(2)
		
		objectives_label = QLabel("Filter by Objectives:")
		objectives_layout.addWidget(objectives_label)
		
		self.objective_checkboxes = {}
		for objective in self.objective_order:
			obj_layout = QHBoxLayout()
			obj_layout.setSpacing(4)
			
			# Include checkbox with label
			include_checkbox = QCheckBox()
			include_checkbox.setToolTip(f"Include results where '{objective}' is successful")
			include_checkbox.setStyleSheet("""
				QCheckBox::indicator {
					width: 15px;
					height: 15px;
				}
				QCheckBox::indicator:unchecked {
					border: 2px solid #999;
					background: white;
				}
				QCheckBox::indicator:checked {
					border: 2px solid #32CD32;
					background: #32CD32;
				}
			""")
			include_checkbox.stateChanged.connect(
				lambda state, obj=objective, type='include': 
				self.handle_checkbox_change(obj, type, state)
			)
			obj_layout.addWidget(include_checkbox)
			
			on_label = QLabel("(on)")
			on_label.setStyleSheet("color: #32CD32;")
			obj_layout.addWidget(on_label)
			
			# Exclude checkbox with label
			exclude_checkbox = QCheckBox()
			exclude_checkbox.setToolTip(f"Exclude results where '{objective}' is successful")
			exclude_checkbox.setStyleSheet("""
				QCheckBox::indicator {
					width: 15px;
					height: 15px;
				}
				QCheckBox::indicator:unchecked {
					border: 2px solid #999;
					background: white;
				}
				QCheckBox::indicator:checked {
					border: 2px solid #FF4040;
					background: #FF4040;
				}
			""")
			exclude_checkbox.stateChanged.connect(
				lambda state, obj=objective, type='exclude': 
				self.handle_checkbox_change(obj, type, state)
			)
			obj_layout.addWidget(exclude_checkbox)
			
			off_label = QLabel("(off)")
			off_label.setStyleSheet("color: #FF4040;")
			obj_layout.addWidget(off_label)
			
			# Add divider
			divider = QLabel("|")
			divider.setStyleSheet("color: #999999;")
			obj_layout.addWidget(divider)
			
			# Objective name
			obj_label = QLabel(objective)
			obj_layout.addWidget(obj_label)
			
			obj_layout.addStretch()
			objectives_layout.addLayout(obj_layout)
			self.objective_checkboxes[objective] = {
				'include': include_checkbox,
				'exclude': exclude_checkbox
			}
		
		controls_layout.addWidget(objectives_widget)
		
		# Refresh button in its own row
		refresh_button = QPushButton("Refresh")
		refresh_button.clicked.connect(self.fetch_and_update_jobs)
		controls_layout.addWidget(refresh_button)
		
		jobs_layout.addLayout(controls_layout)

		# Jobs table
		self.jobs_table = QTableWidget()
		self.base_columns = ["Scenario"]
		self.base_columns_after = ["Subject", "Body"]
		self.time_columns = ["Scheduled Time", "Started Time"]

		self.jobs_table.setColumnCount(len(self.base_columns))
		self.jobs_table.setHorizontalHeaderLabels(self.base_columns)
		self.jobs_table.itemClicked.connect(self.show_job_details)
		self.jobs_table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)  # Enable multi-selection
		self.jobs_table.setContextMenuPolicy(Qt.CustomContextMenu)  # Enable custom context menu
		self.jobs_table.customContextMenuRequested.connect(self.show_context_menu)  # Connect context menu handler

		self.jobs_table.horizontalHeader().sectionClicked.connect(self.sort_table)
		self.sort_column = 0
		self.sort_order = Qt.AscendingOrder
		
		self.jobs_table.setHorizontalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
		self.jobs_table.setVerticalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
		
		jobs_layout.addWidget(self.jobs_table)
		
		return jobs_panel

	def show_queue_window(self):
		"""Update the queue display"""
		self.update_queue_window()


	def update_queue_window(self):
		"""Update the embedded queue table"""
		self.queue_table.setRowCount(len(self.job_queue) + (1 if self.current_job else 0))
		row = 0
		
		# Show current job if exists
		if self.current_job:
			self.queue_table.setItem(row, 0, QTableWidgetItem(self.current_job.scenario))
			
			subject_item = QTableWidgetItem(self.current_job.subject)
			subject_item.setToolTip(self.current_job.subject)
			self.queue_table.setItem(row, 1, subject_item)
			
			body_item = QTableWidgetItem(self.current_job.body)
			body_item.setToolTip(self.current_job.body)
			self.queue_table.setItem(row, 2, body_item)
			
			self.queue_table.setItem(row, 3, QTableWidgetItem("Processing"))
			self.queue_table.setItem(row, 4, QTableWidgetItem("Current"))
			retries = getattr(self.current_job, 'retries', 0)
			last_response = getattr(self.current_job, 'last_response', '')
			self.queue_table.setItem(row, 5, QTableWidgetItem(str(retries)))
			self.queue_table.setItem(row, 6, QTableWidgetItem(str(last_response)))
			row += 1
		
		# Show queued jobs
		for i, job in enumerate(self.job_queue):
			self.queue_table.setItem(row, 0, QTableWidgetItem(job['scenario']))
			
			subject_item = QTableWidgetItem(job['subject'])
			subject_item.setToolTip(job['subject'])
			self.queue_table.setItem(row, 1, subject_item)
			
			body_item = QTableWidgetItem(job['body'])
			body_item.setToolTip(job['body'])
			self.queue_table.setItem(row, 2, body_item)
			
			self.queue_table.setItem(row, 3, QTableWidgetItem("Queued"))
			self.queue_table.setItem(row, 4, QTableWidgetItem(str(i + 1)))
			retries = job.get('retries', 0)
			last_response = job.get('last_response', '')
			self.queue_table.setItem(row, 5, QTableWidgetItem(str(retries)))
			self.queue_table.setItem(row, 6, QTableWidgetItem(str(last_response)))
			row += 1



	def show_context_menu(self, position):
		"""Show context menu for jobs table"""
		menu = QMenu()
		
		# Add copy actions
		copy_info_action = QAction("Copy Job Info", self)
		copy_subject_action = QAction("Copy Subject", self)
		copy_body_action = QAction("Copy Body", self)
		copy_subject_body_action = QAction("Copy Subject and Body", self)
		
		# Connect actions to handlers
		copy_info_action.triggered.connect(self.copy_job_info)
		copy_subject_action.triggered.connect(self.copy_subject)
		copy_body_action.triggered.connect(self.copy_body)
		copy_subject_body_action.triggered.connect(self.copy_subject_and_body)
		
		# Add actions to menu
		menu.addAction(copy_info_action)
		menu.addAction(copy_subject_action)
		menu.addAction(copy_body_action)
		menu.addAction(copy_subject_body_action)
		
		# Show menu at cursor position
		menu.exec_(self.jobs_table.viewport().mapToGlobal(position))

	def get_selected_jobs(self):
		"""Get list of selected jobs from table"""
		selected_rows = set(item.row() for item in self.jobs_table.selectedItems())
		selected_jobs = []
		
		for row in selected_rows:
			job_id = self.jobs_table.item(row, 0).data(Qt.UserRole)
			job = next((job for job in self.jobs_data if job['job_id'] == job_id), None)
			if job:
				selected_jobs.append(job)
		
		return selected_jobs

	def copy_job_info(self):
		"""Copy complete job info to clipboard"""
		selected_jobs = self.get_selected_jobs()
		if not selected_jobs:
			return
			
		text = []
		for job in selected_jobs:
			job_text = f"Scenario: {job['scenario']}\n"
			job_text += f"Subject: {job['subject']}\n"
			job_text += f"Body: {job['body']}\n"
			if job['objectives']:
				job_text += "Objectives:\n"
				objectives = eval(job['objectives'])
				for objective, result in objectives.items():
					status = "✓" if result else "✗"
					job_text += f"{status} {objective}\n"
			text.append(job_text)
		
		QApplication.clipboard().setText("\n---\n".join(text))

	def copy_subject(self):
		"""Copy just the subject(s) to clipboard"""
		selected_jobs = self.get_selected_jobs()
		if not selected_jobs:
			return
			
		subjects = [job['subject'] for job in selected_jobs]
		QApplication.clipboard().setText("\n".join(subjects))

	def copy_body(self):
		"""Copy just the body/bodies to clipboard"""
		selected_jobs = self.get_selected_jobs()
		if not selected_jobs:
			return
			
		bodies = [job['body'] for job in selected_jobs]
		QApplication.clipboard().setText("\n".join(bodies))

	def copy_subject_and_body(self):
		"""Copy subject and body together to clipboard"""
		selected_jobs = self.get_selected_jobs()
		if not selected_jobs:
			return
			
		text = []
		for job in selected_jobs:
			text.append(f"Subject: {job['subject']}\nBody: {job['body']}")
		
		QApplication.clipboard().setText("\n---\n".join(text))


def main():
	app = QApplication(sys.argv)
	window = SubmitJobWindow()
	window.show()
	sys.exit(app.exec())

if __name__ == "__main__":
	main()
