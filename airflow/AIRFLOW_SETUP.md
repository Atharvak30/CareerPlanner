# Apache Airflow Setup for LinkedIn Job Scraper

This guide will help you set up Apache Airflow to automate your LinkedIn job scraping with scheduling, monitoring, and data management.

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation Methods](#installation-methods)
  - [Method 1: Docker (Recommended)](#method-1-docker-recommended)
  - [Method 2: Local Installation](#method-2-local-installation)
- [Configuration](#configuration)
- [Running the DAG](#running-the-dag)
- [Monitoring](#monitoring)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)

---

## Overview

The Airflow DAG (`linkedin_job_scraper_dag.py`) automates:
- **Scheduled scraping** - Runs daily (customizable)
- **Multiple searches** - Different job titles and locations
- **Data deduplication** - Removes duplicate job postings
- **Archiving** - Moves old data to archive folder
- **Reporting** - Generates summary reports

### DAG Workflow

```
scrape_linkedin_jobs → deduplicate_jobs → archive_old_data → generate_summary
```

---

## Prerequisites

1. **Python 3.8+** installed
2. **Docker & Docker Compose** (for Docker method) OR **PostgreSQL** (for local method)
3. **Chrome/Chromium** browser installed
4. **LinkedIn credentials** in `.env` file

---

## Installation Methods

### Method 1: Docker (Recommended)

Docker provides an isolated, reproducible environment for Airflow.

#### Step 1: Create Required Directories

```bash
cd /Users/siddhant/Developer/CareerPlanner

# Create Airflow directories
mkdir -p airflow/dags airflow/logs airflow/plugins airflow/config data
```

#### Step 2: Set Environment Variables

Create a `.env` file in the project root:

```bash
# .env file
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password

# Airflow web UI credentials
_AIRFLOW_WWW_USER_USERNAME=admin
_AIRFLOW_WWW_USER_PASSWORD=admin123

# Set Airflow UID (required on Linux/Mac)
AIRFLOW_UID=50000
```

#### Step 3: Initialize Airflow

```bash
# On Linux/Mac, set the UID
echo "AIRFLOW_UID=$(id -u)" >> .env

# Initialize the database and create admin user
docker-compose up airflow-init
```

#### Step 4: Start Airflow Services

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

#### Step 5: Access Airflow UI

1. Open browser to: `http://localhost:8080`
2. Login with credentials from `.env` file (default: admin/admin123)
3. You should see the `linkedin_job_scraper` DAG

#### Step 6: Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove all data (WARNING: deletes database)
docker-compose down -v
```

---

### Method 2: Local Installation

For development or if you prefer not to use Docker.

#### Step 1: Create Virtual Environment

```bash
cd /Users/siddhant/Developer/CareerPlanner

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Step 2: Install Dependencies

```bash
# Install Airflow and dependencies
pip install -r requirements.txt

# Or install Airflow with specific constraints
AIRFLOW_VERSION=2.7.3
PYTHON_VERSION="$(python --version | cut -d " " -f 2 | cut -d "." -f 1-2)"
CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"
pip install selenium pandas python-dotenv
```

#### Step 3: Initialize Airflow Database

```bash
# Set Airflow home directory
export AIRFLOW_HOME=/Users/siddhant/Developer/CareerPlanner/airflow

# Initialize database (SQLite by default)
airflow db init

# Create admin user
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin123
```

#### Step 4: Configure Airflow

Edit `airflow/airflow.cfg`:

```ini
[core]
# Point to your DAGs folder
dags_folder = /Users/siddhant/Developer/CareerPlanner/airflow/dags

# Disable example DAGs
load_examples = False

[scheduler]
# How often to scan for new DAGs (in seconds)
dag_dir_list_interval = 300
```

#### Step 5: Start Airflow

Open two terminal windows:

**Terminal 1 - Web Server:**
```bash
export AIRFLOW_HOME=/Users/siddhant/Developer/CareerPlanner/airflow
source venv/bin/activate
airflow webserver --port 8080
```

**Terminal 2 - Scheduler:**
```bash
export AIRFLOW_HOME=/Users/siddhant/Developer/CareerPlanner/airflow
source venv/bin/activate
airflow scheduler
```

Access UI at: `http://localhost:8080`

---

## Configuration

### Setting Airflow Variables

Airflow Variables control DAG behavior. Set them via UI or CLI:

#### Via Web UI:
1. Go to `Admin` → `Variables`
2. Click `+` to add new variable
3. Add these variables:

| Key | Value | Description |
|-----|-------|-------------|
| `linkedin_job_queries` | `Software Engineer,Data Scientist,ML Engineer` | Comma-separated job titles |
| `linkedin_locations` | `San Francisco,New York,Seattle` | Comma-separated locations |
| `linkedin_time_filter` | `24hrs` | Time filter: `24hrs`, `1week`, `1month`, or `any` |
| `linkedin_max_jobs_per_search` | `20` | Max jobs per search query |
| `linkedin_output_dir` | `/opt/airflow/data` (Docker) or `/Users/siddhant/Developer/CareerPlanner/data` (Local) | Output directory |
| `linkedin_archive_days` | `7` | Archive files older than X days |

#### Via CLI:
```bash
airflow variables set linkedin_job_queries "Software Engineer,Data Scientist,ML Engineer"
airflow variables set linkedin_locations "San Francisco,New York,Seattle"
airflow variables set linkedin_time_filter "24hrs"
airflow variables set linkedin_max_jobs_per_search "20"
airflow variables set linkedin_output_dir "/opt/airflow/data"
airflow variables set linkedin_archive_days "7"
```

### Changing Schedule

Edit the DAG file `airflow/dags/linkedin_job_scraper_dag.py`:

```python
dag = DAG(
    'linkedin_job_scraper',
    schedule_interval='0 9 * * *',  # Cron expression
    # Examples:
    # '0 9 * * *'      - Daily at 9 AM
    # '0 */6 * * *'    - Every 6 hours
    # '0 9 * * 1'      - Every Monday at 9 AM
    # '0 9 1 * *'      - First day of month at 9 AM
    # '@daily'         - Daily at midnight
    # '@weekly'        - Weekly on Sunday at midnight
    # None             - Manual trigger only
)
```

---

## Running the DAG

### Manual Trigger (First Time)

1. Go to Airflow UI: `http://localhost:8080`
2. Find `linkedin_job_scraper` DAG
3. Toggle the DAG to "On" (unpause)
4. Click the "Play" button → "Trigger DAG"

### Monitor Progress

1. Click on the DAG name
2. View "Graph" view to see task progress
3. Click on individual tasks to see logs
4. Green = Success, Red = Failed, Yellow = Running

### Scheduled Runs

Once unpaused, the DAG will run automatically according to the schedule.

---

## Monitoring

### View Logs

**Via UI:**
1. Click on DAG → Click on task → Click on "Log" tab

**Via Docker:**
```bash
# View all logs
docker-compose logs -f airflow-scheduler

# View specific container logs
docker-compose logs -f airflow-webserver
```

**Via Local Install:**
```bash
# Logs are in:
tail -f airflow/logs/dag_id=linkedin_job_scraper/run_id=*/task_id=*/attempt=*.log
```

### Check Output Data

```bash
# List generated CSV files
ls -lh data/

# View latest file
ls -t data/*.csv | head -1 | xargs cat

# Count jobs in latest file
ls -t data/*.csv | head -1 | xargs wc -l
```

---

## Customization

### Add Email Notifications

Edit the DAG file:

```python
default_args = {
    'email': ['your_email@example.com'],
    'email_on_failure': True,
    'email_on_success': True,  # Add this for success emails
}
```

Configure SMTP in `airflow.cfg`:

```ini
[smtp]
smtp_host = smtp.gmail.com
smtp_starttls = True
smtp_ssl = False
smtp_user = your_email@gmail.com
smtp_password = your_app_password
smtp_port = 587
smtp_mail_from = your_email@gmail.com
```

### Add Slack Notifications

Install Slack provider:
```bash
pip install apache-airflow-providers-slack
```

Add to DAG:
```python
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator

slack_alert = SlackWebhookOperator(
    task_id='slack_notification',
    http_conn_id='slack_webhook',
    message='LinkedIn scraping completed! {{ ti.xcom_pull(task_ids="generate_summary") }}',
    dag=dag
)

summary_task >> slack_alert
```

### Add More Search Queries

Update the Airflow variable:
```bash
airflow variables set linkedin_job_queries "Software Engineer,Data Scientist,ML Engineer,Product Manager,DevOps Engineer"
```

Or modify directly in the DAG file for static queries.

### Change Maximum Jobs Per Search

```bash
airflow variables set linkedin_max_jobs_per_search "50"
```

---

## Troubleshooting

### Problem: DAG Not Appearing in UI

**Solution:**
1. Check DAG file for Python syntax errors:
   ```bash
   python airflow/dags/linkedin_job_scraper_dag.py
   ```

2. Check Airflow can parse the DAG:
   ```bash
   airflow dags list
   airflow dags show linkedin_job_scraper
   ```

3. Check scheduler logs:
   ```bash
   docker-compose logs airflow-scheduler | grep ERROR
   ```

### Problem: "ModuleNotFoundError: No module named 'linkedin_job_scraper'"

**Solution (Docker):**
Ensure the project directory is mounted in `docker-compose.yml`:
```yaml
volumes:
  - .:/opt/airflow/project
```

**Solution (Local):**
Add project to Python path:
```bash
export PYTHONPATH="${PYTHONPATH}:/Users/siddhant/Developer/CareerPlanner"
```

### Problem: Selenium/Chrome Not Working in Docker

**Solution:**
1. Use the Chrome service defined in `docker-compose.yml`
2. Update `linkedin_job_scraper.py` to use remote WebDriver:

```python
def setup_chrome_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Connect to remote Chrome (in Docker)
    driver = webdriver.Remote(
        command_executor='http://chrome:4444/wd/hub',
        options=options
    )
    return driver
```

### Problem: Permission Denied on Directories

**Solution (Docker):**
```bash
chmod -R 777 airflow/logs airflow/dags data
```

### Problem: Task Timeout

**Solution:**
Increase timeout in default_args:
```python
default_args = {
    'execution_timeout': timedelta(hours=3),  # Increase from 2 to 3 hours
}
```

### Problem: LinkedIn Blocking Requests

**Solution:**
1. Reduce frequency - increase delay times
2. Add humanization (use the `humanize_scraper.py` module)
3. Reduce `linkedin_max_jobs_per_search`
4. Use residential proxies (advanced)

---

## Testing

### Test the DAG Without Running

```bash
# Test DAG structure
airflow dags test linkedin_job_scraper 2024-01-01

# Test individual task
airflow tasks test linkedin_job_scraper scrape_linkedin_jobs 2024-01-01
```

### Dry Run

Set `max_jobs_per_search` to a small number (like 3) for testing:

```bash
airflow variables set linkedin_max_jobs_per_search "3"
```

---

## Advanced: Production Deployment

### Use Celery Executor (Distributed)

For production with multiple workers:

1. Update `docker-compose.yml` to use CeleryExecutor
2. Add Redis/RabbitMQ service
3. Add worker services
4. Scale workers: `docker-compose up --scale airflow-worker=3`

### Database Backup

```bash
# Backup PostgreSQL database
docker-compose exec postgres pg_dump -U airflow airflow > backup.sql

# Restore
docker-compose exec -T postgres psql -U airflow airflow < backup.sql
```

### Monitoring with Prometheus

Add metrics exporter to track DAG performance over time.

---

## Quick Reference

### Useful Commands

```bash
# List all DAGs
airflow dags list

# Pause/Unpause DAG
airflow dags pause linkedin_job_scraper
airflow dags unpause linkedin_job_scraper

# Trigger DAG manually
airflow dags trigger linkedin_job_scraper

# Clear task instances (rerun)
airflow tasks clear linkedin_job_scraper

# View DAG structure
airflow dags show linkedin_job_scraper

# Test task
airflow tasks test linkedin_job_scraper scrape_linkedin_jobs 2024-01-01
```

### Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart specific service
docker-compose restart airflow-scheduler

# Access container shell
docker-compose exec airflow-webserver bash

# Clean up everything
docker-compose down -v
rm -rf airflow/logs/*
```

---

## Support

If you encounter issues:

1. Check Airflow logs
2. Verify environment variables are set
3. Test the scraper script independently
4. Check LinkedIn credentials are valid
5. Ensure Chrome/ChromeDriver versions match

For Airflow-specific issues, see: https://airflow.apache.org/docs/

---

## Summary

You now have a fully automated LinkedIn job scraping pipeline with:
- ✅ **Scheduled execution** - Runs automatically
- ✅ **Multiple searches** - Different roles and locations
- ✅ **Data management** - Deduplication and archiving
- ✅ **Monitoring** - Web UI and logs
- ✅ **Scalability** - Easy to add more searches
- ✅ **Reliability** - Retries and error handling

Happy scraping!
