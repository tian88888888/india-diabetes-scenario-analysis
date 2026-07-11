import pandas as pd


INDICATOR_METADATA = {
    "DALYS_RATE": {
        "label": "DALYs rate",
        "domain": "Disease burden",
        "direction": "lower_better",
    },
    "DEATHS_RATE": {
        "label": "Deaths rate",
        "domain": "Disease burden",
        "direction": "lower_better",
    },
    "PREVALENCE_RATE": {
        "label": "Prevalence rate",
        "domain": "Disease burden",
        "direction": "lower_better",
    },
    "POP_65PLUS": {
        "label": "Population aged 65+",
        "domain": "Risk pressure",
        "direction": "higher_risk",
    },
    "URBAN_POP": {
        "label": "Urban population",
        "domain": "Risk pressure",
        "direction": "context",
    },
    "POVERTY_HEADCOUNT": {
        "label": "Poverty headcount",
        "domain": "Economic constraint",
        "direction": "lower_better",
    },
    "GDP_PC": {
        "label": "GDP per capita",
        "domain": "Economic capability",
        "direction": "higher_better",
    },
    "HEALTH_EXP_GDP": {
        "label": "Health expenditure % GDP",
        "domain": "Health system capacity",
        "direction": "higher_better",
    },
    "OOP_HEALTH_EXP": {
        "label": "Out-of-pocket health expenditure",
        "domain": "Health system barrier",
        "direction": "lower_better",
    },
    "SECONDARY_ENROL": {
        "label": "Secondary school enrolment",
        "domain": "Individual capability",
        "direction": "higher_better",
    },
    "INTERNET_USERS": {
        "label": "Internet users",
        "domain": "Individual capability",
        "direction": "higher_better",
    },
    "LIBDEM": {
        "label": "Liberal democracy index",
        "domain": "Governance context",
        "direction": "higher_better",
    },
}


def calculate_indicator_change(panel: pd.DataFrame, indicator_id: str):
    if indicator_id not in panel.columns:
        return None

    clean = panel[["year", indicator_id]].dropna().sort_values("year")

    if len(clean) < 2:
        return None

    start_year = int(clean.iloc[0]["year"])
    end_year = int(clean.iloc[-1]["year"])
    start_value = clean.iloc[0][indicator_id]
    end_value = clean.iloc[-1][indicator_id]

    absolute_change = end_value - start_value
    percent_change = (
        absolute_change / start_value * 100
        if start_value != 0
        else None
    )

    return {
        "indicator_id": indicator_id,
        "start_year": start_year,
        "end_year": end_year,
        "start_value": start_value,
        "end_value": end_value,
        "absolute_change": absolute_change,
        "percent_change": percent_change,
    }


def classify_change(change, direction: str):
    if change is None or change["percent_change"] is None:
        return "insufficient_data"

    pct = change["percent_change"]

    if abs(pct) < 5:
        trend = "stable"
    elif pct > 0:
        trend = "increased"
    else:
        trend = "decreased"

    if direction == "higher_better":
        interpretation = "improved" if pct > 0 else "weakened"
    elif direction == "lower_better":
        interpretation = "improved" if pct < 0 else "worsened"
    elif direction == "higher_risk":
        interpretation = "risk_increased" if pct > 0 else "risk_decreased"
    else:
        interpretation = "context_changed"

    return f"{trend} / {interpretation}"


def build_indicator_summary(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for indicator_id, meta in INDICATOR_METADATA.items():
        change = calculate_indicator_change(panel, indicator_id)

        if change is None:
            rows.append({
                "indicator_id": indicator_id,
                "label": meta["label"],
                "domain": meta["domain"],
                "direction": meta["direction"],
                "start_year": None,
                "end_year": None,
                "start_value": None,
                "end_value": None,
                "absolute_change": None,
                "percent_change": None,
                "interpretation": "insufficient_data",
            })
            continue

        rows.append({
            "indicator_id": indicator_id,
            "label": meta["label"],
            "domain": meta["domain"],
            "direction": meta["direction"],
            "start_year": change["start_year"],
            "end_year": change["end_year"],
            "start_value": change["start_value"],
            "end_value": change["end_value"],
            "absolute_change": change["absolute_change"],
            "percent_change": change["percent_change"],
            "interpretation": classify_change(change, meta["direction"]),
        })

    return pd.DataFrame(rows)


def build_domain_summary(indicator_summary: pd.DataFrame) -> pd.DataFrame:
    available = indicator_summary[
        indicator_summary["interpretation"] != "insufficient_data"
    ].copy()

    if available.empty:
        return pd.DataFrame(columns=["domain", "summary"])

    rows = []

    for domain, group in available.groupby("domain"):
        interpretations = group["interpretation"].tolist()

        rows.append({
            "domain": domain,
            "indicators_available": len(group),
            "summary": "; ".join(interpretations),
        })

    return pd.DataFrame(rows)