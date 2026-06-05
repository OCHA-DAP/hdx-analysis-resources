import csv
from unittest.mock import MagicMock, patch


def make_resource(
    name, fmt, url, resource_id="rid", hash_="", last_modified="", broken_link=False
):
    r = MagicMock()
    r.__getitem__ = lambda self, k: {
        "name": name,
        "id": resource_id,
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


def make_dataset(name, resources, dataset_id="did"):
    d = MagicMock()
    d.__getitem__ = lambda self, k: {"name": name, "id": dataset_id}[k]
    d.get_resources.return_value = resources
    return d


class TestResources:
    def test_get_resources_sorted(self, configuration):
        from hdx.analysis.resources.__main__ import get_resources

        datasets = [
            make_dataset(
                "zoo-dataset",
                [
                    make_resource(
                        "b-file",
                        "CSV",
                        "http://example.com/b",
                        resource_id="r-b",
                        hash_="abc",
                    ),
                    make_resource(
                        "a-file",
                        "XLSX",
                        "http://example.com/a",
                        resource_id="r-a",
                        hash_="xyz",
                    ),
                ],
                dataset_id="d-zoo",
            ),
            make_dataset(
                "alpha-dataset",
                [
                    make_resource(
                        "data",
                        "JSON",
                        "http://example.com/data",
                        resource_id="r-data",
                        hash_="111",
                    ),
                ],
                dataset_id="d-alpha",
            ),
        ]

        with patch(
            "hdx.analysis.resources.__main__.Dataset.get_all_datasets",
            return_value=datasets,
        ):
            rows = get_resources()

        assert rows[0]["dataset_name"] == "alpha-dataset"
        assert rows[0]["dataset_id"] == "d-alpha"
        assert rows[0]["resource_id"] == "r-data"
        assert rows[1]["dataset_name"] == "zoo-dataset"
        assert rows[1]["dataset_id"] == "d-zoo"
        assert rows[1]["resource_name"] == "b-file"
        assert rows[1]["resource_id"] == "r-b"
        assert rows[2]["resource_name"] == "a-file"
        assert rows[2]["resource_id"] == "r-a"

    def test_save_csv(self, tmp_path, configuration):
        from hdx.analysis.resources.__main__ import FIELDS, save_csv

        rows = [
            {
                "dataset_name": "ds",
                "dataset_id": "d-1",
                "resource_name": "r",
                "resource_id": "r-1",
                "format": "CSV",
                "hash": "abc",
                "size": "1024",
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
        assert written[0]["dataset_id"] == "d-1"
        assert written[0]["resource_id"] == "r-1"
        assert written[0]["hash"] == "abc"
