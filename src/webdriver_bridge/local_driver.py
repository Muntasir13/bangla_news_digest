import logging
from abc import ABC, abstractmethod

import undetected_chromedriver as uc
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.remote.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from src.conf import WebDriverConfig

logger = logging.getLogger(__name__)


class LocalDriverBaseClass(ABC):
    def __init__(self, config: WebDriverConfig) -> None:
        """Initializes the local driver base class with a specified driver path.

        Sets up the driver path and initializes the driver instance using the subclass implementation.

        Args:
            config (dict[str, bool | str]): the web driver config
        """
        self.driver_config = config
        self.driver = self._init_driver()

    @abstractmethod
    def _init_driver(self) -> WebDriver | uc.Chrome:
        """Local driver initialization"""
        return WebDriver()


class ChromeLocalDriver(LocalDriverBaseClass):
    """Chrome local web driver class. All properties gained from parent web driver class"""

    def __init__(self, config: WebDriverConfig) -> None:
        super().__init__(config)
        self.__enable_network_filtering()

    def _init_driver(self) -> WebDriver | uc.Chrome:
        options = uc.ChromeOptions()
        for config, cfg_val in self.driver_config.options.items():
            options.add_argument(f"--{config}={cfg_val}")
        options.add_argument(f"user-agent={UserAgent().random}")

        driver_path = ChromeDriverManager().install()
        return uc.Chrome(options=options, driver_executable_path=driver_path)

    def __enable_network_filtering(self) -> None:
        """This method will ensure that unnecessary content loading (CSS, PNG, JPG)
        does not reduce scraping speed.
        """
        self.driver.execute_cdp_cmd("Network.enable", {})
        self.driver.execute_cdp_cmd(
            "Network.setBlockedURLs",
            {
                "urls": [
                    "*.png",
                    "*.jpg",
                    "*.css",
                    "*/analytics.js",
                    "*.woff2",
                    "*googletagmanager.com/*",
                    "*googlesyndication.com/*",
                    "*googleads*",
                    "*doubleclick.net/*",
                    "*adservice.google.com/*",
                    "*ads.pubmatic.com/*",
                    "*adnxs.com/*",
                    "*adsafeprotected.com/*",
                ]
            },
        )


class FirefoxLocalDriver(LocalDriverBaseClass):
    """Firefox local web driver class. All properties gained from parent web driver class"""

    def _init_driver(self) -> WebDriver | uc.Chrome:
        options = FirefoxOptions()
        for config, cfg_val in self.driver_config.options.items():
            options.add_argument(f"--{config}={cfg_val}")
        options.add_argument(f"user-agent: {UserAgent().random}")

        service = FirefoxService(executable_path=GeckoDriverManager().install())
        return webdriver.Firefox(options=options, service=service)


# Wrapper for loading webdrivers
def load_webdriver(driver_config: WebDriverConfig) -> WebDriver:
    """Returns a local driver based on the config set up in default.yaml

    Args:
        driver_config (WebDriverConfig): the driver config for the web driver

    Returns:
        WebDriver: Selenium Webdriver with loaded options
    """
    if driver_config.driver_name == "chrome":
        logger.info("Loading Chrome Local Driver")
        return ChromeLocalDriver(config=driver_config).driver
    else:
        logger.info("Loading Firefox Local Driver")
        return FirefoxLocalDriver(config=driver_config).driver
