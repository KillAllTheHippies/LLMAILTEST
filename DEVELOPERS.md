# LLMail Competition GUI Developer Guide

## System Architecture

### Core Components

1. **Main Application (submit_job_gui.py)**
   - Entry point and main window management
   - Coordinates between all components
   - Handles UI initialization and updates
   - Manages application state

2. **Job Processing (job_processor.py)**
   - Handles job submission queue
   - Manages rate limiting
   - Processes API responses
   - Handles retry logic
   - Maintains job state persistence

3. **Table Management (table_manager.py)**
   - Controls job history display
   - Implements filtering logic
   - Manages sorting functionality
   - Handles column management

4. **UI Components (ui_components.py)**
   - Panel creation and layout
   - Widget initialization
   - Event binding
   - Style management

5. **API Client (submit_job.py)**
   - Competition API communication
   - Job submission and retrieval
   - Response parsing
   - Error handling

6. **Context Menu (context_menu.py)**
   - Right-click menu functionality
   - Copy operations
   - Job selection handling

7. **Queue Window (queue_window.py)**
   - Dedicated queue management interface
   - Queue status display
   - Job position tracking

## Data Flow

### Job Submission Flow
1. User Input → SubmitJobWindow
2. SubmitJobWindow → JobProcessor
3. JobProcessor → CompetitionClient
4. CompetitionClient → API
5. Response → JobProcessor
6. JobProcessor → CSV Storage
7. Update UI Components

### Job Status Update Flow
1. Timer Trigger → JobProcessor
2. JobProcessor → CompetitionClient
3. CompetitionClient → API
4. Response → JobProcessor
5. Update TableManager
6. Refresh UI Display

## Component Interactions

### SubmitJobWindow
- Initializes all managers and components
- Maintains application state
- Coordinates between components
- Handles high-level event flow

### JobProcessor
- Receives submission requests
- Manages submission queue
- Handles rate limiting
- Updates job status
- Maintains data persistence

### TableManager
- Receives filtered data
- Applies sort operations
- Updates table display
- Manages column state

### UIPanels
- Creates UI components
- Binds event handlers
- Updates display state
- Manages layout

## Key Classes

### SubmitJobWindow
```python
class SubmitJobWindow(QMainWindow):
	# Core state
	scenarios: List[Tuple[str, str]]  # Display name, internal value
	jobs_data: List[Dict]             # All job records
	objective_columns: Set[str]        # Active objective types
	
	# Component references
	job_processor: JobProcessor
	table_manager: TableManager
	context_menu_manager: ContextMenuManager
```

### JobProcessor
```python
class JobProcessor:
	# Configuration
	submit_rate_limit: int            # Seconds between submissions
	
	# State
	current_job: Optional[Job]        # Currently processing job
	job_queue: List[Dict]            # Pending jobs
	last_submit_time: float          # Last submission timestamp
```

### TableManager
```python
class TableManager:
	# Sort state
	sort_column: int                 # Current sort column index
	sort_order: Qt.SortOrder        # Ascending/Descending
	
	# Column definitions
	base_columns: List[str]         # Primary columns
	time_columns: List[str]         # Time-based columns
```

## Data Structures

### Job Dictionary
```python
job_data = {
	'job_id': str,          # Unique identifier
	'scenario': str,        # Scenario name
	'subject': str,         # Email subject
	'body': str,            # Email body
	'scheduled_time': str,  # ISO timestamp
	'started_time': str,    # ISO timestamp
	'completed_time': str,  # ISO timestamp
	'output': str,          # Job output
	'objectives': str       # Serialized objectives dict
}
```

### Objectives Dictionary
```python
objectives = {
	'email.retrieved': bool,
	'defense.undetected': bool,
	'exfil.sent': bool,
	'exfil.destination': bool,
	'exfil.content': bool
}
```

## Timer System

### Active Timers
1. **job_check_timer**: Polls API for job status
   - Interval: 5000ms
   - Triggered: On job submission

2. **queue_timer**: Processes job queue
   - Interval: 1000ms
   - Always active

3. **counter_timer**: Updates UI counters
   - Interval: 1000ms
   - Always active

## File Storage

### CSV Structure (jobs_data.csv)
- Primary job storage
- Automatic backups (.bak)
- Columns match Job Dictionary
- UTF-8 encoded

## Error Handling

### Hierarchy
1. API Communication Errors
   - Backup restoration
   - User notification
   - Queue preservation

2. Data Processing Errors
   - Graceful degradation
   - State maintenance
   - User feedback

3. UI Update Errors
   - Silent recovery
   - State consistency
   - Default values

## Development Guidelines

### Adding New Features
1. Identify target component
2. Update data structures
3. Implement core logic
4. Add UI elements
5. Update documentation

### Modifying Existing Features
1. Review component interactions
2. Check data flow impact
3. Update affected components
4. Test integration points
5. Update documentation

### Code Style
- Follow existing patterns
- Document public methods
- Use type hints
- Maintain error handling
- Keep UI responsive

## Testing Considerations

### Areas to Test
1. Job submission flow
2. Rate limiting logic