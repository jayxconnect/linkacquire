"""Common types for marketplace adapters."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass, field

USER_AGENT = "backlink-price-checker/0.1 (+https://github.com/jayxconnect/backlink-price-checker)"


class MarketplaceError(Exception):
    """Raised when a marketplace API call fails."""


@dataclass
class Offer:
    marketplace: str
    domain: str
    format: str
    price: float
    currency: str = "USD"
    writing_price: float | None = None
    sensitive_price: float | None = None
    sensitive_niches: str = ""
    link_type: str = ""
    links: int | None = None
    url: str = ""


@dataclass
class SiteResult:
    domain: str
    found: bool = False
    offers: list[Offer] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)
    error: str = ""

    @property
    def best(self) -> Offer | None:
        return min(self.offers, key=lambda o: o.price) if self.offers else None


class Marketplace:
    """Base class. Subclasses set `id`, `name`, `env_key` and implement `lookup()`."""

    id = ""
    name = ""
    env_key = ""  # environment variable that holds the API key
    timeout = 20

    def __init__(self, api_key: str):
        if not api_key:
            raise MarketplaceError(f"{self.name}: missing API key (set {self.env_key})")
        self.api_key = api_key

    def lookup(self, domain: str) -> SiteResult:  # pragma: no cover - implemented by subclasses
        raise NotImplementedError

    # Small helper so adapters don't need third-party HTTP libraries.
    def _get_json(self, url: str, headers: dict) -> dict:
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json", **headers})
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:  # noqa: S310 (https only)
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code in (401, 403):
                raise MarketplaceError(f"{self.name}: API key rejected (HTTP {exc.code})") from exc
            if exc.code == 429:
                raise MarketplaceError(f"{self.name}: rate limited, try again later") from exc
            raise MarketplaceError(f"{self.name}: HTTP {exc.code}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise MarketplaceError(f"{self.name}: network error ({exc})") from exc
        except json.JSONDecodeError as exc:
            raise MarketplaceError(f"{self.name}: unexpected response") from exc
