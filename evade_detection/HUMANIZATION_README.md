# Web Scraping Humanization Guide

This guide explains how to use the humanization utilities to make your web scraping more reliable and less likely to be detected.

## Overview

The `humanize_scraper.py` module provides a `HumanBehavior` class that adds realistic human-like behaviors to Selenium automation:

- **Variable delays** between actions
- **Realistic typing** with natural keystroke timing
- **Smooth scrolling** instead of instant jumps
- **Mouse movements** to simulate natural browsing
- **Reading pauses** to simulate content consumption
- **Random variations** to avoid predictable patterns

## Quick Start

### Basic Setup

```python
from selenium import webdriver
from humanize_scraper import HumanBehavior

# Setup your driver
driver = webdriver.Chrome()

# Create HumanBehavior instance
human = HumanBehavior(driver, delay_min=3.0, delay_max=7.0)

# Now use human behavior methods instead of direct Selenium calls
```

### Replace Your Current Random Delay

**Old way:**
```python
DELAY_MIN = 4.0
DELAY_MAX = 8.0

def random_delay():
    delay = random.uniform(DELAY_MIN, DELAY_MAX)
    time.sleep(delay)

random_delay()
```

**New way:**
```python
from humanize_scraper import HumanBehavior

human = HumanBehavior(driver, delay_min=4.0, delay_max=8.0)
human.random_delay()  # Same behavior, but part of a larger humanization system
```

## Key Features

### 1. Typing with Human-Like Speed

Instead of `element.send_keys(text)`:

```python
# Slow typing (0.15-0.35s between keystrokes)
human.human_type(email_field, "user@example.com", typing_speed='slow')

# Normal typing (0.08-0.18s between keystrokes) - recommended
human.human_type(password_field, "password123", typing_speed='normal')

# Fast typing (0.03-0.08s between keystrokes)
human.human_type(search_box, "Software Engineer", typing_speed='fast')
```

Features:
- Random delays between keystrokes
- Occasional longer pauses (simulates thinking/correcting)
- Clicks element first, then types naturally

### 2. Smooth Scrolling

Instead of `element.location_once_scrolled_into_view`:

```python
# Smooth scroll to element with animation
human.smooth_scroll_to_element(job_card)

# Random scroll in a direction
human.random_scroll(direction='down', distance=300)
human.random_scroll(direction='up')  # Random distance
human.random_scroll(direction='random')  # Random direction and distance

# Page down behavior (scrolls 70-90% of viewport, not perfect 100%)
human.page_down_scroll()
```

### 3. Scanning Pages (Like a Human Reader)

```python
# Simulate reading/scanning a page with multiple scrolls
human.scan_page(num_scrolls=3)  # Scrolls down 3 times with reading pauses

# Will also occasionally:
# - Scroll back up to re-read something (30% chance)
# - Vary scroll distances
# - Add realistic reading pauses between scrolls
```

### 4. Realistic Clicking

Instead of `element.click()`:

```python
# Simple click with pre-hover
human.hover_and_click(button)

# Full realistic click: scroll into view → pause → hover → click
human.realistic_click(job_card)
```

### 5. Mouse Movements

```python
# Move mouse to element with slight randomness
human.move_to_element(element)

# Random mouse movements (simulates browsing)
human.random_mouse_movement()
```

### 6. Delay Variations

```python
# Quick delay (0.5-1.5s)
human.short_delay()

# Very quick delay for typing rhythm (0.05-0.15s)
human.micro_delay()

# Standard random delay (uses your min/max)
human.random_delay()

# Override min/max for specific call
human.random_delay(min_override=2.0, max_override=4.0)

# Delay between switching UI elements (0.5-2.0s)
human.between_actions_delay()

# Simulate reading content (2-5s by default)
human.pause_and_read(min_seconds=3.0, max_seconds=6.0)

# Variable page load wait (adds ±30% variation)
human.variable_wait_for_load(base_wait=2.0)
```

## Integration Examples

### Example 1: Humanized Login

```python
from humanize_scraper import HumanBehavior

def humanized_login(driver, email, password):
    human = HumanBehavior(driver, delay_min=3.0, delay_max=6.0)

    # Navigate
    driver.get("https://www.linkedin.com/login")
    human.variable_wait_for_load(2.5)

    # Scan page briefly (look around)
    human.scan_page(num_scrolls=2)

    # Find and fill email
    email_field = driver.find_element(By.ID, "username")
    human.smooth_scroll_to_element(email_field)
    human.human_type(email_field, email, typing_speed='normal')

    # Brief pause before next field
    human.between_actions_delay()

    # Find and fill password
    password_field = driver.find_element(By.ID, "password")
    human.move_to_element(password_field)  # Move mouse first
    human.human_type(password_field, password, typing_speed='normal')

    # Pause before clicking (review what was entered)
    human.pause_and_read(1.0, 2.0)

    # Click login button
    login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    human.realistic_click(login_button)

    # Wait for redirect
    human.random_delay()
```

### Example 2: Browsing Job Listings

```python
def browse_jobs_humanized(driver, num_jobs=10):
    human = HumanBehavior(driver, delay_min=3.0, delay_max=7.0)

    # Initial page scan
    human.scan_page(num_scrolls=2)

    # Find job cards
    job_cards = driver.find_elements(By.CSS_SELECTOR, "div.job-card-container")

    for i in range(min(num_jobs, len(job_cards))):
        # Refresh cards in case DOM updated
        job_cards = driver.find_elements(By.CSS_SELECTOR, "div.job-card-container")
        card = job_cards[i]

        # Scroll to card smoothly
        human.smooth_scroll_to_element(card)

        # Brief pause (reading job title)
        human.short_delay()

        # Click with realistic behavior
        human.realistic_click(card)

        # Wait for details to load
        human.variable_wait_for_load(2.0)

        # Simulate reading the job description
        human.pause_and_read(3.0, 8.0)

        # Occasionally scroll within description
        if i % 2 == 0:
            human.random_scroll('down', 200)
            human.short_delay()
            human.random_scroll('up', 100)

        # Extract your data here...

        # Random delay before next job
        human.random_delay()

        # Occasionally do extra human actions
        if i % 3 == 0:
            human.random_mouse_movement()
            human.short_delay()
```

### Example 3: Updating Your Existing Code

Here's how to update your existing `extract_linkedin_jobs` function:

```python
import pandas as pd
from humanize_scraper import HumanBehavior

def extract_linkedin_jobs(driver, max_jobs=10, output_file="linkedin_jobs.csv"):
    # Create human behavior instance
    human = HumanBehavior(driver, delay_min=4.0, delay_max=8.0)

    jobs_data = []

    # Switch to iframe
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    driver.switch_to.frame(iframes[0])

    # Initial scan
    human.scan_page(num_scrolls=2)

    # Get job cards
    job_cards = driver.find_elements(By.CSS_SELECTOR, "div.job-card-container")
    total_jobs = min(len(job_cards), max_jobs)

    for i in range(total_jobs):
        # Refresh cards
        job_cards = driver.find_elements(By.CSS_SELECTOR, "div.job-card-container")

        # Scroll to card and click with human behavior
        human.smooth_scroll_to_element(job_cards[i])
        human.short_delay()
        human.realistic_click(job_cards[i])

        # Wait for details
        human.variable_wait_for_load(2.0)

        # Simulate reading
        human.pause_and_read(3.0, 7.0)

        # Extract data
        try:
            details_panel = driver.find_element(By.CSS_SELECTOR, "div.jobs-search__job-details")
            links = details_panel.find_elements(By.TAG_NAME, "a")

            company = links[1].text.strip() if len(links) > 1 else "N/A"
            title = links[2].text.strip() if len(links) > 2 else "N/A"

            # Get description
            desc_elem = details_panel.find_element(By.CSS_SELECTOR, "article.jobs-description__container")
            description = desc_elem.text.strip()

            jobs_data.append({
                'company': company,
                'title': title,
                'description': description
            })

        except Exception as e:
            print(f"Error extracting job {i}: {e}")

        # Random delay before next job (REPLACE your old random_delay() call)
        human.random_delay()

        # Occasionally do extra human actions
        if i % 3 == 0:
            human.random_mouse_movement()
            human.short_delay()

    # Switch back
    driver.switch_to.default_content()

    # Save to CSV
    if jobs_data:
        df = pd.DataFrame(jobs_data)
        df.to_csv(output_file, index=False)
        print(f"Saved {len(jobs_data)} jobs")

    return jobs_data
```

## Best Practices

### 1. **Vary Your Patterns**

Don't make every action the same:

```python
# Good: Vary your delays
for i in range(10):
    human.realistic_click(cards[i])

    if i % 2 == 0:
        human.pause_and_read(3.0, 6.0)  # Longer pause
    else:
        human.pause_and_read(2.0, 4.0)  # Shorter pause
```

### 2. **Add Random "Human Mistakes"**

```python
# Occasionally scroll past, then back
if random.random() < 0.2:  # 20% chance
    human.random_scroll('down', 400)  # Overshoot
    human.short_delay()
    human.random_scroll('up', 200)  # Correct
```

### 3. **Combine Multiple Behaviors**

```python
# More realistic: scan page, move mouse, pause, then click
human.scan_page(num_scrolls=1)
human.random_mouse_movement()
human.short_delay()
human.realistic_click(element)
```

### 4. **Adjust Delays Based on Context**

```python
# Shorter delays for simple actions
human_fast = HumanBehavior(driver, delay_min=1.0, delay_max=3.0)

# Longer delays for complex pages
human_slow = HumanBehavior(driver, delay_min=5.0, delay_max=10.0)
```

### 5. **Don't Overdo It**

Balance realism with efficiency:

```python
# Too much (every single action is over-humanized)
human.scan_page(10)  # Too many scrolls
human.random_mouse_movement()
human.pause_and_read(10.0, 20.0)  # Too long
human.random_mouse_movement()
human.realistic_click(element)

# Just right (natural but efficient)
human.scan_page(2)
human.realistic_click(element)
human.pause_and_read(3.0, 6.0)
```

## Additional Anti-Detection Tips

### 1. **Vary Your User Agent**

```python
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36...",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36..."
]

random_ua = random.choice(user_agents)
options.add_argument(f"user-agent={random_ua}")
```

### 2. **Vary Session Duration**

```python
# Don't scrape for exactly the same duration each time
session_duration = random.uniform(300, 900)  # 5-15 minutes
start_time = time.time()

while time.time() - start_time < session_duration:
    # Scrape jobs...
    pass
```

### 3. **Take Breaks**

```python
# Every 20 jobs, take a longer break
if i > 0 and i % 20 == 0:
    print("Taking a break...")
    human.random_delay(30.0, 60.0)  # 30-60 second break
```

### 4. **Don't Run at Fixed Times**

```python
import random
import time

# Add random startup delay
startup_delay = random.uniform(0, 300)  # 0-5 minutes
print(f"Starting in {startup_delay:.0f} seconds...")
time.sleep(startup_delay)

# Then start scraping
```

## Complete Workflow

See `humanize_scraper_examples.py` for a complete end-to-end example including:
- Humanized login
- Humanized job search
- Humanized browsing through listings
- Humanized scrolling to load more content
- Full workflow from start to finish

## Summary

The key to successful humanization:

1. **Replace direct Selenium calls** with humanized equivalents
2. **Add variety** - don't make every action identical
3. **Balance realism with efficiency** - don't overdo it
4. **Combine multiple behaviors** for more realistic interaction
5. **Use appropriate delays** for different contexts

By using these techniques, your scraper will be:
- ✅ Slower and more reliable
- ✅ Less likely to trigger anti-bot systems
- ✅ More respectful of rate limits
- ✅ Better suited for long-term data collection

Happy (responsible) scraping!
