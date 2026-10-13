# Contributing

Thanks for helping make backlink prices easier to compare.

## Ground rules

- Use only **official, documented marketplace APIs**. No scraping, no logged-in browser automation.
- Never commit API keys. Keys come from environment variables only.
- Keep the package dependency-free (Python standard library).

## Development

```bash
git clone https://github.com/jayxconnect/backlink-price-checker.git
cd backlink-price-checker
python -m venv .venv && source .venv/bin/activate
pip install -e .
python -m unittest discover -s tests -v
```

## Adding a marketplace

1. Add `src/backlink_price_checker/marketplaces/<name>.py` with a class extending `Marketplace`.
2. Register it in `marketplaces/__init__.py`.
3. Add a test that feeds a saved, anonymised sample response to your parser.
4. Add the marketplace and its environment variable to the table in `README.md`.

## Reporting bugs

Open an issue with the command you ran, the output (remove any keys) and your Python version.
