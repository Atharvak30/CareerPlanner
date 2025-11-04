"""
Logging configuration for LinkedIn Job Scraper.

Provides detailed logging to both console and files, with separate log directories
for each scraping run.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from .constants import DATETIME_FORMAT, DATETIME_FORMAT_READABLE


class ScraperLogger:
    """
    Custom logger for the scraper with file and console output.
    Creates a new log directory for each run with timestamped logs and screenshots.
    """

    def __init__(self, log_base_dir="logs", run_name=None):
        """
        Initialize the logger.

        Args:
            log_base_dir (str): Base directory for all logs
            run_name (str): Optional name for this run (default: timestamp)
        """
        self.log_base_dir = Path(log_base_dir)
        self.timestamp = datetime.now().strftime(DATETIME_FORMAT)

        # Create run name
        if run_name:
            self.run_name = f"{self.timestamp}_{run_name}"
        else:
            self.run_name = f"{self.timestamp}_run"

        # Create log directory for this run
        self.run_log_dir = self.log_base_dir / self.run_name
        self.run_log_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        self.screenshots_dir = self.run_log_dir / "screenshots"
        self.screenshots_dir.mkdir(exist_ok=True)

        self.html_dumps_dir = self.run_log_dir / "html_dumps"
        self.html_dumps_dir.mkdir(exist_ok=True)

        # Log files
        self.main_log_file = self.run_log_dir / "scraper.log"
        self.error_log_file = self.run_log_dir / "errors.log"
        self.debug_log_file = self.run_log_dir / "debug.log"

        # Set up loggers
        self.logger = self._setup_logger()

    def _setup_logger(self):
        """Set up the logging configuration."""
        logger = logging.getLogger(f"scraper_{self.run_name}")
        logger.setLevel(logging.DEBUG)

        # Remove existing handlers
        logger.handlers = []

        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt=DATETIME_FORMAT_READABLE
        )

        simple_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )

        # Console handler (DEBUG level for development, simple format)
        # Change to INFO for production to reduce console noise
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)  # Changed from INFO to DEBUG
        console_handler.setFormatter(simple_formatter)
        logger.addHandler(console_handler)

        # Main log file handler (INFO level, detailed format)
        main_file_handler = logging.FileHandler(self.main_log_file)
        main_file_handler.setLevel(logging.INFO)
        main_file_handler.setFormatter(detailed_formatter)
        logger.addHandler(main_file_handler)

        # Error log file handler (ERROR level, detailed format)
        error_file_handler = logging.FileHandler(self.error_log_file)
        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(detailed_formatter)
        logger.addHandler(error_file_handler)

        # Debug log file handler (DEBUG level, detailed format)
        debug_file_handler = logging.FileHandler(self.debug_log_file)
        debug_file_handler.setLevel(logging.DEBUG)
        debug_file_handler.setFormatter(detailed_formatter)
        logger.addHandler(debug_file_handler)

        return logger

    def info(self, message):
        """Log info level message."""
        self.logger.info(message)

    def debug(self, message):
        """Log debug level message."""
        self.logger.debug(message)

    def warning(self, message):
        """Log warning level message."""
        self.logger.warning(message)

    def error(self, message, exc_info=False):
        """Log error level message."""
        self.logger.error(message, exc_info=exc_info)

    def critical(self, message, exc_info=False):
        """Log critical level message."""
        self.logger.critical(message, exc_info=exc_info)

    def save_screenshot(self, driver, name="screenshot"):
        """
        Save a screenshot to the screenshots directory.

        Args:
            driver: Selenium WebDriver instance
            name (str): Name for the screenshot (without extension)

        Returns:
            str: Path to saved screenshot
        """
        try:
            timestamp = datetime.now().strftime(DATETIME_FORMAT)
            filename = f"{name}_{timestamp}.png"
            filepath = self.screenshots_dir / filename

            driver.save_screenshot(str(filepath))
            self.info(f"Screenshot saved: {filepath}")
            return str(filepath)
        except Exception as e:
            self.error(f"Failed to save screenshot: {e}")
            return None

    def save_page_source(self, driver, name="page_source"):
        """
        Save the current page HTML source.

        Args:
            driver: Selenium WebDriver instance
            name (str): Name for the HTML file (without extension)

        Returns:
            str: Path to saved HTML file
        """
        try:
            timestamp = datetime.now().strftime(DATETIME_FORMAT)
            filename = f"{name}_{timestamp}.html"
            filepath = self.html_dumps_dir / filename

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(driver.page_source)

            self.info(f"Page source saved: {filepath}")
            return str(filepath)
        except Exception as e:
            self.error(f"Failed to save page source: {e}")
            return None

    def log_exception(self, exception, context=""):
        """
        Log an exception with full traceback.

        Args:
            exception: The exception object
            context (str): Additional context about where the exception occurred
        """
        import traceback

        error_msg = f"Exception in {context}: {type(exception).__name__}: {str(exception)}"
        self.error(error_msg)
        self.error("Full traceback:", exc_info=True)

        # Also write detailed traceback to error log
        with open(self.error_log_file, 'a') as f:
            f.write("\n" + "="*80 + "\n")
            f.write(f"Exception Details - {datetime.now()}\n")
            f.write(f"Context: {context}\n")
            f.write("="*80 + "\n")
            traceback.print_exc(file=f)
            f.write("\n")

    def log_step(self, step_name, step_number=None):
        """
        Log a major step in the scraping process.

        Args:
            step_name (str): Name of the step
            step_number (int): Optional step number
        """
        if step_number:
            msg = f"{'='*80}\nSTEP {step_number}: {step_name}\n{'='*80}"
        else:
            msg = f"{'='*80}\n{step_name}\n{'='*80}"

        self.info(msg)

    def log_summary(self, stats):
        """
        Log a summary of the scraping run.

        Args:
            stats (dict): Dictionary of statistics to log
        """
        summary = "\n" + "="*80 + "\n"
        summary += "SCRAPING RUN SUMMARY\n"
        summary += "="*80 + "\n"

        for key, value in stats.items():
            summary += f"  {key}: {value}\n"

        summary += "="*80

        self.info(summary)

    def get_run_dir(self):
        """Get the log directory for this run."""
        return str(self.run_log_dir)

    def get_screenshots_dir(self):
        """Get the screenshots directory for this run."""
        return str(self.screenshots_dir)

    def get_html_dumps_dir(self):
        """Get the HTML dumps directory for this run."""
        return str(self.html_dumps_dir)


# Convenience function to create a logger
def create_logger(log_base_dir="logs", run_name=None):
    """
    Create and return a ScraperLogger instance.

    Args:
        log_base_dir (str): Base directory for all logs
        run_name (str): Optional name for this run

    Returns:
        ScraperLogger: Configured logger instance
    """
    return ScraperLogger(log_base_dir, run_name)
