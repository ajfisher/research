# Global Electricity Availability Analysis

## Objective
Build a reusable, cited dataset and visual summary of global electricity generation over the longest possible period, broken down by country and by energy source.

## Background
Electricity generation mixes have shifted from hydro-dominated beginnings toward fossil fuels and, more recently, modern renewables. Understanding these long-run shifts helps frame transition pathways and infrastructure planning.

## Methodology
- **Source data**: Our World in Data energy compilation (`owid-energy-data.csv`), which consolidates BP, Ember, IEA, and other historical series (public GitHub mirror: <https://github.com/owid/energy-data>).【F:global-electricity-availability/code/build_dataset.py†L23-L48】
- **Processing**: `code/build_dataset.py` downloads the CSV, reshapes nine generation sources into long form (coal, gas, oil, hydro, nuclear, solar, wind, biofuel, other renewables), preserves the full historical window available in OWID, and aggregates country/global totals with per-capita fields.【F:global-electricity-availability/code/build_dataset.py†L51-L105】
- **Rollups and early-history summary**: The pipeline produces fossil vs. low-carbon rollups with per-capita metrics plus a best-effort pre-1965 decadal table (now populated with 1960–1964 World Bank world totals).【F:global-electricity-availability/code/build_dataset.py†L108-L206】
- **Outputs**:
  - `data/processed/electricity_by_country_source.csv`: country/year/source TWh values and per-capita MWh (1965–2024 based on OWID coverage).【F:global-electricity-availability/data/processed/electricity_by_country_source.csv†L1-L5】
  - `data/processed/global_electricity_by_source.csv`: global TWh totals per year/source with per-capita values.【F:global-electricity-availability/data/processed/global_electricity_by_source.csv†L1-L10】
  - `data/processed/global_electricity_rollups.csv`: fossil vs. low-carbon totals and per-capita metrics.【F:global-electricity-availability/data/processed/global_electricity_rollups.csv†L1-L10】
   - `data/processed/global_electricity_decadal_pre1965.csv`: decadal averages before 1965, currently populated with 1960–1964 World Bank world totals and per-capita values.【F:global-electricity-availability/data/processed/global_electricity_decadal_pre1965.csv†L1-L3】
  - `results/dashboard.html`: interactive Plotly dashboard (global mix, fossil vs. low-carbon, per-capita, top countries).【F:global-electricity-availability/code/build_dataset.py†L200-L281】 Static PNG figure generation remains available via Matplotlib but outputs are gitignored.

## Results
- **Coverage**: OWID’s electricity-by-source coverage begins in 1965. For 1960–1964 the pipeline now ingests World Bank WDI global production totals (indicator `EG.ELC.PROD.KH`) and World Bank population (`SP.POP.TOTL`) to provide a pre-1965 decadal anchor; these values are higher than later OWID/BP vintages but offer a sourced early datapoint.【F:global-electricity-availability/data/processed/global_electricity_decadal_pre1965.csv†L2-L3】
- **Long-run growth**: Global generation expanded from ~6,000 TWh in 1965 (dominated by hydro) to ~208,000 TWh in 2024, a ~35× increase.【F:global-electricity-availability/notes.md†L10-L13】
- **Mix evolution (2024)**: Fossil fuels supplied ~57% of tracked electricity, while low-carbon sources delivered ~43%.【F:global-electricity-availability/notes.md†L10-L13】
- **Per-capita context**: Fossil electricity reached ~7.6 MWh/person vs. ~5.8 MWh/person for low-carbon sources in 2024.【F:global-electricity-availability/data/processed/global_electricity_rollups.csv†L52-L61】
- **Interactive exploration**: Open `results/dashboard.html` in a browser to explore the stacked mix, fossil vs. low-carbon split, per-capita trends, and top-15 generators; rerun the script to refresh from the latest OWID data.【F:global-electricity-availability/code/build_dataset.py†L200-L281】

## How to Reproduce
```bash
pip install pandas matplotlib plotly
python code/build_dataset.py --skip-figures  # dashboard + CSVs only
```
Re-running regenerates processed CSVs and the interactive dashboard from the live OWID source. Omit `--skip-figures` if you want local PNGs (they are gitignored).【F:global-electricity-availability/code/build_dataset.py†L284-L302】

## Limitations and Future Work
- Pre-1965 electricity reporting is absent in the public OWID feed; supplementing with archival IEA/BP digests or national utility records would enable earlier-point estimates.
- Regional aggregations and technology subcategories (e.g., geothermal, CSP vs. PV) could refine the low-carbon breakdown once available.
- Per-capita figures inherit OWID population estimates; alternative demographic baselines (urban population, electrified population) could offer additional perspective.
