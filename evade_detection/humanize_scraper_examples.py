"""
Example usage of the HumanBehavior class for LinkedIn scraping.

This file demonstrates how to integrate human-like behaviors into your
LinkedIn scraping workflow to reduce detection risk.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from humanize_scraper import HumanBehavior
import time


def humanized_login_example(driver, email, password):
    """
    Example: Login to LinkedIn with human-like behavior.

    Args:
        driver: Selenium WebDriver instance
        email (str): LinkedIn email
        password (str): LinkedIn password

    Returns:
        bool: Success status
    """
    # Create HumanBehavior instance
    human = HumanBehavior(driver, delay_min=3.0, delay_max=6.0)

    try:
        # Navigate to login page
        print("Navigating to LinkedIn login...")
        driver.get("https://www.linkedin.com/login")

        # Wait for page load with human-like delay
        human.variable_wait_for_load(2.5)

        # Scan the page briefly (simulate looking around)
        human.scan_page(num_scrolls=2)

        # Wait for email field
        wait = WebDriverWait(driver, 10)
        email_field = wait.until(
            EC.presence_of_element_located((By.ID, "username"))
        )

        # Scroll to email field smoothly
        human.smooth_scroll_to_element(email_field)

        # Type email with human-like speed
        print("Typing email...")
        human.human_type(email_field, email, typing_speed='normal')

        # Brief pause (like switching focus)
        human.between_actions_delay()

        # Find password field
        password_field = driver.find_element(By.ID, "password")

        # Move mouse to password field before typing
        human.move_to_element(password_field)

        # Type password
        print("Typing password...")
        human.human_type(password_field, password, typing_speed='normal')

        # Pause before clicking login (simulate reviewing what was entered)
        human.pause_and_read(1.0, 2.0)

        # Find and click login button with realistic behavior
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        print("Clicking login button...")
        human.realistic_click(login_button)

        # Wait for redirect
        human.random_delay()

        print("Login complete!")
        return True

    except Exception as e:
        print(f"Error during login: {e}")
        return False


def humanized_job_search_example(driver, job_query, location_query):
    """
    Example: Search for jobs with human-like behavior.

    Args:
        driver: Selenium WebDriver instance
        job_query (str): Job title/keywords
        location_query (str): Location

    Returns:
        bool: Success status
    """
    human = HumanBehavior(driver, delay_min=2.0, delay_max=5.0)

    try:
        # Navigate to jobs page
        print("Navigating to jobs page...")
        driver.get("https://www.linkedin.com/jobs/")

        # Wait and scan page
        human.variable_wait_for_load(2.0)
        human.scan_page(num_scrolls=1)

        # Wait for search boxes
        wait = WebDriverWait(driver, 10)

        # Find job title input
        job_input = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "[placeholder='Title, skill or Company']")
            )
        )

        # Scroll to and type job query
        human.smooth_scroll_to_element(job_input)
        human.short_delay()
        print(f"Typing job query: {job_query}")
        human.human_type(job_input, job_query, typing_speed='normal')

        # Delay between fields
        human.between_actions_delay()

        # Find location input
        location_input = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "[placeholder='City, state, or zip code']")
            )
        )

        # Type location
        print(f"Typing location: {location_query}")
        human.human_type(location_input, location_query, typing_speed='normal')

        # Pause before submitting (simulate thinking)
        human.pause_and_read(1.0, 2.0)

        # Submit search
        location_input.submit()

        print("Search submitted!")
        human.variable_wait_for_load(3.0)

        return True

    except Exception as e:
        print(f"Error during job search: {e}")
        return False


def humanized_browse_jobs_example(driver, num_jobs=10):
    """
    Example: Browse through job listings with human-like behavior.

    Args:
        driver: Selenium WebDriver instance
        num_jobs (int): Number of jobs to browse through

    Returns:
        list: Job data extracted
    """
    human = HumanBehavior(driver, delay_min=3.0, delay_max=7.0)
    jobs_data = []

    try:
        # Switch to iframe if needed
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        if iframes:
            driver.switch_to.frame(iframes[0])

        # Initial page scan
        human.scan_page(num_scrolls=2)

        # Find job cards
        job_cards = driver.find_elements(By.CSS_SELECTOR, "div.job-card-container")
        total_jobs = min(len(job_cards), num_jobs)

        print(f"Browsing {total_jobs} jobs with human-like behavior...")

        for i in range(total_jobs):
            # Refresh job cards (in case DOM updated)
            job_cards = driver.find_elements(By.CSS_SELECTOR, "div.job-card-container")

            if i >= len(job_cards):
                break

            card = job_cards[i]

            # Scroll to card smoothly
            human.smooth_scroll_to_element(card)

            # Brief pause (like reading the job title)
            human.short_delay()

            # Click with realistic behavior
            print(f"Clicking job {i+1}/{total_jobs}...")
            human.realistic_click(card)

            # Wait for details to load
            human.variable_wait_for_load(2.0)

            # Simulate reading the job description
            print(f"Reading job details...")
            human.pause_and_read(3.0, 8.0)

            # Occasionally scroll within job description
            if i % 2 == 0:  # Every other job
                human.random_scroll('down', 200)
                human.short_delay()
                human.random_scroll('up', 100)

            # Extract job data (your existing extraction logic)
            try:
                details_panel = driver.find_element(
                    By.CSS_SELECTOR,
                    "div.jobs-search__job-details"
                )

                links = details_panel.find_elements(By.TAG_NAME, "a")
                company = links[1].text.strip() if len(links) > 1 else "N/A"
                title = links[2].text.strip() if len(links) > 2 else "N/A"

                # Extract description
                try:
                    desc_elem = details_panel.find_element(
                        By.CSS_SELECTOR,
                        "article.jobs-description__container"
                    )
                    description = desc_elem.text.strip()
                except:
                    description = "N/A"

                jobs_data.append({
                    'company': company,
                    'title': title,
                    'description': description
                })

                print(f"  ✓ Extracted: {title} at {company}")

            except Exception as e:
                print(f"  ✗ Error extracting job data: {e}")

            # Random delay between job views (simulate browsing)
            human.random_delay()

            # Occasionally do extra "human" actions
            if i % 3 == 0:  # Every 3rd job
                # Random mouse movement
                human.random_mouse_movement()
                human.short_delay()

        # Switch back from iframe
        driver.switch_to.default_content()

        print(f"\nCompleted browsing {len(jobs_data)} jobs!")
        return jobs_data

    except Exception as e:
        print(f"Error during job browsing: {e}")
        driver.switch_to.default_content()
        return jobs_data


def humanized_scroll_and_load_more_example(driver):
    """
    Example: Scroll to load more jobs with human-like behavior.

    This simulates scrolling through a feed to load additional content.

    Args:
        driver: Selenium WebDriver instance
    """
    human = HumanBehavior(driver, delay_min=2.0, delay_max=4.0)

    try:
        print("Scrolling to load more jobs...")

        # Switch to iframe if needed
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        if iframes:
            driver.switch_to.frame(iframes[0])

        # Get initial scroll height
        last_height = driver.execute_script("return document.body.scrollHeight")

        # Scroll down multiple times
        for i in range(5):  # Scroll 5 times
            print(f"Scroll {i+1}/5...")

            # Scroll down with page_down behavior
            human.page_down_scroll()

            # Pause to "read" content
            human.pause_and_read(2.0, 4.0)

            # Occasionally scroll back up a bit (like re-reading)
            if i % 2 == 0:
                human.random_scroll('up', 150)
                human.short_delay()

            # Check if new content loaded
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("No more content to load")
                break
            last_height = new_height

        driver.switch_to.default_content()
        print("Finished scrolling")

    except Exception as e:
        print(f"Error during scrolling: {e}")
        driver.switch_to.default_content()


# Complete workflow example
def complete_humanized_workflow_example():
    """
    Complete example workflow with full humanization.

    This demonstrates a full scraping session from start to finish.
    """
    from selenium.webdriver.chrome.options import Options
    import os

    print("Starting humanized LinkedIn scraping workflow...")
    print("="*80)

    # Setup Chrome with anti-detection
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-bots")
    options.add_argument("--disable-automation")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-blink-features=AutomationControlled")

    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    options.add_argument(f"user-agent={user_agent}")

    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # Initialize driver
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    # Create human behavior instance
    human = HumanBehavior(driver, delay_min=4.0, delay_max=8.0)

    try:
        # Step 1: Login with human behavior
        email = os.getenv('LINKEDIN_EMAIL')
        password = os.getenv('LINKEDIN_PASSWORD')

        if not email or not password:
            print("Error: Set LINKEDIN_EMAIL and LINKEDIN_PASSWORD environment variables")
            return

        success = humanized_login_example(driver, email, password)
        if not success:
            print("Login failed!")
            return

        # Random delay after login (simulate user getting oriented)
        human.random_delay()

        # Step 2: Search for jobs
        success = humanized_job_search_example(driver, "Software Engineer", "San Francisco")
        if not success:
            print("Job search failed!")
            return

        # Random delay after search
        human.random_delay()

        # Step 3: Browse jobs with human behavior
        jobs_data = humanized_browse_jobs_example(driver, num_jobs=10)

        # Step 4: Save results
        if jobs_data:
            import pandas as pd
            df = pd.DataFrame(jobs_data)
            df.to_csv("humanized_jobs.csv", index=False)
            print(f"\n✓ Saved {len(jobs_data)} jobs to humanized_jobs.csv")

        print("\n" + "="*80)
        print("Workflow complete!")
        print("="*80)

    except Exception as e:
        print(f"Error in workflow: {e}")

    finally:
        # Close browser after a human-like delay
        print("\nClosing browser...")
        human.random_delay(2.0, 4.0)
        driver.quit()


if __name__ == "__main__":
    # Run the complete workflow
    complete_humanized_workflow_example()
