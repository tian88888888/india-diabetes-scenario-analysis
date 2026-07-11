from pathlib import Path
import pandas as pd


SCENARIO_LEVER_MAP = {
    "Reference": {
        "lever": "Baseline / current trajectory",
        "idea": "Use as the comparison baseline for other improvement scenarios.",
    },
    "Safer Environment": {
        "lever": "Environmental risk reduction",
        "idea": "Consider environmental and living-condition interventions that reduce exposure to unsafe environments.",
    },
    "Improved Behavioral and Metabolic Risks": {
        "lever": "Behavioral and metabolic risk reduction",
        "idea": (
            "Prioritise obesity prevention, healthy diets, physical activity, "
            "glucose control, blood pressure control, and primary-care risk screening."
        ),
    },
    "Improved Childhood Nutrition and Vaccination": {
        "lever": "Early-life prevention and immunisation",
        "idea": (
            "Strengthen childhood nutrition, vaccination, and early-life health investments "
            "to reduce long-run disease vulnerability."
        ),
    },
    "Combined": {
        "lever": "Combined multi-risk improvement",
        "idea": (
            "Coordinate interventions across environmental, behavioral, metabolic, "
            "nutrition, and vaccination domains."
        ),
    },
}


def build_forecast_scenario_summary(
    foresight: pd.DataFrame,
    country: str,
    condition: str,
) -> pd.DataFrame:
    """
    Summarise 2025 and 2050 DALYs forecast by IHME Foresight scenario.
    """
    output_dir = Path(f"outputs/{country}/{condition}")
    output_dir.mkdir(parents=True, exist_ok=True)

    if foresight.empty:
        summary = pd.DataFrame(
            columns=[
                "country",
                "condition",
                "scenario",
                "dalys_rate_2025",
                "dalys_rate_2050",
                "dalys_percent_change_2025_2050",
            ]
        )
        summary.to_csv(output_dir / "forecast_scenario_summary.csv", index=False)
        return summary

    rate = foresight[
        foresight["forecast_measure"] == "DALYS_RATE_FORECAST"
    ].copy()

    pct = foresight[
        foresight["forecast_measure"] == "DALYS_PERCENT_CHANGE_FORECAST"
    ].copy()

    rows = []

    for scenario in sorted(foresight["scenario"].dropna().unique()):
        scenario_rate = rate[rate["scenario"] == scenario]
        scenario_pct = pct[pct["scenario"] == scenario]

        dalys_2025 = None
        dalys_2050 = None
        pct_change = None

        row_2025 = scenario_rate[scenario_rate["year"] == "2025"]
        row_2050 = scenario_rate[scenario_rate["year"] == "2050"]

        if not row_2025.empty:
            dalys_2025 = row_2025.iloc[0]["value"]

        if not row_2050.empty:
            dalys_2050 = row_2050.iloc[0]["value"]

        if not scenario_pct.empty:
            pct_change = scenario_pct.iloc[0]["value"]

        if (
            (pct_change is None or pd.isna(pct_change))
            and dalys_2025 is not None
            and dalys_2050 is not None
            and not pd.isna(dalys_2025)
            and dalys_2025 != 0
        ):
            pct_change = ((dalys_2050 - dalys_2025) / dalys_2025) * 100

        rows.append(
            {
                "country": country,
                "condition": condition,
                "scenario": scenario,
                "dalys_rate_2025": dalys_2025,
                "dalys_rate_2050": dalys_2050,
                "dalys_percent_change_2025_2050": pct_change,
            }
        )

    summary = pd.DataFrame(rows)
    summary.to_csv(output_dir / "forecast_scenario_summary.csv", index=False)

    return summary


def build_scenario_comparison(
    forecast_summary: pd.DataFrame,
    country: str,
    condition: str,
) -> pd.DataFrame:
    """
    Compare each IHME Foresight improvement scenario against Reference.
    """
    output_dir = Path(f"outputs/{country}/{condition}")
    output_dir.mkdir(parents=True, exist_ok=True)

    if forecast_summary.empty:
        comparison = pd.DataFrame(
            columns=[
                "country",
                "condition",
                "scenario",
                "dalys_rate_2050",
                "absolute_reduction_vs_reference_2050",
                "percent_reduction_vs_reference_2050",
                "lever",
                "improvement_idea",
            ]
        )
        comparison.to_csv(output_dir / "scenario_comparison.csv", index=False)
        return comparison

    reference = forecast_summary[forecast_summary["scenario"] == "Reference"]

    if reference.empty:
        reference_2050 = None
    else:
        reference_2050 = reference.iloc[0]["dalys_rate_2050"]

    rows = []

    for _, row in forecast_summary.iterrows():
        scenario = row["scenario"]
        dalys_2050 = row["dalys_rate_2050"]

        if (
            reference_2050 is None
            or pd.isna(reference_2050)
            or pd.isna(dalys_2050)
        ):
            absolute_reduction = None
            percent_reduction = None
        else:
            absolute_reduction = reference_2050 - dalys_2050
            percent_reduction = (absolute_reduction / reference_2050) * 100

        meta = SCENARIO_LEVER_MAP.get(
            scenario,
            {
                "lever": "Unmapped scenario lever",
                "idea": "Add this scenario to SCENARIO_LEVER_MAP.",
            },
        )

        rows.append(
            {
                "country": country,
                "condition": condition,
                "scenario": scenario,
                "dalys_rate_2050": dalys_2050,
                "absolute_reduction_vs_reference_2050": absolute_reduction,
                "percent_reduction_vs_reference_2050": percent_reduction,
                "lever": meta["lever"],
                "improvement_idea": meta["idea"],
            }
        )

    comparison = pd.DataFrame(rows)

    comparison = comparison.sort_values(
        by="absolute_reduction_vs_reference_2050",
        ascending=False,
        na_position="last",
    ).reset_index(drop=True)

    comparison.to_csv(output_dir / "scenario_comparison.csv", index=False)

    return comparison


def build_improvement_levers(
    scenario_comparison: pd.DataFrame,
    country: str,
    condition: str,
) -> pd.DataFrame:
    """
    Translate Foresight scenario comparison into improvement levers.
    """
    output_dir = Path(f"outputs/{country}/{condition}")
    output_dir.mkdir(parents=True, exist_ok=True)

    if scenario_comparison.empty:
        levers = pd.DataFrame(
            columns=[
                "country",
                "condition",
                "priority_rank",
                "scenario",
                "lever",
                "estimated_reduction_vs_reference_2050",
                "estimated_percent_reduction_vs_reference_2050",
                "improvement_idea",
            ]
        )
        levers.to_csv(output_dir / "improvement_levers.csv", index=False)
        return levers

    usable = scenario_comparison[
        scenario_comparison["scenario"] != "Reference"
    ].copy()

    usable = usable[
        usable["absolute_reduction_vs_reference_2050"].notna()
    ].copy()

    usable = usable.sort_values(
        by="absolute_reduction_vs_reference_2050",
        ascending=False,
    ).reset_index(drop=True)

    rows = []

    for i, (_, row) in enumerate(usable.iterrows(), start=1):
        rows.append(
            {
                "country": country,
                "condition": condition,
                "priority_rank": i,
                "scenario": row["scenario"],
                "lever": row["lever"],
                "estimated_reduction_vs_reference_2050": row[
                    "absolute_reduction_vs_reference_2050"
                ],
                "estimated_percent_reduction_vs_reference_2050": row[
                    "percent_reduction_vs_reference_2050"
                ],
                "improvement_idea": row["improvement_idea"],
            }
        )

    levers = pd.DataFrame(rows)
    levers.to_csv(output_dir / "improvement_levers.csv", index=False)

    return levers