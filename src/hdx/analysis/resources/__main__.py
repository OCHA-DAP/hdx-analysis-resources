import csv
import logging
from os.path import expanduser, join

from hdx.data.dataset import Dataset
from hdx.facades.simple import facade
from hdx.utilities.easy_logging import setup_logging

from ._version import __version__

setup_logging()
logger = logging.getLogger(__name__)

lookup = "hdx-analysis-resources"

FIELDS = [
    "dataset_name",
    "resource_name",
    "format",
    "hash",
    "url",
    "last_modified",
    "broken_link",
]


def get_resources() -> list[dict]:
    rows = []
    for dataset in Dataset.get_all_datasets():
        dataset_name = dataset["name"]
        for resource in dataset.get_resources():
            rows.append(
                {
                    "dataset_name": dataset_name,
                    "resource_name": resource["name"],
                    "format": resource.get_format(),
                    "hash": resource.get("hash", ""),
                    "url": resource["url"],
                    "last_modified": resource.get("last_modified", ""),
                    "broken_link": resource.get("broken_link", ""),
                }
            )
    rows.sort(key=lambda r: (r["dataset_name"], r["resource_name"], r["format"], r["hash"]))
    return rows


def save_csv(rows: list[dict], output_path: str) -> None:
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    logger.info(f"Saved {len(rows)} resource rows to {output_path}")


def main() -> None:
    logger.info(f"##### {lookup} version {__version__} ####")
    rows = get_resources()
    save_csv(rows, "resources.csv")


if __name__ == "__main__":
    facade(
        main,
        user_agent_config_yaml=join(expanduser("~"), ".useragents.yaml"),
        user_agent_lookup=lookup,
    )
