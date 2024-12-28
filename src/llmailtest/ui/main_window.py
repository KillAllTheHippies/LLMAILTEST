"""
Main Window Module

Implements the main application window and coordinates UI components.
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from .components import UIPanels
from .job_processor import JobProcessor
from .table_manager import TableManager
from .context_menu import ContextMenuManager
from ..client.submit_job import CompetitionClient

class SubmitJobWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.init_window()
		self.init_components()
		self.load_jobs()
		
	def init_window(self):
		"""Initialize window properties."""
		self.setWindowTitle("Submit Job")
		self.resize(1800, 800)
		
	def init_components(self):
		"""Initialize core components and managers."""
		self.client = CompetitionClient("your-api-key-here")
		self.jobs_file = "jobs_data.csv"
		
		self.job_processor = JobProcessor(self, self.client, self.jobs_file)
		self.table_manager = TableManager(self)
		self.context_menu_manager = ContextMenuManager(self)
		
		# Setup UI panels
		central_widget = UIPanels.setup_main_layout(self)
		self.setCentralWidget(central_widget)

def main():
	app = QApplication(sys.argv)
	window = SubmitJobWindow()
	window.show()
	sys.exit(app.exec())

if __name__ == "__main__":
	main()