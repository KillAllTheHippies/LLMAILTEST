from PySide6.QtWidgets import (QDialog, QVBoxLayout, QPushButton, 
                                      QTableWidget, QTableWidgetItem, QMenu)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication

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
