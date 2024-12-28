"""
Context Menu Manager Module

Handles right-click context menu functionality for the jobs table.
"""

from PySide6.QtWidgets import QMenu

class ContextMenuManager:
	def __init__(self, parent):
		self.parent = parent
		
	def show_context_menu(self, position):
		"""Show the context menu at the specified position."""
		menu = QMenu()
		
		# Add menu actions
		use_template_action = menu.addAction("Use as Template")
		use_template_action.triggered.connect(self.parent.use_as_template)
		
		# Show menu
		menu.exec_(self.parent.jobs_table.viewport().mapToGlobal(position))