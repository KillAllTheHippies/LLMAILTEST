![image](https://github.com/user-attachments/assets/40e99013-d13c-4b6c-a9d0-ece2c74e6dd3)


# LLMail Competition Job Submission GUI

A professional Qt-based GUI application for managing and monitoring competition job submissions with comprehensive job tracking, analysis, and management capabilities.

## Core Features

### Job Submission System
- **Scenario Selection**: 40 predefined competition scenarios across 4 levels
- **Model Types**: Support for Phi3 and GPT4-o-mini models
- **Defense Mechanisms**: 
    - prompt_shield
    - task_tracker
    - spotlight
    - llm_judge
    - Combined defense options
- **Rate-Limited Queue**:
    - Configurable submission intervals
    - Override capability for testing
    - Visual status indicators
    - Automatic retry handling

### Job Management
- **Real-Time Monitoring**:
    - Live status updates
    - Queue position tracking
    - Completion detection
    - Error handling with retries
- **Data Persistence**:
    - CSV-based storage
    - Automatic backups
    - API synchronization
    - Recovery mechanisms

### Advanced Interface

#### Input Panel
- Scenario input field
- Subject line entry
- Body text area
- Rate limit controls
- Submit button with status colors:
    - Green: Ready
    - Orange: Rate limited
    - Crimson: Rate limited with retries
- Queue status display

#### Response Panel
- Detailed job information
- HTML-formatted output
- Color-coded objectives
- Template creation capability
- Interactive job selection

#### Jobs Panel
- **Comprehensive Filtering**:
    - Scenario-based
    - Model type
    - Defense mechanism
    - Objective completion
- **Advanced Sorting**:
    - Multi-column support
    - Ascending/descending toggle
    - Time-based ordering
- **Visual Indicators**:
    - Success/failure markers
    - Progress tracking
    - Status updates

### Objective Tracking
- **Five Key Objectives**:
    1. email.retrieved
    2. defense.undetected
    3. exfil.sent
    4. exfil.destination
    5. exfil.content
- Visual status indicators (✓/✗)
- Color-coded results (green/red)
- Filtering by completion status

## Technical Details

### Dependencies
- **PySide6** (≥6.0.0): Qt framework implementation
- **requests** (≥2.31.0): API communication
- **python-dateutil** (≥2.8.2): Time handling
- **pandas** (≥2.1.0): Data management
- **colorama** (≥0.4.6): Console output formatting

### System Requirements
- Python 3.8 or higher
- Modern operating system with GUI support
- Network connectivity for API access

### Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd [repository-name]
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Launch application:
```bash
python submit_job_gui.py
```

### Project Structure
```
project/
├── submit_job_gui.py    # Main application
├── submit_job.py        # API client implementation
├── job_processor.py     # Job handling logic
├── table_manager.py     # Table data management
├── ui_components.py     # UI panel definitions
├── context_menu.py      # Context menu handling
├── queue_window.py      # Queue management window
└── requirements.txt     # Package dependencies
```

## Usage Guide

### Basic Operation
1. Select competition scenario
2. Enter email subject and body
3. Click submit button
4. Monitor job progress

### Advanced Features
- **Template Usage**: Select existing job and use as template
- **Queue Management**: Monitor and manage submission queue
- **Job Analysis**: Filter and sort completed jobs
- **Data Export**: Copy job details via context menu
- **Status Tracking**: Monitor objectives completion

### Troubleshooting

#### Common Issues
1. **Rate Limiting**:
     - Wait for cooldown period
     - Check rate limit settings
     - Use override for testing

2. **Data Synchronization**:
     - Verify network connection
     - Check API accessibility
     - Ensure file permissions

3. **UI Responsiveness**:
     - Reduce filtered data size
     - Clear queue if necessary
     - Restart for memory cleanup

## Contributing

1. Fork repository
2. Create feature branch
3. Implement changes
4. Submit pull request

## Support

For assistance:
- Submit GitHub issues
- Check documentation
- Contact development team

## License

[Specify License]



