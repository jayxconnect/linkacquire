# Backlink Price Checker (open source)

**An open-source backlink price checker for the command line.** Paste a list of websites and compare guest post and link insertion prices across link marketplaces, using your own marketplace API keys.

[![tests](https://github.com/jayxconnect/backlink-price-checker/actions/workflows/tests.yml/badge.svg)](https://github.com/jayxconnect/backlink-price-checker/actions/workflows/tests.yml)
![License: MIT](https://img.shields.io/badge/license-MIT-orange)
![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)

> Don't have marketplace API keys? Use the free hosted version at **[linkacquire.com](https://linkacquire.com)**. Nothing to install and no keys needed.

---

## Why

"How much does this backlink cost?" usually has more than one answer. The same website is often listed at different prices on different guest post marketplaces. This tool asks each marketplace you have an API key for and puts the prices side by side, cheapest first.

- **Bulk guest post price checker:** check one domain or hundreds from a file.
- **Every offer:** guest posts and link insertions (niche edits), with content writing costs and sensitive-niche surcharges (casino, crypto, CBD…).
- **Site metrics:** Domain Authority, Trust Flow, Citation Flow, traffic and country, where the marketplace provides them.
- **Quote comparison:** add the price a publisher quoted you and see how much you'd save.
- **Table, CSV or JSON output:** pipe it into a spreadsheet or your own scripts.
- **Zero dependencies:** Python standard library only. Your API keys stay on your machine.

## Install

```bash
pip install git+https://github.com/jayxconnect/backlink-price-checker.git
```

Or clone and run without installing:

```bash
git clone https://github.com/jayxconnect/backlink-price-checker.git
cd backlink-price-checker
PYTHONPATH=src python -m backlink_price_checker --help
```

## Add your marketplace API key

Keys are read from environment variables:

| Marketplace | Environment variable | Where to get it |
|---|---|---|
| [Collaborator](https://collaborator.pro) | `COLLABORATOR_API_KEY` | Your Collaborator account → API ([docs](https://collaborator.pro/api/public/default/docs)) |

```bash
export COLLABORATOR_API_KEY="your-key-here"
```

More marketplaces are welcome. See [Adding a marketplace](#adding-a-marketplace).

## Usage

```bash
# One or more domains (URLs are fine too)
bpc example.com https://www.another-blog.net/post

# Add the price you were quoted with a colon
bpc example.com:250

# From a file: one domain per line, optional quoted price after a space
bpc -f examples/domains.txt

# Every offer instead of only the cheapest, as CSV
bpc -f domains.txt --all-offers --format csv > prices.csv

# JSON for scripts
bpc example.com --format json
```

Example output:

```
Domain            Best price  Quoted  Save  Marketplace   Format          Link      DA  TF  Traffic  Country
----------------  ----------  ------  ----  ------------  --------------  --------  --  --  -------  -------------
example-news.com  $110        $250    $140  Collaborator  Link insertion  dofollow  52  31  41.2 k   United States
other.net         not listed  -       -     -             -               -         -   -   -        -
```

Prices are the marketplace's listed prices at the time of the request and can change. Always confirm the total on the marketplace before you buy.

## Adding a marketplace

Each marketplace is one small adapter in `src/backlink_price_checker/marketplaces/`:

1. Create a class that extends `Marketplace`, with `id`, `name` and `env_key`.
2. Implement `lookup(domain)` so it returns a `SiteResult` with `Offer` objects.
3. Register it in `marketplaces/__init__.py` and add a test with a saved sample response.

Only use official, documented APIs, and respect each marketplace's terms and rate limits. Please don't submit scrapers.

## FAQ

**Is this the same as linkacquire.com?**
No. This is a separate, minimal command-line tool for people who already have marketplace API keys. [LinkAcquire](https://linkacquire.com) is a free hosted backlink price checker that needs no keys or installation.

**How much does a backlink cost?**
It varies a lot: from under $100 for a guest post on a small niche blog to thousands on major news sites. Authority, real traffic, niche, link type, content writing and sensitive-niche fees all change the price. That's why comparing marketplaces is worth it.

**Is it safe to use my API key?**
The key is only read from your environment and sent straight to that marketplace's API over HTTPS. Nothing is sent anywhere else.

## Contributing

Issues and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md). Run the tests with:

```bash
python -m unittest discover -s tests -v
```

## License

[MIT](LICENSE). Not affiliated with or endorsed by any marketplace listed here. Marketplace names are trademarks of their owners.
