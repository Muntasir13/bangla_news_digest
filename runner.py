import time
from multiprocessing import Manager

import hydra
from dotenv import load_dotenv

from src.conf import ProjectConfig
from src.news_scrapers import (
    BaseScraper,
    BonikBartaScraper,
    DailyStarScraper,
    JanakanthaScraper,
    ProthomAloScraper,
    ScraperEnum,
)
from src.utils import init_logging
from src.webdriver_bridge import WebDriverAdapter, load_webdriver


@hydra.main(version_base=None, config_path="./config", config_name="default")
def main(cfg: ProjectConfig) -> None:
    # start_time = time.time()

    # Logger Initialization
    logger, log_queue, listener = init_logging(cfg=cfg.logging)
    logger.info("Project Config Loaded")
    logger.info("Setting up the environment...")

    # Environment Variables
    load_dotenv()

    # # Shared List Manager for storing all the compiled data across processes
    # m = Manager()
    # process_shared_list = m.list()
    # logger.info("Process Shared List Created")

    logger.info("Attempting pre-warm install to ensure chromedriver is installed in intended location")
    driver = load_webdriver(driver_config=cfg.webdriver)
    driver.get("https://google.com/")
    driver.close()

    listener.stop()
    return


if __name__ == "__main__":
    main()
