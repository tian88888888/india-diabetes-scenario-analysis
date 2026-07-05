from pathlib import Path
import pandas as pd


MEASURE_NAME_MAP = {
    "DALYs (Disability-Adjusted Life Years)": "DALYS_RATE",
    "Deaths": "DEATHS_RATE",
    "Prevalence": "PREVALENCE_RATE",
    "YLDs (Years Lived with Disability)": "YLDS_RATE",
    "Incidence": "INCIDENCE_RATE",
}


def make_file_stem(country: str, condition: str) -> str:
    return f"{country.lower()}_{condition.lower().replace(' ', '_')}"


def clean_ihme_burden(country: str, condition: str) -> pd.DataFrame:
    """
    Clean raw IHME GBD disease burden data for one country-condition pair.

    Expected input:
        data/raw/ihme/{country}_{condition}_gbd.csv

    Example:
        data/raw/ihme/ind_diabetes_gbd.csv

    Output:
        data/processed/{country}_{condition}_burden_clean.csv
    """
    file_stem = make_file_stem(country, condition)

    input_path = Path(f"data/raw/ihme/{file_stem}_gbd.csv")

    if not input_path.exists():
        raise FileNotFoundError(
            f"Missing IHME raw file: {input_path}\n"
            f"Please download the IHME GBD CSV and save it there."
        )

    gbd = pd.read_csv(input_path)

    required_cols = [
        "year",
        "measure_name",
        "metric_name",
        "val",
    ]

    missing_cols = [col for col in required_cols if col not in gbd.columns]

    if missing_cols:
        raise ValueError(
            f"IHME file is missing required columns: {missing_cols}\n"
            f"Available columns are: {list(gbd.columns)}"
        )

    clean = gbd.copy()

    if "metric_name" in clean.columns:
        clean = clean[clean["metric_name"] == "Rate"]

    if "age_name" in clean.columns:
        clean = clean[clean["age_name"] == "Age-standardized"]

    if "sex_name" in clean.columns:
        clean = clean[clean["sex_name"] == "Both"]

    clean = clean[
        clean["measure_name"].isin(MEASURE_NAME_MAP.keys())
    ].copy()

    clean["indicator_id"] = clean["measure_name"].map(MEASURE_NAME_MAP)

    burden = clean.pivot_table(
        index="year",
        columns="indicator_id",
        values="val",
        aggfunc="mean",
    ).reset_index()

    burden.columns.name = None
    burden = burden.sort_values("year").reset_index(drop=True)

    output_path = Path(f"data/processed/{file_stem}_burden_clean.csv")
    burden.to_csv(output_path, index=False)

    return burden