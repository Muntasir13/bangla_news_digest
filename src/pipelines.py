import logging
import time
from datetime import date, datetime
from random import randint
from uuid import uuid4

from tqdm import tqdm

from src.news_scrapers import BaseScraper
from src.utils import (
    clear_from_vault,
    compute_news_article_fingerprint,
    get_start_and_end_date,
    read_from_vault,
    save_to_vault,
)

logger = logging.getLogger(__name__)


def news_summary_generator(news_body: str) -> list[str]:
    """This is the news summary generator. It will generate the news summary
    in two bullet points.

    Args:
        news_body (str): the news body

    Returns:
        list[str]: the two bullet points
    """
    return news_body.split("\n")[:2]


def extract_news_links_list(scraper: BaseScraper, url: str, max_retries: int) -> list[str]:
    """Extracting news links list. This method is purely for separating
    extraction and compilation of extracted news data

    Args:
        scraper (BaseScraper): the scraper to use for extraction
        url (str): the url from which news links are to be extracted. There are multiple sources
        max_retries (int, optional): max retries for news links extraction.

    Returns:
        list[str]: the news links list
    """
    scraper.get_url(url)
    news_links = []
    for _ in range(max_retries):
        try:
            news_links = scraper.extract_news_links()
        except Exception:
            scraper.adapter.browser_refresh()
    return news_links


def extract_from_single_news_link(scraper: BaseScraper, news_link: str) -> tuple[str, datetime, str]:
    """Extract news title, publishing datetime, and body from a news link.

    Args:
        scraper (BaseScraper): The scraper to use for extraction
        news_link (str): The news link to extract from

    Returns:
        tuple[str, datetime, str]: a tuple containing news title, publishing date and body (in this serial)
    """
    scraper.get_url(news_link)
    date_and_time = scraper.extract_publishing_datetime()
    title = scraper.extract_news_title()
    body = scraper.extract_news_body()
    return (title, date_and_time, body)


def compile_extracted_data(scraper: BaseScraper, news_links: list[str], news_cat: str, vault_location: str) -> list[dict[str, str | list[str]]]:
    """Compile extracted data from news links using each scraper

    Args:
        scraper (BaseScraper): the scraper to use for extraction
        news_links (list[str]): the list of news links
        news_cat (str): the news category mentioned in the news portal
        vault_location (str): vault for saving unscraped news links

    Returns:
        list[dict[str, str]]: news data compiled into a list. Each entry contains
        a title, body and link of each news
    """
    logger.info(f"{len(news_links)} news links found for {news_cat} in {scraper.site_config.name}")
    today, yesterday = get_start_and_end_date(end_timedelta=3 if datetime.now().strftime("%A") == "Sunday" else 1)

    compiled_data: list[dict[str, str | list[str]]] = []
    for news_link in tqdm(news_links):
        time.sleep(randint(1, scraper.site_config.rate_limiter) if scraper.site_config.rate_limiter > 0 else 0)  # nosec: B311
        try:
            title, date_and_time, body = extract_from_single_news_link(scraper=scraper, news_link=news_link)
            if not (date_and_time > yesterday) and (date_and_time <= today):
                continue

            summary_points = news_summary_generator(news_body=body)
            compiled_data.append(
                {
                    "id": str(uuid4()),
                    "title": title,
                    "body": body,
                    "summary_points": summary_points,
                    "published_at": str(date_and_time),
                    "fingerprint": compute_news_article_fingerprint(title, body),
                    "source": scraper.site_config.name,
                    "source_url": scraper.site_config.base_url,
                    "category": news_cat,
                    "scraped_at": str(datetime.now()).split(".")[0],  # removing the micro second part
                    "date": date.today().strftime("%B %d, %Y"),
                    "language": "Bangla",
                    "url": news_link,
                }
            )
        except Exception:
            logger.exception(
                "Saving news link to vault",
                extra={"scraper": scraper.site_config.name, "news_link": news_link},
            )

            save_to_vault(
                website_name=scraper.site_config.name,
                news_cat=news_cat,
                vault_location=vault_location,
                link_list=[news_link],
            )
    logger.info(f"{len(compiled_data)} valid news data compiled from {news_cat} in {scraper.site_config.name}")
    return compiled_data


def extract_from_unscraped(scraper: BaseScraper, vault_location: str, max_retries: int = 5) -> list[dict[str, str | list[str]]]:
    """This method is intended to extract from those links that could not be scraped from
    using compile_extracted_data() method. This function will take the unscraped news links
    from the vault and scrap till the number of max_retries expires

    Args:
        scraper (BaseScraper): the scraper to be used for scraping
        vault_location (str): vault to retrieve the list of unscraped news links from
        max_retries (int): the number of retries the scraper should make to extract. Defaults to 5

    Returns:
        list[dict[str, str]]: news data compiled into a list. Each entry contains
        a title, body and link of each news
    """
    compiled_data: list[dict[str, str | list[str]]] = []
    for _ in range(max_retries):
        logger.info("Attempting extraction from initially unscraped links...")
        unscraped_news_links = read_from_vault(website_name=scraper.site_config.name, vault_location=vault_location)
        if unscraped_news_links == {}:
            logger.info(f"No unscraped news links found for {scraper.site_config.name}")
            break

        # Clears all the unscraped news links under the website from vault
        clear_from_vault(website_name=scraper.site_config.name, vault_location=vault_location)

        # This step also adds any news link to the vault
        # that might have survived the extraction process
        for news_cat, news_links in unscraped_news_links.items():
            compiled_data.extend(
                compile_extracted_data(
                    scraper=scraper,
                    news_links=news_links,
                    news_cat=news_cat,
                    vault_location=vault_location,
                )
            )

    unscraped_news_links = read_from_vault(website_name=scraper.site_config.name, vault_location=vault_location)
    if unscraped_news_links != {}:
        logger.warning(
            f"News links from {len(unscraped_news_links)} categories still remain to be scraped even after {max_retries} retries",
            extra={"unscraped_news_links": unscraped_news_links},
        )
        clear_from_vault(website_name=scraper.site_config.name, vault_location=vault_location)

    logger.info(
        f"{len(compiled_data)} valid news data compiled from unscraped news links \
            list found under '{scraper.site_config.name}' in vault"
    )
    return compiled_data


def data_extraction_pipeline(scraper: BaseScraper, vault_location: str, max_retries: int) -> list[dict[str, str | list[str]]]:
    """The total pipeline for extracting news data from each scraper

    Args:
        scraper (BaseScraper): the scraper to be used for extracting news data
        vault_location (str): the vault location for storing unscraped news links
        max_retries (int): number of times to retry scraping news

    Returns:
        list[dict[str, str | list[str]]]: the compiled news data after extraction
    """
    compiled_data: list[dict[str, str | list[str]]] = []
    for news_cat, news_cat_url in scraper.site_config.url_list.items():
        news_links = extract_news_links_list(scraper=scraper, url=news_cat_url, max_retries=max_retries)
        logger.info(f"{len(news_links)} news links found for {scraper.site_config.name}")
        compiled_data += compile_extracted_data(
            scraper=scraper,
            news_links=news_links,
            news_cat=news_cat,
            vault_location=vault_location,
        )
        compiled_data += extract_from_unscraped(scraper=scraper, vault_location=vault_location)
        del news_links  # destroying variable to save resource
    return compiled_data


def separate_into_categories(compiled_data: list[dict[str, str | list[str]]]) -> dict[str, dict[str, str | list[str]]]:
    cat_separated_data: dict[str, dict[str, str | list[str]]] = {
        "Economy": {},
        "Business": {},
        "Politics": {},
        "Bangladesh": {},
        "International": {},
        "Others": {},
    }
    for data in compiled_data:
        if str(data["category"]) == "National":
            cat_separated_data["Bangladesh"] = data
        elif str(data["category"]) in {"Sports", "Education", "Migration"}:
            cat_separated_data["Others"] = data
        elif str(data["category"]) == "World":
            cat_separated_data["International"] = data
        cat_separated_data[str(data["category"])] = data
    return cat_separated_data


def remove_similar_news(
    news_list: list[dict[str, str]], similar_news_dict: dict[str, dict[str, str]], id_to_date: dict[str, str]
) -> list[dict[str, str]]:
    """Keep only one instance of similar news

    Args:
        news_list (list[dict[str, str]]): today's scraped news list
        similar_news_dict (dict[str, dict[str, str]]): the news title list arranged based on similarity (found from model output)
        id_to_date (dict[str, str]): key-value pair of id and published date of news

    Returns:
        list[dict[str, str]]: Reduced compiled news data
    """
    id_to_news = {news["id"]: news for news in news_list}
    reduced_news_list = []
    for sent_list in similar_news_dict:
        date_list = [id_to_date[id] for id in similar_news_dict[sent_list]]
        if datetime.fromisoformat(sorted(date_list)[0]) < datetime.today().replace(hour=0, minute=0, second=0):
            continue
        reduced_news_list.append(id_to_news[list(similar_news_dict[sent_list].keys())[0]])
    return reduced_news_list
