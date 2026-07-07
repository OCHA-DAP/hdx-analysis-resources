import csv
import logging
from os.path import expanduser, join
from pathlib import Path

from hdx.data.dataset import Dataset
from hdx.facades.simple import facade
from hdx.utilities.easy_logging import setup_logging
from hdx.utilities.url import get_filename_extension_from_url

from ._version import __version__

setup_logging()
logger = logging.getLogger(__name__)

lookup = "hdx-analysis-resources"

OUTPUT_DIR = Path("output_data")
OUTPUT_CSV = OUTPUT_DIR / "resources.csv"

FIELDS = [
    "dataset_name",
    "resource_name",
    "format",
    "extension",
    "hash",
    "size",
    "last_modified",
    "broken_link",
    "url",
    "dataset_id",
    "resource_id",
]


def get_resources() -> list[dict]:
    rows = []
    for dataset in Dataset.get_all_datasets():
        dataset_id = dataset["id"]
        dataset_name = dataset["name"]
        for resource in dataset.get_resources():
            url = resource["url"]
            _, extension = get_filename_extension_from_url(url)
            extension = extension.lstrip(".")
            rows.append(
                {
                    "dataset_name": dataset_name,
                    "resource_name": resource["name"],
                    "format": resource.get_format(),
                    "extension": extension,
                    "hash": resource.get("hash", ""),
                    "size": resource.get("size", ""),
                    "last_modified": resource.get("last_modified", ""),
                    "broken_link": resource.get("broken_link", ""),
                    "url": url,
                    "dataset_id": dataset_id,
                    "resource_id": resource["id"],
                }
            )
    rows.sort(key=lambda r: r["dataset_name"])
    return rows


def save_csv(rows: list[dict], output_path: Path) -> None:
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    logger.info(f"Saved {len(rows)} resource rows to {output_path}")


def main() -> None:
    logger.info(f"##### {lookup} version {__version__} ####")
    rows = get_resources()
    OUTPUT_CSV.parent.mkdir(exist_ok=True)
    save_csv(rows, OUTPUT_CSV)


if __name__ == "__main__":
    facade(
        main,
        user_agent_config_yaml=join(expanduser("~"), ".useragents.yaml"),
        user_agent_lookup=lookup,
    )
