import time
from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtCore import Qt
from defense_filters import load_defense_levels

class TableManager:
    def __init__(self, parent):
        self.parent = parent
        self.sort_column = 0
        self.sort_order = Qt.AscendingOrder
        self.base_columns = ["Scenario"]
        self.base_columns_after = ["Subject", "Body"]
        self.time_columns = ["Scheduled Time", "Started Time"]

    def apply_filters(self):
        """Apply filters to jobs data and update table"""
        current_index = self.parent.scenario_filter.currentIndex()
        selected_scenario_value = self.parent.scenario_filter.itemData(current_index)
        selected_model = self.parent.model_filter.currentText()
        selected_defense = self.parent.defense_filter.currentText()
        
        # Load defense levels data
        defense_data = load_defense_levels('defense_levels.txt')

        # Get checked objectives
        include_objectives = [obj for obj, cbs in self.parent.objective_checkboxes.items() if cbs['include'].isChecked()]
        exclude_objectives = [obj for obj, cbs in self.parent.objective_checkboxes.items() if cbs['exclude'].isChecked()]
        
        filtered_jobs = []
        for job in self.parent.jobs_data:
            # Apply scenario filter
            if selected_scenario_value != "all" and selected_scenario_value != job['scenario'].lower():
                continue

            # Apply defense filters
            scenario_level = job['scenario'].lower()
            
            if selected_model != "All":
                if selected_model == "Phi3":
                    if scenario_level not in defense_data['Phi3']:
                        continue
                elif selected_model == "GPT4-o-mini":
                    if scenario_level not in defense_data['GPT4-o-mini']:
                        continue
                        
            if selected_defense != "All":
                if scenario_level not in defense_data[selected_defense]:
                    continue
                
            # Apply objectives filter
            if include_objectives or exclude_objectives:
                if not job['objectives']:
                    continue
                objectives = eval(job['objectives'])
                
                # Check included objectives
                if include_objectives and not all(objectives.get(obj, False) for obj in include_objectives):
                    continue
                    
                # Check excluded objectives
                if exclude_objectives and any(objectives.get(obj, False) for obj in exclude_objectives):
                    continue
                    
            filtered_jobs.append(job)

        # Update table
        self.update_table_with_jobs(filtered_jobs)

    def update_table_with_jobs(self, filtered_jobs):
        """Update table with filtered jobs"""
        self.parent.jobs_table.setRowCount(len(filtered_jobs))
        
        # Update job count label
        total_jobs = len(self.parent.jobs_data)
        filtered_count = len(filtered_jobs)
        if total_jobs == filtered_count:
            self.parent.job_count_label.setText(f"Total Jobs: {total_jobs}")
        else:
            self.parent.job_count_label.setText(f"Showing {filtered_count} of {total_jobs} jobs")
        
        # Calculate total columns and set them
        total_columns = len(self.base_columns) + len(self.parent.objective_columns) + len(self.base_columns_after) + len(self.time_columns)
        self.parent.jobs_table.setColumnCount(total_columns)
        
        # Set headers in correct order
        headers = self.base_columns + list(self.parent.objective_columns) + self.base_columns_after + self.time_columns
        self.parent.jobs_table.setHorizontalHeaderLabels(headers)

        for row, job in enumerate(filtered_jobs):
            col = 0
            
            # Set scenario (first column)
            item = QTableWidgetItem(job['scenario'])
            item.setData(Qt.UserRole, job['job_id'])
            self.parent.jobs_table.setItem(row, col, item)
            col += 1
            
            # Set objective columns
            if job['objectives']:
                objectives = eval(job['objectives'])
                for objective_name in self.parent.objective_columns:
                    result = objectives.get(objective_name, False)
                    item = QTableWidgetItem('✓' if result else '✗')
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setForeground(Qt.green if result else Qt.red)
                    self.parent.jobs_table.setItem(row, col, item)
                    col += 1
            else:
                # Skip objective columns if no objectives
                col += len(self.parent.objective_columns)
            
            # Set remaining base columns
            for base_col in self.base_columns_after:
                key = base_col.lower().replace(' ', '_')
                item = QTableWidgetItem(job[key])
                item.setToolTip(job[key])  # Add tooltip for subject and body
                self.parent.jobs_table.setItem(row, col, item)
                col += 1
            
            # Set time columns
            for time_col in self.time_columns:
                key = time_col.lower().replace(' ', '_')
                timestamp = job[key]
                if timestamp:
                    # Store original timestamp as data for sorting
                    item = QTableWidgetItem()
                    item.setData(Qt.UserRole, timestamp)
                    
                    if time_col == "Scheduled Time":
                        # Calculate relative time for Scheduled Time
                        try:
                            # Remove fractional seconds and convert T to space
                            clean_timestamp = timestamp.split('.')[0].replace('T', ' ')
                            timestamp_time = time.strptime(clean_timestamp, "%Y-%m-%d %H:%M:%S")
                            timestamp_seconds = time.mktime(timestamp_time)
                            current_time = time.time()
                            diff_seconds = current_time - timestamp_seconds
                            
                            # Format relative time
                            if diff_seconds < 60:
                                display_text = "just now"
                            elif diff_seconds < 3600:
                                minutes = int(diff_seconds / 60)
                                seconds = int(diff_seconds % 60)
                                display_text = f"{minutes}m {seconds}s ago"
                            elif diff_seconds < 86400:
                                hours = int(diff_seconds / 3600)
                                minutes = int((diff_seconds % 3600) / 60)
                                display_text = f"{hours}h {minutes}m ago"
                            else:
                                days = int(diff_seconds / 86400)
                                hours = int((diff_seconds % 86400) / 3600)
                                minutes = int((diff_seconds % 3600) / 60)
                                if hours == 0:
                                    display_text = f"{days}d ago"
                                else:
                                    display_text = f"{days}d {hours}h {minutes}m ago"
                            
                            item.setText(display_text)
                        except:
                            item.setText(timestamp)  # Fallback to original if parsing fails
                    else:
                        # For Started Time, just show the timestamp
                        item.setText(timestamp)
                    
                    item.setToolTip(timestamp)  # Show full timestamp on hover
                else:
                    item = QTableWidgetItem('')
                
                self.parent.jobs_table.setItem(row, col, item)
                col += 1

        # Set column widths based on content
        font_metrics = self.parent.jobs_table.fontMetrics()
        for col in range(self.parent.jobs_table.columnCount()):
            header_text = self.parent.jobs_table.horizontalHeaderItem(col).text()
            if header_text == "Scenario":
                width = font_metrics.horizontalAdvance("1234567") + 20  # 7 chars + padding
            elif col < len(self.base_columns) + len(self.parent.objective_columns):
                width = font_metrics.horizontalAdvance("Objective") + 20
            elif header_text in ["Subject", "Body"]:
                width = font_metrics.horizontalAdvance(header_text * 3) + 20
            else:
                width = font_metrics.horizontalAdvance("YYYY-MM-DD HH:MM:SS") + 20
            self.parent.jobs_table.setColumnWidth(col, width)

    def sort_table(self, column):
        """Sort table by clicked column header"""
        if self.sort_column == column:
            # Toggle sort order if clicking the same column
            self.sort_order = Qt.DescendingOrder if self.sort_order == Qt.AscendingOrder else Qt.AscendingOrder
            self.parent.sort_order_btn.setText("↑" if self.sort_order == Qt.AscendingOrder else "↓")
        else:
            # Default to ascending order for new column
            self.sort_order = Qt.AscendingOrder
            self.parent.sort_order_btn.setText("↓")
        
        self.sort_column = column
        self.parent.sort_combo.setCurrentText(self.parent.jobs_table.horizontalHeaderItem(column).text())
        
        # Custom sorting for timestamp columns
        header_text = self.parent.jobs_table.horizontalHeaderItem(column).text()
        if header_text in self.time_columns:
            # Sort by the stored timestamp data
            rows = []
            for row in range(self.parent.jobs_table.rowCount()):
                item = self.parent.jobs_table.item(row, column)
                timestamp = item.data(Qt.UserRole) if item else ''
                rows.append((timestamp, row))
            
            # Sort rows based on timestamp
            rows.sort(key=lambda x: x[0] if x[0] else '', reverse=(self.sort_order == Qt.DescendingOrder))
            
            # Reorder table rows
            for new_row, (_, old_row) in enumerate(rows):
                # Take all items from old row
                items = []
                for col in range(self.parent.jobs_table.columnCount()):
                    items.append(self.parent.jobs_table.takeItem(old_row, col))
                
                # Put items in new row
                for col, item in enumerate(items):
                    if item:
                        self.parent.jobs_table.setItem(new_row, col, item)
        else:
            # Use default sorting for other columns
            self.parent.jobs_table.sortItems(column, self.sort_order)

    def toggle_sort_order(self):
        """Toggle between ascending and descending sort order"""
        self.sort_order = Qt.DescendingOrder if self.sort_order == Qt.AscendingOrder else Qt.AscendingOrder
        self.parent.sort_order_btn.setText("↑" if self.sort_order == Qt.AscendingOrder else "↓")
        self.parent.jobs_table.sortItems(self.sort_column, self.sort_order)
