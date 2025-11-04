# Quick Start Guide - LinkedIn Job Scraper with Airflow

Get your automated LinkedIn job scraper running in 5 minutes!

## 🚀 Super Quick Start (Docker)

### Prerequisites
- Docker & Docker Compose installed
- LinkedIn account credentials

### Installation

```bash
# 1. Navigate to project directory
cd /Users/siddhant/Developer/CareerPlanner

# 2. Run the setup script
./setup_airflow.sh

# 3. Follow the prompts and wait for setup to complete
```

That's it! The script will:
- Create required directories
- Set up environment variables
- Initialize Airflow database
- Start all services

### Access Airflow

Open your browser to: **http://localhost:8080**

**Login:**
- Username: `admin`
- Password: `admin123`

---

## 📋 Configure Your Scraping Jobs

### Method 1: Via Web UI (Recommended)

1. Go to **Admin** → **Variables**
2. Click the **+** button
3. Add these variables:

| Variable Name | Example Value | Description |
|--------------|---------------|-------------|
| `linkedin_job_queries` | `Software Engineer,Data Scientist,ML Engineer` | Job titles to search (comma-separated) |
| `linkedin_locations` | `San Francisco,New York,Seattle` | Locations to search (comma-separated) |
| `linkedin_max_jobs_per_search` | `20` | Max jobs per search query |
| `linkedin_output_dir` | `/opt/airflow/data` | Where to save CSV files |
| `linkedin_archive_days` | `7` | Archive files older than X days |

### Method 2: Via Command Line

```bash
docker-compose exec airflow-webserver airflow variables set linkedin_job_queries "Software Engineer,Data Scientist"
docker-compose exec airflow-webserver airflow variables set linkedin_locations "San Francisco,New York"
docker-compose exec airflow-webserver airflow variables set linkedin_max_jobs_per_search "20"
docker-compose exec airflow-webserver airflow variables set linkedin_output_dir "/opt/airflow/data"
docker-compose exec airflow-webserver airflow variables set linkedin_archive_days "7"
```

---

## ▶️ Run Your First Scraping Job

### 1. Enable the DAG

In the Airflow UI:
1. Find `linkedin_job_scraper` in the DAG list
2. Click the toggle to turn it **On** (unpause)

### 2. Trigger a Manual Run

1. Click the **Play** button (▶️) next to the DAG name
2. Select **Trigger DAG**
3. Wait for execution to complete

### 3. Monitor Progress

1. Click on the DAG name
2. View the **Graph** to see task status:
   - 🟢 Green = Success
   - 🔴 Red = Failed
   - 🟡 Yellow = Running
   - ⚪ Gray = Not started

3. Click on any task to view logs

---

## 📊 View Your Results

### Check Output Files

```bash
# List all scraped data
ls -lh data/

# View latest file
ls -t data/*.csv | head -1

# Count jobs in latest file
ls -t data/*.csv | head -1 | xargs wc -l

# View first few rows
ls -t data/*_deduped.csv | head -1 | xargs head -20
```

### CSV File Format

Your data will contain these columns:
- `company` - Company name
- `title` - Job title
- `description` - Full job description
- `search_job_query` - The query used to find this job
- `search_location` - The location searched
- `scrape_date` - When the job was scraped
- `extraction_timestamp` - Exact timestamp

---

## ⏰ Schedule Automated Runs

The DAG is already scheduled to run **daily at 9 AM** by default.

### Change Schedule

Edit `airflow/dags/linkedin_job_scraper_dag.py`:

```python
schedule_interval='0 9 * * *',  # Cron expression
```

**Common schedules:**
- `'0 9 * * *'` - Daily at 9 AM
- `'0 */6 * * *'` - Every 6 hours
- `'0 9 * * 1'` - Every Monday at 9 AM
- `'0 0 1 * *'` - First day of month at midnight
- `'@daily'` - Daily at midnight
- `'@weekly'` - Weekly on Sunday
- `None` - Manual trigger only

Save the file and the DAG will automatically reload.

---

## 🛠 Common Commands

### Docker Management

```bash
# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f airflow-scheduler

# Stop all services
docker-compose down

# Restart services
docker-compose restart

# Start services again
docker-compose up -d

# Remove everything (WARNING: deletes data)
docker-compose down -v
```

### Airflow Commands

```bash
# List all DAGs
docker-compose exec airflow-webserver airflow dags list

# Pause/Unpause DAG
docker-compose exec airflow-webserver airflow dags pause linkedin_job_scraper
docker-compose exec airflow-webserver airflow dags unpause linkedin_job_scraper

# Trigger DAG manually
docker-compose exec airflow-webserver airflow dags trigger linkedin_job_scraper

# Test individual task
docker-compose exec airflow-webserver airflow tasks test linkedin_job_scraper scrape_linkedin_jobs 2024-01-01
```

---

## 🔧 Troubleshooting

### DAG Not Showing Up

1. Check for syntax errors:
   ```bash
   docker-compose exec airflow-webserver python /opt/airflow/dags/linkedin_job_scraper_dag.py
   ```

2. Check scheduler logs:
   ```bash
   docker-compose logs airflow-scheduler | grep ERROR
   ```

3. Restart scheduler:
   ```bash
   docker-compose restart airflow-scheduler
   ```

### Scraping Fails

1. **Check credentials:**
   - Verify `.env` file has correct LinkedIn credentials
   - Restart services: `docker-compose restart`

2. **Check logs:**
   - Click on failed task in UI → View Log
   - Look for error messages

3. **LinkedIn blocking:**
   - Reduce `linkedin_max_jobs_per_search` to 10 or less
   - Increase delays in scraper code
   - Add humanization features

### Services Won't Start

```bash
# Check if ports are already in use
lsof -i :8080  # Airflow web UI
lsof -i :5432  # PostgreSQL

# Stop and clean up
docker-compose down -v

# Remove old containers
docker system prune -a

# Start fresh
./setup_airflow.sh
```

---

## 📈 Scaling Up

### More Job Searches

Simply add more items to your variables:

```bash
# 10 job titles × 5 locations = 50 searches per run
docker-compose exec airflow-webserver airflow variables set linkedin_job_queries \
  "Software Engineer,Senior Software Engineer,Staff Engineer,Principal Engineer,\
   Engineering Manager,Data Scientist,ML Engineer,DevOps Engineer,Frontend Engineer,Backend Engineer"

docker-compose exec airflow-webserver airflow variables set linkedin_locations \
  "San Francisco,New York,Seattle,Austin,Boston"
```

### Increase Jobs Per Search

```bash
docker-compose exec airflow-webserver airflow variables set linkedin_max_jobs_per_search "50"
```

**Warning:** Higher numbers increase scraping time and detection risk!

### Run More Frequently

Change schedule to every 6 hours:

```python
schedule_interval='0 */6 * * *',
```

---

## 📚 Next Steps

1. **Add Humanization:**
   - Integrate `humanize_scraper.py` module
   - Reduces detection risk
   - See `HUMANIZATION_README.md`

2. **Set Up Notifications:**
   - Email alerts on success/failure
   - Slack notifications
   - See `AIRFLOW_SETUP.md`

3. **Data Analysis:**
   - Use pandas to analyze scraped data
   - Track trends over time
   - Build dashboards

4. **Advanced Features:**
   - Add job filtering (keywords, salary ranges)
   - Implement deduplication across runs
   - Export to database instead of CSV

---

## 🆘 Need Help?

- **Full Documentation:** See [AIRFLOW_SETUP.md](AIRFLOW_SETUP.md)
- **Humanization Guide:** See [HUMANIZATION_README.md](HUMANIZATION_README.md)
- **Airflow Docs:** https://airflow.apache.org/docs/

---

## 📦 Project Structure

```
CareerPlanner/
├── airflow/
│   ├── dags/
│   │   └── linkedin_job_scraper_dag.py  # Main DAG file
│   ├── logs/                             # Airflow logs
│   ├── plugins/                          # Custom plugins
│   └── config/                           # Config files
├── data/                                 # Scraped job data (CSV files)
│   └── archive/                          # Archived old data
├── linkedin_job_scraper.py               # Main scraper script
├── humanize_scraper.py                   # Humanization utilities
├── docker-compose.yml                    # Docker services config
├── requirements.txt                      # Python dependencies
├── .env                                  # Environment variables (not in git)
├── .env.example                          # Example env file
├── setup_airflow.sh                      # Quick setup script
├── AIRFLOW_SETUP.md                      # Full setup guide
├── HUMANIZATION_README.md                # Humanization guide
└── QUICK_START.md                        # This file!
```

---

## ✅ Checklist

Before running your first scrape, make sure:

- [ ] Docker & Docker Compose are installed
- [ ] `.env` file exists with LinkedIn credentials
- [ ] Airflow services are running (`docker-compose ps`)
- [ ] Can access Airflow UI at http://localhost:8080
- [ ] Airflow Variables are configured
- [ ] DAG is unpaused (toggled On)
- [ ] Have triggered a test run
- [ ] Logs show successful execution
- [ ] CSV files appear in `data/` directory

---

Happy scraping! 🎉

For detailed documentation, see [AIRFLOW_SETUP.md](AIRFLOW_SETUP.md)
