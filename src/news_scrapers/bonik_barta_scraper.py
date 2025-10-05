from datetime import datetime
from logging import Logger

from src.conf import ScraperSiteConfig
from src.news_scrapers import BaseScraper
from src.utils import bangla_to_english_datetime_parsing
from src.webdriver_bridge import WebDriverAdapter


class BonikBartaScraper(BaseScraper):
    def __init__(self, driver_adapter: WebDriverAdapter, logger: Logger, site_config: ScraperSiteConfig) -> None:
        super().__init__(driver_adapter, logger, site_config)

    def extract_news_links(self) -> list[str]:
        try:
            news_link_webelement_list = self.adapter.extract_elements(
                cloudflare_css_selector=self.site_config.selectors.cloudflare,
                element_css_selector=self.site_config.selectors.news_link_list,
            )
            return [str(web_element.get_attribute("href")) for web_element in news_link_webelement_list]
        except Exception as e:
            self.logger.exception(
                f"Something went wrong. Exception found when extracting news links. \
                The exception found: {e}",
                extra={"scraper": self.site_config.name},
            )
            raise

    def extract_publishing_datetime(self) -> datetime:
        try:
            publishing_datetime_list = self.adapter.extract_elements(
                cloudflare_css_selector=self.site_config.selectors.cloudflare,
                element_css_selector=self.site_config.selectors.datetime,
            )
            date_and_time = publishing_datetime_list[0].text.split(": ")[1]
            # Final Format: Sunday 5 October 2025, 15:09
            return datetime.strptime(bangla_to_english_datetime_parsing(date_and_time), "%A %d %B %Y, %H:%M")
        except Exception as e:
            self.logger.exception(
                f"Something went wrong. Exception found when extracting publishing datetime. \
                    The exception found: {e}",
                extra={"scraper": self.site_config.name, "url": self.adapter.driver.current_url},
            )
            raise

    def extract_news_title(self) -> str:
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
        try:
            news_body_webelement = self.adapter.extract_elements(
                cloudflare_css_selector=self.site_config.selectors.cloudflare,
                element_css_selector=self.site_config.selectors.body,
            )
            news_body = [web_element.text for web_element in news_body_webelement]
            return " \n ".join(news_body)
        except Exception as e:
            self.logger.exception(
                f"Something went wrong. Exception found when extracting news body. \
                    The exception found: {e}",
                extra={"scraper": self.site_config.name, "url": self.adapter.driver.current_url},
            )
            raise
