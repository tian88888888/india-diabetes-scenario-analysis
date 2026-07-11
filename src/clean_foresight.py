from pathlib import Path
import pandas as pd

from src.clean_ihme import make_file_stem


MEASURE_MAP = {
    "DALYs per 100,000": "DALYS_RATE_FORECAST",
    "DALY rank": "DALY_RANK_FORECAST",
    "DALYs % change": "DALYS_PERCENT_CHANGE_FORECAST",
}


SCENARIO_NAME_MAP = {
    "reference": "Reference",
    "safer_environment": "Safer Environment",
    "improved_behavioral_metabolic_risks": "Improved Behavioral and Metabolic Risks",
    "improved_childhood_nutrition_vaccination": "Improved Childhood Nutrition and Vaccination",
    "combined": "Combined",
}


FORESIGHT_CAUSE_MAP = {
    "diabetes": "Diabetes and kidney diseases",
    "diabetes mellitus": "Diabetes and kidney diseases",
    "copd": "Chronic respiratory diseases",
    "chronic obstructive pulmonary disease": "Chronic respiratory diseases",
    "stroke": "Cardiovascular diseases",
    "ischemic heart disease": "Cardiovascular diseases",
    "cardiovascular disease": "Cardiovascular diseases",
    "depression": "Mental disorders",
    "depressive disorders": "Mental disorders",
    "mental health": "Mental disorders",
    "neoplasms": "Neoplasms",
    "cancer": "Neoplasms",
}


COUNTRY_NAME_MAP = {
    "IND": "India",
    "THA": "Thailand",
    "IDN": "Indonesia",
    "CHN": "China",
    "JPN": "Japan",
    "AUS": "Australia",
    "USA": "United States of America",
    "GBR": "United Kingdom",
}


def normalise_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def get_foresight_cause(condition: str) -> str:
    key = condition.lower().strip().replace("_", " ")
    return FORESIGHT_CAUSE_MAP.get(key, condition)


def get_country_name(country: str) -> str:
    return COUNTRY_NAME_MAP.get(country.upper(), country)


def to_numeric(value):
    if pd.isna(value):
        return pd.NA

    text = str(value).replace(",", "").replace("%", "").strip()

    try:
        return float(text)
    except ValueError:
        return pd.NA


def scenario_from_filename(path: Path) -> str:
    stem = path.stem.lower().strip()
    return SCENARIO_NAME_MAP.get(stem, stem.replace("_", " ").title())


def clean_one_foresight_file(
    file_path: Path,
    scenario_name: str,
    country: str,
    condition: str,
) -> pd.DataFrame:
    raw = pd.read_csv(file_path)

    required_cols = [
        "Location",
        "Year",
        "Age",
        "Sex",
        "Cause of death or injury",
        "Measure",
        "Value",
        "Lower bound",
        "Upper bound",
    ]

    missing_cols = [col for col in required_cols if col not in raw.columns]

    if missing_cols:
        raise ValueError(
            f"{file_path} is missing required columns: {missing_cols}\n"
            f"Available columns: {list(raw.columns)}"
        )

    clean = raw.copy()

    for col in ["Location", "Year", "Age", "Sex", "Cause of death or injury", "Measure"]:
        clean[col] = clean[col].apply(normalise_text)

    target_location = get_country_name(country)
    target_cause = get_foresight_cause(condition)

    clean = clean[clean["Year"] != ""].copy()
    clean = clean[clean["Measure"] != ""].copy()

    clean = clean[clean["Location"] == target_location].copy()
    clean = clean[clean["Sex"] == "Both"].copy()
    clean = clean[clean["Age"] == "All ages"].copy()
    clean = clean[clean["Cause of death or injury"] == target_cause].copy()
    clean = clean[clean["Measure"].isin(MEASURE_MAP.keys())].copy()

    if clean.empty:
        print(f"Warning: no usable rows after filtering {file_path}")
        return pd.DataFrame(
            columns=[
                "location",
                "year",
                "scenario",
                "age",
                "sex",
                "cause",
                "forecast_measure",
                "value",
                "lower",
                "upper",
            ]
        )

    clean["scenario"] = scenario_name
    clean["forecast_measure"] = clean["Measure"].map(MEASURE_MAP)

    clean = clean.rename(
        columns={
            "Location": "location",
            "Year": "year",
            "Age": "age",
            "Sex": "sex",
            "Cause of death or injury": "cause",
            "Value": "value",
            "Lower bound": "lower",
            "Upper bound": "upper",
        }
    )

    clean["value"] = clean["value"].apply(to_numeric)
    clean["lower"] = clean["lower"].apply(to_numeric)
    clean["upper"] = clean["upper"].apply(to_numeric)

    return clean[
        [
            "location",
            "year",
            "scenario",
            "age",
            "sex",
            "cause",
            "forecast_measure",
            "value",
            "lower",
            "upper",
        ]
    ].copy()


def clean_foresight_burden(country: str, condition: str) -> pd.DataFrame:
    """
    Clean IHME GBD Foresight exports.

    Expected folder:
        data/raw/ihme_foresight/{country}_{condition}/

    Example:
        data/raw/ihme_foresight/ind_diabetes/reference.csv
        data/raw/ihme_foresight/ind_diabetes/combined.csv
    """
    file_stem = make_file_stem(country, condition)
    input_dir = Path(f"data/raw/ihme_foresight/{file_stem}")

    if not input_dir.exists():
        raise FileNotFoundError(
            f"Missing IHME Foresight folder: {input_dir}\n"
            f"Create this folder and add one CSV per scenario."
        )

    csv_files = sorted(input_dir.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files found in {input_dir}\n"
            f"Add files like reference.csv, combined.csv, etc."
        )

    all_dfs = []

    for file_path in csv_files:
        scenario_name = scenario_from_filename(file_path)
        print(f"Cleaning Foresight scenario: {scenario_name} from {file_path}")

        df = clean_one_foresight_file(
            file_path=file_path,
            scenario_name=scenario_name,
            country=country,
            condition=condition,
        )

        all_dfs.append(df)

    foresight = pd.concat(all_dfs, ignore_index=True)

    if foresight.empty:
        raise ValueError(
            "Foresight data was loaded, but all rows were filtered out. "
            "Check Location, Age, Sex, Cause, and Measure values."
        )

    output_path = Path(f"data/processed/{file_stem}_foresight_clean.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    foresight.to_csv(output_path, index=False)

    return foresight