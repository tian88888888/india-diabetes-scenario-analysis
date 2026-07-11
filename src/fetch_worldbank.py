from pathlib import Path
import requests
import pandas as pd


WORLD_BANK_INDICATORS = {
    "GDP_PC": "NY.GDP.PCAP.CD",
    "POVERTY_HEADCOUNT": "SI.POV.NAHC",
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

    response = requests.get(url, params=params, timeout=30)
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

    return pd.DataFrame(rows)


def fetch_worldbank_determinants(country: str, force_refresh: bool = False) -> pd.DataFrame:
    """
    Fetch World Bank determinant indicators for one country.

    Uses local cached processed file by default if available.

    Output:
        data/processed/{country}_worldbank_determinants.csv
    """
    output_path = Path(f"data/processed/{country.lower()}_worldbank_determinants.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists() and not force_refresh:
        print(f"Using cached World Bank determinants: {output_path}")
        return pd.read_csv(output_path)

    dfs = []

    for indicator_id, wb_code in WORLD_BANK_INDICATORS.items():
        print(f"Fetching World Bank indicator: {indicator_id} ({wb_code})")

        try:
            df = fetch_worldbank_indicator(country, indicator_id, wb_code)
        except requests.RequestException as error:
            print(f"Warning: failed to fetch {indicator_id}: {error}")
            df = pd.DataFrame(columns=["year", indicator_id])

        dfs.append(df)

    determinants = dfs[0]

    for df in dfs[1:]:
        determinants = determinants.merge(df, on="year", how="outer")

    determinants = determinants.sort_values("year").reset_index(drop=True)
    determinants.to_csv(output_path, index=False)

    return determinants