from dataclasses import dataclass
from typing import Optional


@dataclass
class ScraperSiteSelectorConfig:
    news_link_list: str
    datetime: str
    title: str
    body: str
    cloudflare: Optional[str]


@dataclass
class ScraperSiteConfig:
    name: str
    base_url: str
    url_list: dict[str, str]
    selectors: ScraperSiteSelectorConfig
    rate_limiter: int
