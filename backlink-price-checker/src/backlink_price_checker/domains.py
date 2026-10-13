"""Turn pasted URLs / domains into clean host names."""

from __future__ import annotations

import re
from dataclasses import dataclass

_HOST_RE = re.compile(
    r"^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+(?:[a-z]{2,63}|xn--[a-z0-9-]{2,59})$"
)


def normalize_domain(raw: str) -> str:
    """Return a bare host name ("www.Example.com/page" -> "example.com") or "" if invalid."""
    value = (raw or "").strip().lower()
    if not value or len(value) > 300:
        return ""
    value = re.sub(r"^[a-z][a-z0-9+.\-]*://", "", value)
    value = re.sub(r"^[^@/]*@", "", value)
    value = re.sub(r"[/?#].*$", "", value)
    value = re.sub(r":\d+$", "", value)
    value = value.rstrip(".")
    value = re.sub(r"^www\d*\.", "", value)
    if not value.isascii():
        try:
            value = value.encode("idna").decode("ascii")
        except UnicodeError:
            return ""
    if len(value) > 253 or not _HOST_RE.match(value):
        return ""
    return value


@dataclass
class Target:
    domain: str
    quoted_price: float | None = None


def parse_targets(text: str, limit: int = 500) -> tuple[list[Target], list[str]]:
    """Parse lines like "example.com" or "example.com 150" (a price you were quoted).

    Returns (targets, invalid_inputs). Duplicates are removed.
    """
    targets: list[Target] = []
    invalid: list[str] = []
    seen: set[str] = set()
    for line in re.split(r"[\r\n,;]+", text or ""):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        domain = normalize_domain(parts[0])
        if not domain:
            invalid.append(parts[0][:80])
            continue
        if domain in seen:
            continue
        quoted = None
        if len(parts) > 1:
            try:
                quoted = float(parts[1].replace("$", "").replace(",", ""))
            except ValueError:
                quoted = None
        seen.add(domain)
        targets.append(Target(domain, quoted))
        if len(targets) >= limit:
            break
    return targets, invalid
