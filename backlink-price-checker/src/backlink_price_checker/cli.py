"""Command line interface: `bpc example.com other-site.net` or `bpc -f domains.txt`."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import asdict

from . import __version__
from .checker import check, enabled_marketplaces
from .domains import parse_targets
from .marketplaces import REGISTRY

HOSTED = "https://linkacquire.com"


def _money(value, currency="USD"):
    if value is None:
        return "-"
    symbol = {"USD": "$", "EUR": "€", "GBP": "£"}.get(currency, currency + " ")
    return f"{symbol}{value:,.0f}" if float(value).is_integer() else f"{symbol}{value:,.2f}"


def _table(rows, quoted):
    headers = ["Domain", "Best price", "Marketplace", "Format", "Link", "DA", "TF", "Traffic", "Country"]
    if quoted:
        headers[2:2] = ["Quoted", "Save"]
    body = []
    for res, target in rows:
        best = res.best
        m = res.metrics
        line = [
            res.domain,
            _money(best.price, best.currency) if best else ("error" if res.error else "not listed"),
            best.marketplace if best else "-",
            best.format if best else "-",
            (best.link_type or "-") if best else "-",
            str(m.get("da", "-")),
            str(m.get("tf", "-")),
            str(m.get("traffic", "-")),
            str(m.get("country", "-")),
        ]
        if quoted:
            save = (target.quoted_price - best.price) if (best and target.quoted_price) else None
            line[2:2] = [_money(target.quoted_price), _money(save) if save and save > 0 else "-"]
        body.append(line)
    widths = [max(len(str(r[i])) for r in [headers] + body) for i in range(len(headers))]
    fmt = "  ".join("{:<%d}" % w for w in widths)
    out = [fmt.format(*headers), fmt.format(*["-" * w for w in widths])]
    out += [fmt.format(*r) for r in body]
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="bpc",
        description="Open-source backlink price checker: compare guest post prices across marketplaces with your own API keys.",
        epilog=f"Marketplaces: {', '.join(f'{c.name} (${c.env_key})' for c in REGISTRY.values())}. "
        f"No API keys? Use the free hosted version at {HOSTED}",
    )
    parser.add_argument("domains", nargs="*", help="domains or URLs; add a quoted price after a domain as 'site.com:150'")
    parser.add_argument("-f", "--file", help="file with one domain per line (optionally followed by a quoted price)")
    parser.add_argument("--format", choices=["table", "csv", "json"], default="table", help="output format (default: table)")
    parser.add_argument("--all-offers", action="store_true", help="list every offer, not just the cheapest")
    parser.add_argument("--workers", type=int, default=4, help="parallel lookups (1-8, default 4)")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args(argv)

    text = "\n".join(d.replace(":", " ", 1) if d.count(":") == 1 and "//" not in d else d for d in args.domains)
    if args.file:
        with open(args.file, encoding="utf-8") as fh:
            text += "\n" + fh.read()
    if not args.domains and not args.file and not sys.stdin.isatty():
        text += "\n" + sys.stdin.read()

    targets, invalid = parse_targets(text)
    for bad in invalid:
        print(f"skipped (not a domain): {bad}", file=sys.stderr)
    if not targets:
        parser.error("give at least one domain, a --file, or pipe domains on stdin")

    marketplaces = enabled_marketplaces()
    if not marketplaces:
        keys = ", ".join(c.env_key for c in REGISTRY.values())
        print(f"No marketplace API key found. Set one of: {keys}\nOr use the free hosted checker: {HOSTED}", file=sys.stderr)
        return 2

    results = check(targets, marketplaces, workers=args.workers)
    pairs = list(zip(results, targets))

    if args.format == "json":
        print(json.dumps([{**asdict(r), "quoted_price": t.quoted_price} for r, t in pairs], indent=2))
    elif args.format == "csv":
        writer = csv.writer(sys.stdout)
        writer.writerow(["domain", "marketplace", "format", "price", "currency", "writing_price", "sensitive_price", "link_type", "links", "quoted_price", "url"])
        for res, target in pairs:
            offers = res.offers if args.all_offers else ([res.best] if res.best else [])
            if not offers:
                writer.writerow([res.domain, "", "", "", "", "", "", "", "", target.quoted_price or "", ""])
            for o in offers:
                writer.writerow([res.domain, o.marketplace, o.format, o.price, o.currency, o.writing_price or "", o.sensitive_price or "", o.link_type, o.links or "", target.quoted_price or "", o.url])
    else:
        quoted = any(t.quoted_price for t in targets)
        print(_table(pairs, quoted))
        if args.all_offers:
            for res in results:
                for o in res.offers[1:]:
                    print(f"  {res.domain}: {o.marketplace} {o.format} {_money(o.price, o.currency)}")
        errors = [r for r in results if r.error]
        for r in errors:
            print(f"! {r.domain}: {r.error}", file=sys.stderr)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
