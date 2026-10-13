"""Run lookups across marketplaces and combine the results."""

from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor

from .domains import Target
from .marketplaces import REGISTRY, Marketplace, MarketplaceError, SiteResult


def enabled_marketplaces(keys: dict[str, str] | None = None) -> list[Marketplace]:
    """Every marketplace that has an API key (from `keys` or the environment)."""
    keys = keys or {}
    out = []
    for mp_id, cls in REGISTRY.items():
        key = keys.get(mp_id) or os.environ.get(cls.env_key, "")
        if key:
            out.append(cls(key))
    return out


def check(targets: list[Target], marketplaces: list[Marketplace], workers: int = 4) -> list[SiteResult]:
    """Look every target up on every marketplace. Offers are merged and sorted by price."""

    def one(target: Target) -> SiteResult:
        merged = SiteResult(domain=target.domain)
        errors = []
        for mp in marketplaces:
            try:
                res = mp.lookup(target.domain)
            except MarketplaceError as exc:
                errors.append(str(exc))
                continue
            if res.found:
                merged.found = True
                merged.offers.extend(res.offers)
                merged.metrics = {**res.metrics, **merged.metrics}
        merged.offers.sort(key=lambda o: o.price)
        if errors and not merged.found:
            merged.error = "; ".join(errors)
        return merged

    with ThreadPoolExecutor(max_workers=max(1, min(workers, 8))) as pool:
        return list(pool.map(one, targets))
