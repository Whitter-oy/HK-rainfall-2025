# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib"]
# ///

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt


HERE = Path(__file__).parent

RAINFALL_FILE = HERE / "data" / "hko-daily-rainfall-2025.csv"
BOUNDARY_FILE = HERE / "data" / "hk-district-boundary.json"

OUT = HERE / "out"
OUT_FILE = OUT / "hong-kong-rainfall-2025.png"

SITE = HERE / "site"
SITE_FILE = SITE / "index.html"


# =========================================================
# DATA
# =========================================================

def rainfall_value(text):
    """Convert HKO rainfall text to a number."""
    text = text.strip()

    if text == "Trace":
        return 0.0

    return float(text)


def load_rainfall():
    """Read the committed HKO daily rainfall CSV."""
    records = []

    with RAINFALL_FILE.open(
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.reader(file)

        # HKO title rows + column heading
        next(reader)
        next(reader)
        next(reader)

        for row in reader:

            if len(row) < 5:
                continue

            if not row[0].strip().isdigit():
                continue

            records.append({
                "year": int(row[0]),
                "month": int(row[1]),
                "day": int(row[2]),
                "rainfall": rainfall_value(row[3]),
            })

    return records


def load_boundaries():
    """Read the committed Hong Kong district GeoJSON."""
    with BOUNDARY_FILE.open(encoding="utf-8") as file:
        return json.load(file)


def monthly_totals(records):
    """Return rainfall total for every month."""
    totals = []

    for month in range(1, 13):

        total = 0.0

        for record in records:
            if record["month"] == month:
                total += record["rainfall"]

        totals.append(total)

    return totals


# =========================================================
# STATIC OUTPUT
# =========================================================

def make_static_picture(records):
    """Create the static image required by the assignment."""

    totals = monthly_totals(records)
    months = list(range(1, 13))

    OUT.mkdir(exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 5))

    ax.plot(
        months,
        totals,
        marker="o",
        linewidth=2,
    )

    ax.set_title(
        "Hong Kong Observatory — Monthly Rainfall, 2025"
    )

    ax.set_xlabel("Month")
    ax.set_ylabel("Total rainfall (mm)")
    ax.set_xticks(months)

    plt.tight_layout()

    plt.savefig(
        OUT_FILE,
        dpi=180,
        bbox_inches="tight",
    )

    plt.close(fig)

    print(f"saved {OUT_FILE}")


# =========================================================
# INTERACTIVE DASHBOARD
# =========================================================

def make_dashboard(records, boundaries):

    rainfall_json = json.dumps(records)

    boundary_json = json.dumps(
        boundaries,
        ensure_ascii=False
    )

    html = r'''<!doctype html>

<html lang="en">

<head>

<meta charset="utf-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1"
>

<title>Hong Kong Rainfall Monitor · 2025</title>


<style>

/* ======================================================
   COLOUR SYSTEM
====================================================== */

:root {
    --bg: #02080b;
    --panel: #061116;
    --panel2: #08191e;

    --cyan: #27e0d1;
    --cyan2: #58adb3;

    --green: #32e88a;
    --yellow: #f5d84b;
    --orange: #ff9e42;

    --white: #eaf8f7;
    --muted: #6d888d;

    --line: rgba(56, 217, 207, .19);
}


/* ======================================================
   BASE
====================================================== */

* {
    box-sizing: border-box;
}


html,
body {
    margin: 0;

    width: 100%;
    height: 100%;

    overflow: hidden;

    background:
        radial-gradient(
            circle at 38% 42%,
            #0b2226 0%,
            #030b0e 45%,
            #020608 100%
        );

    color: var(--white);

    font-family:
        Inter,
        Arial,
        Helvetica,
        sans-serif;
}


body::before {
    content: "";

    position: fixed;
    inset: 0;

    pointer-events: none;

    opacity: .12;

    background-image:
        linear-gradient(
            rgba(255,255,255,.035) 1px,
            transparent 1px
        ),
        linear-gradient(
            90deg,
            rgba(255,255,255,.035) 1px,
            transparent 1px
        );

    background-size: 32px 32px;
}


/* ======================================================
   PAGE LAYOUT
====================================================== */

.dashboard {
    height: 100vh;

    display: grid;

    /*
    Reduced header/footer height so the main dashboard
    always has enough vertical space.
    */
    grid-template-rows:
        76px
        minmax(0, 1fr)
        96px;
}


/* ======================================================
   HEADER
====================================================== */

.topbar {
    display: flex;

    align-items: center;
    justify-content: space-between;

    padding:
        0 28px;

    border-bottom:
        1px solid var(--line);

    background:
        rgba(2, 10, 13, .8);

    backdrop-filter:
        blur(14px);
}


.eyebrow {
    margin-bottom: 5px;

    color: var(--cyan);

    font-size: 10px;

    letter-spacing: .22em;

    text-transform: uppercase;
}


h1 {
    margin: 0;

    font-size: 23px;

    font-weight: 520;

    letter-spacing: .04em;
}


.header-right {
    display: flex;

    align-items: center;

    gap: 25px;

    color: var(--muted);

    font-size: 10px;

    letter-spacing: .12em;

    text-transform: uppercase;
}


.archive-status {
    display: flex;

    align-items: center;

    gap: 8px;

    color: var(--green);
}


.status-dot {
    width: 7px;
    height: 7px;

    border-radius: 50%;

    background: var(--green);

    box-shadow:
        0 0 8px var(--green),
        0 0 18px rgba(50,232,138,.5);

    animation:
        statusPulse
        1.8s
        infinite;
}


@keyframes statusPulse {

    0%,
    100% {
        opacity: .4;
    }

    50% {
        opacity: 1;
    }
}


/* ======================================================
   MAIN
====================================================== */

.main {
    min-height: 0;

    display: grid;

    grid-template-columns:
        minmax(0, 1fr)
        350px;

    gap: 10px;

    padding:
        10px 12px;
}


/* ======================================================
   MAP PANEL
====================================================== */

.map-panel {
    --storm: 0;

    min-width: 0;
    min-height: 0;

    position: relative;

    overflow: hidden;

    border:
        1px solid var(--line);

    background:
        radial-gradient(
            circle at 52% 55%,
            rgba(20, 95, 96, .16),
            rgba(2, 10, 13, .9) 62%
        );
}


.map-panel::after {
    content: "";

    position: absolute;
    inset: 0;

    pointer-events: none;

    z-index: 1;

    opacity:
        calc(var(--storm) * .55);

    background:
        radial-gradient(
            circle at 52% 58%,
            rgba(32, 216, 207, .21),
            rgba(5, 34, 40, .08) 35%,
            transparent 68%
        );

    transition:
        opacity .35s ease;
}


#map {
    position: absolute;

    inset: 0;

    z-index: 3;

    display: block;

    width: 100%;
    height: 100%;
}


/*
Rain is placed above the map but cannot block clicks.
*/

#rainCanvas {
    position: absolute;

    inset: 0;

    z-index: 4;

    width: 100%;
    height: 100%;

    pointer-events: none;
}


.map-header {
    position: absolute;

    top: 20px;
    left: 22px;

    z-index: 20;

    width: 225px;
}


.map-number {
    font-family:
        "SFMono-Regular",
        Consolas,
        monospace;

    color: var(--cyan);

    font-size: 31px;

    letter-spacing: .025em;

    text-shadow:
        0 0 18px
        rgba(35,224,208,.25);
}


.map-caption {
    margin-top: 4px;

    color: var(--muted);

    font-size: 9px;

    letter-spacing: .13em;

    text-transform: uppercase;
}


.selected-date {
    margin-top: 7px;

    font-family:
        "SFMono-Regular",
        Consolas,
        monospace;

    color: var(--white);

    font-size: 11px;

    letter-spacing: .08em;
}


/* ======================================================
   SELECTORS
====================================================== */

.selector {
    margin-top: 18px;
}


.selector label {
    display: block;

    margin-bottom: 7px;

    color: var(--muted);

    font-size: 9px;

    letter-spacing: .16em;

    text-transform: uppercase;
}


.month-select-wrap {
    position: relative;
}


.month-select-wrap::after {
    content: "▼";

    position: absolute;

    right: 12px;
    top: 12px;

    color: var(--cyan);

    font-size: 8px;

    pointer-events: none;
}


#monthSelect {
    width: 100%;

    appearance: none;

    padding:
        10px 34px
        10px 12px;

    border:
        1px solid
        rgba(35,224,208,.5);

    outline: none;

    border-radius: 0;

    background:
        rgba(5, 26, 31, .93);

    color: var(--cyan);

    font-family:
        "SFMono-Regular",
        Consolas,
        monospace;

    font-size: 12px;

    cursor: pointer;
}


#monthSelect:hover,
#monthSelect:focus {
    border-color:
        var(--cyan);

    box-shadow:
        0 0 12px
        rgba(35,224,208,.13);
}


/* ======================================================
   DAY SLIDER
====================================================== */

.day-row {
    display: flex;

    justify-content:
        space-between;

    align-items: center;

    margin-bottom: 7px;
}


.day-value {
    font-family:
        "SFMono-Regular",
        Consolas,
        monospace;

    color: var(--cyan);

    font-size: 10px;
}


#daySlider {
    appearance: none;

    width: 100%;

    height: 2px;

    outline: none;

    cursor: pointer;

    background:
        rgba(35,224,208,.26);
}


#daySlider::-webkit-slider-thumb {
    appearance: none;

    width: 10px;
    height: 10px;

    border-radius: 50%;

    background: var(--yellow);

    box-shadow:
        0 0 9px
        rgba(245,216,75,.65);
}


/* ======================================================
   DISTRICTS
====================================================== */

.district {
    fill:
        rgba(10, 37, 42, .62);

    stroke:
        rgba(52, 222, 208, .44);

    stroke-width: 1.1;

    vector-effect:
        non-scaling-stroke;

    transition:
        fill .2s,
        stroke .2s;
}


.district:hover {
    fill:
        rgba(20, 100, 103, .48);

    stroke:
        var(--cyan);
}


/* ======================================================
   RADAR
====================================================== */

.radar-circle {
    fill: none;

    stroke:
        rgba(35,224,208,.17);

    stroke-width: 1;
}


.station-ring {
    fill: none;

    stroke: var(--cyan);

    transform-box:
        fill-box;

    transform-origin:
        center;
}


.ring-one {
    animation:
        stationPulse
        2.2s
        infinite
        ease-out;
}


.ring-two {
    animation:
        stationPulse
        2.2s
        .85s
        infinite
        ease-out;
}


@keyframes stationPulse {

    from {
        opacity: .75;

        transform:
            scale(.25);
    }

    to {
        opacity: 0;

        transform:
            scale(2.7);
    }
}


#rainHalo {
    fill:
        rgba(35,224,208,.05);

    stroke:
        rgba(35,224,208,.26);

    stroke-width: 1;

    transition:
        r .35s,
        fill .35s,
        stroke .35s;
}


.station-core {
    fill: white;

    stroke: var(--cyan);

    stroke-width: 3;

    filter:
        drop-shadow(
            0 0 8px
            var(--cyan)
        );

    transition:
        r .3s;
}


.station-label {
    fill: white;

    font-size: 12px;

    font-family:
        "SFMono-Regular",
        Consolas,
        monospace;
}


#sweep {
    stroke: var(--cyan);

    stroke-width: 1.5;

    opacity: .65;

    filter:
        drop-shadow(
            0 0 7px
            var(--cyan)
        );
}


/* ======================================================
   SIDEBAR
====================================================== */

.sidebar {
    min-height: 0;

    /*
    The sidebar is now a fixed two-row grid.
    This prevents the main panel from pushing
    underneath the bottom timeline.
    */
    display: grid;

    grid-template-rows:
        minmax(0, 1fr)
        auto;

    gap: 8px;

    overflow: hidden;
}


.side-block {
    border:
        1px solid var(--line);

    padding: 14px;

    background:
        linear-gradient(
            145deg,
            rgba(8, 28, 33, .96),
            rgba(3, 13, 17, .96)
        );
}


.side-block.primary {
    min-height: 0;

    /*
    Normally everything fits.
    If the browser height is unusually small,
    the panel scrolls internally instead of
    disappearing behind the footer.
    */
    overflow-y: auto;

    scrollbar-width: thin;

    scrollbar-color:
        rgba(35,224,208,.25)
        transparent;
}


.side-block.primary::-webkit-scrollbar {
    width: 4px;
}


.side-block.primary::-webkit-scrollbar-thumb {
    background:
        rgba(35,224,208,.25);
}


.label {
    color: var(--muted);

    font-size: 9px;

    letter-spacing: .16em;

    text-transform: uppercase;
}


.big-month {
    margin-top: 6px;

    font-size: 27px;

    font-weight: 500;
}


.month-total {
    margin-top: 3px;

    color: var(--cyan);

    font-family:
        "SFMono-Regular",
        Consolas,
        monospace;

    font-size: 37px;

    line-height: 1;

    text-shadow:
        0 0 16px
        rgba(35,224,208,.18);
}


.unit {
    color: var(--muted);

    font-size: 10px;
}


/* ======================================================
   MONTH METRICS
====================================================== */

.metrics {
    margin-top: 14px;
}


.metric {
    display: grid;

    grid-template-columns:
        1fr auto;

    gap: 12px;

    padding: 8px 0;

    border-top:
        1px solid var(--line);
}


.metric-name {
    color: var(--muted);

    font-size: 8.5px;

    letter-spacing: .1em;

    text-transform: uppercase;
}


.metric-value {
    font-family:
        "SFMono-Regular",
        Consolas,
        monospace;

    font-size: 12px;
}


/* ======================================================
   MONTH MINI CHART
====================================================== */

.spark-section {
    margin-top: 10px;

    padding-top: 9px;

    border-top:
        1px solid var(--line);
}


#monthSpark {
    display: block;

    width: 100%;
    height: 64px;

    margin-top: 5px;
}


.spark-bar {
    fill:
        rgba(35,224,208,.34);

    cursor: pointer;

    transition:
        fill .15s;
}


.spark-bar:hover {
    fill: var(--cyan);
}


.spark-bar.active {
    fill: var(--yellow);

    filter:
        drop-shadow(
            0 0 5px
            rgba(245,216,75,.55)
        );
}


/* ======================================================
   CONTROLS
====================================================== */

.controls {
    display: grid;

    grid-template-columns:
        1fr 1.2fr 1fr;

    gap: 5px;

    margin-top: 10px;
}


.month-controls {
    display: flex;

    gap: 5px;

    margin-top: 6px;
}


.control-button {
    appearance: none;

    border:
        1px solid
        rgba(35,224,208,.36);

    background:
        rgba(35,224,208,.055);

    color: var(--cyan);

    padding:
        7px 7px;

    cursor: pointer;

    font-size: 8.5px;

    letter-spacing: .08em;

    text-transform: uppercase;

    transition:
        background .2s,
        border .2s;
}


.control-button:hover {
    border-color:
        var(--cyan);

    background:
        rgba(35,224,208,.14);
}


.control-button.playing {
    border-color:
        var(--yellow);

    color: var(--yellow);

    background:
        rgba(245,216,75,.08);
}


/* ======================================================
   EXPLANATION NOTE
====================================================== */

.station-note {
    margin-top: 10px;

    padding-top: 9px;

    border-top:
        1px solid var(--line);

    color: var(--muted);

    font-size: 8.5px;

    line-height: 1.4;
}


/* ======================================================
   BOTTOM TIMELINE
====================================================== */

.timeline {
    padding:
        8px 16px
        10px;

    border-top:
        1px solid var(--line);

    background:
        rgba(3,11,14,.97);
}


.timeline-head {
    height: 18px;

    display: flex;

    justify-content:
        space-between;

    align-items: center;

    color: var(--muted);

    font-size: 8.5px;

    letter-spacing: .13em;

    text-transform: uppercase;
}


.months {
    height: 53px;

    display: grid;

    grid-template-columns:
        repeat(12, 1fr);

    gap: 5px;

    align-items: end;
}


.month {
    position: relative;

    height: 100%;

    display: flex;

    align-items: end;

    justify-content: center;

    cursor: pointer;

    border-left:
        1px solid
        rgba(255,255,255,.04);
}


.month-bar {
    position: absolute;

    bottom: 17px;

    left: 21%;
    right: 21%;

    min-height: 2px;

    background:
        rgba(48, 201, 192, .28);

    border-top:
        1px solid
        var(--cyan);

    transition:
        background .2s,
        box-shadow .2s;
}


.month.active
.month-bar {
    background:
        var(--yellow);

    border-color:
        var(--yellow);

    box-shadow:
        0 0 11px
        rgba(245,216,75,.5);
}


.month-name {
    position: relative;

    z-index: 3;

    padding-bottom: 1px;

    color: var(--muted);

    font-size: 8.5px;

    letter-spacing: .1em;
}


.month.active
.month-name {
    color: var(--yellow);
}


/* ======================================================
   SMALL HEIGHT FALLBACK
====================================================== */

@media (max-height: 760px) {

    .dashboard {
        grid-template-rows:
            68px
            minmax(0, 1fr)
            86px;
    }

    .topbar {
        padding:
            0 20px;
    }

    h1 {
        font-size: 20px;
    }

    .map-header {
        top: 14px;
        left: 17px;
    }

    .map-number {
        font-size: 27px;
    }

    .selector {
        margin-top: 13px;
    }

    .side-block {
        padding: 11px;
    }

    .big-month {
        font-size: 23px;
    }

    .month-total {
        font-size: 32px;
    }

    #monthSpark {
        height: 52px;
    }

    .station-note {
        font-size: 8px;
    }

    .timeline {
        padding-top: 5px;
    }

    .months {
        height: 46px;
    }
}


/* ======================================================
   NARROW SCREEN FALLBACK
====================================================== */

@media (max-width: 1000px) {

    html,
    body {
        overflow: auto;
    }

    .dashboard {
        min-width: 950px;
    }
}

</style>

</head>


<body>

<div class="dashboard">


<!-- =====================================================
     HEADER
===================================================== -->

<header class="topbar">

    <div>

        <div class="eyebrow">
            SD5913 · Natural Phenomenon Study · Ouyang Wensi
        </div>

        <h1>
            Hong Kong Rainfall Monitor · 2025
        </h1>

    </div>


    <div class="header-right">

        <span id="headerDate">
            01 JAN 2025
        </span>

        <span>
            HONG KONG OBSERVATORY
        </span>

        <span class="archive-status">

            <span class="status-dot"></span>

            2025 ARCHIVE READY

        </span>

    </div>

</header>


<!-- =====================================================
     MAIN
===================================================== -->

<main class="main">


<!-- LEFT MAP -->

<section
    class="map-panel"
    id="mapPanel"
>

    <canvas
        id="rainCanvas"
    ></canvas>


    <div class="map-header">

        <div
            class="map-number"
            id="dailyValue"
        >
            0.0 MM
        </div>

        <div class="map-caption">
            Selected daily rainfall
        </div>

        <div
            class="selected-date"
            id="selectedDate"
        >
            2025-01-01
        </div>


        <!-- MONTH -->

        <div class="selector">

            <label>
                Select month
            </label>

            <div class="month-select-wrap">

                <select id="monthSelect">

                    <option value="1">January</option>
                    <option value="2">February</option>
                    <option value="3">March</option>
                    <option value="4">April</option>
                    <option value="5">May</option>
                    <option value="6">June</option>
                    <option value="7">July</option>
                    <option value="8">August</option>
                    <option value="9">September</option>
                    <option value="10">October</option>
                    <option value="11">November</option>
                    <option value="12">December</option>

                </select>

            </div>

        </div>


        <!-- DAY -->

        <div class="selector">

            <div class="day-row">

                <label
                    style="margin:0;"
                >
                    Select day
                </label>

                <span
                    class="day-value"
                    id="dayDisplay"
                >
                    01
                </span>

            </div>


            <input
                id="daySlider"
                type="range"
                min="1"
                max="31"
                value="1"
            >

        </div>

    </div>


    <svg
        id="map"
        viewBox="0 0 1000 650"
    ></svg>

</section>


<!-- RIGHT PANEL -->

<aside class="sidebar">


<section
    class="side-block primary"
>

    <div class="label">
        Selected month
    </div>

    <div
        class="big-month"
        id="monthTitle"
    >
        January
    </div>

    <div
        class="month-total"
        id="monthTotal"
    >
        —
    </div>

    <span class="unit">
        MM / MONTH
    </span>


    <div class="metrics">

        <div class="metric">

            <div class="metric-name">
                Rainy days
            </div>

            <div
                class="metric-value"
                id="rainyDays"
            >
                —
            </div>

        </div>


        <div class="metric">

            <div class="metric-name">
                Wettest day
            </div>

            <div
                class="metric-value"
                id="wettestDay"
            >
                —
            </div>

        </div>


        <div class="metric">

            <div class="metric-name">
                Peak rainfall
            </div>

            <div
                class="metric-value"
                id="peakValue"
            >
                —
            </div>

        </div>

    </div>


    <div class="spark-section">

        <div class="label">
            Daily rainfall · click a bar
        </div>

        <svg
            id="monthSpark"
            viewBox="0 0 300 80"
            preserveAspectRatio="none"
        ></svg>

    </div>


    <div class="controls">

        <button
            class="control-button"
            id="previousDayButton"
        >
            ◀ DAY
        </button>

        <button
            class="control-button"
            id="playButton"
        >
            ▶ PLAY
        </button>

        <button
            class="control-button"
            id="nextDayButton"
        >
            DAY ▶
        </button>

    </div>


    <div class="month-controls">

        <button
            class="control-button"
            id="prevMonthButton"
        >
            ◀ PREV MONTH
        </button>

        <button
            class="control-button"
            id="nextMonthButton"
        >
            NEXT MONTH ▶
        </button>

    </div>


    <div class="station-note">

        Rainfall values are daily totals measured
        at the Hong Kong Observatory station.

        The animated rain field visualises the
        selected station value only.

        District boundaries provide geographic
        context and do not represent district-level
        rainfall measurements.

    </div>

</section>


<section class="side-block">

    <div class="label">
        Observation station
    </div>

    <div
        style="
            margin-top:8px;
            font-size:14px;
        "
    >
        HKO Headquarters
    </div>

    <div
        style="
            margin-top:4px;
            color:var(--cyan);
            font-family:monospace;
            font-size:10px;
        "
    >
        22.3019° N · 114.1742° E
    </div>

</section>


</aside>

</main>


<!-- =====================================================
     YEAR TIMELINE
===================================================== -->

<footer class="timeline">

    <div class="timeline-head">

        <span>
            Annual rainfall timeline
        </span>

        <span>
            Monthly totals · select to inspect
        </span>

    </div>

    <div
        class="months"
        id="months"
    ></div>

</footer>


</div>


<script>

/* ======================================================
   EMBEDDED DATA
====================================================== */

const RAINFALL = __RAINFALL__;
const GEO = __BOUNDARIES__;


/* ======================================================
   CONSTANTS
====================================================== */

const MONTH_NAMES = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
];


const MONTH_SHORT = [
    "JAN",
    "FEB",
    "MAR",
    "APR",
    "MAY",
    "JUN",
    "JUL",
    "AUG",
    "SEP",
    "OCT",
    "NOV",
    "DEC"
];


const HKO = {
    lon: 114.1742,
    lat: 22.3019
};


let selectedMonth = 1;
let selectedDay = 1;

let playing = false;
let playTimer = null;

let rainIntensity = 0;
let radarSpeed = .007;


/* ======================================================
   ELEMENTS
====================================================== */

const map =
    document.getElementById("map");


const mapPanel =
    document.getElementById("mapPanel");


const monthSelect =
    document.getElementById("monthSelect");


const daySlider =
    document.getElementById("daySlider");


const playButton =
    document.getElementById("playButton");


/* ======================================================
   SVG HELPERS
====================================================== */

const SVG_NS =
    "http://www.w3.org/2000/svg";


function makeSVG(
    name,
    attributes = {}
) {

    const element =
        document.createElementNS(
            SVG_NS,
            name
        );

    for (
        const [key, value]
        of Object.entries(attributes)
    ) {

        element.setAttribute(
            key,
            value
        );
    }

    return element;
}


/* ======================================================
   MAP BOUNDS
====================================================== */

const allPoints = [];


for (const feature of GEO.features) {

    const rings =
        feature.geometry.coordinates;

    for (const ring of rings) {

        for (const point of ring) {

            allPoints.push(point);
        }
    }
}


const longitudes =
    allPoints.map(
        point => point[0]
    );


const latitudes =
    allPoints.map(
        point => point[1]
    );


const minLon =
    Math.min(...longitudes);


const maxLon =
    Math.max(...longitudes);


const minLat =
    Math.min(...latitudes);


const maxLat =
    Math.max(...latitudes);


const WIDTH = 1000;
const HEIGHT = 650;
const MAP_PADDING = 90;


const lonRange =
    maxLon - minLon;


const latRange =
    maxLat - minLat;


const mapScale =
    Math.min(
        (
            WIDTH
            -
            MAP_PADDING * 2
        )
        /
        lonRange,

        (
            HEIGHT
            -
            MAP_PADDING * 2
        )
        /
        latRange
    );


const mapWidth =
    lonRange
    *
    mapScale;


const mapHeight =
    latRange
    *
    mapScale;


const offsetX =
    (
        WIDTH
        -
        mapWidth
    )
    /
    2;


const offsetY =
    (
        HEIGHT
        -
        mapHeight
    )
    /
    2;


function project(
    lon,
    lat
) {

    const x =
        offsetX
        +
        (
            lon
            -
            minLon
        )
        *
        mapScale;


    const y =
        offsetY
        +
        (
            maxLat
            -
            lat
        )
        *
        mapScale;


    return [
        x,
        y
    ];
}


/* ======================================================
   DRAW MAP
====================================================== */

function drawMap() {

    for (const feature of GEO.features) {

        const rings =
            feature
            .geometry
            .coordinates;


        let pathData = "";


        for (const ring of rings) {

            ring.forEach(
                (
                    point,
                    index
                ) => {

                    const [x, y] =
                        project(
                            point[0],
                            point[1]
                        );


                    pathData +=
                        (
                            index === 0
                            ?
                            "M"
                            :
                            "L"
                        )
                        +
                        x
                        +
                        " "
                        +
                        y
                        +
                        " ";
                }
            );


            pathData += "Z ";
        }


        const path =
            makeSVG(
                "path",
                {
                    d: pathData,
                    class: "district"
                }
            );


        const title =
            makeSVG("title");


        title.textContent =
            feature.properties.District
            ||
            "District";


        path.appendChild(title);

        map.appendChild(path);
    }
}


/* ======================================================
   STATION
====================================================== */

const station =
    project(
        HKO.lon,
        HKO.lat
    );


function drawStation() {

    const [x, y] =
        station;


    for (
        const radius
        of [
            80,
            135,
            190
        ]
    ) {

        map.appendChild(
            makeSVG(
                "circle",
                {
                    cx: x,
                    cy: y,
                    r: radius,
                    class: "radar-circle"
                }
            )
        );
    }


    map.appendChild(
        makeSVG(
            "circle",
            {
                id: "rainHalo",
                cx: x,
                cy: y,
                r: 25
            }
        )
    );


    map.appendChild(
        makeSVG(
            "circle",
            {
                cx: x,
                cy: y,
                r: 22,
                class:
                    "station-ring ring-one"
            }
        )
    );


    map.appendChild(
        makeSVG(
            "circle",
            {
                cx: x,
                cy: y,
                r: 22,
                class:
                    "station-ring ring-two"
            }
        )
    );


    map.appendChild(
        makeSVG(
            "circle",
            {
                id: "stationCore",
                cx: x,
                cy: y,
                r: 6,
                class: "station-core"
            }
        )
    );


    const label =
        makeSVG(
            "text",
            {
                x: x + 14,
                y: y - 13,
                class: "station-label"
            }
        );


    label.textContent =
        "HKO";


    map.appendChild(label);


    const sweep =
        makeSVG(
            "line",
            {
                id: "sweep",
                x1: x,
                y1: y,
                x2: x,
                y2: y - 180
            }
        );


    map.appendChild(sweep);
}


/* ======================================================
   RADAR
====================================================== */

let sweepAngle = 0;


function animateRadar() {

    const sweep =
        document.getElementById(
            "sweep"
        );


    const [x, y] =
        station;


    const radius = 180;


    sweepAngle +=
        radarSpeed;


    const x2 =
        x
        +
        Math.sin(
            sweepAngle
        )
        *
        radius;


    const y2 =
        y
        -
        Math.cos(
            sweepAngle
        )
        *
        radius;


    sweep.setAttribute(
        "x2",
        x2
    );


    sweep.setAttribute(
        "y2",
        y2
    );


    requestAnimationFrame(
        animateRadar
    );
}


/* ======================================================
   RAIN CANVAS
====================================================== */

const rainCanvas =
    document.getElementById(
        "rainCanvas"
    );


const rainContext =
    rainCanvas.getContext(
        "2d"
    );


let rainDrops = [];


function resizeRainCanvas() {

    const rect =
        mapPanel
        .getBoundingClientRect();


    const dpr =
        Math.min(
            window.devicePixelRatio
            ||
            1,
            2
        );


    rainCanvas.width =
        rect.width
        *
        dpr;


    rainCanvas.height =
        rect.height
        *
        dpr;


    rainCanvas.style.width =
        rect.width
        +
        "px";


    rainCanvas.style.height =
        rect.height
        +
        "px";


    rainContext.setTransform(
        dpr,
        0,
        0,
        dpr,
        0,
        0
    );
}


function newDrop() {

    const width =
        mapPanel.clientWidth;


    const height =
        mapPanel.clientHeight;


    return {

        x:
            Math.random()
            *
            width,

        y:
            Math.random()
            *
            height,

        length:
            6
            +
            Math.random()
            *
            16,

        speed:
            2.5
            +
            Math.random()
            *
            5
            +
            rainIntensity
            *
            7,

        opacity:
            .10
            +
            Math.random()
            *
            .30
            +
            rainIntensity
            *
            .25

    };
}


function syncRainDrops() {

    let target = 0;


    if (
        rainIntensity
        >
        0
    ) {

        target =
            Math.round(
                8
                +
                rainIntensity
                *
                115
            );
    }


    while (
        rainDrops.length
        <
        target
    ) {

        rainDrops.push(
            newDrop()
        );
    }


    if (
        rainDrops.length
        >
        target
    ) {

        rainDrops =
            rainDrops.slice(
                0,
                target
            );
    }
}


function animateRain() {

    const width =
        mapPanel.clientWidth;


    const height =
        mapPanel.clientHeight;


    rainContext.clearRect(
        0,
        0,
        width,
        height
    );


    rainContext.lineWidth =
        1;


    for (const drop of rainDrops) {

        rainContext.beginPath();


        rainContext.strokeStyle =
            "rgba(72, 220, 224,"
            +
            drop.opacity
            +
            ")";


        rainContext.moveTo(
            drop.x,
            drop.y
        );


        rainContext.lineTo(
            drop.x - 3,
            drop.y + drop.length
        );


        rainContext.stroke();


        drop.y +=
            drop.speed;


        drop.x -=
            drop.speed
            *
            .12;


        if (
            drop.y
            >
            height + 20
            ||
            drop.x
            <
            -20
        ) {

            const replacement =
                newDrop();


            drop.x =
                replacement.x;


            drop.y =
                -20;


            drop.length =
                replacement.length;


            drop.speed =
                replacement.speed;


            drop.opacity =
                replacement.opacity;
        }
    }


    requestAnimationFrame(
        animateRain
    );
}


/* ======================================================
   DATA HELPERS
====================================================== */

function recordsForMonth(
    month
) {

    return RAINFALL.filter(
        record =>
            record.month
            ===
            month
    );
}


function currentRecord() {

    const records =
        recordsForMonth(
            selectedMonth
        );


    return records[
        Math.max(
            0,
            Math.min(
                selectedDay - 1,
                records.length - 1
            )
        )
    ];
}


function monthTotal(
    month
) {

    return recordsForMonth(
        month
    )
    .reduce(
        (
            sum,
            record
        ) =>
            sum
            +
            record.rainfall,
        0
    );
}


const totals = [];


for (
    let month = 1;
    month <= 12;
    month++
) {

    totals.push(
        monthTotal(
            month
        )
    );
}


const largestMonthlyTotal =
    Math.max(
        ...totals
    );


const maximumDailyRainfall =
    Math.max(
        ...RAINFALL.map(
            record =>
                record.rainfall
        )
    );


/* ======================================================
   MONTH PANEL
====================================================== */

function updateMonthPanel() {

    const records =
        recordsForMonth(
            selectedMonth
        );


    const total =
        records.reduce(
            (
                sum,
                record
            ) =>
                sum
                +
                record.rainfall,
            0
        );


    const rainy =
        records.filter(
            record =>
                record.rainfall
                >
                0
        );


    let wettest =
        records[0];


    for (const record of records) {

        if (
            record.rainfall
            >
            wettest.rainfall
        ) {

            wettest =
                record;
        }
    }


    document.getElementById(
        "monthTitle"
    ).textContent =
        MONTH_NAMES[
            selectedMonth - 1
        ];


    document.getElementById(
        "monthTotal"
    ).textContent =
        total.toFixed(1);


    document.getElementById(
        "rainyDays"
    ).textContent =
        rainy.length
        +
        " / "
        +
        records.length;


    document.getElementById(
        "wettestDay"
    ).textContent =
        wettest.day
        +
        " "
        +
        MONTH_SHORT[
            selectedMonth - 1
        ];


    document.getElementById(
        "peakValue"
    ).textContent =
        wettest.rainfall
        .toFixed(1)
        +
        " mm";
}


/* ======================================================
   DAILY STATE
====================================================== */

function updateDailyState() {

    const records =
        recordsForMonth(
            selectedMonth
        );


    selectedDay =
        Math.max(
            1,
            Math.min(
                selectedDay,
                records.length
            )
        );


    const record =
        currentRecord();


    daySlider.max =
        records.length;


    daySlider.value =
        selectedDay;


    document.getElementById(
        "dayDisplay"
    ).textContent =
        String(
            selectedDay
        )
        .padStart(
            2,
            "0"
        );


    const dateText =
        record.year
        +
        "-"
        +
        String(
            record.month
        )
        .padStart(
            2,
            "0"
        )
        +
        "-"
        +
        String(
            record.day
        )
        .padStart(
            2,
            "0"
        );


    document.getElementById(
        "selectedDate"
    ).textContent =
        dateText;


    document.getElementById(
        "headerDate"
    ).textContent =
        String(
            record.day
        )
        .padStart(
            2,
            "0"
        )
        +
        " "
        +
        MONTH_SHORT[
            record.month - 1
        ]
        +
        " "
        +
        record.year;


    document.getElementById(
        "dailyValue"
    ).textContent =
        record.rainfall
        .toFixed(1)
        +
        " MM";


    rainIntensity =
        record.rainfall <= 0
        ?
        0
        :
        Math.sqrt(
            record.rainfall
            /
            maximumDailyRainfall
        );


    mapPanel.style.setProperty(
        "--storm",
        rainIntensity
    );


    radarSpeed =
        .006
        +
        rainIntensity
        *
        .014;


    const core =
        document.getElementById(
            "stationCore"
        );


    core.setAttribute(
        "r",
        6
        +
        rainIntensity
        *
        5
    );


    const halo =
        document.getElementById(
            "rainHalo"
        );


    halo.setAttribute(
        "r",
        25
        +
        rainIntensity
        *
        82
    );


    halo.style.fill =
        "rgba(35,224,208,"
        +
        (
            .025
            +
            rainIntensity
            *
            .12
        )
        +
        ")";


    halo.style.stroke =
        "rgba(35,224,208,"
        +
        (
            .18
            +
            rainIntensity
            *
            .55
        )
        +
        ")";


    const rings =
        document.querySelectorAll(
            ".station-ring"
        );


    const ringDuration =
        2.4
        -
        rainIntensity
        *
        1.2;


    rings.forEach(
        ring => {

            ring.style.animationDuration =
                ringDuration
                +
                "s";
        }
    );


    syncRainDrops();
}


/* ======================================================
   MINI MONTH CHART
====================================================== */

function drawSparkline() {

    const spark =
        document.getElementById(
            "monthSpark"
        );


    spark.innerHTML =
        "";


    const records =
        recordsForMonth(
            selectedMonth
        );


    const width = 300;
    const height = 80;
    const gap = 2;


    const barWidth =
        (
            width
            -
            gap
            *
            (
                records.length - 1
            )
        )
        /
        records.length;


    const maxValue =
        Math.max(
            1,
            ...records.map(
                record =>
                    record.rainfall
            )
        );


    const baseline =
        makeSVG(
            "line",
            {
                x1: 0,
                y1: 76,
                x2: width,
                y2: 76,
                stroke:
                    "rgba(35,224,208,.18)"
            }
        );


    spark.appendChild(
        baseline
    );


    records.forEach(
        (
            record,
            index
        ) => {

            const normalised =
                record.rainfall
                /
                maxValue;


            const barHeight =
                record.rainfall === 0
                ?
                1
                :
                Math.max(
                    2,
                    normalised
                    *
                    67
                );


            const rect =
                makeSVG(
                    "rect",
                    {
                        x:
                            index
                            *
                            (
                                barWidth
                                +
                                gap
                            ),

                        y:
                            76
                            -
                            barHeight,

                        width:
                            barWidth,

                        height:
                            barHeight,

                        class:
                            "spark-bar"
                            +
                            (
                                index + 1
                                ===
                                selectedDay
                                ?
                                " active"
                                :
                                ""
                            )
                    }
                );


            const title =
                makeSVG(
                    "title"
                );


            title.textContent =
                record.day
                +
                " "
                +
                MONTH_SHORT[
                    selectedMonth - 1
                ]
                +
                ": "
                +
                record.rainfall
                .toFixed(1)
                +
                " mm";


            rect.appendChild(
                title
            );


            rect.addEventListener(
                "click",
                () => {

                    setPlaying(false);

                    selectedDay =
                        index + 1;

                    render();
                }
            );


            spark.appendChild(
                rect
            );
        }
    );
}


/* ======================================================
   YEAR TIMELINE
====================================================== */

function drawTimeline() {

    const holder =
        document.getElementById(
            "months"
        );


    holder.innerHTML =
        "";


    totals.forEach(
        (
            total,
            index
        ) => {

            const item =
                document.createElement(
                    "div"
                );


            item.className =
                "month"
                +
                (
                    index + 1
                    ===
                    selectedMonth
                    ?
                    " active"
                    :
                    ""
                );


            const bar =
                document.createElement(
                    "div"
                );


            bar.className =
                "month-bar";


            bar.style.height =
                Math.max(
                    2,
                    (
                        total
                        /
                        largestMonthlyTotal
                    )
                    *
                    34
                )
                +
                "px";


            const label =
                document.createElement(
                    "div"
                );


            label.className =
                "month-name";


            label.textContent =
                MONTH_SHORT[
                    index
                ];


            item.appendChild(
                bar
            );


            item.appendChild(
                label
            );


            item.addEventListener(
                "click",
                () => {

                    setPlaying(false);

                    selectedMonth =
                        index + 1;

                    selectedDay =
                        1;

                    render();
                }
            );


            holder.appendChild(
                item
            );
        }
    );
}


/* ======================================================
   PLAYBACK
====================================================== */

function nextDay() {

    const records =
        recordsForMonth(
            selectedMonth
        );


    if (
        selectedDay
        <
        records.length
    ) {

        selectedDay++;

    } else {

        selectedDay =
            1;


        selectedMonth++;


        if (
            selectedMonth
            >
            12
        ) {

            selectedMonth =
                1;
        }
    }


    render();
}


function previousDay() {

    if (
        selectedDay
        >
        1
    ) {

        selectedDay--;

    } else {

        selectedMonth--;


        if (
            selectedMonth
            <
            1
        ) {

            selectedMonth =
                12;
        }


        selectedDay =
            recordsForMonth(
                selectedMonth
            )
            .length;
    }


    render();
}


function setPlaying(
    shouldPlay
) {

    playing =
        shouldPlay;


    if (
        playTimer
    ) {

        clearInterval(
            playTimer
        );


        playTimer =
            null;
    }


    if (
        playing
    ) {

        playButton.textContent =
            "Ⅱ PAUSE";


        playButton.classList.add(
            "playing"
        );


        playTimer =
            setInterval(
                nextDay,
                480
            );

    } else {

        playButton.textContent =
            "▶ PLAY";


        playButton.classList.remove(
            "playing"
        );
    }
}


/* ======================================================
   INPUT EVENTS
====================================================== */

monthSelect.addEventListener(
    "change",
    () => {

        setPlaying(false);

        selectedMonth =
            Number(
                monthSelect.value
            );


        selectedDay =
            1;


        render();
    }
);


daySlider.addEventListener(
    "input",
    () => {

        setPlaying(false);

        selectedDay =
            Number(
                daySlider.value
            );


        render();
    }
);


document.getElementById(
    "previousDayButton"
)
.addEventListener(
    "click",
    () => {

        setPlaying(false);

        previousDay();
    }
);


document.getElementById(
    "nextDayButton"
)
.addEventListener(
    "click",
    () => {

        setPlaying(false);

        nextDay();
    }
);


playButton.addEventListener(
    "click",
    () => {

        setPlaying(
            !playing
        );
    }
);


document.getElementById(
    "prevMonthButton"
)
.addEventListener(
    "click",
    () => {

        setPlaying(false);

        selectedMonth--;


        if (
            selectedMonth
            <
            1
        ) {

            selectedMonth =
                12;
        }


        selectedDay =
            1;


        render();
    }
);


document.getElementById(
    "nextMonthButton"
)
.addEventListener(
    "click",
    () => {

        setPlaying(false);

        selectedMonth++;


        if (
            selectedMonth
            >
            12
        ) {

            selectedMonth =
                1;
        }


        selectedDay =
            1;


        render();
    }
);


/* ======================================================
   RENDER
====================================================== */

function render() {

    const records =
        recordsForMonth(
            selectedMonth
        );


    if (
        selectedDay
        >
        records.length
    ) {

        selectedDay =
            records.length;
    }


    monthSelect.value =
        selectedMonth;


    updateMonthPanel();

    updateDailyState();

    drawSparkline();

    drawTimeline();
}


/* ======================================================
   START
====================================================== */

drawMap();

drawStation();

resizeRainCanvas();

render();

animateRadar();

animateRain();


window.addEventListener(
    "resize",
    resizeRainCanvas
);

</script>

</body>

</html>
'''


    html = html.replace(
        "__RAINFALL__",
        rainfall_json
    )


    html = html.replace(
        "__BOUNDARIES__",
        boundary_json
    )


    SITE.mkdir(
        exist_ok=True
    )


    SITE_FILE.write_text(
        html,
        encoding="utf-8"
    )


    print(
        f"saved {SITE_FILE}"
    )


# =========================================================
# MAIN
# =========================================================

def main():

    rainfall = load_rainfall()

    boundaries = load_boundaries()

    make_static_picture(
        rainfall
    )

    make_dashboard(
        rainfall,
        boundaries
    )

    print(
        f"{len(rainfall)} rainfall records"
    )

    print(
        f"{len(boundaries['features'])} districts"
    )


if __name__ == "__main__":
    main()