# Logging System Guide

## Overview

The scraper now includes a comprehensive logging system that creates detailed logs for each run, making it easy to debug issues and track progress.

## Quick Start

### Run Test with Logging

```bash
python test_scraper_with_logging.py
```

This will:
1. Create a new log directory under `logs/test_YYYYMMDD_HHMMSS/`
2. Log to both console and files
3. Capture screenshots on errors
4. Save HTML page dumps for debugging
5. Create separate debug and error logs

## Log Directory Structure

Each run creates a directory like this:

```
logs/
└── test_20240129_143022/           # Run timestamp
    ├── scraper.log                 # Main log file (INFO level)
    ├── errors.log                  # Errors only
    ├── debug.log                   # Detailed debug info
    ├── screenshots/                # Screenshots captured during run
    │   ├── login_failed_143045.png
    │   └── search_box_error_143102.png
    └── html_dumps/                 # Page source HTML dumps
        ├── login_failed_143045.html
        └── search_box_error_143102.html
```

## Log Files Explained

### `scraper.log` - Main Log
Contains INFO and above messages. This is your go-to file for understanding what happened.

**Example:**
```
2024-01-29 14:30:22 | INFO     | Starting LinkedIn Scraper Test
2024-01-29 14:30:25 | INFO     | Chrome driver initialized successfully
2024-01-29 14:30:45 | INFO     | Successfully logged in to LinkedIn!
2024-01-29 14:31:02 | INFO     | Jobs page loaded successfully
2024-01-29 14:31:15 | INFO     | Search submitted successfully!
2024-01-29 14:32:30 | INFO     | ✓ Job 1/5: Software Engineer at Google
```

### `errors.log` - Errors Only
Contains only ERROR and CRITICAL messages with full stack traces.

**Example:**
```
2024-01-29 14:31:15 | ERROR    | Exception in find_and_fill_search_boxes: NoSuchElementException
2024-01-29 14:31:15 | ERROR    | Full traceback:
Traceback (most recent call last):
  File "linkedin_job_scraper_with_logging.py", line 245, in find_and_fill_search_boxes
    job_title_input = wait.until(...)
selenium.common.exceptions.NoSuchElementException: Message:
```

### `debug.log` - Detailed Debug Info
Contains ALL messages including DEBUG level for deep troubleshooting.

**Example:**
```
2024-01-29 14:30:22 | DEBUG    | User agent: Mozilla/5.0 (Windows NT 10.0...
2024-01-29 14:30:25 | DEBUG    | Delaying for 5.23 seconds
2024-01-29 14:30:30 | DEBUG    | LINKEDIN_EMAIL set: True
2024-01-29 14:30:30 | DEBUG    | LINKEDIN_PASSWORD set: True
2024-01-29 14:30:35 | DEBUG    | Waiting for login form to load...
2024-01-29 14:30:40 | DEBUG    | Email field found
```

## Screenshots

Screenshots are automatically captured when errors occur:

- `login_failed.png` - Login page when login fails
- `search_box_error.png` - When search box can't be found
- `no_iframe.png` - When iframe is missing
- `extraction_error.png` - During job extraction errors

## HTML Dumps

Full page source is saved on errors for detailed inspection:

- `login_failed.html` - Login page HTML
- `search_box_error.html` - Jobs page HTML when search fails
- Inspect these to see exactly what LinkedIn served

## Using the Logger in Your Code

### Basic Usage

```python
from logger_config import create_logger

# Create logger for this run
logger = create_logger(run_name="my_scrape")

# Log messages
logger.info("This is an info message")
logger.debug("Detailed debug info")
logger.warning("Warning message")
logger.error("Error occurred")

# Log exceptions with full traceback
try:
    # your code
except Exception as e:
    logger.log_exception(e, context="doing something")

# Save screenshots
logger.save_screenshot(driver, "error_state")

# Save page HTML
logger.save_page_source(driver, "page_dump")
```

### Advanced Usage

```python
# Custom run name
logger = create_logger(
    log_base_dir="my_logs",
    run_name="production_scrape"
)

# Log major steps
logger.log_step("Data Extraction", step_number=3)

# Log summary at end
logger.log_summary({
    'Total Jobs': 100,
    'Successful': 95,
    'Errors': 5,
    'Duration': '15 minutes'
})

# Get log directory
log_dir = logger.get_run_dir()
print(f"Logs saved to: {log_dir}")
```

## Troubleshooting with Logs

### Issue: Login Fails

1. **Check** `scraper.log` for login messages
2. **Look at** `screenshots/login_failed_*.png`
3. **Inspect** `html_dumps/login_failed_*.html`
4. **Review** `errors.log` for error messages

### Issue: Search Box Not Found

1. **Check** `debug.log` for detailed element search
2. **Look at** `screenshots/search_box_error_*.png`
3. **Inspect** `html_dumps/search_box_error_*.html`
4. **Verify** LinkedIn hasn't changed page structure

### Issue: No Jobs Extracted

1. **Check** `scraper.log` for extraction messages
2. **Look for** warnings about missing descriptions
3. **Review** `debug.log` for iframe switching
4. **Check** if max_jobs is too small

## Log Retention

Logs are kept indefinitely by default. To manage log storage:

### Manual Cleanup

```bash
# Delete logs older than 30 days
find logs/ -type d -mtime +30 -exec rm -rf {} +

# Keep only last 10 runs
ls -t logs/ | tail -n +11 | xargs rm -rf
```

### Automated Cleanup (Add to script)

```python
import shutil
from pathlib import Path
from datetime import datetime, timedelta

def cleanup_old_logs(log_dir="logs", days=30):
    """Delete log directories older than X days."""
    cutoff = datetime.now() - timedelta(days=days)

    for path in Path(log_dir).iterdir():
        if path.is_dir():
            mtime = datetime.fromtimestamp(path.stat().st_mtime)
            if mtime < cutoff:
                shutil.rmtree(path)
                print(f"Deleted old log: {path}")
```

## Best Practices

1. **Always use logging** - Run `test_scraper_with_logging.py` instead of the basic script
2. **Review logs after failed runs** - Check `errors.log` first
3. **Save important logs** - Archive successful run logs for reference
4. **Use screenshots** - They're invaluable for debugging UI issues
5. **Check HTML dumps** - When screenshots aren't enough, inspect the actual HTML
6. **Clean up periodically** - Delete old logs to save disk space

## Integration with Airflow

When using Airflow, logs will be created in:

```
logs/
├── test_20240129_143022/          # Manual test runs
├── airflow_20240129_090000/       # Automated Airflow runs
└── production_20240129_120000/    # Production runs
```

Airflow also has its own logs in `airflow/logs/`, but these custom logs provide more detail about the scraping process itself.

## Summary

The logging system provides:
- ✅ **Multiple log levels** - INFO, DEBUG, ERROR, CRITICAL
- ✅ **Separate log files** - Main, errors, debug
- ✅ **Automatic screenshots** - On any error
- ✅ **HTML page dumps** - For detailed inspection
- ✅ **Full stack traces** - Easy debugging
- ✅ **Organized by run** - Each run in its own directory
- ✅ **Timestamps** - Track exactly when things happened

Now you can easily debug any issues that occur during scraping!
