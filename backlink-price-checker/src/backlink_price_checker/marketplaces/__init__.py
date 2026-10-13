"""Marketplace adapters. Each adapter turns one marketplace API into `Offer` objects."""

from .base import Marketplace, Offer, SiteResult, MarketplaceError
from .collaborator import Collaborator

#: Adapters that ship with the package, keyed by id.
REGISTRY: dict[str, type[Marketplace]] = {
    Collaborator.id: Collaborator,
}

__all__ = ["Marketplace", "Offer", "SiteResult", "MarketplaceError", "Collaborator", "REGISTRY"]
