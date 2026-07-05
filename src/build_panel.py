from pathlib import Path
import pandas as pd

from src.clean_ihme import clean_ihme_burden, make_file_stem
from src.fetch_worldbank import fetch_worldbank_determinants
from src.fetch_vdem import fetch_vdem_indicators


def build_panel(country: str, condition: str) -> pd.DataFrame:
    """
    Build a standardised panel dataset for one country-condition pair.

    Steps:
    1. Clean IHME disease burden data
    2. Fetch World Bank determinants
    3. Fetch V-Dem / governance indicators
    4. Merge into one scenario panel
    """
    burden = clean_ihme_burden(country, condition)
    determinants = fetch_worldbank_determinants(country)
    vdem = fetch_vdem_indicators(country)

    panel = burden.merge(determinants, on="year", how="left")
    panel = panel.merge(vdem, on="year", how="left")

    panel.insert(0, "country", country)
    panel.insert(1, "condition", condition)

    output_dir = Path(f"outputs/{country}/{condition}")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "panel.csv"
    panel.to_csv(output_path, index=False)

    file_stem = make_file_stem(country, condition)
    processed_path = Path(f"data/processed/{file_stem}_scenario_panel.csv")
    panel.to_csv(processed_path, index=False)

    return panel