## 2025-02-26 00:00 UTC - Task setup
- Created research folder structure per repository guidelines.
- Goal: compile historical global electricity availability dataset by country and energy type, visualize long-term trends.
## 2025-02-26 00:10 UTC - Data source scouting
- Checked OWID energy dataset columns via pandas to identify electricity generation fields (e.g., electricity_generation, electricity_from sources like coal, gas, hydro, solar, wind, nuclear, oil, biofuel, other_renewables).
## 2025-02-26 00:20 UTC - Processing pipeline
- Installed matplotlib for plotting (pip).
- Implemented `code/build_dataset.py` to download OWID energy data, reshape electricity sources, aggregate global totals, and create figures.
- Generated processed datasets and plots; coverage spans 1965–2024 across 265 entities.
## 2025-02-26 00:35 UTC - Quick stats
- Processed dataset covers 1965–2024 with 265 entities and 9 source categories.
- Added pre-1965 anchor via World Bank world total production (1960–1964) plus population to compute per-capita MWh; source-level mix remains unavailable for those early years.
- 2024 totals: ~208k TWh global generation; fossil fuels ~57% vs ~43% low-carbon (hydro+nuclear+wind+solar+biofuel+other renewables).
## 2025-02-27 11:15 UTC - Enhancements
- Installed plotly to enable interactive outputs (`pip install pandas matplotlib plotly`).
- Extended processing to keep the full historical range, add per-capita MWh, and emit fossil vs. low-carbon rollups plus a pre-1965 decadal table (now fed by World Bank WDI world totals for 1960–1964 and population for per-capita context).
- Added an interactive Plotly dashboard (global mix, fossil vs. low-carbon, per-capita, top countries) saved to `results/dashboard.html`; Matplotlib PNG generation remains available but is gitignored for commits.
- Latest (2024) snapshot: 208,163 TWh global electricity with fossil 118,479 TWh vs. low-carbon 89,684 TWh; per-capita ~7.6 vs. ~5.8 MWh respectively.【F:global-electricity-availability/data/processed/global_electricity_by_source.csv†L446-L454】【F:global-electricity-availability/data/processed/global_electricity_rollups.csv†L52-L61】
