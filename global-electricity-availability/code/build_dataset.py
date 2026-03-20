"""Download and process global electricity generation data from OWID.

Outputs:
- data/processed/electricity_by_country_source.csv
- data/processed/global_electricity_by_source.csv
- data/processed/global_electricity_rollups.csv
- data/processed/global_electricity_decadal_pre1965.csv
- results/dashboard.html (interactive Plotly views)
- results/figures/global_electricity_by_source.png (optional, not committed)
- results/figures/top10_electricity_generation.png (optional, not committed)
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

DATA_URL = "https://raw.githubusercontent.com/owid/energy-data/master/owid-energy-data.csv"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "processed"
FIGURE_DIR = PROJECT_ROOT / "results" / "figures"
WORLD_BANK_ELECTRICITY_URL = (
    "https://api.worldbank.org/v2/en/indicator/EG.ELC.PROD.KH?downloadformat=csv"
)
WORLD_BANK_POPULATION_URL = (
    "https://api.worldbank.org/v2/en/indicator/SP.POP.TOTL?downloadformat=csv"
)


ELECTRICITY_COLUMNS = {
    "coal": "coal_electricity",
    "gas": "gas_electricity",
    "oil": "oil_electricity",
    "biofuel": "biofuel_electricity",
    "hydro": "hydro_electricity",
    "nuclear": "nuclear_electricity",
    "solar": "solar_electricity",
    "wind": "wind_electricity",
    "other_renewables": "other_renewable_electricity",
}

FOSSIL_SOURCES = {"coal", "gas", "oil"}


def load_dataset() -> pd.DataFrame:
    """Load the OWID energy dataset from the public URL."""
    df = pd.read_csv(DATA_URL)
    return df


def prepare_long_format(df: pd.DataFrame) -> pd.DataFrame:
    """Transform wide electricity columns into a long format by source."""
    required_cols = [
        "country",
        "iso_code",
        "year",
        "population",
        "electricity_generation",
        *ELECTRICITY_COLUMNS.values(),
    ]
    subset = df[required_cols].copy()
    long_df = subset.melt(
        id_vars=["country", "iso_code", "year", "population", "electricity_generation"],
        value_vars=list(ELECTRICITY_COLUMNS.values()),
        var_name="source_column",
        value_name="electricity_twh",
    )
    long_df["source"] = long_df["source_column"].map({v: k for k, v in ELECTRICITY_COLUMNS.items()})
    long_df.drop(columns="source_column", inplace=True)
    long_df.dropna(subset=["electricity_twh"], inplace=True)
    long_df["per_capita_mwh"] = (
        (long_df["electricity_twh"] * 1_000_000) / long_df["population"]
    )
    return long_df


def save_processed_data(long_df: pd.DataFrame) -> None:
    """Save country-level, global, and rollup datasets."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    country_path = DATA_DIR / "electricity_by_country_source.csv"
    long_df.to_csv(country_path, index=False)

    population_totals = (
        long_df[["year", "country", "population"]]
        .drop_duplicates()
        .groupby("year", as_index=False)["population"]
        .sum()
        .rename(columns={"population": "population_total"})
    )

    global_df = long_df.groupby(["year", "source"], as_index=False)["electricity_twh"].sum()
    global_df = global_df.merge(population_totals, on="year", how="left")
    global_df["per_capita_mwh"] = (global_df["electricity_twh"] * 1_000_000) / global_df[
        "population_total"
    ]
    global_path = DATA_DIR / "global_electricity_by_source.csv"
    global_df.to_csv(global_path, index=False)

    rollups = build_rollups(global_df, population_totals)
    rollup_path = DATA_DIR / "global_electricity_rollups.csv"
    rollups.to_csv(rollup_path, index=False)

    decadal = build_pre1965_decadal(global_df, population_totals)
    decadal_path = DATA_DIR / "global_electricity_decadal_pre1965.csv"
    decadal.to_csv(decadal_path, index=False)


def load_world_bank_pre1965() -> pd.DataFrame:
    """Fetch 1960-1964 global electricity production from the World Bank WDI feed."""

    try:
        wb_zip = pd.read_csv(
            WORLD_BANK_ELECTRICITY_URL, storage_options={"User-Agent": "Mozilla/5.0"}
        )
        parsed_directly = wb_zip.shape[1] > 5
    except Exception:
        parsed_directly = False

    if parsed_directly:
        # Already parsed (some environments unzip automatically)
        df = wb_zip
    else:
        import io
        import zipfile
        import requests

        resp = requests.get(WORLD_BANK_ELECTRICITY_URL)
        resp.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
            data_name = [n for n in zf.namelist() if n.startswith("API_") and n.endswith(".csv")][0]
            df = pd.read_csv(zf.open(data_name), skiprows=4)

    world = df[df["Country Code"] == "WLD"].copy()
    year_cols = [c for c in world.columns if c.isdigit()]
    melted = world.melt(id_vars=["Country Name", "Country Code"], value_vars=year_cols, var_name="year", value_name="kwh")
    melted.dropna(subset=["kwh"], inplace=True)
    melted["year"] = melted["year"].astype(int)
    melted = melted[(melted["year"] >= 1960) & (melted["year"] < 1965)]
    melted["electricity_twh"] = melted["kwh"] / 1_000_000_000
    melted["source"] = "total"
    return melted[["year", "source", "electricity_twh"]]


def load_world_bank_population(years: set[int]) -> pd.DataFrame:
    """Get World Bank world population for the requested years."""

    try:
        wb_zip = pd.read_csv(
            WORLD_BANK_POPULATION_URL, storage_options={"User-Agent": "Mozilla/5.0"}
        )
        parsed_directly = wb_zip.shape[1] > 5
    except Exception:
        parsed_directly = False

    if parsed_directly:
        df = wb_zip
    else:
        import io
        import zipfile
        import requests

        resp = requests.get(WORLD_BANK_POPULATION_URL)
        resp.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
            data_name = [n for n in zf.namelist() if n.startswith("API_") and n.endswith(".csv")][0]
            df = pd.read_csv(zf.open(data_name), skiprows=4)

    world = df[df["Country Code"] == "WLD"].copy()
    year_cols = [c for c in world.columns if c.isdigit()]
    melted = world.melt(
        id_vars=["Country Name", "Country Code"],
        value_vars=year_cols,
        var_name="year",
        value_name="population",
    )
    melted.dropna(subset=["population"], inplace=True)
    melted["year"] = melted["year"].astype(int)
    melted = melted[melted["year"].isin(years)]
    return melted[["year", "population"]]


def build_rollups(global_df: pd.DataFrame, population_totals: pd.DataFrame) -> pd.DataFrame:
    """Create fossil vs low-carbon rollups with per-capita metrics."""
    tmp = global_df.copy()
    tmp["category"] = tmp["source"].apply(lambda s: "fossil" if s in FOSSIL_SOURCES else "low_carbon")

    rollups = tmp.groupby(["year", "category"], as_index=False)["electricity_twh"].sum()
    rollups = rollups.pivot(index="year", columns="category", values="electricity_twh").reset_index()
    rollups = rollups.merge(population_totals, on="year", how="left")
    rollups["fossil_per_capita_mwh"] = (rollups["fossil"] * 1_000_000) / rollups["population_total"]
    rollups["low_carbon_per_capita_mwh"] = (rollups["low_carbon"] * 1_000_000) / rollups["population_total"]
    rollups = rollups.rename(
        columns={
            "fossil": "electricity_twh_fossil",
            "low_carbon": "electricity_twh_low_carbon",
            "population_total": "population",
        }
    )
    return rollups


def build_pre1965_decadal(global_df: pd.DataFrame, population_totals: pd.DataFrame) -> pd.DataFrame:
    """Summarize pre-1965 global electricity generation by decade (best-effort)."""
    pre1965 = global_df[global_df["year"] < 1965].copy()

    # Supplement with World Bank totals for 1960-1964 when OWID coverage is missing
    wb_extra = load_world_bank_pre1965()
    if not wb_extra.empty:
        pre1965 = pd.concat([pre1965, wb_extra], ignore_index=True, sort=False)

    if pre1965.empty:
        return pd.DataFrame(columns=["decade", "source", "electricity_twh", "per_capita_mwh"])

    needed_years = set(pre1965["year"].unique())
    wb_population = load_world_bank_population(needed_years)
    population_totals = population_totals.copy()
    population_totals = pd.concat(
        [population_totals, wb_population.rename(columns={"population": "population_total"})],
        ignore_index=True,
    ).drop_duplicates(subset=["year"], keep="last")

    pre1965["decade"] = (pre1965["year"] // 10) * 10
    decadal = pre1965.groupby(["decade", "source"], as_index=False)["electricity_twh"].mean()
    pop_decadal = (
        population_totals[population_totals["year"] < 1965]
        .assign(decade=lambda df: (df["year"] // 10) * 10)
        .groupby("decade", as_index=False)["population_total"]
        .mean()
    )
    decadal = decadal.merge(pop_decadal, on="decade", how="left")
    decadal["per_capita_mwh"] = (decadal["electricity_twh"] * 1_000_000) / decadal[
        "population_total"
    ]
    decadal = decadal.rename(columns={"population_total": "population"})
    return decadal


def plot_global_mix(long_df: pd.DataFrame) -> None:
    """Create stacked area chart for global electricity generation by source."""
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    global_df = long_df.groupby(["year", "source"], as_index=False)["electricity_twh"].sum()
    pivot = global_df.pivot(index="year", columns="source", values="electricity_twh").fillna(0)
    pivot.sort_index(inplace=True)

    colors = {
        "coal": "#4B4B4B",
        "gas": "#FF8C00",
        "oil": "#8B4513",
        "biofuel": "#66C2A5",
        "hydro": "#1E90FF",
        "nuclear": "#FFD700",
        "solar": "#FDB813",
        "wind": "#00A9CE",
        "other_renewables": "#9E9AC8",
    }

    pivot[list(colors.keys())].plot.area(color=[colors[c] for c in colors], linewidth=0)
    plt.title("Global Electricity Generation by Source (TWh)")
    plt.ylabel("TWh")
    plt.xlabel("Year")
    plt.tight_layout()
    out_path = FIGURE_DIR / "global_electricity_by_source.png"
    plt.savefig(out_path, dpi=200)
    plt.close()


def plot_top_countries(long_df: pd.DataFrame, top_n: int = 10) -> None:
    """Plot the top N countries by most recent electricity generation."""
    latest_year = int(long_df["year"].max())
    latest_totals = (
        long_df[long_df["year"] == latest_year]
        .groupby("country", as_index=False)["electricity_twh"].sum()
        .sort_values("electricity_twh", ascending=False)
        .head(top_n)
    )

    plt.figure(figsize=(10, 6))
    plt.barh(latest_totals["country"], latest_totals["electricity_twh"], color="#1f77b4")
    plt.gca().invert_yaxis()
    plt.title(f"Top {top_n} Electricity Generators in {latest_year} (TWh)")
    plt.xlabel("TWh")
    plt.tight_layout()
    out_path = FIGURE_DIR / "top10_electricity_generation.png"
    plt.savefig(out_path, dpi=200)
    plt.close()


def build_dashboard(long_df: pd.DataFrame) -> None:
    """Create an interactive HTML dashboard with Plotly charts."""
    results_dir = PROJECT_ROOT / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    population_totals = (
        long_df[["year", "country", "population"]]
        .drop_duplicates()
        .groupby("year", as_index=False)["population"]
        .sum()
        .rename(columns={"population": "population_total"})
    )

    global_df = long_df.groupby(["year", "source"], as_index=False)["electricity_twh"].sum()
    global_df = global_df.merge(population_totals, on="year", how="left")
    rollups = build_rollups(global_df, population_totals)

    fig_mix = px.area(
        global_df,
        x="year",
        y="electricity_twh",
        color="source",
        title="Global Electricity Generation by Source (TWh)",
    )

    fig_rollup = px.area(
        rollups,
        x="year",
        y=["electricity_twh_fossil", "electricity_twh_low_carbon"],
        title="Fossil vs Low-Carbon Electricity (TWh)",
        labels={"value": "TWh", "year": "Year", "variable": "Category"},
    )

    fig_per_capita = go.Figure()
    fig_per_capita.add_trace(
        go.Scatter(
            x=rollups["year"],
            y=rollups["fossil_per_capita_mwh"],
            mode="lines",
            name="Fossil",
        )
    )
    fig_per_capita.add_trace(
        go.Scatter(
            x=rollups["year"],
            y=rollups["low_carbon_per_capita_mwh"],
            mode="lines",
            name="Low carbon",
        )
    )
    fig_per_capita.update_layout(
        title="Per-Capita Electricity by Category (MWh/person)",
        xaxis_title="Year",
        yaxis_title="MWh per person",
    )

    latest_year = long_df["year"].max()
    latest_totals = (
        long_df[long_df["year"] == latest_year]
        .groupby("country", as_index=False)["electricity_twh"]
        .sum()
        .sort_values("electricity_twh", ascending=False)
        .head(15)
    )
    fig_top_countries = px.bar(
        latest_totals,
        x="electricity_twh",
        y="country",
        orientation="h",
        title=f"Top 15 Electricity Generators in {int(latest_year)}",
        labels={"electricity_twh": "TWh"},
    )

    html_parts = [
        pio.to_html(fig_mix, full_html=False, include_plotlyjs="cdn"),
        pio.to_html(fig_rollup, full_html=False, include_plotlyjs=False),
        pio.to_html(fig_per_capita, full_html=False, include_plotlyjs=False),
        pio.to_html(fig_top_countries, full_html=False, include_plotlyjs=False),
    ]
    html = "\n".join(html_parts)
    out_path = results_dir / "dashboard.html"
    out_path.write_text(html)


def main(generate_figures: bool = True) -> None:
    df = load_dataset()
    long_df = prepare_long_format(df)
    save_processed_data(long_df)
    build_dashboard(long_df)
    if generate_figures:
        plot_global_mix(long_df)
        plot_top_countries(long_df)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-figures",
        action="store_true",
        help="Skip generating static PNG figures (interactive dashboard is always produced).",
    )
    args = parser.parse_args()
    main(generate_figures=not args.skip_figures)
