"""Office Jukebox: Selenium Test Suite"""

# Python Standard Libraries
import unittest

# Selenium Imports
from selenium import webdriver
from selenium.webdriver.common.keys import keys


################################################################################
### (1) Test Suite Setup


class OfficeJukeboxTest(unittest.TestCase):
    """Example test case for Selenium + Office Jukebox."""

    def setUp(self):
        """Runs on test case setup."""

        self.driver = webdriver.Firefox()  # or some other browser

    def tearDown(self):
        """Runs on test case teardown."""

        self.driver.close()

    def test_case(self):
        """Runs when a test case is executed."""

        driver = self.driver
        driver.get("localhost:5000")
        # do some other stuff, include assert
