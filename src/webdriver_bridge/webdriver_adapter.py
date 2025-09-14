from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class WebDriverAdapter:
    """The Adapter Layer for the WebDriver. This layer will specifically work on
    Selenium specific functions. This will help to separate Selenium specific methods
    and Scraper specific post extraction logic
    """

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver

    def retrieve_url(self, url: str) -> None:
        """Retrieves the intended URL

        Args:
            url (str): the intended URL
        """
        self.driver.get(url)

    def browser_refresh(self) -> None:
        """This function will simply perform a refresh on
        the browser. It is kind of like hitting F5 on the browser.
        """
        self.driver.refresh()

    def extract_elements(self, cloudflare_css_selector: str | None, element_css_selector: str) -> list[WebElement]:
        """Fetch all web elements from URL using the element_css_selector

        Args:
            cloudflare_css_selector (str): the css selector for cloudflare. This is needed to check whether
            cloudflare has been bypassed or not. If bypassed, only then will the adapter look for the
            web element css selector
            element_css_selector (str): the web element css selector

        Returns:
            list[WebElement]: the list of web elements
        """
        if cloudflare_css_selector:
            WebDriverWait(self.driver, 30, poll_frequency=5).until(
                EC.invisibility_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        cloudflare_css_selector,
                    )
                )
            )

        return (
            WebDriverWait(self.driver, 30, poll_frequency=5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, element_css_selector))) or []
        )

    def quit(self) -> None:
        """Gracefully quitting the web driver instance"""
        self.driver.close()
