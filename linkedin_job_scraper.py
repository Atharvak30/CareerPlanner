import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from dotenv import load_dotenv

import os
import time
import random

DELAY_MIN = 4.0
DELAY_MAX = 8.0
JOBS_IFRAME_INDEX = 0


def random_delay():
    delay = random.uniform(DELAY_MIN, DELAY_MAX)
    time.sleep(delay)

def setup_chrome_driver():
    """
    Initialize Chrome WebDriver with options to appear more like a real browser.

    Returns:
        webdriver.Chrome: Configured Chrome driver instance
    """
    options = webdriver.ChromeOptions()

    # Add options to make the browser appear more human-like
    options.add_argument("--start-maximized")
    options.add_argument("--disable-bots")
    options.add_argument("--disable-automation")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    random_delay()
    # Set a real browser user agent
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    options.add_argument(f"user-agent={user_agent}")

    # Additional options to avoid detection
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    random_delay()
    # Initialize and return the driver
    driver = webdriver.Chrome(options=options)

    # Remove webdriver property to avoid detection
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    return driver

def open_linkedin_session():
    """
    Main function to open a LinkedIn session with automated login.
    Loads credentials from environment variables and returns an active driver.

    Returns:
        webdriver.Chrome: Active Chrome driver instance logged into LinkedIn
        None: If login fails or credentials are missing
    """
    try:
        #
        # Load credentials from environment variables
        # never load and keep creds in stack, always query from
        # env when needed
        #
        print("Loading credentials from environment variables...")
        isEmail = bool(os.getenv('LINKEDIN_EMAIL'))
        isPwd = bool(os.getenv('LINKEDIN_EMAIL'))

        # Validate credentials
        if not isEmail or not isPwd:
            print("Error: LINKEDIN_EMAIL and LINKEDIN_PASSWORD environment variables must be set")
            print("Set them using:")
            print('  export LINKEDIN_EMAIL="your@email.com"')
            print('  export LINKEDIN_PASSWORD="yourpassword"')
            return None

        print(f"Credentials loaded.")

        # Setup Chrome driver
        print("Setting up Chrome driver...")
        driver = setup_chrome_driver()

        # Login to LinkedIn
        print("Attempting to login to LinkedIn...")
        login_success = login_to_linkedin(driver, 
                                          os.getenv('LINKEDIN_EMAIL'), 
                                          os.getenv('LINKEDIN_PASSWORD'))

        if login_success:
            print("\n" + "="*50)
            print("Successfully logged into LinkedIn!")
            print(f"Current URL: {driver.current_url}")
            print("="*50 + "\n")
            return driver
        else:
            print("\nLogin failed. Closing driver...")
            driver.quit()
            return None

    except Exception as e:
        print(f"Error in open_linkedin_session: {e}")
        if 'driver' in locals():
            driver.quit()
        return None

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
        # Navigate to LinkedIn login page
        print("Navigating to LinkedIn login page...")
        driver.get("https://www.linkedin.com/login")

        # Wait for the login page to load
        wait = WebDriverWait(driver, 10)

        random_delay()
        # Wait for and find the email field
        print("Waiting for login form to load...")
        email_field = wait.until(
            EC.presence_of_element_located((By.ID, "username"))
        )

        random_delay()
        # Fill in the email
        print("Entering email...")
        email_field.clear()
        email_field.send_keys(email)
        random_delay()  # Small delay to mimic human behavior

        # Find and fill the password field
        password_field = driver.find_element(By.ID, "password")
        print("Entering password...")
        password_field.clear()
        password_field.send_keys(password)
        random_delay()

        # Find and click the sign in button
        print("Clicking sign in button...")
        sign_in_button = driver.find_element(
            By.XPATH, "//button[@type='submit']"
        )
        sign_in_button.click()

        # Wait for redirect to feed/home page
        print("Waiting for login to complete...")
        random_delay()  # Give time for redirect

        # Verify login success
        current_url = driver.current_url

        # Check for successful login indicators
        if '/feed/' in current_url or '/mynetwork/' in current_url or '/jobs/' in current_url:
            print("Login successful - redirected to authenticated page!")
            return True

        # Alternative check: Look for navigation elements that only appear when logged in
        try:
            wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "global-nav"))
            )
            print("Login successful - navigation bar detected!")
            return True
        except TimeoutException:
            # Check if there's an error message or we're still on login page
            if '/login' in driver.current_url:
                print("Login failed - still on login page")
                # Try to capture error message if present
                try:
                    error_element = driver.find_element(By.ID, "error-for-password")
                    print(f"Error message: {error_element.text}")
                except NoSuchElementException:
                    pass
                return False
            else:
                # If we're not on login page but didn't find nav, still might be successful
                print("Login may have succeeded - not on login page anymore")
                return True

    except TimeoutException:
        print("Timeout while waiting for page elements")
        return False
    except NoSuchElementException as e:
        print(f"Could not find required element: {e}")
        return False
    except Exception as e:
        print(f"Error during login: {e}")
        return False

def navigate_to_jobs_page(driver):
    """
    Navigate to LinkedIn Jobs page and wait for it to load.
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        bool: True if navigation successful, False otherwise
    """
    try:
        print("Navigating to LinkedIn Jobs page...")
        driver.get("https://www.linkedin.com/jobs/")
        
        # Wait for page to load - look for the jobs search container
        wait = WebDriverWait(driver, 10)
        
        random_delay()
        # Wait for either the search container or jobs content to appear
        try:
            # wait.until(
            #     EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-search-box, .jobs-home, [class*='jobs-search']"))
            # )
            wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[placeholder='Title, skill or Company']"))
            )
            print("Jobs page loaded successfully!")
            return True
        except TimeoutException:
            print("Jobs page elements not found, but continuing...")
            return True  # Still return True as we navigated to the URL
            
    except Exception as e:
        print(f"Error navigating to jobs page: {e}")
        return False

def find_and_fill_search_boxes(driver, job_query, location_query):
    """
    Find and fill LinkedIn job search boxes using specific placeholder text.
    Searches for boxes with placeholders:
    1. "Title, skill or Company" 
    2. "City, state, or zip code"
    
    Args:
        driver: Selenium WebDriver instance
        job_query (str): Job title/keyword to search for
        location_query (str): Location to search in
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        wait = WebDriverWait(driver, 10)

        job_title_input = None
        location_input = None

        random_delay()

        # Wait for and fill the job title input
        job_title_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[placeholder='Title, skill or Company']"))
        )
        # Check if we found both boxes
        if not job_title_input:
            return (False, "Job search box not found")

        print(f"\nFilling search boxes...")
        print(f"  Job query: '{job_query}'")

        # job_title_input.clear()
        # driver.execute_script("arguments[0].value = '';", job_title_input)
        # random_delay()
        job_title_input.click()
        job_title_input.send_keys(Keys.CONTROL + "a")
        job_title_input.send_keys(job_query)

        random_delay()

        # Wait for and fill the location input
        location_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[placeholder='City, state, or zip code']"))
        )
        if not location_input:
            return (False, "Location box not found")

        print(f"  Location query: '{location_query}'")


        location_input.click()
        location_input.send_keys(Keys.CONTROL + "a")
        location_input.send_keys(location_query)
        time.sleep(1)  # Wait for dropdown
        location_input.send_keys(Keys.ARROW_DOWN)  # Select first suggestion
        # Press Enter to submit the search
        print("  Pressing Enter to submit search...")
        location_input.send_keys(Keys.RETURN)

        # random_delay()

        # # Wait for and fill the location input
        # location_input = wait.until(
        #     EC.presence_of_element_located((By.CSS_SELECTOR, "[placeholder='City, state, or zip code']"))
        # )
        # location_input.send_keys(Keys.RETURN)
        # random_delay()  # Wait for search results to load
        
        print("  ✓ Search submitted successfully!")
                        
        return (True, "Success")
        
    except Exception as e:
        return (False, f"Error: {str(e)}")

def load_env_variables():
    
    # Load environment variables from .env file
    load_dotenv()

    # Verify they're loaded (will show True/False without revealing the actual values)
    print(f"LINKEDIN_EMAIL set: {bool(os.getenv('LINKEDIN_EMAIL'))}")
    print(f"LINKEDIN_PASSWORD set: {bool(os.getenv('LINKEDIN_PASSWORD'))}")

def extract_linkedin_jobs(driver, max_jobs=20, output_file="linkedin_jobs.csv"):
    """
    Extract job listings from LinkedIn jobs page and save to CSV.
    
    Args:
        driver: Selenium WebDriver instance (should be on LinkedIn jobs page)
        max_jobs (int): Maximum number of jobs to extract
        output_file (str): CSV filename to save results
        
    Returns:
        tuple: (DataFrame, success_count, error_count)
    """
    jobs_data = []
    success_count = 0
    error_count = 0
    
    try:
        # Switch to main jobs iframe
        print("Switching to jobs iframe...")
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        if not iframes:
            print("No iframe found!")
            return None, 0, 0
        print(f"Found {len(iframes)} iframes on the page.")
            
        driver.switch_to.frame(iframes[JOBS_IFRAME_INDEX])
        
        # Get all job cards
        job_cards = driver.find_elements(By.CSS_SELECTOR, "div.job-card-container")
        total_jobs = min(len(job_cards), max_jobs)
        texts = []
        print(f"\nFound {len(job_cards)} job cards. Extracting {total_jobs} jobs...")
        print("="*80)

        for i in range(total_jobs):
            job_cards[i].click()
            time.sleep(2) # Wait for details to load

            # Get the job description article
            try:
                # # Get details panel
                details_panel = driver.find_element(By.CSS_SELECTOR, "div.jobs-search__job-details")

                links = details_panel.find_elements(By.TAG_NAME, "a")
                company = links[1].text.strip() if len(links) > 1 else "N/A"
                title = links[2].text.strip() if len(links) > 2 else "N/A"

                print("links:", links)
                
                if not company or not title:
                    print("Company({company}) or Title({title}) not found for job_card[{i}]: {card}")

                random_delay()
                
                # Extract full job description
                try:
                    job_description_elem = details_panel.find_element(By.CSS_SELECTOR, "article.jobs-description__container")
                    description = job_description_elem.text.strip()
                    # print("Job Description (first 200 chars):")
                    # print("="*80)
                    # print(description[:200])  # Print first 200 chars
                    # print("="*80)
                except:
                    description = "Description not available"
                    print("***** Warning: Job description not found. Job: {company} - {title}")
                
                texts.append(description)
                
                # Store job data
                job_info = {
                    'company': company,
                    'title': title,
                    'description': description,
                    'extraction_timestamp': pd.Timestamp.now()
                }

                jobs_data.append(job_info)
                success_count += 1
                
                print(f"✓ Job {i}/{total_jobs}: {title} at {company}")
                random_delay() # humanize
                
            except Exception as e:
                error_count += 1
                print(f"✗ Job {i}/{total_jobs}: Error - {str(e)[:100]}")
                continue        
        
        # Switch back to main content
        driver.switch_to.default_content()
        
        # Create DataFrame
        if jobs_data:
            df = pd.DataFrame(jobs_data)
            
            # Save to CSV
            df.to_csv(output_file, index=False)
            print(f"\n{'='*80}")
            print(f"✓ Successfully saved {len(df)} jobs to '{output_file}'")
            print(f"  Success: {success_count} | Errors: {error_count}")
            print(f"{'='*80}")
            
            return df, success_count, error_count
        else:
            print("No jobs extracted!")
            return None, 0, error_count
            
    except Exception as e:
        print(f"Fatal error: {e}")
        driver.switch_to.default_content()
        return None, success_count, error_count

# Usage:
# df, success, errors = extract_linkedin_jobs(driver, max_jobs=20, output_file="my_jobs.csv")