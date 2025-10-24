# Airflow DAG Workflow Visualization

## Overview

This document explains the automated workflow for the LinkedIn Job Scraper.

---

## DAG Task Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    linkedin_job_scraper DAG                         │
│                                                                      │
│  Schedule: Daily at 9 AM (configurable)                             │
│  Max Runtime: 2 hours                                               │
│  Retries: 2 (with 5 min delay)                                      │
└─────────────────────────────────────────────────────────────────────┘

                              ↓

        ┌─────────────────────────────────────┐
        │   Task 1: scrape_linkedin_jobs      │
        │                                     │
        │   • Login to LinkedIn               │
        │   • For each job query:             │
        │     - For each location:            │
        │       - Search jobs                 │
        │       - Extract data                │
        │       - Save to CSV                 │
        │   • Combine all results             │
        │                                     │
        │   Duration: ~30-90 minutes          │
        └─────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────┐
        │   Task 2: deduplicate_jobs          │
        │                                     │
        │   • Read combined CSV               │
        │   • Remove duplicates by:           │
        │     - Company name                  │
        │     - Job title                     │
        │   • Save deduped version            │
        │                                     │
        │   Duration: ~10-30 seconds          │
        └─────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────┐
        │   Task 3: archive_old_data          │
        │                                     │
        │   • Find CSV files > 7 days old     │
        │   • Move to archive/ folder         │
        │   • Keep data directory clean       │
        │                                     │
        │   Duration: ~5-10 seconds           │
        └─────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────┐
        │   Task 4: generate_summary          │
        │                                     │
        │   • Count total jobs scraped        │
        │   • Count unique jobs               │
        │   • Generate summary report         │
        │   • Log statistics                  │
        │                                     │
        │   Duration: ~1-2 seconds            │
        └─────────────────────────────────────┘
                              ↓
                        ✅ Complete!
```

---

## Data Flow

```
┌─────────────────┐
│  Airflow        │
│  Variables      │──────┐
│                 │      │
│ • job_queries   │      │
│ • locations     │      │
│ • max_jobs      │      │
└─────────────────┘      │
                         ↓
                ┌─────────────────┐
                │  Scraper Task   │
                └─────────────────┘
                         ↓
         ┌───────────────────────────────┐
         │     For each combination:     │
         │                               │
         │  Job Query 1 + Location 1 →   │──→ job1_loc1_timestamp.csv
         │  Job Query 1 + Location 2 →   │──→ job1_loc2_timestamp.csv
         │  Job Query 2 + Location 1 →   │──→ job2_loc1_timestamp.csv
         │  ...                          │
         └───────────────────────────────┘
                         ↓
                ┌─────────────────┐
                │  Combine All    │
                └─────────────────┘
                         ↓
            all_jobs_YYYYMMDD_HHMMSS.csv
                         ↓
                ┌─────────────────┐
                │  Deduplicate    │
                └─────────────────┘
                         ↓
        all_jobs_YYYYMMDD_HHMMSS_deduped.csv
                         ↓
                ┌─────────────────┐
                │  Archive Old    │
                └─────────────────┘
                         ↓
         data/           data/archive/
         └── recent.csv  └── old.csv
```

---

## Example Run Scenario

### Configuration
- **Job Queries:** `Software Engineer, Data Scientist`
- **Locations:** `San Francisco, New York`
- **Max Jobs Per Search:** `20`

### Execution Timeline

```
09:00:00  DAG triggered (scheduled)
          ↓
09:00:01  Task 1 starts: scrape_linkedin_jobs
          ↓
09:00:15  Login to LinkedIn successful
          ↓
09:02:00  Searching: Software Engineer in San Francisco
09:05:30  Extracted 20 jobs → SoftwareEngineer_SanFrancisco_20240129_090000.csv
          ↓
09:06:00  Searching: Software Engineer in New York
09:09:30  Extracted 20 jobs → SoftwareEngineer_NewYork_20240129_090000.csv
          ↓
09:10:00  Searching: Data Scientist in San Francisco
09:13:30  Extracted 20 jobs → DataScientist_SanFrancisco_20240129_090000.csv
          ↓
09:14:00  Searching: Data Scientist in New York
09:17:30  Extracted 20 jobs → DataScientist_NewYork_20240129_090000.csv
          ↓
09:18:00  Combining all results (80 total jobs)
09:18:05  Saved: all_jobs_20240129_091800.csv
          ↓
09:18:05  Task 1 complete ✅ (Duration: 18 minutes)
          ────────────────────────────────────────────
09:18:06  Task 2 starts: deduplicate_jobs
          ↓
09:18:10  Removed 5 duplicates
09:18:15  Saved: all_jobs_20240129_091800_deduped.csv (75 unique jobs)
          ↓
09:18:15  Task 2 complete ✅ (Duration: 9 seconds)
          ────────────────────────────────────────────
09:18:16  Task 3 starts: archive_old_data
          ↓
09:18:20  Found 3 files older than 7 days
09:18:25  Moved to archive/ folder
          ↓
09:18:25  Task 3 complete ✅ (Duration: 9 seconds)
          ────────────────────────────────────────────
09:18:26  Task 4 starts: generate_summary
          ↓
09:18:27  Summary Report:
          - Total jobs scraped: 80
          - Unique jobs: 75
          - Duplicates removed: 5
          ↓
09:18:27  Task 4 complete ✅ (Duration: 1 second)
          ────────────────────────────────────────────
09:18:27  DAG run complete! ✅
          Total Duration: ~18.5 minutes
```

---

## File Structure Over Time

### Day 1 (First Run)
```
data/
├── all_jobs_20240129_090000.csv
├── all_jobs_20240129_090000_deduped.csv
└── archive/
```

### Day 2 (Second Run)
```
data/
├── all_jobs_20240129_090000.csv
├── all_jobs_20240129_090000_deduped.csv
├── all_jobs_20240130_090000.csv
├── all_jobs_20240130_090000_deduped.csv
└── archive/
```

### Day 8 (Eighth Run - Old Files Archived)
```
data/
├── all_jobs_20240202_090000.csv
├── all_jobs_20240202_090000_deduped.csv
├── all_jobs_20240203_090000.csv
├── all_jobs_20240203_090000_deduped.csv
├── all_jobs_20240204_090000.csv
├── all_jobs_20240204_090000_deduped.csv
├── all_jobs_20240205_090000.csv
├── all_jobs_20240205_090000_deduped.csv
└── archive/
    ├── all_jobs_20240129_090000.csv  ← Archived (>7 days old)
    ├── all_jobs_20240129_090000_deduped.csv
    ├── all_jobs_20240130_090000.csv
    └── all_jobs_20240130_090000_deduped.csv
```

---

## Scaling Examples

### Small Scale (Testing)
```
Queries:     Software Engineer
Locations:   San Francisco
Max Jobs:    5

= 1 × 1 × 5 = 5 jobs
Runtime: ~3 minutes
```

### Medium Scale (Personal Use)
```
Queries:     Software Engineer, Data Scientist, ML Engineer
Locations:   San Francisco, New York, Seattle
Max Jobs:    20

= 3 × 3 × 20 = 180 jobs (before deduplication)
Runtime: ~30-45 minutes
```

### Large Scale (Market Research)
```
Queries:     Software Engineer, Senior SWE, Staff Engineer,
             Data Scientist, ML Engineer, DevOps Engineer,
             Product Manager, Engineering Manager
Locations:   San Francisco, New York, Seattle, Austin,
             Boston, Los Angeles, Chicago, Denver
Max Jobs:    50

= 8 × 8 × 50 = 3,200 jobs (before deduplication)
Runtime: ~2-3 hours
WARNING: May trigger LinkedIn anti-bot systems!
```

---

## Error Handling Flow

```
                Task Execution
                      ↓
             ┌────────┴────────┐
             │                 │
         Success           Error?
             │                 │
             ↓                 ↓
        Next Task      ┌──────────────┐
                       │ Retry Logic  │
                       └──────────────┘
                              ↓
                    ┌─────────┴─────────┐
                    │                   │
                Retry 1             Retry 2
                    │                   │
                Success?            Success?
                    ↓                   ↓
                Next Task       ┌───────┴───────┐
                                │               │
                            Success         Final
                                │          Failure
                            Next Task         │
                                              ↓
                                      ┌──────────────┐
                                      │ Send Alert   │
                                      │ (if enabled) │
                                      └──────────────┘
```

**Retry Settings:**
- **Retries:** 2 attempts
- **Retry Delay:** 5 minutes between attempts
- **Timeout:** 2 hours max per task

---

## Monitoring Points

### Key Metrics to Watch

1. **DAG Success Rate**
   - Location: Airflow UI → DAG → Graph View
   - Green tasks = success

2. **Execution Duration**
   - Location: Airflow UI → DAG → Duration chart
   - Should be consistent

3. **Job Count**
   - Check logs in `generate_summary` task
   - Sudden drops may indicate issues

4. **Error Logs**
   - Location: Airflow UI → Task → Logs
   - Check for LinkedIn blocking errors

5. **Data Output**
   - Directory: `data/`
   - Verify CSV files are being created

---

## Integration with Humanization

When using `humanize_scraper.py`:

```
Standard Flow:              With Humanization:

Login                       Login
  ↓                           ↓
Click search box            Scan page (human-like)
  ↓                           ↓
Type query                  Scroll to search box
  ↓                           ↓
Click location              Human-type query slowly
  ↓                           ↓
Type location               Pause and read
  ↓                           ↓
Submit                      Scroll to location box
                              ↓
                            Human-type location
                              ↓
                            Pause before submit
                              ↓
                            Submit

Runtime:                    Runtime:
~30 min for 100 jobs       ~45-60 min for 100 jobs

Detection Risk:             Detection Risk:
Medium                     Low
```

**Trade-off:** Humanization adds 50-100% more time but significantly reduces detection risk.

---

## Recommended Schedules

### Conservative (Recommended for Personal Use)
```
Schedule:   Daily at 9 AM
Queries:    3-5 job titles
Locations:  3-5 cities
Max Jobs:   20 per search
Total Jobs: ~300-500/day

Risk Level: ✅ Low
```

### Moderate (For Active Job Search)
```
Schedule:   Twice daily (9 AM, 6 PM)
Queries:    5-8 job titles
Locations:  5-8 cities
Max Jobs:   20 per search
Total Jobs: ~1,000-1,500/day

Risk Level: ⚠️ Medium
Recommendation: Use humanization
```

### Aggressive (Market Research Only)
```
Schedule:   Every 6 hours
Queries:    10+ job titles
Locations:  10+ cities
Max Jobs:   30-50 per search
Total Jobs: ~4,000+/day

Risk Level: ❌ High
Recommendation: Use humanization + proxies + rate limiting
WARNING: May get account flagged!
```

---

## Summary

This Airflow automation provides:
- ✅ **Scheduled scraping** - No manual intervention
- ✅ **Parallel searches** - Multiple queries at once
- ✅ **Data management** - Automatic deduplication and archiving
- ✅ **Monitoring** - Track success/failure in UI
- ✅ **Reliability** - Automatic retries on failure
- ✅ **Scalability** - Easy to add more searches

For setup instructions, see [QUICK_START.md](QUICK_START.md)
