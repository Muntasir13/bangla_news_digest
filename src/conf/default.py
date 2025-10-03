from dataclasses import dataclass

from .celery import CeleryConfig
from .runtime import RuntimeConfig
from .site_config import ScraperSiteConfig
from .webdriver import WebDriverConfig


@dataclass
class ScraperSiteList:
    bonik_barta: ScraperSiteConfig
    daily_star: ScraperSiteConfig
    janakantha: ScraperSiteConfig
    prothom_alo: ScraperSiteConfig


@dataclass
class OutputLocationConfig:
    raw: str
    processed: str


@dataclass
class ProjectResourceConfig:
    news_digest_template: str
    vault: str


@dataclass
class ProjectConfig:
    runtime: RuntimeConfig
    webdriver: WebDriverConfig
    celery: CeleryConfig
    sites: ScraperSiteList
    max_retries: int
    output_location: OutputLocationConfig
    resource: ProjectResourceConfig
