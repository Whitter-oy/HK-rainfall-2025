# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib"]
# ///

import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt


HERE = Path(__file__).parent
DATA_FILE = HERE / "data" / "hko-daily-rainfall-2025.csv"
OUT = HERE / "out"
OUT_FILE = OUT / "hong-kong-rainfall-wheel-2025.png"


def rainfall_value(text):
    """Convert HKO rainfall text into millimetres."""
    text = text.strip()

    if text == "Trace":
        return 0.0

    return float(text)


def load_rainfall():
    """Read the committed HKO CSV and return daily rainfall values."""
    values = []

    with DATA_FILE.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.reader(file)

        # Skip the two title rows and the column headings.
        next(reader)
        next(reader)
        next(reader)

        for row in reader:
            if len(row) < 5:
                continue

            # Daily data rows begin with the year.
            if not row[0].strip().isdigit():
                continue

            values.append(rainfall_value(row[3]))

    return values


def day_angle(index, total):
    """Turn a day number into an angle around one full year."""
    return 2 * math.pi * index / total


def visual_length(rainfall):
    """Compress large rainfall values so smaller rainy days remain visible."""
    return math.sqrt(rainfall)


rainfall = load_rainfall()
total_days = len(rainfall)

angles = []
lengths = []

for index, value in enumerate(rainfall):
    angles.append(day_angle(index, total_days))
    lengths.append(visual_length(value))


fig, ax = plt.subplots(
    figsize=(9, 9),
    subplot_kw={"projection": "polar"}
)

ax.set_theta_zero_location("N")
ax.set_theta_direction(-1)

bar_width = 2 * math.pi / total_days

ax.bar(
    angles,
    lengths,
    width=bar_width,
    bottom=1.0
)

ax.set_title(
    "Hong Kong Rainfall Wheel — 2025\n"
    "Each stroke is one day; length represents daily rainfall",
    pad=30
)

ax.set_yticklabels([])
ax.set_xticklabels([])
ax.grid(False)

OUT.mkdir(exist_ok=True)
plt.savefig(OUT_FILE, dpi=180, bbox_inches="tight")

print(f"{total_days} daily rainfall values")
print(f"Maximum rainfall: {max(rainfall)} mm")
print(f"Total rainfall: {sum(rainfall):.1f} mm")
print(f"saved {OUT_FILE}")

plt.show()
