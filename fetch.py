# /// script
# requires-python = ">=3.10"
# dependencies = ["requests"]
# ///

from pathlib import Path

import requests


HERE = Path(__file__).parent
DATA = HERE / "data"


# 2025 daily rainfall at the Hong Kong Observatory
RAINFALL_URL = (
    "https://data.weather.gov.hk/weatherAPI/cis/csvfile/"
    "HKO/2025/daily_HKO_RF_2025.csv"
)

# Official Hong Kong 18-district boundaries
BOUNDARY_URL = (
    "https://www.had.gov.hk/psi/"
    "hong-kong-administrative-boundaries/"
    "hksar_18_district_boundary.json"
)


RAINFALL_FILE = DATA / "hko-daily-rainfall-2025.csv"
BOUNDARY_FILE = DATA / "hk-district-boundary.json"


def fetch_once(url, path):
    """Download a published raw file only once."""

    DATA.mkdir(exist_ok=True)

    if path.exists():
        print(f"{path.name} already exists — using the saved copy.")
        return path

    print(f"asking {url}")

    response = requests.get(
        url,
        headers={
            "User-Agent": "SD5913 data visualisation assignment"
        },
        timeout=30,
    )

    response.raise_for_status()

    # Keep the publisher's raw reply unchanged.
    path.write_bytes(response.content)

    print(f"saved {path}")

    return path


fetch_once(RAINFALL_URL, RAINFALL_FILE)
fetch_once(BOUNDARY_URL, BOUNDARY_FILE)
