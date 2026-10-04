# Hong Kong Rainfall Monitor · 2025

![Hong Kong Rainfall Monitor interface](assets/rainfall-monitor-ui.png)

## The phenomenon

This project studies **daily rainfall in Hong Kong in 2025**, using official data from the Hong Kong Observatory. Rainfall is a natural phenomenon that changes across time: some days are completely dry, while others bring intense storms and extremely high precipitation. Instead of showing rainfall only as a simple static chart, this project explores how it can be turned into a more visual and interactive experience.

The final outcome is an **interactive rainfall monitor** that lets the viewer inspect the year by month and by day. The interface combines monthly totals, daily values, animated rainfall effects, and a stylised map of Hong Kong. My aim was to make the data feel more alive and atmospheric, while still remaining readable and grounded in real measurements.

## Source

The rainfall data comes from the **Hong Kong Observatory (HKO)** open data service.  
It uses daily total rainfall records from the Hong Kong Observatory station for the year 2025.

- Source organisation: **Hong Kong Observatory**
- Dataset: **Daily Total Rainfall (mm) at the Hong Kong Observatory**
- District boundary reference: **Hong Kong administrative district boundary GeoJSON**

## The picture

The main visualisation is an interactive web interface called **Hong Kong Rainfall Monitor · 2025**.

It shows:
- the selected month,
- daily rainfall values inside that month,
- the wettest day and peak rainfall,
- the number of rainy days,
- annual monthly totals,
- and a stylised Hong Kong map used as geographic context.

The animated rain layer changes with the selected data, so wetter days appear more active and intense. The month can be changed through the dropdown, navigation buttons, or the monthly timeline.

## What the picture shows

This work shows the **temporal rhythm of rainfall** across the year. It makes clear that rainfall in Hong Kong is not evenly distributed: summer months are much wetter, while winter months are relatively dry. The visualisation also highlights extremes, such as peak rainfall days, and helps the audience compare monthly totals quickly.

Because the page is interactive, the audience can move between months and days instead of only looking at one fixed chart. This makes the rainfall pattern easier to explore and more engaging than a single static plot.

## What the picture hides

Although the design uses a Hong Kong district map, the rainfall data itself comes from **one observation station only**: the Hong Kong Observatory station. This means the project does **not** represent district-level rainfall differences. The map is used mainly as visual and geographic context.

The visualisation also simplifies rainfall into daily totals. It does not show hourly variation, storm duration, wind, cloud movement, or uncertainty. In other words, it communicates seasonal pattern, intensity, and comparison well, but it hides more detailed meteorological complexity.

## How to run

### 1. Fetch the data

```bash
uv run fetch.py