from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                      QLineEdit, QTextEdit, QPushButton, QComboBox,
                                      QCheckBox, QTableWidget, QTableWidgetItem,
                                      QSizePolicy)
from PySide6.QtCore import Qt

class UIPanels:
    @staticmethod
    def setup_input_panel(parent):
        """Setup the input panel with job submission controls"""
        input_panel = QWidget()
        layout = QVBoxLayout(input_panel)
        
        # Scenario input
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
        
        # Rate limit input
        rate_layout = QHBoxLayout()
        rate_label = QLabel("Rate Limit (seconds):")
        parent.rate_limit_input = QLineEdit(str(parent.submit_rate_limit))
        parent.rate_limit_input.setFixedWidth(50)
        parent.rate_limit_input.editingFinished.connect(parent.update_rate_limit)
        
        # Add override checkbox
        parent.override_rate_limit = QCheckBox("Override (Testing)")
        parent.override_rate_limit.setToolTip("Disable rate limit for testing")
        parent.override_rate_limit.stateChanged.connect(parent.update_submit_button_state)
        
        rate_layout.addWidget(rate_label)
        rate_layout.addWidget(parent.rate_limit_input)
        rate_layout.addWidget(parent.override_rate_limit)
        rate_layout.addStretch()
        layout.addLayout(rate_layout)
        
        # Submit button
        parent.submit_button = QPushButton("Submit Job")
        parent.submit_button.setStyleSheet("""
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
        """)
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

        # Add queue table
        parent.queue_table = QTableWidget()
        parent.queue_table.setColumnCount(7)
        parent.queue_table.setHorizontalHeaderLabels(["Scenario", "Subject", "Body", "Status", "Position", "Retries", "Last Response"])
        parent.queue_table.horizontalHeader().setStretchLastSection(True)
        parent.queue_table.setContextMenuPolicy(Qt.CustomContextMenu)
        parent.queue_table.customContextMenuRequested.connect(parent.show_context_menu)
        parent.queue_table.setMaximumHeight(200)
        layout.addWidget(parent.queue_table)

        layout.addStretch()
        
        # Set size policy
        input_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        input_panel.setMinimumWidth(0)
        
        return input_panel

    @staticmethod
    def setup_response_panel(parent):
        """Setup the response panel with text display area"""
        response_panel = QWidget()
        layout = QVBoxLayout(response_panel)
        
        # Template button at top
        template_button = QPushButton("Use as Template")
        template_button.clicked.connect(parent.use_as_template)
        layout.addWidget(template_button)
        
        # Response text area
        parent.response_text = QTextEdit()
        parent.response_text.setReadOnly(True)
        parent.response_text.mousePressEvent = parent.response_text_clicked
        layout.addWidget(parent.response_text)
        
        # Set size policy
        response_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        response_panel.setMinimumWidth(0)
        
        return response_panel

    @staticmethod
    def setup_jobs_panel(parent):
        """Setup the jobs panel with filtering and table"""
        jobs_panel = QWidget()
        jobs_layout = QVBoxLayout(jobs_panel)

        # Controls layout
        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(5)
        
        # Sort controls
        sort_widget = QWidget()
        sort_layout = QHBoxLayout(sort_widget)
        sort_layout.setContentsMargins(0, 0, 0, 0)
        
        sort_label = QLabel("Sort by:")
        parent.sort_combo = QComboBox()
        # Initialize sort combo with all possible columns
        initial_headers = parent.base_columns + parent.objective_order + parent.base_columns_after + parent.time_columns
        parent.sort_combo.addItems(initial_headers)
        parent.sort_combo.setCurrentText("Started Time")  # Set default sort
        parent.sort_combo.currentTextChanged.connect(parent.handle_sort_change)
        
        parent.sort_order_btn = QPushButton("↓")
        parent.sort_order_btn.setFixedWidth(30)
        parent.sort_order_btn.clicked.connect(parent.toggle_sort_order)
        
        sort_layout.addWidget(sort_label)
        sort_layout.addWidget(parent.sort_combo)
        sort_layout.addWidget(parent.sort_order_btn)
        sort_layout.addStretch()
        
        controls_layout.addWidget(sort_widget)

        # Defense filters
        defense_widget = QWidget()
        defense_layout = QHBoxLayout(defense_widget)
        defense_layout.setContentsMargins(0, 0, 0, 0)
        
        model_label = QLabel("Model:")
        parent.model_filter = QComboBox()
        parent.model_filter.addItems(["All", "Phi3", "GPT4-o-mini"])
        parent.model_filter.currentTextChanged.connect(parent.apply_filters)
        
        defense_label = QLabel("Defense:")
        parent.defense_filter = QComboBox()
        parent.defense_filter.addItems(["All", "prompt_shield", "task_tracker", "spotlight", "llm_judge", "all defenses"])
        parent.defense_filter.currentTextChanged.connect(parent.apply_filters)
        
        defense_layout.addWidget(model_label)
        defense_layout.addWidget(parent.model_filter)
        defense_layout.addWidget(defense_label)
        defense_layout.addWidget(parent.defense_filter)
        defense_layout.addStretch()
        
        controls_layout.addWidget(defense_widget)

        # Scenario filter
        scenario_widget = QWidget()
        scenario_layout = QHBoxLayout(scenario_widget)
        scenario_layout.setContentsMargins(0, 0, 0, 0)
        
        scenario_label = QLabel("Scenario:")
        parent.scenario_filter = QComboBox()
        parent.scenario_filter.addItem("All Scenarios", "all")
        for display_name, filter_value in parent.scenarios:
            parent.scenario_filter.addItem(display_name, filter_value)
        parent.scenario_filter.currentTextChanged.connect(parent.apply_filters)
        
        scenario_layout.addWidget(scenario_label)
        scenario_layout.addWidget(parent.scenario_filter)
        scenario_layout.addStretch()
        
        controls_layout.addWidget(scenario_widget)
        
        # Add refresh button
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(parent.fetch_and_update_jobs)
        controls_layout.addWidget(refresh_button)
        
        jobs_layout.addLayout(controls_layout)

        # Jobs table
        parent.jobs_table = QTableWidget()
        parent.jobs_table.setColumnCount(len(parent.base_columns))
        parent.jobs_table.setHorizontalHeaderLabels(parent.base_columns)
        parent.jobs_table.itemClicked.connect(parent.show_job_details)
        parent.jobs_table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        parent.jobs_table.setContextMenuPolicy(Qt.CustomContextMenu)
        parent.jobs_table.customContextMenuRequested.connect(parent.show_context_menu)
        parent.jobs_table.horizontalHeader().sectionClicked.connect(parent.sort_table)
        parent.jobs_table.setHorizontalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        parent.jobs_table.setVerticalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        
        jobs_layout.addWidget(parent.jobs_table)
        
        # Set size policy
        jobs_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        jobs_panel.setMinimumWidth(0)
        
        return jobs_panel
