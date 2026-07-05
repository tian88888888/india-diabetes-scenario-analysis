from pathlib import Path
from io import StringIO

import pandas as pd
import requests


VDEM_INDICATORS = {
    "LIBDEM": {
        "url": "https://ourworldindata.org/grapher/liberal-democracy-index.csv",
        "value_column": "Liberal democracy index",
    }
}


def download_csv_with_cache(url: str, cache_path: Path) -> pd.DataFrame:
    """
    Download a CSV from a URL and cache it locally.
    If download fails, use the cached copy if available.
    """
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        cache_path.write_text(response.text, encoding="utf-8")
        return pd.read_csv(StringIO(response.text))

    except requests.RequestException as error:
        if cache_path.exists():
            print(f"Warning: download failed, using cached file: {cache_path}")
            print(f"Original error: {error}")
            return pd.read_csv(cache_path)

        raise RuntimeError(
            f"Failed to download {url} and no cached file exists at {cache_path}"
        ) from error


def fetch_owid_grapher_indicator(
    country: str,
    indicator_id: str,
    url: str,
    value_column: str,
) -> pd.DataFrame:
    """
    Fetch one OWID grapher indicator for one country.
    """
    cache_path = Path(f"data/raw/vdem/{indicator_id.lower()}_owid.csv")
    df = download_csv_with_cache(url, cache_path)

    required_cols = ["Entity", "Code", "Year", value_column]
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        raise ValueError(
            f"Missing columns in OWID data: {missing_cols}\n"
            f"Available columns: {list(df.columns)}"
        )

    country_df = df[df["Code"] == country].copy()

    country_df = country_df[["Year", value_column]].rename(
        columns={
            "Year": "year",
            value_column: indicator_id,
        }
    )

    return country_df.sort_values("year").reset_index(drop=True)


def fetch_vdem_indicators(country: str) -> pd.DataFrame:
    """
    Fetch V-Dem / governance indicators for one country.

    Output:
        data/processed/{country}_vdem_indicators.csv
    """
    dfs = []

    for indicator_id, meta in VDEM_INDICATORS.items():
        df = fetch_owid_grapher_indicator(
            country=country,
            indicator_id=indicator_id,
            url=meta["url"],
            value_column=meta["value_column"],
        )
        dfs.append(df)

    vdem = dfs[0]

    for df in dfs[1:]:
        vdem = vdem.merge(df, on="year", how="outer")

    vdem = vdem.sort_values("year").reset_index(drop=True)

    output_path = Path(f"data/processed/{country.lower()}_vdem_indicators.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    vdem.to_csv(output_path, index=False)

    return vdem