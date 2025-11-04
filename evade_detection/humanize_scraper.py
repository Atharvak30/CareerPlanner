"""
Humanization utilities for web scraping with Selenium.

This module provides functions to make automated browser actions appear more human-like,
reducing the likelihood of detection and blocking by anti-bot systems.
"""

import time
import random
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import JavascriptException


class HumanBehavior:
    """
    A class to simulate human-like behavior in Selenium web scraping.
    """

    def __init__(self, driver, delay_min=4.0, delay_max=8.0):
        """
        Initialize the HumanBehavior simulator.

        Args:
            driver: Selenium WebDriver instance
            delay_min (float): Minimum delay in seconds (default: 4.0)
            delay_max (float): Maximum delay in seconds (default: 8.0)
        """
        self.driver = driver
        self.delay_min = delay_min
        self.delay_max = delay_max
        self.actions = ActionChains(driver)

    def random_delay(self, min_override=None, max_override=None):
        """
        Sleep for a random duration to simulate human reading/thinking time.

        Args:
            min_override (float): Override the default minimum delay
            max_override (float): Override the default maximum delay
        """
        min_delay = min_override if min_override is not None else self.delay_min
        max_delay = max_override if max_override is not None else self.delay_max
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)

    def short_delay(self):
        """Quick delay for minor actions (0.5-1.5 seconds)."""
        time.sleep(random.uniform(0.5, 1.5))

    def micro_delay(self):
        """Very short delay for natural typing rhythm (0.05-0.15 seconds)."""
        time.sleep(random.uniform(0.05, 0.15))

    def human_type(self, element, text, typing_speed='normal'):
        """
        Type text into an element with human-like delays between keystrokes.

        Args:
            element: WebElement to type into
            text (str): Text to type
            typing_speed (str): 'slow', 'normal', or 'fast'
        """
        # Define typing speed ranges (seconds between keystrokes)
        speed_ranges = {
            'slow': (0.15, 0.35),
            'normal': (0.08, 0.18),
            'fast': (0.03, 0.08)
        }

        min_delay, max_delay = speed_ranges.get(typing_speed, speed_ranges['normal'])

        element.click()
        self.short_delay()

        for char in text:
            element.send_keys(char)
            # Occasionally pause longer (simulating thinking or correcting)
            if random.random() < 0.1:  # 10% chance of longer pause
                time.sleep(random.uniform(0.3, 0.8))
            else:
                time.sleep(random.uniform(min_delay, max_delay))

    def smooth_scroll_to_element(self, element):
        """
        Smoothly scroll to an element in view with human-like behavior.

        Args:
            element: WebElement to scroll to
        """
        # Get element location
        try:
            location = element.location_once_scrolled_into_view

            # Get current scroll position
            current_scroll = self.driver.execute_script("return window.pageYOffset;")

            # Calculate target scroll position (with some randomness to avoid perfect centering)
            target_scroll = location['y'] - random.randint(100, 300)

            # Perform smooth scroll in increments
            self._smooth_scroll(current_scroll, target_scroll)

        except JavascriptException:
            # Fallback to simple scroll
            element.location_once_scrolled_into_view

    def _smooth_scroll(self, start, end, steps=None):
        """
        Perform a smooth scroll animation from start to end position.

        Args:
            start (int): Starting scroll position
            end (int): Ending scroll position
            steps (int): Number of scroll steps (auto-calculated if None)
        """
        distance = abs(end - start)

        # Auto-calculate steps based on distance
        if steps is None:
            steps = max(5, min(20, distance // 50))

        # Calculate step size with some variation
        step_size = (end - start) / steps

        for i in range(steps):
            # Add randomness to step size
            current_step = step_size * (1 + random.uniform(-0.1, 0.1))
            new_position = start + (step_size * i) + current_step

            self.driver.execute_script(f"window.scrollTo(0, {new_position});")

            # Variable delay between scroll steps
            time.sleep(random.uniform(0.01, 0.05))

        # Final position
        self.driver.execute_script(f"window.scrollTo(0, {end});")
        self.short_delay()

    def random_scroll(self, direction='down', distance=None):
        """
        Perform a random scroll action to simulate browsing behavior.

        Args:
            direction (str): 'down', 'up', or 'random'
            distance (int): Scroll distance in pixels (random if None)
        """
        if direction == 'random':
            direction = random.choice(['down', 'up'])

        if distance is None:
            distance = random.randint(200, 600)

        current_scroll = self.driver.execute_script("return window.pageYOffset;")

        if direction == 'down':
            target = current_scroll + distance
        else:
            target = max(0, current_scroll - distance)

        self._smooth_scroll(current_scroll, target)

    def page_down_scroll(self):
        """Simulate page down behavior with some variation."""
        viewport_height = self.driver.execute_script("return window.innerHeight;")
        # Scroll 70-90% of viewport height (not perfect full page)
        scroll_amount = int(viewport_height * random.uniform(0.7, 0.9))
        self.random_scroll('down', scroll_amount)

    def scan_page(self, num_scrolls=None):
        """
        Simulate scanning/reading a page with multiple scroll actions.

        Args:
            num_scrolls (int): Number of scroll actions (random 2-5 if None)
        """
        if num_scrolls is None:
            num_scrolls = random.randint(2, 5)

        for _ in range(num_scrolls):
            self.random_scroll('down')
            self.random_delay(1.0, 3.0)  # Reading time

            # Occasionally scroll back up (like re-reading something)
            if random.random() < 0.3:  # 30% chance
                self.random_scroll('up', random.randint(100, 300))
                self.short_delay()

    def move_to_element(self, element, offset_x=0, offset_y=0):
        """
        Move mouse to an element with human-like curved movement.

        Args:
            element: WebElement to move to
            offset_x (int): X offset from element center
            offset_y (int): Y offset from element center
        """
        # Add random offset to avoid perfect centering
        random_offset_x = offset_x + random.randint(-5, 5)
        random_offset_y = offset_y + random.randint(-5, 5)

        self.actions.move_to_element_with_offset(
            element,
            random_offset_x,
            random_offset_y
        ).perform()

        # Small delay after moving mouse
        time.sleep(random.uniform(0.1, 0.3))

    def hover_and_click(self, element):
        """
        Hover over an element briefly before clicking (more human-like).

        Args:
            element: WebElement to click
        """
        # Move to element
        self.move_to_element(element)

        # Brief hover
        time.sleep(random.uniform(0.2, 0.5))

        # Click
        element.click()

        # Brief delay after click
        time.sleep(random.uniform(0.1, 0.3))

    def realistic_click(self, element):
        """
        Click with realistic behavior: scroll into view, hover, then click.

        Args:
            element: WebElement to click
        """
        # Scroll element into view smoothly
        self.smooth_scroll_to_element(element)

        # Short delay (like looking at it)
        self.short_delay()

        # Hover and click
        self.hover_and_click(element)

    def random_mouse_movement(self):
        """
        Perform random mouse movements to simulate natural browsing.
        """
        viewport_width = self.driver.execute_script("return window.innerWidth;")
        viewport_height = self.driver.execute_script("return window.innerHeight;")

        # Random number of movements
        num_movements = random.randint(1, 3)

        for _ in range(num_movements):
            # Random target position
            x = random.randint(100, viewport_width - 100)
            y = random.randint(100, viewport_height - 100)

            # Use ActionChains to move
            self.actions.move_by_offset(x, y).perform()
            time.sleep(random.uniform(0.1, 0.3))

            # Reset action chains
            self.actions = ActionChains(self.driver)

    def pause_and_read(self, min_seconds=2.0, max_seconds=5.0):
        """
        Simulate reading/analyzing content with realistic pause.

        Args:
            min_seconds (float): Minimum pause duration
            max_seconds (float): Maximum pause duration
        """
        duration = random.uniform(min_seconds, max_seconds)
        time.sleep(duration)

    def variable_wait_for_load(self, base_wait=2.0):
        """
        Wait for page to load with human-like variation.

        Args:
            base_wait (float): Base wait time in seconds
        """
        wait_time = base_wait * random.uniform(0.8, 1.3)
        time.sleep(wait_time)

    def between_actions_delay(self):
        """
        Random delay to use between different actions (like switching between UI elements).
        """
        time.sleep(random.uniform(0.5, 2.0))


# Standalone helper functions for quick use

def create_human_behavior(driver, delay_min=4.0, delay_max=8.0):
    """
    Factory function to create a HumanBehavior instance.

    Args:
        driver: Selenium WebDriver instance
        delay_min (float): Minimum delay in seconds
        delay_max (float): Maximum delay in seconds

    Returns:
        HumanBehavior: Configured instance
    """
    return HumanBehavior(driver, delay_min, delay_max)
