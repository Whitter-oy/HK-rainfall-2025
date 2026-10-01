# /// script
# requires-python = ">=3.10"
# dependencies = ["requests"]
# ///

from pathlib import Path
import requests

URL = "https://data.weather.gov.hk/weatherAPI/cis/csvfile/HKO/2025/daily_HKO_RF_2025.csv"

HERE = Path(__file__).parent
DATA = HERE / "data"
FILE = DATA / "hko-daily-rainfall-2025.csv"


def fetch_once():
    DATA.mkdir(exist_ok=True)

    if FILE.exists():
        print(f"{FILE.name} already exists — using the saved copy.")
        return FILE

    print(f"asking {URL}")

    response = requests.get(
        URL,
        headers={"User-Agent": "SD5913 data visualisation assignment"},
        timeout=30,
    )
    response.raise_for_status()

    # Save the raw reply exactly as it arrived.
    FILE.write_bytes(response.content)

    print(f"saved {FILE}")
    return FILE


fetch_once()
