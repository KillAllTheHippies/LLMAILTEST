from PySide6.QtWidgets import (QDialog, QVBoxLayout, QPushButton, 
                                      QTableWidget, QTableWidgetItem, QMenu)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication

class JobQueueWindow(QDialog):
    """
    Dialog window for displaying and managing the job submission queue.
    
    This window provides a detailed view of currently queued and processing jobs,
    including their status, retry counts, and any error responses. It supports
    copying job information through a context menu and displays tooltips for
    longer text fields.
    
    Attributes:
        parent: Reference to parent window containing job processor
        queue_table: QTableWidget displaying queued and processing jobs
    """
    def __init__(self, parent=None):
        """
        Initialize the queue window with table and controls.
        
        Sets up the queue table with columns for job details, status tracking,
        and error handling information. Configures the window size and layout.
        
        Args:
            parent: Parent window reference for modal behavior
        """
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
        """
        Update the queue table display with current jobs.
        
        Refreshes the table with the current processing job (if any) and all
        queued jobs. Adds tooltips to text fields and displays retry counts
        and error responses.
        
        Args:
            job_queue: List of jobs waiting to be processed
            current_job: Currently processing job object or None
        """
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
        """
        Display the context menu for copying job information.
        
        Creates and shows a context menu with options to copy various parts
        of the selected jobs' information to the clipboard.
        
        Args:
            position: QPoint object specifying where to display the menu
        """
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
        """
        Retrieve data for all selected jobs in the queue table.
        
        Extracts job information from selected table rows and returns
        it in a consistent dictionary format.
        
        Returns:
            list: List of dictionaries containing selected jobs' data
        """
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
        """
        Copy complete information for selected jobs to clipboard.
        
        Formats and copies comprehensive job information including scenario,
        subject, body, and status for all selected jobs. Jobs are separated
        by divider lines in the output.
        """
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
        """
        Copy only the subjects of selected jobs to clipboard.
        
        Extracts and copies just the subject lines from selected jobs,
        with each subject on a new line.
        """
        selected_jobs = self.get_selected_jobs()
        if not selected_jobs:
            return
            
        subjects = [job['subject'] for job in selected_jobs]
        QApplication.clipboard().setText("\n".join(subjects))

    def copy_body(self):
        """
        Copy only the bodies of selected jobs to clipboard.
        
        Extracts and copies just the body content from selected jobs,
        with each body separated by a new line.
        """
        selected_jobs = self.get_selected_jobs()
        if not selected_jobs:
            return
            
        bodies = [job['body'] for job in selected_jobs]
        QApplication.clipboard().setText("\n".join(bodies))

    def copy_subject_and_body(self):
        """
        Copy both subject and body of selected jobs to clipboard.
        
        Formats and copies the subject and body for each selected job,
        with entries separated by divider lines.
        """
        selected_jobs = self.get_selected_jobs()
        if not selected_jobs:
            return
            
        text = []
        for job in selected_jobs:
            text.append(f"Subject: {job['subject']}\nBody: {job['body']}")
        
        QApplication.clipboard().setText("\n---\n".join(text))
