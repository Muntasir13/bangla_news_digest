from dataclasses import dataclass
from enum import Enum

from .base_scraper import BaseScraper
from .bonik_barta_scraper import BonikBartaScraper
from .daily_star_scraper import DailyStarScraper
from .janakantha_scraper import JanakanthaScraper
from .prothom_alo_scraper import ProthomAloScraper

__all__ = ["BaseScraper", "BonikBartaScraper", "DailyStarScraper", "JanakanthaScraper", "ProthomAloScraper"]


@dataclass
class ScraperDesc:
    scraper_name: str
    class_obj: type[BaseScraper]


class ScraperEnum(Enum):
    bonik_barta = ScraperDesc(scraper_name="bonik_barta", class_obj=BonikBartaScraper)
    daily_star = ScraperDesc(scraper_name="daily_star", class_obj=DailyStarScraper)
    janakantha = ScraperDesc(scraper_name="janakantha", class_obj=JanakanthaScraper)
    prothom_alo = ScraperDesc(scraper_name="prothom_alo", class_obj=ProthomAloScraper)
