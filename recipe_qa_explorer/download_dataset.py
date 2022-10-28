from __future__ import annotations

from pathlib import Path
import requests
import shutil
import os
import zipfile
from tqdm.auto import tqdm
import argparse


DATASET_JSON_URLS = [
    "https://vision.cs.hacettepe.edu.tr/files/recipeqa/train.json",
    "https://vision.cs.hacettepe.edu.tr/files/recipeqa/val.json",
    "https://vision.cs.hacettepe.edu.tr/files/recipeqa/test.json",
]
DATASET_IMAGES_URL = "https://vision.cs.hacettepe.edu.tr/files/recipeqa/images.zip"


# based on https://www.alpharithms.com/progress-bars-for-python-downloads-580122/
def download_file_with_progress(
    file_url: str,
    target_dir: Path,
) -> Path:
    """Download a file from a URL to a target directory."""
    with requests.get(file_url, stream=True) as r:
        # check header to get content length, in bytes
        total_length = int(r.headers.get("Content-Length") or "0")
        output_file = target_dir / f"{os.path.basename(r.url)}"

        # implement progress bar via tqdm
        with tqdm.wrapattr(r.raw, "read", total=total_length, desc="") as raw:

            # save the output to a file
            with open(target_dir / f"{os.path.basename(r.url)}", "wb") as output:
                shutil.copyfileobj(raw, output)
        return output_file


def download_dataset(target_dir: Path) -> None:
    """Download the dataset to a target directory."""
    # create target directory
    target_dir.mkdir(parents=True, exist_ok=True)

    for dataset_url in DATASET_JSON_URLS:
        download_file_with_progress(dataset_url, target_dir)
    images_path = download_file_with_progress(DATASET_IMAGES_URL, target_dir)
    with zipfile.ZipFile(images_path, "r") as zip_ref:
        zip_ref.extractall(target_dir)
    os.remove(images_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--target_dir",
        type=str,
        default="data",
        help="Target directory for the dataset",
    )
    args = parser.parse_args()
    download_dataset(Path(args.target_dir))
