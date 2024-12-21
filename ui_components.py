from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                      QLineEdit, QTextEdit, QPushButton, QComboBox,
                                      QCheckBox, QTableWidget, QTableWidgetItem,
                                      QSizePolicy, QFrame)
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
        parent.rate_limit_input = QLineEdit(str(parent.job_processor.submit_rate_limit))
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
    def setup_objectives_widget(parent):
        """Setup the objectives widget with Y/N checkboxes"""
        objectives_widget = QWidget()
        objectives_layout = QVBoxLayout(objectives_widget)
        objectives_layout.setContentsMargins(0, 0, 0, 0)
        objectives_layout.setSpacing(2)  # Reduced spacing
        
        # Create checkbox pairs for each objective
        parent.objective_checkboxes = {}
        for objective in parent.objective_order:
            obj_widget = QWidget()
            obj_layout = QHBoxLayout(obj_widget)
            obj_layout.setContentsMargins(0, 0, 0, 0)
            obj_layout.setSpacing(2)
            
            yes_cb = QCheckBox("Y")
            no_cb = QCheckBox("N")
            
            yes_cb.setStyleSheet("QCheckBox { color: green; }")
            no_cb.setStyleSheet("QCheckBox { color: red; }")
            
            yes_cb.stateChanged.connect(parent.apply_filters)
            no_cb.stateChanged.connect(parent.apply_filters)
            
            obj_layout.addWidget(yes_cb)
            obj_layout.addWidget(no_cb)
            obj_layout.addWidget(QLabel("|"))
            obj_layout.addWidget(QLabel(objective))
            obj_layout.addStretch()
            
            parent.objective_checkboxes[objective] = {
                'yes': yes_cb,
                'no': no_cb
            }
            
            objectives_layout.addWidget(obj_widget)
            
        return objectives_widget

    @staticmethod
    def setup_jobs_panel(parent):
        """Setup the jobs panel with filtering and table"""
        jobs_panel = QWidget()
        jobs_layout = QVBoxLayout(jobs_panel)

        # Controls layout - main container with horizontal layout
        controls_container = QWidget()
        controls_layout = QHBoxLayout(controls_container)
        controls_layout.setSpacing(10)
        controls_layout.setContentsMargins(0, 0, 0, 0)

        # Filters container
        filters_container = QWidget()
        filters_layout = QVBoxLayout(filters_container)
        filters_layout.setSpacing(2)
        filters_layout.setContentsMargins(0, 0, 0, 0)
        
        # Left side filters container
        left_filters = QWidget()
        left_layout = QVBoxLayout(left_filters)
        left_layout.setSpacing(1)  # Minimal spacing between elements
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scenario filter
        scenario_widget = QWidget()
        scenario_layout = QHBoxLayout(scenario_widget)
        scenario_layout.setContentsMargins(0, 0, 0, 0)
        scenario_layout.setSpacing(2)  # Minimal spacing between label and combobox
        
        scenario_label = QLabel("Scenario:")
        parent.scenario_filter = QComboBox()
        parent.scenario_filter.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        parent.scenario_filter.addItem("All Scenarios", "all")
        for display_name, filter_value in parent.scenarios:
            parent.scenario_filter.addItem(display_name, filter_value)
        parent.scenario_filter.currentTextChanged.connect(parent.apply_filters)
        
        scenario_layout.addWidget(scenario_label)
        scenario_layout.addWidget(parent.scenario_filter)
        scenario_layout.addStretch()
        
        left_layout.addWidget(scenario_widget)

        # Sort controls
        sort_widget = QWidget()
        sort_layout = QHBoxLayout(sort_widget)
        sort_layout.setContentsMargins(0, 0, 0, 0)
        sort_layout.setSpacing(2)
        
        sort_label = QLabel("Sort by:")
        parent.sort_combo = QComboBox()
        parent.sort_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        initial_headers = parent.base_columns + parent.objective_order + parent.base_columns_after + parent.time_columns
        parent.sort_combo.addItems(initial_headers)
        parent.sort_combo.setCurrentText("Started Time")
        parent.sort_combo.currentTextChanged.connect(parent.handle_sort_change)


        
        parent.sort_order_btn = QPushButton("↓")
        parent.sort_order_btn.setFixedWidth(20)  # Smaller width
        parent.sort_order_btn.setFixedHeight(20)  # Match height to combobox
        parent.sort_order_btn.clicked.connect(parent.toggle_sort_order)
        
        sort_layout.addWidget(sort_label)
        sort_layout.addWidget(parent.sort_combo)
        sort_layout.addWidget(parent.sort_order_btn)
        sort_layout.addStretch()
        
        left_layout.addWidget(sort_widget)

        # Model filter
        model_widget = QWidget()
        model_layout = QHBoxLayout(model_widget)
        model_layout.setContentsMargins(0, 0, 0, 0)
        model_layout.setSpacing(2)
        
        model_label = QLabel("Model:")
        parent.model_filter = QComboBox()
        parent.model_filter.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        parent.model_filter.addItems(["All", "Phi3", "GPT4-o-mini"])
        parent.model_filter.currentTextChanged.connect(parent.apply_filters)
        
        model_layout.addWidget(model_label)
        model_layout.addWidget(parent.model_filter)
        model_layout.addStretch()
        
        left_layout.addWidget(model_widget)

        # Defense filter
        defense_widget = QWidget()
        defense_layout = QHBoxLayout(defense_widget)
        defense_layout.setContentsMargins(0, 0, 0, 0)
        defense_layout.setSpacing(2)
        
        defense_label = QLabel("Defense:")
        parent.defense_filter = QComboBox()
        parent.defense_filter.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        parent.defense_filter.addItems(["All", "prompt_shield", "task_tracker", "spotlight", "llm_judge", "all defenses"])
        parent.defense_filter.currentTextChanged.connect(parent.apply_filters)
        
        defense_layout.addWidget(defense_label)
        defense_layout.addWidget(parent.defense_filter)
        defense_layout.addStretch()
        
        left_layout.addWidget(defense_widget)
        
        # Add filters to container
        filters_layout.addWidget(left_filters)
        
        # Add refresh button at top
        refresh_button = QPushButton("Refresh")
        refresh_button.setFixedHeight(20)  # Make button smaller
        refresh_button.clicked.connect(parent.fetch_and_update_jobs)
        filters_layout.addWidget(refresh_button)
        
        # Add filters container to main controls
        controls_layout.addWidget(filters_container)

        # Add vertical divider
        divider = QFrame()
        divider.setFrameShape(QFrame.VLine)
        divider.setFrameShadow(QFrame.Sunken)
        divider.setStyleSheet("QFrame { color: #999999; }")
        controls_layout.addWidget(divider)

        # Add objectives widget
        objectives_widget = UIPanels.setup_objectives_widget(parent)
        objectives_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        controls_layout.addWidget(objectives_widget)

        
        # Add stretch to ensure components stay left-aligned
        controls_layout.addStretch()
        
        # Add all controls to main layout
        jobs_layout.addWidget(controls_container)



        # Jobs table with custom sorting
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
        # Disable built-in sorting and ensure headers are clickable
        parent.jobs_table.setSortingEnabled(False)
        parent.jobs_table.horizontalHeader().setSortIndicatorShown(True)
        parent.jobs_table.horizontalHeader().setSectionsClickable(True)
        
        jobs_layout.addWidget(parent.jobs_table)
        
        # Initialize the sort column to Started Time after table is set up
        for i in range(parent.jobs_table.columnCount()):
            if parent.jobs_table.horizontalHeaderItem(i).text() == "Started Time":
                parent.table_manager.sort_table(i)
                break

        # Set size policy
        jobs_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        jobs_panel.setMinimumWidth(0)
        
        return jobs_panel
