"""
LinkedIn Job Scraper DAG

This DAG automates the LinkedIn job scraping process with the following features:
- Scheduled scraping at configurable intervals
- Multiple job search queries (job titles and locations)
- Data archiving and deduplication
- Error handling and notifications
- Configurable scraping parameters

Author: Career Planner
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from airflow.models import Variable
from datetime import datetime, timedelta
import os
import sys
import logging

# Add the project directory to Python path
PROJECT_DIR = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, PROJECT_DIR)

# Import datetime format constants
from utils.constants import DATETIME_FORMAT, DATETIME_FORMAT_READABLE

# Configure logging
logger = logging.getLogger(__name__)

# Default arguments for the DAG
default_args = {
    'owner': 'career_planner',
    'depends_on_past': False,
    'email': ['sidsnmb@gmail.com'],  # Replace with your email
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=2),  # Max 2 hours per run
}

# DAG definition
dag = DAG(
    'linkedin_job_scraper',
    default_args=default_args,
    description='Scrape LinkedIn job postings and save to CSV',
    schedule_interval='0 8 * * *',  # Run daily at 8 AM UTC (12 AM PST)
    start_date=days_ago(1),
    catchup=False,
    tags=['scraping', 'linkedin', 'jobs', 'data-collection'],
    max_active_runs=1,  # Only one run at a time
)


def scrape_jobs(**context):
    """
    Main scraping task that runs the LinkedIn job scraper.

    This function:
    1. Loads environment variables
    2. Sets up the Chrome driver
    3. Logs into LinkedIn
    4. Searches for jobs based on configured queries
    5. Extracts job data
    6. Saves results to CSV
    """
    import pandas as pd
    from scrapers.linkedin.linkedin_job_scraper import (
        load_env_variables,
        open_linkedin_session,
        navigate_to_jobs_page,
        find_and_fill_search_boxes,
        extract_linkedin_jobs,
        DateFilter
    )
    from utils.logger_config import ScraperLogger

    # Load configuration from Airflow Variables (set these in Airflow UI)
    # Or use default values
    job_queries = Variable.get("linkedin_job_queries",
                               default_var="Software Engineer,Data Scientist,ML Engineer",
                               deserialize_json=False).split(',')

    locations = Variable.get("linkedin_locations",
                            default_var="San Francisco,New York,Seattle",
                            deserialize_json=False).split(',')

    max_jobs_per_search = int(Variable.get("linkedin_max_jobs_per_search", default_var="20"))

    # Time filter configuration - map string to DateFilter enum
    time_filter_str = Variable.get("linkedin_time_filter", default_var="24hrs")
    time_filter_map = {
        "24hrs": DateFilter.PAST_24_HOURS,
        "1week": DateFilter.PAST_WEEK,
        "1month": DateFilter.PAST_MONTH,
        "any": DateFilter.ANY_TIME
    }
    time_posted = time_filter_map.get(time_filter_str.lower(), DateFilter.PAST_24_HOURS)

    output_dir = Variable.get("linkedin_output_dir",
                             default_var=os.path.join(PROJECT_DIR, "data", "airflow"))

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Initialize custom logger for detailed scraping logs
    custom_logger = ScraperLogger(run_name="airflow_dag")

    logger.info(f"Starting scraping with {len(job_queries)} job queries and {len(locations)} locations")
    logger.info(f"Job Queries: {job_queries}")
    logger.info(f"Locations: {locations}")

    # Load environment variables
    load_env_variables()

    # Open LinkedIn session
    driver = None
    all_jobs_data = []

    try:
        # Use remote Selenium Grid (chrome container) in Docker environment
        remote_url = "http://chrome:4444"
        driver = open_linkedin_session(log=custom_logger, remote_url=remote_url)

        if not driver:
            raise Exception("Failed to open LinkedIn session")

        # Iterate through each job query and location combination
        for job_query in job_queries:
            for location in locations:
                job_query = job_query.strip()
                location = location.strip()

                logger.info(f"Scraping: {job_query} in {location}")

                # Navigate to jobs page
                if not navigate_to_jobs_page(driver):
                    logger.warning(f"Failed to navigate to jobs page for {job_query} - {location}")
                    continue

                # Fill search boxes
                success, message = find_and_fill_search_boxes(driver, job_query, location, time_posted.value)

                if not success:
                    logger.warning(f"Failed to fill search boxes: {message}")
                    continue

                # Generate output filename
                timestamp = datetime.now().strftime(DATETIME_FORMAT)
                filename = f"{job_query.replace(' ', '_')}_{location.replace(' ', '_')}_{timestamp}.csv"
                output_file = os.path.join(output_dir, filename)

                # Extract jobs
                df, success_count, error_count = extract_linkedin_jobs(
                    driver,
                    max_jobs=max_jobs_per_search,
                    output_file=output_file
                )

                if df is not None and not df.empty:
                    # Add metadata
                    df['search_job_query'] = job_query
                    df['search_location'] = location
                    df['scrape_date'] = datetime.now().strftime(DATETIME_FORMAT_READABLE)

                    all_jobs_data.append(df)
                    logger.info(f"Successfully scraped {len(df)} jobs for {job_query} in {location}")
                else:
                    logger.warning(f"No jobs found for {job_query} in {location}")

        # Combine all results
        if all_jobs_data:
            combined_df = pd.concat(all_jobs_data, ignore_index=True)

            # Save combined results
            combined_filename = f"all_jobs_{datetime.now().strftime(DATETIME_FORMAT)}.csv"
            combined_output = os.path.join(output_dir, combined_filename)
            combined_df.to_csv(combined_output, index=False)

            logger.info(f"Saved combined results: {len(combined_df)} total jobs to {combined_output}")

            # Push results to XCom for downstream tasks
            context['task_instance'].xcom_push(key='output_file', value=combined_output)
            context['task_instance'].xcom_push(key='total_jobs', value=len(combined_df))

            return {
                'total_jobs': len(combined_df),
                'output_file': combined_output,
                'searches_completed': len(job_queries) * len(locations)
            }
        else:
            raise Exception("No jobs were scraped from any query")

    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}")
        raise

    finally:
        if driver:
            logger.info("Closing browser...")
            driver.quit()


def deduplicate_jobs(**context):
    """
    Remove duplicate job postings based on company and title.

    Reads the output file from the scraping task and removes duplicates.
    """
    import pandas as pd

    # Get output file from previous task
    output_file = context['task_instance'].xcom_pull(
        task_ids='scrape_linkedin_jobs',
        key='output_file'
    )

    if not output_file or not os.path.exists(output_file):
        logger.warning("No output file found to deduplicate")
        return

    logger.info(f"Deduplicating jobs from {output_file}")

    # Read CSV
    df = pd.read_csv(output_file)
    original_count = len(df)

    # Remove duplicates based on company and title
    df_deduped = df.drop_duplicates(subset=['company', 'title'], keep='first')

    # Save deduplicated version
    deduped_file = output_file.replace('.csv', '_deduped.csv')
    df_deduped.to_csv(deduped_file, index=False)

    removed_count = original_count - len(df_deduped)
    logger.info(f"Removed {removed_count} duplicate jobs. {len(df_deduped)} unique jobs remaining.")

    # Push to XCom
    context['task_instance'].xcom_push(key='deduped_file', value=deduped_file)
    context['task_instance'].xcom_push(key='unique_jobs', value=len(df_deduped))

    return {
        'original_count': original_count,
        'unique_count': len(df_deduped),
        'duplicates_removed': removed_count
    }


def archive_old_data(**context):
    """
    Archive CSV files older than X days to keep the data directory clean.
    """
    import shutil
    from pathlib import Path

    output_dir = Variable.get("linkedin_output_dir",
                             default_var=os.path.join(PROJECT_DIR, "data"))

    archive_dir = os.path.join(output_dir, "archive")
    os.makedirs(archive_dir, exist_ok=True)

    # Archive files older than 7 days
    archive_days = int(Variable.get("linkedin_archive_days", default_var="7"))
    cutoff_date = datetime.now() - timedelta(days=archive_days)

    archived_count = 0

    for csv_file in Path(output_dir).glob("*.csv"):
        # Skip files in archive directory
        if 'archive' in str(csv_file):
            continue

        # Check file modification time
        file_mtime = datetime.fromtimestamp(csv_file.stat().st_mtime)

        if file_mtime < cutoff_date:
            # Move to archive
            dest = os.path.join(archive_dir, csv_file.name)
            shutil.move(str(csv_file), dest)
            archived_count += 1
            logger.info(f"Archived: {csv_file.name}")

    logger.info(f"Archived {archived_count} old CSV files")

    return {'archived_count': archived_count}


def generate_summary_report(**context):
    """
    Generate a summary report of the scraping run.
    """
    total_jobs = context['task_instance'].xcom_pull(
        task_ids='scrape_linkedin_jobs',
        key='total_jobs'
    )

    unique_jobs = context['task_instance'].xcom_pull(
        task_ids='deduplicate_jobs',
        key='unique_jobs'
    )

    logger.info("="*80)
    logger.info("SCRAPING SUMMARY REPORT")
    logger.info("="*80)
    logger.info(f"Run Date: {datetime.now().strftime(DATETIME_FORMAT_READABLE)}")
    logger.info(f"Total Jobs Scraped: {total_jobs}")
    logger.info(f"Unique Jobs: {unique_jobs}")
    logger.info(f"Duplicates Removed: {total_jobs - unique_jobs}")
    logger.info("="*80)

    # Could expand this to send email, Slack notification, etc.
    return {
        'summary': f"Scraped {total_jobs} jobs, {unique_jobs} unique"
    }


# Define tasks
scrape_task = PythonOperator(
    task_id='scrape_linkedin_jobs',
    python_callable=scrape_jobs,
    dag=dag,
    provide_context=True,
)

deduplicate_task = PythonOperator(
    task_id='deduplicate_jobs',
    python_callable=deduplicate_jobs,
    dag=dag,
    provide_context=True,
)

archive_task = PythonOperator(
    task_id='archive_old_data',
    python_callable=archive_old_data,
    dag=dag,
    provide_context=True,
)

summary_task = PythonOperator(
    task_id='generate_summary',
    python_callable=generate_summary_report,
    dag=dag,
    provide_context=True,
)

# Set task dependencies
scrape_task >> deduplicate_task >> archive_task >> summary_task
