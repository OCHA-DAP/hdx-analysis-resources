import csv
from unittest.mock import MagicMock, patch


def make_resource(name, fmt, url, hash_="", last_modified="", broken_link=False):
    r = MagicMock()
    r.__getitem__ = lambda self, k: {
        "name": name,
        "url": url,
        "last_modified": last_modified,
        "broken_link": broken_link,
    }[k]
    r.get = lambda k, default="": {
        "hash": hash_,
        "last_modified": last_modified,
        "broken_link": broken_link,
    }.get(k, default)
    r.get_format.return_value = fmt
    return r


def make_dataset(name, resources):
    d = MagicMock()
    d.__getitem__ = lambda self, k: name if k == "name" else None
    d.get_resources.return_value = resources
    return d


class TestResources:
    def test_get_resources_sorted(self, configuration):
        from hdx.analysis.resources.__main__ import get_resources

        datasets = [
            make_dataset(
                "zoo-dataset",
                [
                    make_resource("b-file", "CSV", "http://example.com/b", hash_="abc"),
                    make_resource(
                        "a-file", "XLSX", "http://example.com/a", hash_="xyz"
                    ),
                ],
            ),
            make_dataset(
                "alpha-dataset",
                [
                    make_resource(
                        "data", "JSON", "http://example.com/data", hash_="111"
                    ),
                ],
            ),
        ]

        with patch(
            "hdx.analysis.resources.__main__.Dataset.get_all_datasets",
            return_value=datasets,
        ):
            rows = get_resources()

        assert rows[0]["dataset_name"] == "alpha-dataset"
        assert rows[1]["dataset_name"] == "zoo-dataset"
        assert rows[1]["resource_name"] == "a-file"
        assert rows[2]["resource_name"] == "b-file"

    def test_save_csv(self, tmp_path, configuration):
        from hdx.analysis.resources.__main__ import FIELDS, save_csv

        rows = [
            {
                "dataset_name": "ds",
                "resource_name": "r",
                "format": "CSV",
                "hash": "abc",
                "url": "http://x.com",
                "last_modified": "2024-01-01",
                "broken_link": False,
            },
        ]
        out = str(tmp_path / "out.csv")
        save_csv(rows, out)

        with open(out, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            assert reader.fieldnames == FIELDS
            written = list(reader)

        assert len(written) == 1
        assert written[0]["dataset_name"] == "ds"
        assert written[0]["hash"] == "abc"
