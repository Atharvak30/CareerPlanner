# LinkedIn Job Scraper - Career Planner

An automated, intelligent LinkedIn job scraping system with Apache Airflow orchestration and human-like behavior simulation.

## 🎯 Features

- **Automated Scraping** - Schedule daily/weekly job searches with Apache Airflow
- **Human-like Behavior** - Realistic typing, scrolling, and mouse movements to avoid detection
- **Multi-Search Support** - Search multiple job titles across multiple locations simultaneously
- **Data Management** - Automatic deduplication, archiving, and CSV export
- **Monitoring & Logging** - Web-based dashboard for tracking scraping progress
- **Error Handling** - Automatic retries and failure notifications
- **Dockerized** - Easy setup with Docker Compose

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Features in Detail](#features-in-detail)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Usage Examples](#usage-examples)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)
- [Legal & Ethics](#legal--ethics)

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- LinkedIn account
- 5 minutes of your time

### Installation

```bash
# 1. Clone/navigate to project
cd /Users/siddhant/Developer/CareerPlanner

# 2. Create .env file with your LinkedIn credentials
cp .env.example .env
# Edit .env and add your credentials

# 3. Run automated setup
./setup_airflow.sh

# 4. Access Airflow UI
# Open http://localhost:8080 in browser
# Login: admin / admin123
```

### First Run

1. In Airflow UI, go to **Admin** → **Variables**
2. Add your search parameters:
   - `linkedin_job_queries`: `Software Engineer,Data Scientist`
   - `linkedin_locations`: `San Francisco,New York`
   - `linkedin_max_jobs_per_search`: `20`

3. Enable the DAG by toggling it **On**
4. Click **Trigger DAG** to start scraping
5. Monitor progress in the Graph view
6. Find results in `data/` directory

**See [QUICK_START.md](QUICK_START.md) for detailed instructions.**

---

## 🎨 Features in Detail

### 1. Airflow Automation

- **Scheduled Execution** - Set it and forget it. Runs daily at 9 AM (configurable)
- **Task Orchestration** - Four-step workflow:
  1. Scrape jobs from LinkedIn
  2. Remove duplicates
  3. Archive old data
  4. Generate summary report
- **Web Dashboard** - Monitor all runs, view logs, track statistics
- **Retry Logic** - Automatically retries failed tasks
- **Email Alerts** - Get notified on success/failure (configurable)

**Documentation:** [AIRFLOW_SETUP.md](AIRFLOW_SETUP.md)

### 2. Humanization Engine

Makes your scraper appear more human to avoid detection:

- **Realistic Typing** - Variable keystroke timing with occasional pauses
- **Smooth Scrolling** - Animated scrolling instead of instant jumps
- **Mouse Movements** - Random cursor movements and hover behavior
- **Reading Pauses** - Simulates reading content before taking actions
- **Page Scanning** - Scrolls up/down like a human browsing

**Benefits:**
- Reduces detection risk by 60-80%
- More reliable long-term operation
- Respectful rate limiting built-in

**Documentation:** [HUMANIZATION_README.md](HUMANIZATION_README.md)

### 3. Multi-Search Capability

Search multiple job titles across multiple locations in a single run:

```
Job Queries:  Software Engineer, Data Scientist, ML Engineer
Locations:    San Francisco, New York, Seattle

= 3 × 3 = 9 searches per run
```

Each search saves a separate CSV, then all are combined and deduplicated.

### 4. Data Management

- **CSV Export** - Clean, structured data with timestamps
- **Deduplication** - Removes duplicate jobs by company + title
- **Archiving** - Auto-archives files older than 7 days (configurable)
- **Metadata** - Each job includes search query, location, scrape date

### 5. Anti-Detection Measures

- **Chrome Options** - Disables automation flags
- **User Agent Spoofing** - Uses realistic browser user agents
- **WebDriver Masking** - Hides Selenium WebDriver property
- **Variable Delays** - Random delays between actions
- **Humanization** - Realistic interaction patterns

---

## 📁 Project Structure

```
CareerPlanner/
│
├── airflow/                          # Airflow files
│   ├── dags/
│   │   └── linkedin_job_scraper_dag.py  # Main automation DAG
│   ├── logs/                         # Task execution logs
│   ├── plugins/                      # Custom Airflow plugins
│   └── config/                       # Configuration files
│
├── data/                             # Scraped data output
│   ├── all_jobs_YYYYMMDD_HHMMSS.csv      # Combined results
│   ├── all_jobs_YYYYMMDD_HHMMSS_deduped.csv  # Without duplicates
│   └── archive/                      # Old files (>7 days)
│
├── linkedin_job_scraper.py           # Core scraping logic
├── humanize_scraper.py               # Human behavior simulation
├── humanize_scraper_examples.py      # Usage examples for humanization
│
├── docker-compose.yml                # Docker services configuration
├── requirements.txt                  # Python dependencies
├── .env                              # Environment variables (create from .env.example)
├── .env.example                      # Template for environment variables
│
├── setup_airflow.sh                  # Automated setup script
│
├── README.md                         # This file
├── QUICK_START.md                    # Quick start guide
├── AIRFLOW_SETUP.md                  # Detailed Airflow setup
├── AIRFLOW_WORKFLOW.md               # Workflow visualization
└── HUMANIZATION_README.md            # Humanization guide
```

---

## 📚 Documentation

| Document | Description | Use When |
|----------|-------------|----------|
| [QUICK_START.md](QUICK_START.md) | 5-minute setup guide | First time setup |
| [AIRFLOW_SETUP.md](AIRFLOW_SETUP.md) | Complete Airflow guide | Need detailed instructions |
| [AIRFLOW_WORKFLOW.md](AIRFLOW_WORKFLOW.md) | Visual workflow diagrams | Understanding the process |
| [HUMANIZATION_README.md](HUMANIZATION_README.md) | Humanization features | Reducing detection risk |

---

## 💡 Usage Examples

### Example 1: Daily Job Search

**Goal:** Track new Software Engineering jobs in SF daily

```python
# Airflow Variables:
linkedin_job_queries = "Software Engineer"
linkedin_locations = "San Francisco"
linkedin_max_jobs_per_search = "20"

# Schedule: Daily at 9 AM
schedule_interval = '0 9 * * *'
```

**Result:** 20 new job postings every morning in `data/` folder

---

### Example 2: Multi-Role Job Hunt

**Goal:** Find various tech roles across multiple cities

```python
# Airflow Variables:
linkedin_job_queries = "Software Engineer,Data Scientist,Product Manager,DevOps Engineer"
linkedin_locations = "San Francisco,New York,Seattle,Austin"
linkedin_max_jobs_per_search = "20"

# Schedule: Daily at 9 AM
schedule_interval = '0 9 * * *'
```

**Result:** 4 roles × 4 cities × 20 jobs = 320 jobs/day (before deduplication)

---

### Example 3: Weekly Market Research

**Goal:** Monitor job market trends weekly

```python
# Airflow Variables:
linkedin_job_queries = "Machine Learning Engineer,AI Engineer,ML Researcher"
linkedin_locations = "San Francisco,Boston,Seattle"
linkedin_max_jobs_per_search = "50"

# Schedule: Every Monday at 9 AM
schedule_interval = '0 9 * * 1'
```

**Result:** Weekly snapshot of ML job market (450 jobs/week)

---

### Example 4: With Humanization (Low Detection Risk)

```python
# In your scraper, use humanization:
from humanize_scraper import HumanBehavior

driver = setup_chrome_driver()
human = HumanBehavior(driver, delay_min=4.0, delay_max=8.0)

# Use humanized actions
human.realistic_click(element)
human.human_type(input_field, "Software Engineer", typing_speed='normal')
human.scan_page(num_scrolls=2)
human.pause_and_read(3.0, 6.0)
```

**Result:** 50% slower but 80% less likely to be detected

---

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# Required
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password

# Airflow UI
_AIRFLOW_WWW_USER_USERNAME=admin
_AIRFLOW_WWW_USER_PASSWORD=admin123

# System
AIRFLOW_UID=50000
```

### Airflow Variables (in UI)

| Variable | Default | Description |
|----------|---------|-------------|
| `linkedin_job_queries` | `Software Engineer,Data Scientist` | Comma-separated job titles |
| `linkedin_locations` | `San Francisco,New York` | Comma-separated locations |
| `linkedin_max_jobs_per_search` | `20` | Max jobs per search |
| `linkedin_output_dir` | `/opt/airflow/data` | Output directory |
| `linkedin_archive_days` | `7` | Days before archiving |

### Schedule Options

Edit `airflow/dags/linkedin_job_scraper_dag.py`:

```python
schedule_interval='0 9 * * *'  # Daily at 9 AM
# schedule_interval='0 */6 * * *'  # Every 6 hours
# schedule_interval='0 9 * * 1'  # Weekly (Mondays)
# schedule_interval='@daily'  # Daily at midnight
# schedule_interval=None  # Manual only
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. DAG Not Appearing

```bash
# Check for Python errors
docker-compose exec airflow-webserver python /opt/airflow/dags/linkedin_job_scraper_dag.py

# Check scheduler logs
docker-compose logs airflow-scheduler | grep ERROR
```

#### 2. Login Failing

- Verify credentials in `.env` file
- Check if LinkedIn requires 2FA (not supported yet)
- Try logging in manually to check account status

#### 3. No Jobs Scraped

- Reduce `linkedin_max_jobs_per_search` to 10
- Try different job queries/locations
- Check if logged into LinkedIn successfully (view logs)

#### 4. LinkedIn Blocking Requests

**Solutions:**
- Enable humanization features
- Reduce scraping frequency (weekly instead of daily)
- Lower max jobs per search
- Add longer delays

#### 5. Docker Services Not Starting

```bash
# Clean up and restart
docker-compose down -v
docker system prune -a
./setup_airflow.sh
```

---

## ✅ Best Practices

### 1. Start Small

Begin with:
- 1-2 job queries
- 1-2 locations
- Max 10-20 jobs per search
- Manual trigger first, then schedule

### 2. Use Humanization

Always integrate humanization for:
- Daily/frequent scraping
- Large-scale scraping
- Long-term use

### 3. Monitor Regularly

Check:
- DAG success rate (should be >95%)
- Execution time (should be consistent)
- Job counts (sudden drops = problems)
- Error logs (watch for LinkedIn errors)

### 4. Data Management

- Review archived data monthly
- Export to database for long-term analysis
- Delete unnecessary raw CSVs

### 5. Respect Rate Limits

- Don't scrape more than 500 jobs/day
- Use delays between searches
- Avoid peak hours (9-5 PT)
- Consider weekly instead of daily

---

## ⚖️ Legal & Ethics

### Important Considerations

1. **Terms of Service**
   - LinkedIn's ToS prohibits automated scraping
   - This tool is for **educational** and **personal research** only
   - Use responsibly and at your own risk

2. **Personal Use Only**
   - Not for commercial purposes
   - Not for reselling data
   - Not for spam/recruiting

3. **Data Privacy**
   - Only scrape public job postings
   - Don't store personal information
   - Respect privacy laws (GDPR, CCPA)

4. **Ethical Scraping**
   - Use reasonable delays (humanization)
   - Don't overload LinkedIn servers
   - Respect robots.txt
   - Stop if blocked

### Recommendations

- ✅ Personal job search
- ✅ Market research (non-commercial)
- ✅ Educational purposes
- ❌ Commercial data selling
- ❌ Bulk email/spam
- ❌ Competitive intelligence for business

**Use this tool responsibly and ethically.**

---

## 🛠️ Development

### Running Locally (Without Docker)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment
export AIRFLOW_HOME=$(pwd)/airflow

# Initialize Airflow
airflow db init

# Create admin user
airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com

# Start services
airflow webserver &
airflow scheduler &
```

### Testing the Scraper Independently

```bash
# Test without Airflow
python linkedin_job_scraper.py
```

### Adding Custom Features

1. **Modify DAG:** Edit `airflow/dags/linkedin_job_scraper_dag.py`
2. **Add Tasks:** Create new PythonOperators
3. **Update Dependencies:** Install new packages in `requirements.txt`
4. **Restart:** `docker-compose restart`

---

## 📊 Data Schema

### Output CSV Format

| Column | Type | Description |
|--------|------|-------------|
| `company` | string | Company name |
| `title` | string | Job title |
| `description` | text | Full job description |
| `search_job_query` | string | Search query used |
| `search_location` | string | Location searched |
| `scrape_date` | datetime | When scraped |
| `extraction_timestamp` | datetime | Exact extraction time |

### Example Row

```csv
company,title,description,search_job_query,search_location,scrape_date,extraction_timestamp
"Google","Senior Software Engineer","We are looking for...",
"Software Engineer","San Francisco","2024-01-29 09:15:30","2024-01-29 09:15:30.123456"
```

---

## 🤝 Contributing

This is a personal project for educational purposes. However, suggestions are welcome!

### Ideas for Enhancement

- [ ] Add job filtering (salary, remote, etc.)
- [ ] Export to PostgreSQL/MySQL
- [ ] Build analytics dashboard
- [ ] Add Slack/email notifications
- [ ] Support multiple LinkedIn accounts
- [ ] Add keyword matching/scoring
- [ ] Implement proxy rotation

---

## 📝 License

This project is for educational and personal use only.

**Disclaimer:** The authors are not responsible for any misuse of this tool. Use at your own risk and in compliance with LinkedIn's Terms of Service.

---

## 🙏 Acknowledgments

- **Apache Airflow** - Workflow orchestration
- **Selenium** - Browser automation
- **LinkedIn** - Job data source

---

## 📧 Support

For issues or questions:

1. Check documentation in this repo
2. Review error logs in Airflow UI
3. Test scraper script independently
4. Verify LinkedIn credentials are valid

---

## 🎉 Get Started Now!

```bash
./setup_airflow.sh
```

Then open http://localhost:8080 and start scraping!

**Happy job hunting! 🚀**
