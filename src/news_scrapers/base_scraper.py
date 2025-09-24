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

    @abstractmethod
    def extract_news_links(self) -> list[str]:
        """Extracts all news links published today

        Returns:
            list[str]: the list of news links
        """

    @abstractmethod
    def extract_publishing_datetime(self) -> datetime:
        """Extracts the publishing date and time of the news

        Returns:
            datetime: the publishing date and time
        """

    @abstractmethod
    def extract_news_title(self) -> str:
        """Extract the title of a single news link

        Returns:
            str: The title of the news
        """

    @abstractmethod
    def extract_news_body(self) -> str:
        """Extract the body of a single news link

        Returns:
            str: The body of the news
        """
