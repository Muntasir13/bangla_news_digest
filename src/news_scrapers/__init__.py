from enum import Enum

from .base_scraper import BaseScraper
from .bonik_barta_scraper import BonikBartaScraper
from .daily_star_scraper import DailyStarScraper
from .janakantha_scraper import JanakanthaScraper
from .prothom_alo_scraper import ProthomAloScraper

__all__ = ["BaseScraper", "BonikBartaScraper", "DailyStarScraper", "JanakanthaScraper", "ProthomAloScraper"]


class ScraperEnum(Enum):
    bonik_barta = "Daily Bonik Barta"
    daily_star = "The Daily Star Bangla"
    janakantha = "Daily Janakantha"
    prothom_alo = "Prothom Alo"
