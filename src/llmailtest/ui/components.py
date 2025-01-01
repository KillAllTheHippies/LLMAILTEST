"""
UI Components Module

Contains reusable UI panel components for the job submission interface.
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
							  QComboBox, QLineEdit, QTextEdit, QPushButton,
							  QTableWidget, QTableWidgetItem, QCheckBox,
							  QFrame)
from PySide6.QtCore import Qt

class UIPanels:
	@staticmethod
	def setup_input_panel(parent) -> QWidget:
		"""Create the job submission input panel."""
		panel = QWidget()
		layout = QVBoxLayout(panel)
		
		# Scenario selection
		scenario_layout = QHBoxLayout()
		scenario_label = QLabel("Scenario:")
		parent.scenario_input = QLineEdit()
		scenario_layout.addWidget(scenario_label)
		scenario_layout.addWidget(parent.scenario_input)
		layout.addLayout(scenario_layout)
		
		# Subject input
		subject_layout = QHBoxLayout()
		subject_label = QLabel("Subject:")
		parent.subject_input = QLineEdit()
		subject_layout.addWidget(subject_label)
		subject_layout.addWidget(parent.subject_input)
		layout.addLayout(subject_layout)
		
		# Body input
		body_label = QLabel("Body:")
		parent.body_input = QTextEdit()
		layout.addWidget(body_label)
		layout.addWidget(parent.body_input)
		
		# Rate limit controls
		rate_layout = QHBoxLayout()
		rate_label = QLabel("Submit Rate (s):")
		parent.rate_limit_input = QLineEdit("60")
		parent.rate_limit_input.setMaximumWidth(50)
		parent.override_rate_limit = QCheckBox("Override")
		rate_layout.addWidget(rate_label)
		rate_layout.addWidget(parent.rate_limit_input)
		rate_layout.addWidget(parent.override_rate_limit)
		rate_layout.addStretch()
		layout.addLayout(rate_layout)
		
		# Submit button
		parent.submit_button = QPushButton("Submit Job")
		parent.submit_button.clicked.connect(parent.submit_job)
		layout.addWidget(parent.submit_button)
		
		# Add job count label
		parent.job_count_label = QLabel()
		font = parent.job_count_label.font()
		font.setPointSize(18)
		font.setBold(True)
		parent.job_count_label.setFont(font)
		parent.job_count_label.setAlignment(Qt.AlignCenter)
		parent.job_count_label.setStyleSheet("""
			QLabel {
				border: 2px solid black;
				border-radius: 5px;
				padding: 5px;
				background: transparent;
			}
		""")
		layout.addWidget(parent.job_count_label)
		
		# Create and setup queue table
		parent.queue_table = QTableWidget()
		parent.queue_table.setColumnCount(7)
		parent.queue_table.setHorizontalHeaderLabels([
			"Scenario", "Subject", "Body", "Status", 
			"Position", "Retries", "Last Response"
		])
		parent.queue_table.horizontalHeader().setStretchLastSection(True)
		layout.addWidget(parent.queue_table)

		return panel

	@staticmethod
	def setup_response_panel(parent) -> QWidget:
		"""Create the job response display panel."""
		panel = QWidget()
		layout = QVBoxLayout(panel)
		
		# Add template button with stormy blue styling
		template_button = QPushButton("Use as Template")
		template_button.clicked.connect(parent.use_as_template)
		template_button.setStyleSheet("""
			QPushButton {
				background-color: #4A6B8A;
				color: white;
				border: 1px solid #354B60;
				border-radius: 3px;
				padding: 5px;
			}
			QPushButton:hover {
				background-color: #5A7B9A;
			}
			QPushButton:pressed {
				background-color: #3A5B7A;
			}
		""")
		layout.addWidget(template_button)
		
		parent.response_text = QTextEdit()
		parent.response_text.setReadOnly(True)
		parent.response_text.mousePressEvent = parent.response_text_clicked
		
		layout.addWidget(parent.response_text)
		return panel

	@staticmethod
	def setup_jobs_panel(parent) -> QWidget:
		"""Create the jobs history panel."""
		panel = QWidget()
		layout = QVBoxLayout(panel)
		
		# Create objectives widget
		objectives_widget = QWidget()
		objectives_layout = QVBoxLayout(objectives_widget)
		objectives_layout.setContentsMargins(5, 5, 5, 5)
		objectives_layout.setSpacing(2)
		
		# Add header labels
		header_widget = QWidget()
		header_layout = QHBoxLayout(header_widget)
		header_layout.setContentsMargins(0, 0, 0, 0)
		header_layout.setAlignment(Qt.AlignLeft)
		
		# Add labels for True/False columns
		pass_label = QLabel("Pass")
		pass_label.setStyleSheet("color: green;")
		fail_label = QLabel("Fail")
		fail_label.setStyleSheet("color: red;")
		header_layout.addWidget(pass_label)
		header_layout.addSpacing(20)  # Add spacing between Pass/Fail
		header_layout.addWidget(fail_label)
		header_layout.addSpacing(10)  # Add spacing before Objective
		header_layout.addWidget(QLabel("Objective"))
		header_layout.addStretch()
		
		objectives_layout.addWidget(header_widget)
		
		# Add objective checkboxes
		for objective in parent.objective_order:
			obj_widget = QWidget()
			obj_layout = QHBoxLayout(obj_widget)
			obj_layout.setContentsMargins(0, 0, 0, 0)
			obj_layout.setAlignment(Qt.AlignLeft)
			
			# True checkbox (green)
			yes_cb = QCheckBox()
			yes_cb.setStyleSheet("QCheckBox::indicator:checked { background-color: green; }")
			yes_cb.setToolTip("Show passed objectives")
			
			# False checkbox (red)
			no_cb = QCheckBox()
			no_cb.setStyleSheet("QCheckBox::indicator:checked { background-color: red; }")
			no_cb.setToolTip("Show failed objectives")
			
			obj_layout.addWidget(yes_cb)
			obj_layout.addSpacing(20)  # Match header spacing
			obj_layout.addWidget(no_cb)
			obj_layout.addSpacing(10)  # Match header spacing
			obj_layout.addWidget(QLabel(objective))
			obj_layout.addStretch()
			
			# Store checkboxes as tuple
			parent.objective_checkboxes[objective] = (yes_cb, no_cb)
			
			yes_cb.stateChanged.connect(parent.apply_filters)
			no_cb.stateChanged.connect(parent.apply_filters)
			
			objectives_layout.addWidget(obj_widget)
		
		layout.addWidget(objectives_widget)
		
		# Filter controls
		filter_layout = QHBoxLayout()
		
		# Scenario filter
		scenario_label = QLabel("Filter Scenario:")
		parent.scenario_filter = QComboBox()
		parent.scenario_filter.addItem("All Scenarios", "all")
		for display_name, filter_value in parent.scenarios:
			parent.scenario_filter.addItem(display_name, filter_value)
		parent.scenario_filter.currentIndexChanged.connect(parent.apply_filters)
		filter_layout.addWidget(scenario_label)
		filter_layout.addWidget(parent.scenario_filter)

		# Model filter
		model_label = QLabel("Model:")
		parent.model_filter = QComboBox()
		parent.model_filter.addItems(["All", "Phi3", "GPT4-o-mini"])
		parent.model_filter.currentTextChanged.connect(parent.apply_filters)
		filter_layout.addWidget(model_label)
		filter_layout.addWidget(parent.model_filter)

		# Defense filter  
		defense_label = QLabel("Defense:")
		parent.defense_filter = QComboBox()
		parent.defense_filter.addItems(["All", "prompt_shield", "task_tracker", "spotlight", "llm_judge", "all"])
		parent.defense_filter.currentTextChanged.connect(parent.apply_filters)
		filter_layout.addWidget(defense_label)
		filter_layout.addWidget(parent.defense_filter)

		# Sort controls
		sort_label = QLabel("Sort by:")
		parent.sort_combo = QComboBox()
		parent.sort_combo.currentTextChanged.connect(parent.handle_sort_change)
		parent.sort_order_btn = QPushButton("↓")
		parent.sort_order_btn.setMaximumWidth(30)
		parent.sort_order_btn.clicked.connect(parent.toggle_sort_order)
		
		filter_layout.addWidget(sort_label)
		filter_layout.addWidget(parent.sort_combo)
		filter_layout.addWidget(parent.sort_order_btn)
		
		layout.addLayout(filter_layout)
		
		# Jobs table
		parent.jobs_table = QTableWidget()
		parent.jobs_table.setContextMenuPolicy(Qt.CustomContextMenu)
		parent.jobs_table.customContextMenuRequested.connect(parent.show_context_menu)
		parent.jobs_table.itemClicked.connect(parent.show_job_details)
		layout.addWidget(parent.jobs_table)
		
		return panel
