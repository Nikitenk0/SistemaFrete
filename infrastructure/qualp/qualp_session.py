from selenium.webdriver.support.ui import WebDriverWait
from infrastructure.qualp.chrome_webdriver_factory import (
    ChromeWebDriverFactory
)

class QualPSession:

    def __init__(
        self,
        timeout: int = 15,
        headless: bool = False
    ):
        self._timeout = timeout
        self._headless = headless
        self._driver = None
        self._wait = None

    def open(self):
        self._driver = ChromeWebDriverFactory.create(
            headless=self._headless
        )

        self._wait = WebDriverWait(
            self._driver,
            self._timeout
        )

        return (
            self._driver,
            self._wait
        )

    def close(self):
        if self._driver is None:
            return

        try:
            self._driver.quit()
        finally:
            self._driver = None
            self._wait = None
