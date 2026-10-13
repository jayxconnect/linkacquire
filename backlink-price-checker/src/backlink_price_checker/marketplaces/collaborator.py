"""Collaborator.pro adapter.

Public API docs: https://collaborator.pro/api/public/default/docs
Get your key in your Collaborator account. The site catalog endpoint may need
to be enabled for your account by Collaborator support.
"""

from __future__ import annotations

import urllib.parse

from ..domains import normalize_domain
from ..money import parse_money
from .base import Marketplace, Offer, SiteResult

API = "https://collaborator.pro/api/public/creator/list"


class Collaborator(Marketplace):
    id = "collaborator"
    name = "Collaborator"
    env_key = "COLLABORATOR_API_KEY"

    def lookup(self, domain: str) -> SiteResult:
        query = urllib.parse.urlencode({"_url": domain, "language": "en", "per-page": 20})
        data = self._get_json(f"{API}?{query}", {"X-Api-Key": self.api_key})
        return self.parse(domain, data)

    @classmethod
    def parse(cls, domain: str, data: dict) -> SiteResult:
        result = SiteResult(domain=domain)
        for item in data.get("items") or []:
            if not isinstance(item, dict):
                continue
            # The `_url` filter is not an exact match, so keep only this exact site.
            if normalize_domain(str(item.get("name", ""))) != domain:
                continue
            result.found = True
            if not result.metrics:
                result.metrics = {
                    key: item.get(src)
                    for key, src in (
                        ("country", "country"),
                        ("traffic", "traffic"),
                        ("da", "daMoz"),
                        ("tf", "tf"),
                        ("cf", "cf"),
                        ("categories", "categories"),
                    )
                    if item.get(src) not in (None, "")
                }
            for price in item.get("prices") or []:
                amount, currency = parse_money(price.get("pricePublication"))
                if not amount:
                    continue
                writing, _ = parse_money(price.get("priceSpelling"))
                sensitive, _ = parse_money(price.get("priceContrCategories"))
                niches = price.get("contrCategories") or ""
                if isinstance(niches, list):
                    niches = ", ".join(str(n) for n in niches)
                result.offers.append(
                    Offer(
                        marketplace=cls.name,
                        domain=domain,
                        format=str(price.get("name") or "Article"),
                        price=amount,
                        currency=currency or "USD",
                        writing_price=writing,
                        sensitive_price=sensitive,
                        sensitive_niches=str(niches),
                        link_type=str(price.get("linkType") or ""),
                        links=price.get("numberOfLinks"),
                        url=str(item.get("url") or ""),
                    )
                )
        return result
