import sys
import os
import csv
import html
import time
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QSplitter, QMessageBox, QTextEdit, QTableWidgetItem)
from PySide6.QtCore import Qt, QTimer

from submit_job import CompetitionClient
from queue_window import JobQueueWindow

from ui_components import UIPanels
from job_processor import JobProcessor
from table_manager import TableManager
from context_menu import ContextMenuManager

class SubmitJobWindow(QMainWindow):
    """
    Main window for submitting and managing competition jobs.
    
    This class provides a GUI interface for:
    - Submitting new jobs with scenario, subject and body
    - Viewing job history and results 
    - Managing job queue and rate limits
    - Filtering and sorting job results
    - Displaying job objectives and completion status
    
    The window is divided into three panels:
    - Input panel: For submitting new jobs
    - Response panel: Shows selected job details
    - Jobs panel: Table view of all jobs and their status
    """
    def __init__(self):
        """
        Initialize the SubmitJobWindow with all required components.
        
        Sets up:
        - Sort state and column configurations
        - Scenario definitions and objective tracking
        - Core components (client, file storage, managers)
        - UI timers for job processing and updates
        - Window layout and panels
        """
        super().__init__()

        # Initialize sort state
        self.sort_column = 0
        self.sort_order = Qt.AscendingOrder

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

        # Initialize column definitions
        self.base_columns = ["Scenario"]
        self.base_columns_after = ["Subject", "Body"]
        self.time_columns = ["Scheduled Time", "Started Time"]

        # Initialize objective order
        self.objective_order = [
            "email.retrieved",
            "defense.undetected",
            "exfil.sent",
            "exfil.destination",
            "exfil.content"
        ]

        # Initialize objective checkboxes dictionary
        self.objective_checkboxes = {}

        # Initialize core components
        self.client = CompetitionClient("eyJsb2dpbiI6ICJraWxsYWxsdGhlaGlwcGllcyIsICJhcGlfa2V5IjogIjAyNzNhNmZlLTE3OWEtNDEyMi05ODk4LTI1YzE3OTNmN2EyMyJ9")
        self.jobs_file = "jobs_data.csv"
        
        # Window setup

        self.setWindowTitle("Submit Job")
        self.resize(1800, 800)
        
        # Initialize data and state
        self.jobs_data = []
        self.selected_job = None
        self.objective_columns = set()

        # Initialize managers
        self.job_processor = JobProcessor(self, self.client, self.jobs_file) 

        self.table_manager = TableManager(self)
        self.context_menu_manager = ContextMenuManager(self)
        
        # Initialize timers
        self.job_check_timer = QTimer()
        self.job_check_timer.timeout.connect(self.job_processor.check_job_status)
        self.queue_timer = QTimer()
        self.queue_timer.timeout.connect(self.job_processor.process_job_queue)
        self.queue_timer.start(1000)
        self.counter_timer = QTimer()
        self.counter_timer.timeout.connect(self.update_submit_counter)
        self.counter_timer.start(1000)
        
        # Setup UI and load jobs
        self.setup_ui()
        self.load_jobs()

    def setup_ui(self):
        """
        Configure and layout the main UI components.
        
        Creates:
        - Menu bar with File and View menus
        - Three-panel horizontal split layout
        - Input panel for job submission
        - Response panel for job details
        - Jobs panel for job history table
        - Status bar for system messages
        
        The panels are arranged in a QSplitter for adjustable sizing.
        """
        # Create menu bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        view_menu = menubar.addMenu("View")
        
        # Add menu actions
        refresh_action = file_menu.addAction("Refresh")
        refresh_action.triggered.connect(self.fetch_and_update_jobs)

        # Create central widget

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create horizontal splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(True)
        splitter.setHandleWidth(5)
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
        
        # Setup panels using UIPanels class
        input_panel = UIPanels.setup_input_panel(self)
        response_panel = UIPanels.setup_response_panel(self)
        self.jobs_panel = UIPanels.setup_jobs_panel(self)
        
        # Add panels to splitter
        splitter.addWidget(input_panel)
        splitter.addWidget(response_panel)
        splitter.addWidget(self.jobs_panel)
        
        # Set initial sizes
        splitter.setSizes([300, 400, 500])
        
        # Add splitter to main layout
        main_layout.addWidget(splitter)
        
        # Add status bar
        self.statusBar().showMessage("Ready")



    def submit_job(self):
        """
        Submit a new job to the competition system.
        
        Retrieves values from input fields:
        - scenario: Selected competition scenario
        - subject: Email subject line
        - body: Email body content
        
        Delegates actual submission to job_processor and updates queue display.
        """
        scenario = self.scenario_input.text()
        subject = self.subject_input.text()
        body = self.body_input.toPlainText()
        
        if self.job_processor.submit_job(scenario, subject, body):
            self.update_queue_display()

    def update_queue_display(self):
        """
        Update the queue table display with current job queue status.
        
        For each queued job, displays:
        - Scenario name
        - Subject and body
        - Processing status
        - Queue position
        - Retry count
        - Last API response
        """
        self.queue_table.setRowCount(len(self.job_processor.job_queue))
        
        for row, job in enumerate(self.job_processor.job_queue):
            # Scenario
            self.queue_table.setItem(row, 0, QTableWidgetItem(job['scenario']))
            # Subject
            self.queue_table.setItem(row, 1, QTableWidgetItem(job['subject']))
            # Body
            self.queue_table.setItem(row, 2, QTableWidgetItem(job['body']))
            # Status
            status = "Processing" if job == self.job_processor.current_job else "Queued"
            self.queue_table.setItem(row, 3, QTableWidgetItem(status))
            # Position
            self.queue_table.setItem(row, 4, QTableWidgetItem(str(row + 1)))
            # Retries
            self.queue_table.setItem(row, 5, QTableWidgetItem(str(job.get('retries', 0))))
            # Last Response
            self.queue_table.setItem(row, 6, QTableWidgetItem(job.get('last_response', '')))

    def load_jobs(self):
        """
        Load job history from CSV storage file.
        
        Processes:
        - Reads job data from CSV
        - Sorts by started_time descending
        - Extracts and sorts objective columns
        - Updates table filters and display
        
        Handles file access errors with user notification.
        """
        self.jobs_data = []
        self.objective_columns = set()
        
        if not os.path.exists(self.jobs_file):
            return

        try:
            with open(self.jobs_file, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                jobs = list(reader)
                # Sort jobs by started_time in descending order
                jobs.sort(key=lambda x: x['started_time'] if x['started_time'] else '', reverse=True)
                for row in jobs:
                    self.jobs_data.append(row)
                    if row['objectives']:
                        objectives = eval(row['objectives'])
                        self.objective_columns.update(objectives.keys())
            
            # Sort objective columns
            sorted_objectives = [obj for obj in self.objective_order if obj in self.objective_columns]
            remaining_objectives = sorted(obj for obj in self.objective_columns if obj not in self.objective_order)
            self.objective_columns = sorted_objectives + remaining_objectives
            
            # Update table
            self.table_manager.apply_filters()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load jobs: {str(e)}")

    def fetch_and_update_jobs(self):
        """
        Fetch latest jobs from API and update local storage.
        
        Process:
        1. Creates backup of existing CSV
        2. Fetches job list from competition API
        3. Converts API response to CSV format
        4. Updates local CSV storage
        5. Refreshes job display
        
        Handles errors by:
        - Restoring CSV backup on failure
        - Showing error messages to user
        - Updating status bar
        """
        try:
            # Create backup of existing CSV if it exists
            if os.path.exists(self.jobs_file):
                backup_file = f"{self.jobs_file}.bak"
                try:
                    os.replace(self.jobs_file, backup_file)
                except Exception as e:
                    QMessageBox.warning(self, "Backup Warning", f"Failed to create backup: {str(e)}")
                    return

            # Use list_jobs instead of get_jobs
            response = self.client.list_jobs()
            if not response:
                raise Exception("Failed to fetch jobs from API")
                
            # Convert jobs to dictionary format
            jobs_data = [{
                'job_id': job.job_id,
                'scenario': job.scenario,
                'subject': job.subject,
                'body': job.body,
                'scheduled_time': job.scheduled_time,
                'started_time': job.started_time,
                'completed_time': job.completed_time if hasattr(job, 'completed_time') else None,
                'output': job.output if hasattr(job, 'output') else '',
                'objectives': str(job.objectives) if hasattr(job, 'objectives') else '{}'
            } for job in response]

            # Save to CSV
            with open(self.jobs_file, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=jobs_data[0].keys())
                writer.writeheader()
                writer.writerows(jobs_data)

            self.statusBar().showMessage("Successfully updated jobs from API")
            self.load_jobs()
            
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

    def update_rate_limit(self):
        """
        Update the job submission rate limit.
        
        Validates user input:
        - Ensures positive integer value
        - Reverts to previous value on invalid input
        
        Updates job_processor rate limit if valid.
        """
        try:
            new_limit = int(self.rate_limit_input.text())
            if new_limit > 0:
                self.job_processor.submit_rate_limit = new_limit
            else:
                self.rate_limit_input.setText(str(self.job_processor.submit_rate_limit))
        except ValueError:
            self.rate_limit_input.setText(str(self.job_processor.submit_rate_limit))


    def update_submit_counter(self):
        """
        Update submission counter and status display.
        
        Shows:
        - Total/filtered job counts
        - Queue length and status
        - Time until next submission
        - Current processing job ID
        
        Updates status bar with formatted status message.
        """
        total_jobs = len(self.jobs_data)
        filtered_count = self.jobs_table.rowCount()
        jobs_count = f"[{filtered_count} of {total_jobs} jobs] - "
        
        self.update_submit_button_state()
        self.update_queue_display()
        
        if not self.job_processor.job_queue:
            self.statusBar().showMessage(f"{jobs_count}Ready - Next submission available")
            return
            
        time_since_last = time.time() - self.job_processor.last_submit_time
        if time_since_last < self.job_processor.submit_rate_limit:
            remaining = int(self.job_processor.submit_rate_limit - time_since_last)
            queue_status = f"{jobs_count}Queue: {len(self.job_processor.job_queue)} job(s) - Next submission in {remaining}s"
            if self.job_processor.current_job:
                queue_status = f"{jobs_count}Processing job {self.job_processor.current_job.job_id} - {queue_status}"
            self.statusBar().showMessage(queue_status)
        else:
            queue_msg = f"{jobs_count}Queue: {len(self.job_processor.job_queue)} job(s) - Ready to submit"
            if self.job_processor.current_job:
                queue_msg = f"{jobs_count}Processing job {self.job_processor.current_job.job_id} - {queue_msg}"
            self.statusBar().showMessage(queue_msg)


    def update_submit_button_state(self):
        """
        Update submit button appearance based on submission state.
        
        Colors:
        - Green: Ready to submit
        - Orange: Rate limited
        - Crimson: Rate limited with retries
        
        Considers:
        - Rate limit override setting
        - Time since last submission
        - Retry status of queued jobs
        """
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
            
        time_since_last = time.time() - self.job_processor.last_submit_time

        
        if time_since_last < self.job_processor.submit_rate_limit:
            # Check if it's rate limited or just counting down
            if any(job.get('retries', 0) > 0 for job in self.job_processor.job_queue):
                self.submit_button.setStyleSheet(button_style % ('#DC143C', '#DC143C'))  # Bright Crimson
            else:
                self.submit_button.setStyleSheet(button_style % ('#FFA500', '#FFA500'))  # Buddhist Orange
        else:
            self.submit_button.setStyleSheet(button_style % ('#228B22', '#228B22'))  # Forest Green

    def use_as_template(self):
        """
        Populate input fields with selected job details.
        Shows warning if no job is selected.
        """
        if not hasattr(self, 'selected_job') or self.selected_job is None:
            QMessageBox.warning(self, "No Job Selected", "Please select a job from the table first")
            return
            
        self.scenario_input.setText(self.selected_job['scenario'])
        self.subject_input.setText(self.selected_job['subject']) 
        self.body_input.setText(self.selected_job['body'])

    def show_job_details(self, item):
        """
        Display detailed information for selected job.
        
        Shows:
        - Job ID and scenario
        - Subject and body text
        - Objectives with completion status
        - Success/failure indicators
        
        Formats output as HTML with color coding for objectives.
        """
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

    def response_text_clicked(self, event):
        """Handle clicks in the response text area"""
        if hasattr(self, 'selected_job'):
            self.highlight_job_in_table(self.selected_job['job_id'])
        super(QTextEdit, self.response_text).mousePressEvent(event)

    def highlight_job_in_table(self, job_id):
        """Highlight the job row in the table"""
        for row in range(self.jobs_table.rowCount()):
            item = self.jobs_table.item(row, 0)
            if item and item.data(Qt.UserRole) == job_id:
                self.jobs_table.selectRow(row)
                break

    # Delegate methods to managers
    def apply_filters(self):
        self.table_manager.apply_filters()

    def sort_table(self, column):
        self.table_manager.sort_table(column)

    def toggle_sort_order(self):
        """Toggle between ascending and descending sort order"""
        # Get the current column from sort combo
        column_name = self.sort_combo.currentText()
        # Find column index
        for i in range(self.jobs_table.columnCount()):
            if self.jobs_table.horizontalHeaderItem(i).text() == column_name:
                self.table_manager.toggle_sort_order()
                self.table_manager.sort_table(i, update_combo=False)
                break

    def handle_sort_change(self, column_name):
        """Handle sort column selection change"""
        # Find column index
        for i in range(self.jobs_table.columnCount()):
            if self.jobs_table.horizontalHeaderItem(i).text() == column_name:
                self.table_manager.sort_table(i, update_combo=False)
                break




    def show_context_menu(self, position):
        self.context_menu_manager.show_context_menu(position)

def main():
    app = QApplication(sys.argv)
    window = SubmitJobWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
