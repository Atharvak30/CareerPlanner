"""
LinkedIn Job Scraper with Comprehensive Logging

This version includes detailed logging to help debug issues and track scraping progress.
Each run creates a separate log directory with logs, screenshots, and HTML dumps.
"""

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from dotenv import load_dotenv

from utils.constants import DATETIME_FORMAT, DATETIME_FORMAT_READABLE

import os
import sys
import time
import random
from enum import Enum
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.logger_config import create_logger

DELAY_MIN = 4.0
DELAY_MAX = 8.0
JOBS_IFRAME_INDEX = 0

JOB_PLACEHOLDER = 'Describe the job you want'


class DateFilter(Enum):
    """Enum for LinkedIn job date filters."""
    PAST_24_HOURS = "Past 24 hours"
    PAST_WEEK = "Past Week"
    PAST_MONTH = "Past Month"
    ANY_TIME = None  # Default - no filter


# Global logger (will be set when functions are called)
logger = None


def random_delay():
    """Random delay to mimic human behavior."""
    delay = random.uniform(DELAY_MIN, DELAY_MAX)
    if logger:
        logger.debug(f"Delaying for {delay:.2f} seconds")
    time.sleep(delay)

def setup_chrome_driver(log=None, remote_url=None):
    """
    Initialize Chrome WebDriver with options to appear more like a real browser.

    Args:
        log: Logger instance
        remote_url: Optional URL for remote Selenium Grid (e.g., http://chrome:4444)

    Returns:
        webdriver.Chrome: Configured Chrome driver instance
    """
    global logger
    logger = log

    if logger:
        logger.info(f"Setting up Chrome driver... (remote: {bool(remote_url)})")

    options = webdriver.ChromeOptions()

    # Add options to make the browser appear more human-like
    options.add_argument("--start-maximized")
    options.add_argument("--disable-bots")
    options.add_argument("--disable-automation")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-blink-features=AutomationControlled")

    # Set a real browser user agent
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    options.add_argument(f"user-agent={user_agent}")

    if logger:
        logger.debug(f"User agent: {user_agent}")

    # Additional options to avoid detection
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    random_delay()

    # Initialize and return the driver
    try:
        if remote_url:
            # Use remote Selenium Grid
            driver = webdriver.Remote(command_executor=remote_url, options=options)
            if logger:
                logger.info(f"Chrome driver connected to remote: {remote_url}")
        else:
            # Use local Chrome driver
            driver = webdriver.Chrome(options=options)
            if logger:
                logger.info("Chrome driver initialized locally")

        # Remove webdriver property to avoid detection
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        return driver

    except Exception as e:
        if logger:
            logger.log_exception(e, "setup_chrome_driver")
        raise

def load_env_variables():
    """Load environment variables from .env file."""
    load_dotenv()

    if logger:
        logger.info("Environment variables loaded")
        logger.debug(f"LINKEDIN_EMAIL set: {bool(os.getenv('LINKEDIN_EMAIL'))}")
        logger.debug(f"LINKEDIN_PASSWORD set: {bool(os.getenv('LINKEDIN_PASSWORD'))}")

def login_to_linkedin(driver, email, password):
    """
    Perform automated login to LinkedIn.

    Args:
        driver: Selenium WebDriver instance
        email (str): LinkedIn account email
        password (str): LinkedIn account password

    Returns:
        bool: True if login successful, False otherwise
    """
    try:
        if logger:
            logger.info("Navigating to LinkedIn login page...")

        driver.get("https://www.linkedin.com/login")

        # Wait for the login page to load
        wait = WebDriverWait(driver, 10)

        random_delay()

        # Wait for and find the email field
        if logger:
            logger.debug("Waiting for login form to load...")

        email_field = wait.until(
            EC.presence_of_element_located((By.ID, "username"))
        )

        if logger:
            logger.debug("Email field found")

        random_delay()

        # Fill in the email
        if logger:
            logger.info("Entering email...")

        email_field.clear()
        email_field.send_keys(email)
        random_delay()

        # Find and fill the password field
        password_field = driver.find_element(By.ID, "password")

        if logger:
            logger.info("Entering password...")

        password_field.clear()
        password_field.send_keys(password)
        random_delay()

        # Find and click the sign in button
        if logger:
            logger.info("Clicking sign in button...")

        sign_in_button = driver.find_element(
            By.XPATH, "//button[@type='submit']"
        )
        sign_in_button.click()

        # Wait for redirect to feed/home page
        if logger:
            logger.info("Waiting for login to complete...")

        random_delay()

        # Verify login success
        current_url = driver.current_url

        if logger:
            logger.debug(f"Current URL after login: {current_url}")

        # Check for successful login indicators
        if '/feed/' in current_url or '/mynetwork/' in current_url or '/jobs/' in current_url:
            if logger:
                logger.info("Login successful - redirected to authenticated page!")
            return True

        # Alternative check: Look for navigation elements
        try:
            wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "global-nav"))
            )
            if logger:
                logger.info("Login successful - navigation bar detected!")
            return True
        except TimeoutException:
            if '/login' in driver.current_url:
                if logger:
                    logger.error("Login failed - still on login page")
                    logger.save_screenshot(driver, "login_failed")
                    logger.save_page_source(driver, "login_failed")

                # Try to capture error message
                try:
                    error_element = driver.find_element(By.ID, "error-for-password")
                    if logger:
                        logger.error(f"Login error message: {error_element.text}")
                except NoSuchElementException:
                    pass
                return False
            else:
                if logger:
                    logger.warning("Login may have succeeded - not on login page anymore")
                return True

    except TimeoutException as e:
        if logger:
            logger.log_exception(e, "login_to_linkedin - Timeout")
            logger.save_screenshot(driver, "login_timeout")
        return False
    except NoSuchElementException as e:
        if logger:
            logger.log_exception(e, "login_to_linkedin - Element not found")
            logger.save_screenshot(driver, "login_element_not_found")
        return False
    except Exception as e:
        if logger:
            logger.log_exception(e, "login_to_linkedin")
            logger.save_screenshot(driver, "login_error")
        return False

def open_linkedin_session(log=None, remote_url=None):
    """
    Main function to open a LinkedIn session with automated login.

    Args:
        log: Logger instance
        remote_url: Optional URL for remote Selenium Grid (e.g., http://chrome:4444)

    Returns:
        webdriver.Chrome: Active Chrome driver instance logged into LinkedIn
        None: If login fails or credentials are missing
    """
    global logger
    logger = log

    try:
        # Load credentials from environment variables
        if logger:
            logger.info("Loading credentials from environment variables...")

        load_env_variables()

        isEmail = bool(os.getenv('LINKEDIN_EMAIL'))
        isPwd = bool(os.getenv('LINKEDIN_PASSWORD'))

        # Validate credentials
        if not isEmail or not isPwd:
            if logger:
                logger.error("LINKEDIN_EMAIL and LINKEDIN_PASSWORD environment variables must be set")
            return None

        if logger:
            logger.info("Credentials validated")

        # Setup Chrome driver
        driver = setup_chrome_driver(logger, remote_url=remote_url)

        # Login to LinkedIn
        login_success = login_to_linkedin(driver,
                                          os.getenv('LINKEDIN_EMAIL'),
                                          os.getenv('LINKEDIN_PASSWORD'))

        if login_success:
            if logger:
                logger.info(f"Successfully logged into LinkedIn! Current URL: {driver.current_url}")
            return driver
        else:
            if logger:
                logger.error("Login failed. Closing driver...")
            driver.quit()
            return None

    except Exception as e:
        if logger:
            logger.log_exception(e, "open_linkedin_session")
        if 'driver' in locals():
            driver.quit()
        return None

def navigate_to_jobs_page(driver):
    """
    Navigate to LinkedIn Jobs page and wait for it to load.

    Args:
        driver: Selenium WebDriver instance

    Returns:
        bool: True if navigation successful, False otherwise
    """
    try:
        if logger:
            logger.info("Navigating to LinkedIn Jobs page...")

        driver.get("https://www.linkedin.com/jobs/")

        # Wait for page to load
        wait = WebDriverWait(driver, 10)

        random_delay()

        # Wait for search box to appear
        try:
            wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[placeholder='Describe the job you want']"))
            )
            if logger:
                logger.info("Jobs page loaded successfully!")
            return True
        except TimeoutException:
            if logger:
                logger.warning("Jobs page search box not found, but continuing...")
                logger.save_screenshot(driver, "jobs_page_timeout")
            return True  # Still return True as we navigated to the URL

    except Exception as e:
        if logger:
            logger.log_exception(e, "navigate_to_jobs_page")
            logger.save_screenshot(driver, "navigate_jobs_error")
        return False

def find_and_fill_search_boxes(driver, job_title, job_location, job_timePosted=DateFilter.PAST_24_HOURS.value):
    """
    Find and fill LinkedIn job search boxes.

    Args:
        driver: Selenium WebDriver instance
        job_query (str): Job title/keyword to search for
        location_query (str): Location to search in

    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        if logger:
            logger.info(f"Filling search boxes - Job: '{job_title}', Location: '{job_location}', Time Posted: '{job_timePosted}'")
        
        search_query = job_title.strip() + " " + job_location.strip() + " " + job_timePosted

        wait = WebDriverWait(driver, 10)

        random_delay()

        # Wait for and fill the job title input
        if logger:
            logger.debug("Looking for {} input box...".format(JOB_PLACEHOLDER))

        search_query_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[placeholder='{}']".format(JOB_PLACEHOLDER)))
        )

        if not search_query_input:
            if logger:
                logger.error("Job search box not found")
                logger.save_screenshot(driver, "job_search_box_not_found")
                logger.save_page_source(driver, "job_search_box_not_found")
            return (False, "Job search box not found")

        if logger:
            logger.debug("Job title input found, filling...")

        search_query_input.click()
        search_query_input.send_keys(Keys.CONTROL + "a")
        search_query_input.send_keys(search_query)

        random_delay()

        search_query_input.send_keys(Keys.RETURN)

        if logger:
            logger.info("Search submitted successfully!")

        return (True, "Success")

    except TimeoutException as e:
        error_msg = f"Timeout finding search elements: {str(e)}"
        if logger:
            logger.log_exception(e, "find_and_fill_search_boxes - Timeout")
            logger.save_screenshot(driver, "search_box_timeout")
            logger.save_page_source(driver, "search_box_timeout")
        return (False, error_msg)

    except Exception as e:
        error_msg = f"Error: {str(e)}"
        if logger:
            logger.log_exception(e, "find_and_fill_search_boxes")
            logger.save_screenshot(driver, "search_box_error")
            logger.save_page_source(driver, "search_box_error")
        return (False, error_msg)

def narrow_job_search(driver, time_filter=DateFilter.PAST_24_HOURS):
    """
    Apply date filter to narrow down job search results.

    This function should be called after find_and_fill_search_boxes() to filter
    jobs by posting date.

    Args:
        driver: Selenium WebDriver instance
        time_filter (DateFilter): Time range to filter by. Options:
            - DateFilter.PAST_24_HOURS (default)
            - DateFilter.PAST_WEEK
            - DateFilter.PAST_MONTH
            - DateFilter.ANY_TIME (no filter applied)

    Returns:
        tuple: (success: bool, message: str)
    """
        #
        # DEPRECIATED APPROACH - kept for reference
        #

    return (True, "No filter applied")

    try:

        # Skip if ANY_TIME
        if time_filter == DateFilter.ANY_TIME or time_filter.value is None:
            if logger:
                logger.debug("Skipping date filter (ANY_TIME selected)")
            return (True, "No filter applied")

        filter_text = time_filter.value

        if logger:
            logger.info(f"Applying date filter: {filter_text}")

        wait = WebDriverWait(driver, 10)

        # Wait for page to load and try to find the filters bar
        if logger:
            logger.debug("Waiting for filters bar to load...")

        # Try multiple selectors for the filters bar
        filters_bar_found = False
        filter_selectors = [
            "ul.search-reusables__filter-list",
            "div#search-reusables__filters-bar",
            "div.jobs-semantic-search-filters-v2",
            "div[class*='search-reusables__filters']"
        ]

        for selector in filter_selectors:
            try:
                if logger:
                    logger.debug(f"Trying selector: {selector}")
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                if logger:
                    logger.debug(f"✅ Filters bar found with: {selector}")
                filters_bar_found = True
                time.sleep(2)  # Give the page time to stabilize
                break
            except TimeoutException:
                if logger:
                    logger.debug(f"❌ Selector not found: {selector}")
                continue

        if not filters_bar_found:
            if logger:
                logger.error("Could not find filters bar with any selector")
                logger.save_screenshot(driver, "filters_bar_not_found")
                logger.save_page_source(driver, "filters_bar_not_found")
            return (False, "Filters bar not found on page")

        # Strategy 1: Try to find "Date Posted" button using new LinkedIn UI
        try:
            if logger:
                logger.debug("Looking for 'Date Posted' filter button with ID: searchFilter_timePostedRange")

            # Use the ID from the HTML you provided
            date_posted_button = wait.until(
                EC.element_to_be_clickable((By.ID, "searchFilter_timePostedRange"))
            )

            if logger:
                logger.debug("Found 'Date Posted' button, clicking...")

            date_posted_button.click()

            # Wait for the dropdown/popover to appear (it's hidden initially)
            if logger:
                logger.debug("Waiting for date filter dropdown to appear...")
            time.sleep(1)  # Give the popover time to animate in

            # Select the specific time range from dropdown (radio buttons)
            if logger:
                logger.debug(f"Looking for '{filter_text}' option...")

            # Wait for the dropdown container to be visible
            wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "ul.search-reusables__collection-values-container"))
            )

            # Find the specific radio button label by matching the text
            # Use the exact input ID based on the filter
            filter_id_map = {
                "Past 24 hours": "timePostedRange-r86400",
                "Past week": "timePostedRange-r604800",
                "Past month": "timePostedRange-r2592000"
            }

            input_id = filter_id_map.get(filter_text)

            if input_id:
                # Click the label associated with this radio button
                label_element = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, f"label[for='{input_id}']"))
                )
            else:
                # Fallback: try matching on the label text
                label_element = wait.until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        f"//label[@class='search-reusables__value-label'][.//span[contains(text(), '{filter_text}')]]"
                    ))
                )

            if logger:
                logger.debug(f"Selecting '{filter_text}' option...")

            label_element.click()
            random_delay()

            # Click "Show results" button
            if logger:
                logger.debug("Looking for 'Show results' button...")

            try:
                show_results_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Apply current filter')]"))
                )
                show_results_button.click()
                random_delay()

                if logger:
                    logger.info(f"Date filter '{filter_text}' applied successfully!")

            except (TimeoutException, NoSuchElementException):
                if logger:
                    logger.warning("Could not find 'Show results' button, filter may auto-apply")

            return (True, f"Filter applied: {filter_text}")

        except (TimeoutException, NoSuchElementException) as e:
            if logger:
                logger.debug("'Date Posted' button not found, trying 'All filters' approach...")

            # Strategy 2: Use "All filters" button
            try:
                all_filters_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'All filters')]"))
                )

                if logger:
                    logger.debug("Found 'All filters' button, clicking...")

                all_filters_button.click()
                random_delay()

                # In the modal, find Date Posted section
                if logger:
                    logger.debug("Looking for 'Date Posted' in filters modal...")

                # Look for the date posted radio buttons or checkboxes
                date_filter_option = wait.until(
                    EC.element_to_be_clickable((By.XPATH, f"//label[contains(., '{filter_text}')]"))
                )

                if logger:
                    logger.info(f"Selecting '{filter_text}' in modal...")

                date_filter_option.click()
                random_delay()

                # Click "Show results" or "Apply" button
                try:
                    show_results_button = wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Show') or contains(., 'Apply')]"))
                    )

                    if logger:
                        logger.debug("Clicking 'Show results' button...")

                    show_results_button.click()
                    random_delay()

                except (TimeoutException, NoSuchElementException):
                    if logger:
                        logger.warning("Could not find 'Show results' button, filter may still be applied")

                if logger:
                    logger.info(f"Date filter '{filter_text}' applied successfully via All filters!")

                return (True, f"Filter applied: {filter_text}")

            except (TimeoutException, NoSuchElementException) as e2:
                error_msg = f"Could not apply date filter. Neither 'Date Posted' nor 'All filters' found."
                if logger:
                    logger.error(error_msg)
                    logger.log_exception(e2, "narrow_job_search - All filters approach")
                    logger.save_screenshot(driver, "date_filter_not_found")
                    logger.save_page_source(driver, "date_filter_not_found")
                return (False, error_msg)

    except Exception as e:
        error_msg = f"Error applying date filter: {str(e)}"
        if logger:
            logger.log_exception(e, "narrow_job_search")
            logger.save_screenshot(driver, "date_filter_error")
            logger.save_page_source(driver, "date_filter_error")
        return (False, error_msg)

def extract_linkedin_jobs(driver, max_jobs=20, output_file="linkedin_jobs.csv"):
    """
    Extract job listings from LinkedIn jobs page and save to CSV.

    Args:
        driver: Selenium WebDriver instance
        max_jobs (int): Maximum number of jobs to extract
        output_file (str): CSV filename to save results

    Returns:
        tuple: (DataFrame, success_count, error_count)
    """
    jobs_data = []
    success_count = 0
    error_count = 0

    try:
        if logger:
            logger.info("Switching to jobs iframe...")

        # Switch to main jobs iframe
        iframes = driver.find_elements(By.TAG_NAME, "iframe")

        if not iframes:
            if logger:
                logger.error("No iframe found!")
                logger.save_screenshot(driver, "no_iframe")
            return None, 0, 0

        if logger:
            logger.info(f"Found {len(iframes)} iframes on the page")
            # Log iframe details for debugging
            for idx, iframe in enumerate(iframes):
                iframe_id = iframe.get_attribute('id')
                iframe_src = iframe.get_attribute('src')
                iframe_name = iframe.get_attribute('name')
                logger.debug(f"Iframe {idx}: id={iframe_id}, name={iframe_name}, src={iframe_src[:100] if iframe_src else 'None'}")
            logger.save_screenshot(driver, "before_iframe_switch")

        driver.switch_to.frame(iframes[JOBS_IFRAME_INDEX])

        # Debug: Wait for iframe content to load and capture state
        if logger:
            logger.info("Switched to iframe, waiting for content to load...")
            time.sleep(3)  # Give iframe content time to load
            logger.save_screenshot(driver, "after_iframe_switch")
            logger.save_page_source(driver, "iframe_content")
            logger.debug(f"Iframe URL: {driver.current_url}")

        # Get all job cards (multiple selectors for resilience against UI changes)
        # Try each selector individually for debugging
        selectors = [
            "div.job-card-job-posting-card-wrapper",
            "div.job-card-container",
            "div.job-card-list__entity-lockup"
        ]

        if logger:
            logger.debug("Trying individual selectors:")
            for selector in selectors:
                cards = driver.find_elements(By.CSS_SELECTOR, selector)
                logger.debug(f"  {selector}: found {len(cards)} elements")

        job_cards = driver.find_elements(
            By.CSS_SELECTOR,
            "div.job-card-job-posting-card-wrapper, div.job-card-container, div.job-card-list__entity-lockup"
        )
        total_jobs = min(len(job_cards), max_jobs)

        if logger:
            logger.info(f"Found {len(job_cards)} job cards. Extracting {total_jobs} jobs...")

        for i in range(total_jobs):
            if logger:
                logger.debug(f"Processing job {i+1}/{total_jobs}...")

            job_cards[i].click()
            time.sleep(2)

            try:
                # Try to extract job title using new LinkedIn UI selectors
                try:
                    title_elem = driver.find_element(By.CSS_SELECTOR, "div.artdeco-entity-lockup__title strong")
                    title = title_elem.text.strip()
                except:
                    # Fallback to old selector
                    try:
                        title_elem = driver.find_element(By.CSS_SELECTOR, "h2.job-title")
                        title = title_elem.text.strip()
                    except:
                        title = "N/A"

                # Try to extract company name using new LinkedIn UI selectors
                try:
                    company_elem = driver.find_element(By.CSS_SELECTOR, "div.artdeco-entity-lockup__subtitle")
                    company = company_elem.text.strip()
                except:
                    # Fallback to old selector
                    try:
                        company_elem = driver.find_element(By.CSS_SELECTOR, "a.job-card-container__company-name")
                        company = company_elem.text.strip()
                    except:
                        company = "N/A"

                if not company or not title or company == "N/A" or title == "N/A":
                    if logger:
                        logger.warning(f"Missing company or title for job {i+1} (Company: {company}, Title: {title})")

                random_delay()

                # Extract full job description
                try:
                    # Try multiple selectors for job description
                    try:
                        job_description_elem = driver.find_element(By.CSS_SELECTOR, "article.jobs-description__container")
                        description = job_description_elem.text.strip()
                    except:
                        # Fallback to other possible selectors
                        job_description_elem = driver.find_element(By.CSS_SELECTOR, "div.jobs-description, div.job-details-jobs-unified-top-card__job-insight")
                        description = job_description_elem.text.strip()
                except:
                    description = "Description not available"
                    if logger:
                        logger.warning(f"No description found for job: {company} - {title}")

                # Store job data
                job_info = {
                    'company': company,
                    'title': title,
                    'description': description,
                    'extraction_timestamp': pd.Timestamp.now()
                }

                jobs_data.append(job_info)
                success_count += 1

                if logger:
                    logger.info(f"✓ Job {i+1}/{total_jobs}: {title} at {company}")

                random_delay()

            except Exception as e:
                error_count += 1
                if logger:
                    logger.error(f"✗ Job {i+1}/{total_jobs}: Error - {str(e)[:100]}")
                    logger.debug(f"Full error for job {i+1}:", exc_info=True)
                continue

        # Switch back to main content
        driver.switch_to.default_content()

        # Create DataFrame
        if jobs_data:
            df = pd.DataFrame(jobs_data)

            # Save to CSV
            df.to_csv(output_file, index=False)

            if logger:
                logger.info(f"Successfully saved {len(df)} jobs to '{output_file}'")
                logger.log_summary({
                    'Total Jobs Extracted': len(df),
                    'Successful Extractions': success_count,
                    'Errors': error_count,
                    'Output File': output_file
                })

            return df, success_count, error_count
        else:
            if logger:
                logger.warning("No jobs extracted!")
            return None, 0, error_count

    except Exception as e:
        if logger:
            logger.log_exception(e, "extract_linkedin_jobs")
            logger.save_screenshot(driver, "extraction_error")
        driver.switch_to.default_content()
        return None, success_count, error_count


def main(job_titles: list[str], locations: list[str], time_posted: DateFilter = DateFilter.PAST_24_HOURS, max_jobs_per_search: int = 20):
    """
    Main function - scrape jobs for multiple titles/locations.

    Args:
        job_titles: ["ML Engineer", "Software Developer"]
        locations: ["San Francisco", "Seattle"]
        time_posted: DateFilter enum
        max_jobs_per_search: Max jobs per search

    Returns:
        (dataframe, success_count, error_count)
    """
    from datetime import datetime

    run_ts = datetime.now().strftime(DATETIME_FORMAT)
    log = create_logger(log_base_dir="logs", run_name=f"main_{run_ts}")

    log.info(f"Titles: {job_titles}, Locations: {locations}")

    driver = None
    all_dfs = []
    total_s, total_e = 0, 0

    try:
        driver = open_linkedin_session(log=log)
        if not driver:
            return None, 0, 0

        for title in job_titles:
            for loc in locations:
                log.info(f"Searching: {title} in {loc}")

                if not navigate_to_jobs_page(driver):
                    continue

                ok, _ = find_and_fill_search_boxes(driver, title, loc, time_posted.value)
                if not ok:
                    continue

                # narrow_job_search(driver, time_posted)

                out = f"jobs_{title.replace(' ','_')}_{loc.replace(' ','_')}_{datetime.now().strftime(DATETIME_FORMAT)}.csv"
                df, s, e = extract_linkedin_jobs(driver, max_jobs_per_search, out)

                if df is not None and not df.empty:
                    df['search_title'] = title
                    df['search_location'] = loc
                    all_dfs.append(df)
                    total_s += s
                    total_e += e

                random_delay()

        if all_dfs:
            combined = pd.concat(all_dfs, ignore_index=True)
            combined = combined.drop_duplicates(subset=['title','company'], keep='first')

            outfile = f"data/airflow/combined_{run_ts}.csv"
            combined.to_csv(outfile, index=False)

            log.info(f"✅ {len(combined)} jobs -> {outfile}")
            return combined, total_s, total_e
        return None, 0, total_e

    except Exception as e:
        if log:
            log.log_exception(e, "main")
        return None, total_s, total_e
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    import argparse, sys

    p = argparse.ArgumentParser()
    p.add_argument('--titles', required=True, help='Comma-separated')
    p.add_argument('--locations', required=True, help='Comma-separated')
    p.add_argument('--time-posted', default="24hrs", choices=["24hrs","1week","1month","any"])
    p.add_argument('--max-jobs', type=int, default=20)

    a = p.parse_args()

    titles = [t.strip() for t in a.titles.split(',')]
    locs = [l.strip() for l in a.locations.split(',')]

    tm = {"24hrs":DateFilter.PAST_24_HOURS, "1week":DateFilter.PAST_WEEK,
          "1month":DateFilter.PAST_MONTH, "any":DateFilter.ANY_TIME}

    df, s, e = main(titles, locs, tm[a.time_posted.lower()], a.max_jobs)
    sys.exit(0 if df is not None else 1)
