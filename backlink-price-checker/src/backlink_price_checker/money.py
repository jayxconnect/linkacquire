"""Parse price strings such as "2 768.78 USD", "$1,200" or "1.200,50 EUR"."""

from __future__ import annotations

import re

_SYMBOLS = {"$": "USD", "€": "EUR", "£": "GBP"}


def parse_money(raw) -> tuple[float | None, str]:
    """Return (amount, currency). Amount is None when nothing numeric is found."""
    if raw is None or raw == "":
        return None, ""
    if isinstance(raw, (int, float)):
        return round(float(raw), 2), ""
    text = str(raw)
    currency = ""
    match = re.search(r"\b([A-Z]{3})\b", text)
    if match:
        currency = match.group(1)
    else:
        for symbol, code in _SYMBOLS.items():
            if symbol in text:
                currency = code
                break
    compact = re.sub(r"[\s   ]+", "", text)
    number = re.search(r"[0-9][0-9.,]*", compact)
    if not number:
        return None, currency
    n = number.group(0)
    if "," in n and "." in n:
        if n.rfind(",") > n.rfind("."):
            n = n.replace(".", "").replace(",", ".")
        else:
            n = n.replace(",", "")
    elif "," in n:
        n = n.replace(",", ".") if re.search(r",\d{1,2}$", n) else n.replace(",", "")
    n = n.rstrip(".")
    try:
        return round(float(n), 2), currency
    except ValueError:
        return None, currency
