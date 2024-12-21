from PySide6.QtWidgets import QMenu, QApplication
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt

class ContextMenuManager:
    def __init__(self, parent):
        self.parent = parent

    def show_context_menu(self, position):
        """Show context menu for jobs table"""
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
        """Get list of selected jobs from table"""
        selected_rows = set(item.row() for item in self.parent.jobs_table.selectedItems())
        selected_jobs = []
        
        for row in selected_rows:
            job_id = self.parent.jobs_table.item(row, 0).data(Qt.UserRole)
            job = next((job for job in self.parent.jobs_data if job['job_id'] == job_id), None)
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
