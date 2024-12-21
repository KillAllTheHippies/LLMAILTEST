from PySide6.QtWidgets import QMenu, QApplication
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt

class ContextMenuManager:
    """
    Manages the right-click context menu functionality for the jobs table.
    
    This class handles the creation and management of context menu actions for copying
    various job information to the clipboard. It provides functionality to copy job details,
    subjects, bodies, or combinations thereof for one or multiple selected jobs.
    
    Attributes:
        parent: The parent widget (SubmitJobWindow) that contains the jobs table and data
    """

    def __init__(self, parent):
        """
        Initialize the ContextMenuManager.
        
        Args:
            parent: Reference to parent window containing jobs_table and jobs_data
        """
        self.parent = parent


    def show_context_menu(self, position):
        """
        Display the context menu at the specified position.
        
        Creates and shows a context menu with various copy options for the selected job(s).
        The menu includes options to copy complete job info, subject only, body only,
        or both subject and body together.
        
        Args:
            position: QPoint object specifying where to display the context menu
        """
        menu = QMenu()
        
        # Add copy actions
        copy_info_action = QAction("Copy Job Info", self.parent)
        copy_subject_action = QAction("Copy Subject", self.parent)
        copy_body_action = QAction("Copy Body", self.parent)
        copy_subject_body_action = QAction("Copy Subject and Body", self.parent)
        
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
        menu.exec_(self.parent.jobs_table.viewport().mapToGlobal(position))

    def get_selected_jobs(self):
        """
        Retrieve the job data for all selected rows in the jobs table.
        
        Iterates through selected table items, extracts job IDs, and finds
        corresponding job data from the parent's jobs_data list.
        
        Returns:
            list: List of dictionaries containing the data for selected jobs
        """
        selected_rows = set(item.row() for item in self.parent.jobs_table.selectedItems())
        selected_jobs = []
        
        for row in selected_rows:
            job_id = self.parent.jobs_table.item(row, 0).data(Qt.UserRole)
            job = next((job for job in self.parent.jobs_data if job['job_id'] == job_id), None)
            if job:
                selected_jobs.append(job)
        
        return selected_jobs

    def copy_job_info(self):
        """
        Copy complete information for selected jobs to clipboard.
        
        Formats and copies comprehensive job information including scenario,
        subject, body, and objectives (if present) for all selected jobs.
        Jobs are separated by divider lines in the output.
        """
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
