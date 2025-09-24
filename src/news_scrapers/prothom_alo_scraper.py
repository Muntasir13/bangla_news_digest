from datetime import datetime
from logging import Logger

from src.conf import ScraperSiteConfig
from src.news_scrapers import BaseScraper
from src.webdriver_bridge import WebDriverAdapter


class ProthomAloScraper(BaseScraper):
    def __init__(self, driver_adapter: WebDriverAdapter, logger: Logger, site_config: ScraperSiteConfig) -> None:
        super().__init__(driver_adapter, logger, site_config)

    def extract_news_links(self) -> list[str]:
        try:
            return []
        except Exception as e:
            self.logger.exception(
                f"Something went wrong. Exception found when extracting news links. \
                The exception found: {e}",
                extra={"scraper": self.site_config.name},
            )
            raise

    def extract_publishing_datetime(self) -> datetime:
        try:
            return datetime.now()
        except Exception as e:
            self.logger.exception(
                f"Something went wrong. Exception found when extracting publishing datetime. \
                    The exception found: {e}",
                extra={"scraper": self.site_config.name, "url": self.adapter.driver.current_url},
            )
            raise

    def extract_news_title(self) -> str:
        try:
            return ""
        except Exception as e:
            self.logger.exception(
                f"Something went wrong. Exception found when extracting news title. \
                    The exception found: {e}",
                extra={"scraper": self.site_config.name, "url": self.adapter.driver.current_url},
            )
            raise

    def extract_news_body(self) -> str:
        try:
            return ""
        except Exception as e:
            self.logger.exception(
                f"Something went wrong. Exception found when extracting news body. \
                    The exception found: {e}",
                extra={"scraper": self.site_config.name, "url": self.adapter.driver.current_url},
            )
            raise
