#!/usr/bin/env python3
"""
Test script for LinkedIn scraper with comprehensive logging.

This creates a detailed log directory for each run with:
- Console and file logging
- Screenshots on errors
- HTML page dumps
- Separate error logs
- Debug logs
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path
from utils.constants import DATETIME_FORMAT, DATETIME_FORMAT_READABLE  

# Add project root to Python path
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import modules
from utils.logger_config import create_logger
from scrapers.linkedin.linkedin_job_scraper import (
    open_linkedin_session,
    navigate_to_jobs_page,
    find_and_fill_search_boxes,
    extract_linkedin_jobs,
    DateFilter
)


def main(debug_test=False, job_title="Software Engineer", location="San Francisco", time_posted="24hrs"):
    """Run the scraper test with detailed logging.

    Args:
        debug_test (bool): If True, keeps browser open on errors for debugging.
        job_title (str): Job title to search for
        location (str): Location to search in
        time_posted (str): Time filter - "24hrs", "1week", "1month", or "any"
    """

    # Parse time_posted string to DateFilter enum
    time_filter_map = {
        "24hrs": DateFilter.PAST_24_HOURS,
        "1week": DateFilter.PAST_WEEK,
        "1month": DateFilter.PAST_MONTH,
        "any": DateFilter.ANY_TIME
    }
    TEST_DATE_FILTER = time_filter_map.get(time_posted.lower(), DateFilter.PAST_24_HOURS)

    # Test configuration
    TEST_JOB_QUERY = job_title
    TEST_LOCATION = location
    TEST_MAX_JOBS = 5  # Small number for testing

    print("="*80)
    print("LinkedIn Job Scraper - Test with Logging")
    print("="*80)
    print()
    print(f"Test Configuration:")
    print(f"  Job Query: {TEST_JOB_QUERY}")
    print(f"  Location: {TEST_LOCATION}")
    print(f"  Max Jobs: {TEST_MAX_JOBS}")
    print(f"  Date Filter: {TEST_DATE_FILTER.value if TEST_DATE_FILTER.value else 'Any Time'}")
    print()
    print("This will create a log directory with:")
    print("  - Console and file logging")
    print("  - Screenshots on errors")
    print("  - HTML page dumps")
    print("  - Separate debug and error logs")
    print()

    input("Press Enter to start, or Ctrl+C to cancel... ")
    print()

    # Create logger for this run
    logger = create_logger(log_base_dir="logs", run_name="test")

    logger.log_step("Starting LinkedIn Scraper Test")
    logger.info(f"Test Configuration: {TEST_JOB_QUERY} in {TEST_LOCATION}")
    logger.info(f"Max jobs to extract: {TEST_MAX_JOBS}")
    logger.info(f"Log directory: {logger.get_run_dir()}")

    driver = None
    success = False

    try:
        # Step 1: Open LinkedIn session
        logger.log_step("Opening LinkedIn Session", 1)

        driver = open_linkedin_session(log=logger)

        if not driver:
            logger.error("Failed to open LinkedIn session")
            print("\n❌ TEST FAILED: Could not login to LinkedIn")
            print(f"Check logs in: {logger.get_run_dir()}")
            return False

        logger.info("Successfully logged in to LinkedIn")

        # Step 2: Navigate to jobs page
        logger.log_step("Navigating to Jobs Page", 2)

        if not navigate_to_jobs_page(driver):
            logger.error("Failed to navigate to jobs page")
            print("\n❌ TEST FAILED: Could not navigate to jobs page")
            print(f"Check logs in: {logger.get_run_dir()}")
            return False

        logger.info("Jobs page loaded successfully")

        # Step 3: Fill search boxes
        logger.log_step("Filling Search Boxes", 3)

        success_flag, message = find_and_fill_search_boxes(
            driver,
            TEST_JOB_QUERY,
            TEST_LOCATION,
            TEST_DATE_FILTER.value
        )

        if not success_flag:
            logger.error(f"Failed to fill search boxes: {message}")
            logger.save_screenshot(driver, "search_failed")
            logger.save_page_source(driver, "search_failed")
            print("\n❌ TEST FAILED: Could not fill search boxes")
            print(f"Error: {message}")
            print(f"Check logs and screenshots in: {logger.get_run_dir()}")
            return False

        logger.info("Search submitted successfully")

        # Step 4: Apply date filter
        # filter_name = TEST_DATE_FILTER.value if TEST_DATE_FILTER.value else "Any Time"
        # logger.log_step(f"Applying Date Filter ({filter_name})", 4)


        # Step 5: Extract jobs
        logger.log_step("Extracting Job Data", 5)

        # Create data/dev directory if it doesn't exist
        data_dir = project_root / "data" / "dev"
        data_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime(DATETIME_FORMAT)
        output_file = str(data_dir / f"test_jobs_{timestamp}.csv")

        df, success_count, error_count = extract_linkedin_jobs(
            driver,
            max_jobs=TEST_MAX_JOBS,
            output_file=output_file
        )

        if df is None or df.empty:
            logger.error("No jobs were extracted")
            logger.save_screenshot(driver, "no_jobs_extracted")
            print("\n❌ TEST FAILED: No jobs extracted")
            print(f"Check logs in: {logger.get_run_dir()}")
            return False

        # Log summary
        stats = {
            'Jobs Extracted': success_count,
            'Errors': error_count,
            'Output File': output_file,
            'Log Directory': logger.get_run_dir(),
            'Duration': f"{(datetime.now() - datetime.strptime(logger.timestamp, DATETIME_FORMAT_READABLE)).total_seconds():.1f} seconds"
        }

        logger.log_summary(stats)

        # Display results
        print("\n" + "="*80)
        print("✅ TEST PASSED!")
        print("="*80)
        print()
        print(f"Successfully extracted {success_count} jobs")
        print(f"Errors: {error_count}")
        print(f"Output file: {output_file}")
        print()
        print("Sample Jobs (first 3):")
        print("-"*80)

        for idx, row in df.head(3).iterrows():
            print(f"\nJob {idx + 1}:")
            print(f"  Company: {row['company']}")
            print(f"  Title: {row['title']}")
            print(f"  Description (first 100 chars): {row['description'][:100]}...")

        print()
        print("="*80)
        print(f"Logs saved to: {logger.get_run_dir()}")
        print("="*80)
        print()
        print("Log files created:")
        print(f"  - scraper.log (main log)")
        print(f"  - errors.log (errors only)")
        print(f"  - debug.log (detailed debug info)")
        print(f"  - screenshots/ (any error screenshots)")
        print(f"  - html_dumps/ (page source on errors)")
        print()

        success = True
        return True

    except KeyboardInterrupt:
        logger.warning("Test interrupted by user")
        print("\n\n⚠️  Test interrupted by user")
        return False

    except Exception as e:
        logger.log_exception(e, "main test function")
        if driver:
            logger.save_screenshot(driver, "unexpected_error")
            logger.save_page_source(driver, "unexpected_error")

        print(f"\n❌ TEST FAILED with unexpected error")
        print(f"Error: {str(e)}")
        print(f"Check logs in: {logger.get_run_dir()}")
        return False

    finally:
        # Clean up
        if driver:
            # If error occurred in debug mode, keep browser open for inspection
            if not success and debug_test:
                logger.info("=" * 80)
                logger.info("DEBUG MODE: Browser left open for inspection")
                logger.info("You can manually inspect the browser state to diagnose the issue")
                logger.info("=" * 80)

                print("\n" + "=" * 80)
                print("🔍 DEBUG MODE: Error occurred - browser window kept open")
                print("=" * 80)
                print("   You can now inspect the browser to see what went wrong")
                print(f"   Screenshots saved to: {logger.screenshots_dir}")
                print(f"   Page HTML saved to: {logger.html_dumps_dir}")
                print(f"   Logs saved to: {logger.run_log_dir}")
                print("=" * 80)
                input("\nPress Enter to close the browser and exit...")
                print()

            logger.info("Closing browser...")
            driver.quit()
            logger.info("Browser closed")

        if success:
            print("\n✅ Next steps:")
            print("  1. Review the CSV file with job data")
            print("  2. Check logs for any warnings")
            print("  3. Set up Airflow for automation (see AIRFLOW_SETUP.md)")
        else:
            print("\n❌ Troubleshooting:")
            print(f"  1. Check logs in: {logger.get_run_dir()}")
            print("  2. Look at screenshots/ for visual errors")
            print("  3. Review html_dumps/ for page structure")
            print("  4. Check errors.log for detailed error messages")


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Test LinkedIn job scraper with detailed logging",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tests/linkedin/test_linkedin_scraper.py
  python tests/linkedin/test_linkedin_scraper.py --debug
  python tests/linkedin/test_linkedin_scraper.py --title "ML Engineer" --location "Seattle" --time-posted "1week"
        """
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode: keep browser open on errors for manual inspection'
    )
    parser.add_argument(
        '--title',
        type=str,
        default="Software Engineer",
        help='Job title to search for (default: "Software Engineer")'
    )
    parser.add_argument(
        '--location',
        type=str,
        default="San Francisco",
        help='Location to search in (default: "San Francisco")'
    )
    parser.add_argument(
        '--time-posted',
        type=str,
        default="24hrs",
        choices=["24hrs", "1week", "1month", "any"],
        help='Time filter: 24hrs, 1week, 1month, or any (default: "24hrs")'
    )

    args = parser.parse_args()

    print()
    success = main(
        debug_test=args.debug,
        job_title=args.title,
        location=args.location,
        time_posted=args.time_posted
    )
    sys.exit(0 if success else 1)
