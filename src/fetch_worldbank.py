from pathlib import Path
import requests
import pandas as pd


WORLD_BANK_INDICATORS = {
    "GDP_PC": "NY.GDP.PCAP.CD",
    "HEALTH_EXP_GDP": "SH.XPD.CHEX.GD.ZS",
    "OOP_HEALTH_EXP": "SH.XPD.OOPC.CH.ZS",
    "SECONDARY_ENROL": "SE.SEC.ENRR",
    "URBAN_POP": "SP.URB.TOTL.IN.ZS",
    "INTERNET_USERS": "IT.NET.USER.ZS",
    "POP_65PLUS": "SP.POP.65UP.TO.ZS",
}


def fetch_worldbank_indicator(country: str, indicator_id: str, wb_code: str) -> pd.DataFrame:
    url = f"https://api.worldbank.org/v2/country/{country}/indicator/{wb_code}"

    params = {
        "format": "json",
        "per_page": 20000,
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    json_data = response.json()

    if len(json_data) < 2 or json_data[1] is None:
        return pd.DataFrame(columns=["year", indicator_id])

    rows = []

    for item in json_data[1]:
        rows.append({
            "year": int(item["date"]),
            indicator_id: item["value"],
        })

    df = pd.DataFrame(rows)
    return df


def fetch_worldbank_determinants(country: str) -> pd.DataFrame:
    """
    Fetch World Bank determinant indicators for one country.

    Output:
        data/processed/{country}_worldbank_determinants.csv
    """
    dfs = []

    for indicator_id, wb_code in WORLD_BANK_INDICATORS.items():
        df = fetch_worldbank_indicator(country, indicator_id, wb_code)
        dfs.append(df)

    determinants = dfs[0]

    for df in dfs[1:]:
        determinants = determinants.merge(df, on="year", how="outer")

    determinants = determinants.sort_values("year").reset_index(drop=True)

    output_path = Path(f"data/processed/{country.lower()}_worldbank_determinants.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    determinants.to_csv(output_path, index=False)

    return determinants