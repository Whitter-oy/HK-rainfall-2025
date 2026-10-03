# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib"]
# ///

import csv
import datetime as dt
import json
import math
from pathlib import Path

import matplotlib.pyplot as plt


HERE = Path(__file__).parent
DATA_FILE = HERE / "data" / "hko-daily-rainfall-2025.csv"

OUT = HERE / "out"
OUT_FILE = OUT / "hong-kong-rainfall-2025.png"

SITE = HERE / "site"
SITE_FILE = SITE / "index.html"


def rainfall_value(text):
    """Convert HKO rainfall text into millimetres."""
    text = text.strip()

    # HKO uses "Trace" for less than 0.05 mm.
    if text == "Trace":
        return 0.0

    return float(text)


def load_rainfall():
    """Read daily rainfall from the committed HKO CSV."""
    records = []

    with DATA_FILE.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.reader(file)

        # Two title rows + one heading row.
        next(reader)
        next(reader)
        next(reader)

        for row in reader:
            if len(row) < 5:
                continue

            if not row[0].strip().isdigit():
                continue

            year = int(row[0])
            month = int(row[1])
            day = int(row[2])

            records.append(
                {
                    "date": dt.date(year, month, day).isoformat(),
                    "month": month,
                    "day": day,
                    "rainfall": rainfall_value(row[3]),
                }
            )

    return records


def visual_length(value):
    """Square-root scale keeps smaller rain events visible."""
    return math.sqrt(value)


def make_static_picture(records):
    """Create an annual still for README and assignment checking."""
    total = len(records)
    angles = []
    lengths = []

    for index, record in enumerate(records):
        angle = 2 * math.pi * index / total
        angles.append(angle)
        lengths.append(visual_length(record["rainfall"]))

    fig, ax = plt.subplots(
        figsize=(10, 10),
        subplot_kw={"projection": "polar"},
        facecolor="#f1eddd",
    )

    ax.set_facecolor("#f1eddd")
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)

    baseline = 2

    # Full year: one faint mark for every day.
    for angle in angles:
        ax.plot(
            [angle, angle],
            [baseline, baseline + 0.35],
            color="#b7b09a",
            linewidth=0.45,
            alpha=0.45,
        )

    # Rainfall marks.
    for angle, length in zip(angles, lengths):
        if length > 0:
            ax.plot(
                [angle, angle],
                [baseline, baseline + length],
                color="#287da1",
                linewidth=1.5,
                alpha=0.8,
            )

    month_names = [
        "JAN", "FEB", "MAR", "APR", "MAY", "JUN",
        "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"
    ]

    starts = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]

    radius = baseline + max(lengths) + 2.3

    for month, start in zip(month_names, starts):
        angle = 2 * math.pi * start / total
        ax.text(
            angle,
            radius,
            month,
            ha="center",
            va="center",
            fontsize=9,
            color="#776d50",
        )

    max_index = max(
        range(total),
        key=lambda i: records[i]["rainfall"]
    )

    max_record = records[max_index]

    ax.scatter(
        [angles[max_index]],
        [baseline + lengths[max_index]],
        s=35,
        color="#a77b2b",
        zorder=10,
    )

    ax.set_title(
        "HONG KONG RAINFALL ATLAS · 2025\n"
        "365 days of rainfall at the Hong Kong Observatory",
        fontsize=17,
        pad=38,
        color="#22221d",
    )

    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.grid(False)
    ax.spines["polar"].set_visible(False)

    OUT.mkdir(exist_ok=True)

    plt.savefig(
        OUT_FILE,
        dpi=200,
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
    )

    plt.close(fig)

    print(f"saved {OUT_FILE}")
    print(
        f"wettest day: {max_record['date']} "
        f"({max_record['rainfall']} mm)"
    )


def make_web_page(records):
    """Build a self-contained interactive rainfall website."""
    data_json = json.dumps(records)

    html = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<title>Hong Kong Rainfall Atlas · 2025</title>

<style>
:root {
    --paper: #ece8d6;
    --ink: #171711;
    --muted: #77715f;
    --line: #c7c0aa;
    --blue: #287da1;
    --blue-soft: #9ec9d8;
    --gold: #a77b2b;
}

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: var(--paper);
    color: var(--ink);
    font-family: Arial, Helvetica, sans-serif;
}

.page {
    width: min(1380px, calc(100% - 48px));
    margin: 0 auto;
    padding: 42px 0 64px;
}

header {
    display: grid;
    grid-template-columns: 1.1fr 0.9fr;
    gap: 56px;
    align-items: start;
    padding-bottom: 34px;
    border-bottom: 1px solid var(--line);
}

.kicker {
    font-size: 12px;
    letter-spacing: .18em;
    text-transform: uppercase;
    color: var(--gold);
    margin-bottom: 14px;
}

h1 {
    margin: 0;
    font-family: Georgia, "Times New Roman", serif;
    font-size: clamp(44px, 7vw, 88px);
    line-height: .91;
    font-weight: normal;
    letter-spacing: -.035em;
}

.intro {
    max-width: 520px;
    margin-top: 5px;
    font-family: Georgia, "Times New Roman", serif;
    font-size: 18px;
    line-height: 1.55;
}

.meta {
    margin-top: 28px;
    font-size: 11px;
    line-height: 1.7;
    letter-spacing: .08em;
    text-transform: uppercase;
    color: var(--muted);
}

.months {
    display: grid;
    grid-template-columns: repeat(12, 1fr);
    border-bottom: 1px solid var(--line);
}

.month-button {
    appearance: none;
    border: 0;
    border-right: 1px solid var(--line);
    background: transparent;
    padding: 15px 4px 13px;
    cursor: pointer;
    font-size: 11px;
    letter-spacing: .08em;
    color: var(--muted);
}

.month-button:last-child {
    border-right: 0;
}

.month-button:hover,
.month-button:focus-visible {
    background: rgba(255,255,255,.22);
}

.month-button.active {
    color: var(--ink);
    background: var(--gold);
}

.visual-layout {
    display: grid;
    grid-template-columns: minmax(0, 1.45fr) minmax(260px, .55fr);
    gap: 46px;
    padding-top: 34px;
    align-items: center;
}

.chart-wrap {
    position: relative;
    min-width: 0;
}

svg {
    display: block;
    width: 100%;
    height: auto;
    overflow: visible;
}

.guide {
    fill: none;
    stroke: var(--line);
    stroke-width: 1;
}

.day-line {
    stroke: var(--blue);
    stroke-linecap: round;
    cursor: pointer;
    transition: opacity .15s, stroke-width .15s;
}

.day-line:hover {
    stroke-width: 5 !important;
    opacity: 1 !important;
}

.zero-line {
    stroke: var(--line);
    opacity: .32;
}

.center-label {
    text-anchor: middle;
}

.month-name {
    font-family: Georgia, "Times New Roman", serif;
    font-size: 33px;
}

.month-total {
    font-size: 14px;
    fill: var(--muted);
    letter-spacing: .08em;
}

.guide-label {
    font-size: 10px;
    fill: var(--muted);
}

.panel {
    border-top: 1px solid var(--ink);
    padding-top: 17px;
}

.panel-title {
    font-family: Georgia, "Times New Roman", serif;
    font-size: 28px;
    margin: 0 0 28px;
    font-weight: normal;
}

.metric {
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 20px;
    padding: 15px 0;
    border-top: 1px solid var(--line);
}

.metric-label {
    color: var(--muted);
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: .11em;
}

.metric-value {
    font-family: Georgia, "Times New Roman", serif;
    font-size: 22px;
    text-align: right;
}

.detail {
    margin-top: 32px;
    min-height: 90px;
    padding: 16px 0;
    border-top: 1px solid var(--ink);
    border-bottom: 1px solid var(--line);
}

.detail-label {
    color: var(--muted);
    font-size: 10px;
    letter-spacing: .12em;
    text-transform: uppercase;
}

.detail-value {
    margin-top: 8px;
    font-family: Georgia, "Times New Roman", serif;
    font-size: 22px;
}

.year {
    margin-top: 54px;
    padding-top: 20px;
    border-top: 1px solid var(--ink);
}

.year-head {
    display: flex;
    justify-content: space-between;
    gap: 24px;
    align-items: baseline;
}

.year-title {
    font-family: Georgia, "Times New Roman", serif;
    font-size: 26px;
    font-weight: normal;
    margin: 0;
}

.year-note {
    color: var(--muted);
    font-size: 11px;
    letter-spacing: .08em;
}

.month-bars {
    height: 170px;
    margin-top: 26px;
    display: grid;
    grid-template-columns: repeat(12, 1fr);
    gap: 9px;
    align-items: end;
}

.month-bar-wrap {
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: end;
    align-items: stretch;
}

.month-bar {
    min-height: 2px;
    background: var(--blue-soft);
    border-top: 2px solid var(--blue);
}

.month-bar.selected {
    background: var(--gold);
    border-top-color: var(--ink);
}

.month-bar-label {
    margin-top: 8px;
    text-align: center;
    font-size: 9px;
    color: var(--muted);
}

footer {
    margin-top: 50px;
    padding-top: 18px;
    border-top: 1px solid var(--line);
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 40px;
    font-size: 11px;
    line-height: 1.55;
    color: var(--muted);
}

@media (max-width: 850px) {
    .page {
        width: min(100% - 28px, 720px);
    }

    header,
    .visual-layout,
    footer {
        grid-template-columns: 1fr;
    }

    .months {
        grid-template-columns: repeat(6, 1fr);
    }

    .month-button:nth-child(6) {
        border-right: 0;
    }

    .visual-layout {
        gap: 20px;
    }
}
</style>
</head>

<body>

<div class="page">

<header>
    <div>
        <div class="kicker">Climate study · Hong Kong · 2025</div>
        <h1>Rainfall<br>Atlas</h1>
    </div>

    <div>
        <div class="intro">
            A year of rain recorded at the Hong Kong Observatory.
            Select a month to reveal the rhythm, intensity and extremes
            of its daily rainfall.
        </div>

        <div class="meta">
            365 DAILY RECORDS<br>
            DAILY TOTAL RAINFALL · MILLIMETRES<br>
            SOURCE · HONG KONG OBSERVATORY
        </div>
    </div>
</header>

<nav class="months" id="months"></nav>

<section class="visual-layout">

    <div class="chart-wrap">
        <svg
            id="chart"
            viewBox="0 0 720 720"
            role="img"
            aria-label="Daily rainfall radial chart"
        ></svg>
    </div>

    <aside class="panel">

        <h2 class="panel-title" id="panelMonth">September</h2>

        <div class="metric">
            <div class="metric-label">Total rainfall</div>
            <div class="metric-value" id="totalRain">—</div>
        </div>

        <div class="metric">
            <div class="metric-label">Rainy days</div>
            <div class="metric-value" id="rainDays">—</div>
        </div>

        <div class="metric">
            <div class="metric-label">Wettest day</div>
            <div class="metric-value" id="wettest">—</div>
        </div>

        <div class="detail">
            <div class="detail-label">Selected day</div>
            <div class="detail-value" id="detail">
                Hover over a rainfall stroke
            </div>
        </div>

    </aside>

</section>

<section class="year">

    <div class="year-head">
        <h2 class="year-title">2025 annual overview</h2>

        <div class="year-note">
            Monthly totals · same source
        </div>
    </div>

    <div class="month-bars" id="monthBars"></div>

</section>

<footer>

    <div>
        <strong>Visual method</strong><br>
        Each radial stroke represents one day.
        Angle represents the day within the selected month.
        Stroke length uses a square-root scale so smaller rainfall events
        remain visible while extreme rainfall still dominates.
    </div>

    <div>
        <strong>Data note</strong><br>
        “Trace” rainfall values published by HKO mean less than 0.05 mm
        and are treated as zero in this visualisation.
        Exact recorded values remain in the committed raw CSV.
    </div>

</footer>

</div>

<script>
const DATA = __DATA__;

const MONTHS = [
    "January","February","March","April","May","June",
    "July","August","September","October","November","December"
];

const SHORT = [
    "JAN","FEB","MAR","APR","MAY","JUN",
    "JUL","AUG","SEP","OCT","NOV","DEC"
];

let selectedMonth = 9;

const monthNav = document.getElementById("months");
const chart = document.getElementById("chart");

const totalRain = document.getElementById("totalRain");
const rainDays = document.getElementById("rainDays");
const wettest = document.getElementById("wettest");
const detail = document.getElementById("detail");
const panelMonth = document.getElementById("panelMonth");
const monthBars = document.getElementById("monthBars");

const SVG_NS = "http://www.w3.org/2000/svg";

const cx = 360;
const cy = 360;
const innerRadius = 118;
const maxLength = 215;

const globalMax = Math.max(...DATA.map(d => d.rainfall));

function svgElement(name, attrs = {}) {
    const el = document.createElementNS(SVG_NS, name);

    Object.entries(attrs).forEach(([key, value]) => {
        el.setAttribute(key, value);
    });

    return el;
}

function radialPoint(angle, radius) {
    return [
        cx + Math.sin(angle) * radius,
        cy - Math.cos(angle) * radius
    ];
}

function monthData(month) {
    return DATA.filter(d => d.month === month);
}

function rainfallLength(value) {
    if (value <= 0) return 0;

    return (
        Math.sqrt(value) /
        Math.sqrt(globalMax)
    ) * maxLength;
}

function renderNavigation() {
    monthNav.innerHTML = "";

    MONTHS.forEach((month, index) => {
        const button = document.createElement("button");

        button.className =
            "month-button" +
            (index + 1 === selectedMonth ? " active" : "");

        button.textContent = SHORT[index];

        button.addEventListener("click", () => {
            selectedMonth = index + 1;
            render();
        });

        monthNav.appendChild(button);
    });
}

function renderChart() {
    chart.innerHTML = "";

    const values = monthData(selectedMonth);
    const total = values.reduce((sum, d) => sum + d.rainfall, 0);

    const guideValues = [25, 100, 300];

    guideValues.forEach(value => {
        const radius = innerRadius + rainfallLength(value);

        const circle = svgElement("circle", {
            cx,
            cy,
            r: radius,
            class: "guide"
        });

        chart.appendChild(circle);

        const label = svgElement("text", {
            x: cx + 8,
            y: cy - radius + 13,
            class: "guide-label"
        });

        label.textContent = value + " mm";
        chart.appendChild(label);
    });

    values.forEach((record, index) => {
        const angle =
            (index / values.length) *
            Math.PI * 2;

        const length = rainfallLength(record.rainfall);

        const start = radialPoint(angle, innerRadius);

        const end = radialPoint(
            angle,
            innerRadius + Math.max(length, 4)
        );

        const line = svgElement("line", {
            x1: start[0],
            y1: start[1],
            x2: end[0],
            y2: end[1],
            class: record.rainfall > 0
                ? "day-line"
                : "zero-line",
            "stroke-width":
                record.rainfall > 0 ? 2.4 : 1
        });

        if (record.rainfall > 0) {
            line.style.opacity =
                0.35 +
                0.65 *
                Math.sqrt(record.rainfall / globalMax);

            line.addEventListener("mouseenter", () => {
                detail.textContent =
                    record.date +
                    " · " +
                    record.rainfall.toFixed(1) +
                    " mm";
            });

            line.addEventListener("click", () => {
                detail.textContent =
                    record.date +
                    " · " +
                    record.rainfall.toFixed(1) +
                    " mm";
            });
        }

        chart.appendChild(line);
    });

    const innerCircle = svgElement("circle", {
        cx,
        cy,
        r: innerRadius - 18,
        fill: "#ece8d6",
        stroke: "#171711",
        "stroke-width": 1
    });

    chart.appendChild(innerCircle);

    const monthLabel = svgElement("text", {
        x: cx,
        y: cy - 8,
        class: "center-label month-name"
    });

    monthLabel.textContent =
        MONTHS[selectedMonth - 1];

    chart.appendChild(monthLabel);

    const totalLabel = svgElement("text", {
        x: cx,
        y: cy + 23,
        class: "center-label month-total"
    });

    totalLabel.textContent =
        total.toFixed(1) + " MM";

    chart.appendChild(totalLabel);
}

function renderMetrics() {
    const values = monthData(selectedMonth);

    const total =
        values.reduce((sum, d) => sum + d.rainfall, 0);

    const rainy =
        values.filter(d => d.rainfall > 0).length;

    const max =
        values.reduce(
            (best, current) =>
                current.rainfall > best.rainfall
                    ? current
                    : best
        );

    panelMonth.textContent =
        MONTHS[selectedMonth - 1];

    totalRain.textContent =
        total.toFixed(1) + " mm";

    rainDays.textContent =
        rainy + " / " + values.length;

    wettest.textContent =
        max.day +
        " " +
        SHORT[selectedMonth - 1] +
        " · " +
        max.rainfall.toFixed(1);

    detail.textContent =
        "Hover over a rainfall stroke";
}

function renderYearBars() {
    monthBars.innerHTML = "";

    const totals = MONTHS.map((_, index) => {
        return monthData(index + 1)
            .reduce((sum, d) => sum + d.rainfall, 0);
    });

    const maximum = Math.max(...totals);

    totals.forEach((total, index) => {
        const wrap = document.createElement("div");
        wrap.className = "month-bar-wrap";

        const bar = document.createElement("div");

        bar.className =
            "month-bar" +
            (index + 1 === selectedMonth ? " selected" : "");

        bar.style.height =
            Math.max(2, (total / maximum) * 130) + "px";

        const label = document.createElement("div");
        label.className = "month-bar-label";
        label.textContent = SHORT[index];

        wrap.appendChild(bar);
        wrap.appendChild(label);

        monthBars.appendChild(wrap);
    });
}

function render() {
    renderNavigation();
    renderChart();
    renderMetrics();
    renderYearBars();
}

render();
</script>

</body>
</html>
'''

    html = html.replace("__DATA__", data_json)

    SITE.mkdir(exist_ok=True)
    SITE_FILE.write_text(html, encoding="utf-8")

    print(f"saved {SITE_FILE}")


def main():
    records = load_rainfall()

    make_static_picture(records)
    make_web_page(records)

    total = sum(record["rainfall"] for record in records)

    print(f"{len(records)} daily rainfall records")
    print(f"annual total: {total:.1f} mm")


if __name__ == "__main__":
    main()