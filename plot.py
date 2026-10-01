# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib"]
# ///

import csv
from pathlib import Path

import matplotlib.pyplot as plt


HERE = Path(__file__).parent
DATA_FILE = HERE / "data" / "hko-daily-rainfall-2025.csv"
OUT = HERE / "out"
OUT_FILE = OUT / "rainfall-first-plot.png"


def rainfall_value(text):
    """Turn the rainfall text into a number."""
    if text == "Trace":
        return 0.0
    return float(text)


def load_rainfall():
    values = []

    with DATA_FILE.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.reader(file)

        # Skip the two title rows and the column headings.
        next(reader)
        next(reader)
        next(reader)

        for line_number, row in enumerate(reader, start=4):

            # Some lines in the published CSV are not daily data.
            if len(row) < 4:
                print(f"Skipping line {line_number}: {row}")
                continue

            rainfall = rainfall_value(row[3].strip())
            values.append(rainfall)

    return values


rainfall = load_rainfall()

print(f"{len(rainfall)} daily rainfall values")
print(f"Maximum rainfall: {max(rainfall)} mm")
print(f"Total rainfall: {sum(rainfall):.1f} mm")

days = range(1, len(rainfall) + 1)

plt.figure(figsize=(12, 5))
plt.plot(days, rainfall)

plt.title("Daily Rainfall at the Hong Kong Observatory — 2025")
plt.xlabel("Day of the year")
plt.ylabel("Daily rainfall (mm)")

OUT.mkdir(exist_ok=True)
plt.savefig(OUT_FILE, dpi=150, bbox_inches="tight")

print(f"saved {OUT_FILE}")
plt.show()
