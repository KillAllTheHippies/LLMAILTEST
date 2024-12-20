# Job Submission GUI Application

A Python-based GUI application for submitting and managing jobs with real-time status tracking and comprehensive job history management.

## Features

- **Job Submission**
    - Submit jobs with scenario, subject, and body
    - Rate-limited submission queue (30s between submissions)
    - Real-time job status monitoring
    - Automatic job completion detection

- **Job History Management**
    - CSV-based persistent storage
    - Backup creation before updates
    - Sortable and filterable job list
    - Detailed job viewing with objectives tracking

- **Advanced UI Features**
    - Detachable jobs panel
    - Detachable response panel
    - Template-based job creation
    - Multi-column sorting
    - Objective-based filtering
    - Scenario text filtering

- **Job Status Visualization**
    - Color-coded objective status
    - Expandable job details
    - HTML-formatted response view
    - Progress tracking

## Prerequisites

- Python 3.8+
- Required Python packages:
    - PySide6 >= 6.0.0 (GUI framework)
    - requests >= 2.31.0 (API communication)
    - python-dateutil >= 2.8.2 (Date handling)

    Install all dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Project Structure

```
LLMail_Inject_Challenge/
├── submit_job_gui.py     # Main GUI application
├── submit_job.py         # Job submission client
├── job_analyzer.py       # Job analysis utilities
├── requirements.txt      # Python dependencies
├── jobs_data.csv        # Job history storage
└── jobs_data.csv.bak    # Backup of job history
```

Required Files:
- submit_job_gui.py: Main application with GUI implementation
- submit_job.py: Contains CompetitionClient and Job classes
- job_analyzer.py: JobAnalyzer class for job data management
- requirements.txt: Lists all Python package dependencies
- jobs_data.csv: Stores job history (created automatically)
- jobs_data.csv.bak: Backup file (created automatically)

## Installation

1. Clone the repository:
     ```bash
     git clone [repository-url]
     cd [repository-name]
     ```

2. Install dependencies:
     ```bash
     pip install -r requirements.txt
     ```

## Usage

1. Start the application:
     ```bash
     python submit_job_gui.py
     ```

2. Submit a job:
     - Enter scenario details
     - Fill in subject and body
     - Click "Submit Job"
     - Monitor progress in response panel

3. Manage jobs:
     - Use filters to find specific jobs
     - Sort by any column
     - Double-click body text to expand
     - Use checkboxes to filter by objectives

4. Use advanced features:
     - Detach panels using "Detach Window" buttons
     - Use existing jobs as templates
     - Monitor queued jobs in status bar
     - Refresh job list manually

## Interface Components

### Main Window
- Left Panel: Job submission form
- Middle Panel: Job response viewer
- Right Panel: Jobs history table

### Jobs Table
- Scenario column
- Objective status columns
- Subject and body columns
- Timestamp columns

### Control Features
- Sort controls
- Filter inputs
- Objective checkboxes
- Refresh button
- Detach controls

## Job Management

### Job Queue
- Automatic rate limiting
- Queue position display
- Status updates
- Error handling

### Job History
- CSV storage
- Automatic updates
- Backup creation
- Data persistence

## Objectives Tracking

Supported objectives:
- email.retrieved
- defense.undetected
- exfil.sent
- exfil.destination
- exfil.content

Each objective shows:
- ✓ (green) for success
- ✗ (red) for failure

## Troubleshooting

Common issues:
1. Job submission fails
     - Check network connection
     - Verify input fields
     - Check rate limit timer

2. CSV file issues
     - Check file permissions
     - Verify file not locked
     - Check backup creation

3. UI responsiveness
     - Reduce table size
     - Close detached windows
     - Refresh data less frequently

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## Support

For support:
- Open an issue
- Contact maintainers
- Check documentation


