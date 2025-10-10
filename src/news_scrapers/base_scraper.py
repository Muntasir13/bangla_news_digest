from abc import ABC, abstractmethod
from datetime import datetime
from logging import Logger

from src.conf import ScraperSiteConfig
from src.webdriver_bridge import WebDriverAdapter


class BaseScraper(ABC):
    """The Scraper Layer - abstract class"""

    def __init__(self, driver_adapter: WebDriverAdapter, logger: Logger, site_config: ScraperSiteConfig) -> None:
        self.adapter = driver_adapter
        self.site_config = site_config
        self.logger = logger

    def get_url(self, url: str) -> None:
        """Retrieves the URL to be scraped

        Args:
            url (str): the URL
        """
        self.adapter.retrieve_url(url=url)

    def extract_news_links(self) -> list[str]:
        """Extracts all news links published today

        Returns:
            list[str]: the list of news links
        """
        try:
            news_link_webelement_list = self.adapter.extract_elements(
                cloudflare_css_selector=self.site_config.selectors.cloudflare,
                element_css_selector=self.site_config.selectors.news_link_list,
            )
            return list({str(web_element.get_attribute("href")) for web_element in news_link_webelement_list})
        except Exception as e:
            self.logger.exception(
                f"Something went wrong. Exception found when extracting news links. \
                The exception found: {e}",
                extra={"scraper": self.site_config.name},
            )
            raise

    @abstractmethod
    def extract_publishing_datetime(self) -> datetime:
        """Extracts the publishing date and time of the news

        Returns:
            datetime: the publishing date and time
        """

    def extract_news_title(self) -> str:
        """Extract the title of a single news link

        Returns:
            str: The title of the news
        """
        try:
            news_title_webelement = self.adapter.extract_elements(
                cloudflare_css_selector=self.site_config.selectors.cloudflare,
                element_css_selector=self.site_config.selectors.title,
            )
            return news_title_webelement[0].text if news_title_webelement != [] else ""
        except Exception as e:
            self.logger.exception(
                f"Something went wrong. Exception found when extracting news title. \
                    The exception found: {e}",
                extra={"scraper": self.site_config.name, "url": self.adapter.driver.current_url},
            )
            raise

    def extract_news_body(self) -> str:
        """Extract the body of a single news link

        Returns:
            str: The body of the news
        """
        try:
            news_body_webelement = self.adapter.extract_elements(
                cloudflare_css_selector=self.site_config.selectors.cloudflare,
                element_css_selector=self.site_config.selectors.body,
            )
            news_body = [web_element.text for web_element in news_body_webelement]
            return "\n".join([s for s in news_body if s.strip()])  # Removes empty string elements in the news body
        except Exception as e:
            self.logger.exception(
                f"Something went wrong. Exception found when extracting news body. \
                    The exception found: {e}",
                extra={"scraper": self.site_config.name, "url": self.adapter.driver.current_url},
            )
            raise
