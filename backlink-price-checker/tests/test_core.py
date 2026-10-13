import io
import json
import unittest
from contextlib import redirect_stdout
from unittest import mock

from backlink_price_checker import cli
from backlink_price_checker.domains import normalize_domain, parse_targets
from backlink_price_checker.marketplaces import Collaborator
from backlink_price_checker.money import parse_money

SAMPLE = {
    "items": [
        {
            "name": "example-news.com",
            "url": "https://collaborator.pro/creator/article/view?id=1",
            "country": "United States",
            "traffic": "41.2 k",
            "daMoz": 52,
            "tf": 31,
            "prices": [
                {"name": "Article", "pricePublication": "1 245.00 USD", "priceSpelling": "25.00 USD", "linkType": "dofollow", "numberOfLinks": 2},
                {"name": "Link insertion", "pricePublication": "110.00 USD", "linkType": "dofollow"},
            ],
        },
        {"name": "blog.example-news.com", "prices": [{"name": "Article", "pricePublication": "5 USD"}]},
    ]
}


class DomainTests(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(normalize_domain("https://www.Example.com/post?x=1"), "example.com")
        self.assertEqual(normalize_domain("user@shop.example.co.uk:8080"), "shop.example.co.uk")
        self.assertEqual(normalize_domain("not a domain"), "")
        self.assertEqual(normalize_domain("localhost"), "")

    def test_parse_targets(self):
        targets, invalid = parse_targets("example.com 150\nEXAMPLE.com\n# comment\nbad\nother.net")
        self.assertEqual([t.domain for t in targets], ["example.com", "other.net"])
        self.assertEqual(targets[0].quoted_price, 150.0)
        self.assertEqual(invalid, ["bad"])


class MoneyTests(unittest.TestCase):
    def test_formats(self):
        self.assertEqual(parse_money("2 768.78 USD"), (2768.78, "USD"))
        self.assertEqual(parse_money("$1,200"), (1200.0, "USD"))
        self.assertEqual(parse_money("1.200,50 EUR"), (1200.5, "EUR"))
        self.assertEqual(parse_money(None), (None, ""))


class CollaboratorTests(unittest.TestCase):
    def test_exact_match_and_offers(self):
        res = Collaborator.parse("example-news.com", SAMPLE)
        self.assertTrue(res.found)
        self.assertEqual(len(res.offers), 2)
        self.assertEqual(res.best.price, 110.0)
        self.assertEqual(res.metrics["da"], 52)

    def test_not_found(self):
        res = Collaborator.parse("nothing.com", SAMPLE)
        self.assertFalse(res.found)
        self.assertIsNone(res.best)


class CliTests(unittest.TestCase):
    def test_json_output(self):
        with mock.patch.dict("os.environ", {"COLLABORATOR_API_KEY": "test"}), mock.patch.object(
            Collaborator, "_get_json", return_value=SAMPLE
        ):
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = cli.main(["example-news.com:150", "--format", "json"])
        self.assertEqual(code, 0)
        data = json.loads(buf.getvalue())
        self.assertEqual(data[0]["quoted_price"], 150.0)
        self.assertEqual(data[0]["offers"][0]["price"], 110.0)

    def test_table_output_not_listed(self):
        with mock.patch.dict("os.environ", {"COLLABORATOR_API_KEY": "test"}), mock.patch.object(
            Collaborator, "_get_json", return_value={"items": []}
        ):
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.main(["nothing.com"])
        self.assertIn("not listed", buf.getvalue())

    def test_no_key(self):
        with mock.patch.dict("os.environ", {}, clear=True):
            self.assertEqual(cli.main(["example.com"]), 2)


if __name__ == "__main__":
    unittest.main()
