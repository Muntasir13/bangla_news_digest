import os
import time
from datetime import date
from logging import getLogger
from typing import cast

import hydra
from celery import group
from dotenv import load_dotenv
from omegaconf import OmegaConf

from src.celery_app import generate_celery_app
from src.conf import ProjectConfig, ScraperSiteConfig, WebDriverConfig
from src.conf.site_config import ScraperSiteSelectorConfig
from src.db import ensure_tables, get_engine, save_scraped_items
from src.news_scrapers import BaseScraper, ScraperEnum
from src.pipelines import data_extraction_pipeline
from src.utils import save_processsed_data, save_raw_data, send_email
from src.webdriver_bridge import WebDriverAdapter, load_webdriver

app = generate_celery_app()


@app.task(name="run_pipeline_and_queue_data", queue="default")
def run_pipeline_and_queue_data(
    scraper_object: type[BaseScraper],
    driver_config: dict,
    site_config: ScraperSiteConfig,
    vault_location: str,
    max_retries: int,
) -> list[dict[str, str | list[str]]]:
    logger = getLogger(__name__)

    # Load webdriver and adapter
    driver = load_webdriver(driver_config=WebDriverConfig(**driver_config))
    logger.info("Web Driver Loaded")

    driver_adapter = WebDriverAdapter(driver=driver)
    logger.info("Web Driver Adapter Created")

    scraper = scraper_object(driver_adapter=driver_adapter, logger=logger, site_config=site_config)

    logger.info(f"{scraper.site_config.name} scraper loaded")
    logger.info("Running extraction...")

    try:
        compiled_data = data_extraction_pipeline(scraper=scraper, vault_location=vault_location, max_retries=max_retries)
    finally:
        driver_adapter.quit()
        logger.info(f"Web driver of {scraper.site_config.name} has gracefully quitted")

    return compiled_data


@hydra.main(version_base=None, config_path="./config", config_name="default")
def main(cfg: ProjectConfig) -> None:
    start_time = time.time()

    # Logger Initialization
    logger = getLogger(__name__)
    logger.info("Project Config Loaded")
    logger.info("Setting up the environment...")

    # Environment Variables Initilization
    load_dotenv()

    # Database Inialization
    ensure_tables(get_engine(cfg.runtime.db))
    logger.info("Database connection established. Ensured that, news_article table exists in database")

    # Asynchronous task assignment to Celery app
    g = group(
        app.signature(
            "run_pipeline_and_queue_data",
            args=[
                scraper.value.class_obj,
                cast(dict, OmegaConf.to_container(cfg.webdriver, resolve=True)),
                cfg.sites.__dict__["_content"][scraper.value.scraper_name],  # loading scraper site config
                cfg.resource.vault,
                cfg.max_retries,
            ],
            options={"serializer": cfg.celery.task_serializer},
        )
        for scraper in ScraperEnum
    )
    logger.info("Environment Setup Completed")
    logger.info("Initiating Scraping...")

    group_result = g.apply_async()
    results = group_result.get(propagate=False)  # blocks; like await
    compiled_data = []
    for data in results:
        compiled_data.extend(data)
    logger.info("News extraction completed.")
    logger.info(f"All news data compiled. Total {len(compiled_data)} news found.")

    save_raw_data(
        data=compiled_data,
        save_location=cfg.output_location.raw,
        filename="bangla_news_digest.json",
    )
    logger.info(f"Raw Data saved at {cfg.output_location.raw}")

    save_processsed_data(
        data=compiled_data,
        save_location=cfg.output_location.processed,
        filename=f"Bangla News Digest {date.today().strftime('%B %d, %Y')}.docx",
        template=cfg.resource.news_digest_template,
    )
    logger.info(f"Processed Data saved at {cfg.output_location.processed}")

    if cfg.runtime.db_send:
        inserted_articles = save_scraped_items(database_config=cfg.runtime.db, items=compiled_data)
        logger.info(f"Processed Data saved at db. No. of articles saved: {inserted_articles}")
    else:
        logger.warning("Data not saved to DB. You might be losing valuable data.")

    if cfg.runtime.email_send:
        try:
            send_email(
                smtp_config={
                    "host": cfg.runtime.email.host,
                    "port": cfg.runtime.email.port,
                    "user": cfg.runtime.email.username,
                    "password": cfg.runtime.email.password,
                },
                email_subject="Today's Bangla News Digest",
                email_body="\n".join(
                    [
                        "Assalamu alaikum,",
                        "Here is today's Bangla News Digest.",
                        f"Time taken for the entire project: {round((time.time() - start_time) / 60, 2)} minutes in total",
                        f"Total valid news scraped: {len(compiled_data)}",
                    ]
                ),
                from_addr=cfg.runtime.email.from_addr,
                to_addr=cfg.runtime.email.to_addr,
                cc_addr=cfg.runtime.email.cc_addr,
                attachment_path=os.path.join(
                    cfg.output_location.processed,
                    f"Bangla News Digest {date.today().strftime('%B %d, %Y')}.docx",
                ),
            )
        except Exception as e:
            logger.exception(
                f"Something went wrong. Exception found when sending email. \
                    The exception found: {e}. "
            )
    else:
        logger.warning("Email not sent to intended users.")

    logger.info(f"Time taken for total process: {round((time.time() - start_time) / 60, 2)} minutes")
    logger.info("System is shutting down...")


if __name__ == "__main__":
    main()
