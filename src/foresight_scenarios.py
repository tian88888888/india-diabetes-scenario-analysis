from pathlib import Path
import pandas as pd


SCENARIO_LEVER_MAP = {
    "Reference": {
        "lever": "Baseline trajectory",
        "investment_option": "Use as baseline only",
        "investment_rationale": (
            "The Reference scenario represents the expected future trajectory without additional "
            "risk-factor improvement. It should be used as the comparison baseline, not as an "
            "active investment option."
        ),
    },
    "Safer Environment": {
        "lever": "Environmental and living-condition improvement",
        "investment_option": "Environmental risk and healthy living environment package",
        "investment_rationale": (
            "This option focuses on reducing environmental exposures and improving living conditions. "
            "For diabetes, this is likely to be a secondary pathway unless the scenario shows a large "
            "reduction relative to Reference."
        ),
    },
    "Improved Behavioral and Metabolic Risks": {
        "lever": "Behavioral and metabolic risk reduction",
        "investment_option": "Metabolic-risk prevention and primary-care package",
        "investment_rationale": (
            "This option targets the most diabetes-relevant risk pathways: obesity, diet, physical "
            "activity, blood glucose, blood pressure, and early risk detection. If this scenario produces "
            "the largest reduction, it provides strong support for prioritising prevention and primary-care "
            "management of metabolic risks."
        ),
    },
    "Improved Behavioral And Metabolic Risks": {
        "lever": "Behavioral and metabolic risk reduction",
        "investment_option": "Metabolic-risk prevention and primary-care package",
        "investment_rationale": (
            "This option targets the most diabetes-relevant risk pathways: obesity, diet, physical "
            "activity, blood glucose, blood pressure, and early risk detection. If this scenario produces "
            "the largest reduction, it provides strong support for prioritising prevention and primary-care "
            "management of metabolic risks."
        ),
    },
    "Improved Childhood Nutrition and Vaccination": {
        "lever": "Early-life nutrition and vaccination improvement",
        "investment_option": "Early-life health foundation package",
        "investment_rationale": (
            "This option focuses on childhood nutrition, vaccination, and early-life health conditions. "
            "For adult diabetes burden, it may be a longer-term or indirect prevention pathway unless "
            "the scenario shows a meaningful reduction."
        ),
    },
    "Improved Childhood Nutrition And Vaccination": {
        "lever": "Early-life nutrition and vaccination improvement",
        "investment_option": "Early-life health foundation package",
        "investment_rationale": (
            "This option focuses on childhood nutrition, vaccination, and early-life health conditions. "
            "For adult diabetes burden, it may be a longer-term or indirect prevention pathway unless "
            "the scenario shows a meaningful reduction."
        ),
    },
    "Combined": {
        "lever": "Combined multi-risk improvement",
        "investment_option": "Integrated multi-risk prevention package",
        "investment_rationale": (
            "This option combines multiple risk-improvement pathways. It is useful as an upper-bound "
            "scenario showing what may be possible if several determinant and risk-factor areas improve "
            "together."
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

        # Always calculate percent change from 2025 and 2050 DALYs rate.
        # This avoids ambiguity in IHME's exported "DALYs % change" values,
        # which may be stored as proportions such as -0.56 rather than -56%.
        if (
            dalys_2025 is not None
            and dalys_2050 is not None
            and not pd.isna(dalys_2025)
            and not pd.isna(dalys_2050)
            and dalys_2025 != 0
        ):
            pct_change = ((dalys_2050 - dalys_2025) / dalys_2025) * 100
        else:
            pct_change = None

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
                "lever": "Unmapped scenario pathway",
                "investment_option": "Unmapped investment option",
                "investment_rationale": (
                    "This scenario was not mapped to an investment option. "
                    "Check scenario naming in SCENARIO_LEVER_MAP."
                ),
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
                "investment_option": meta["investment_option"],
                "investment_rationale": meta["investment_rationale"],
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
    Translate Foresight scenario comparison into ranked investment options.

    Only scenarios that reduce 2050 DALYs rate compared with Reference are kept.
    """
    output_dir = Path(f"outputs/{country}/{condition}")
    output_dir.mkdir(parents=True, exist_ok=True)

    columns = [
        "country",
        "condition",
        "priority_rank",
        "scenario",
        "lever",
        "investment_option",
        "estimated_reduction_vs_reference_2050",
        "estimated_percent_reduction_vs_reference_2050",
        "investment_rationale",
        "investment_priority",
    ]

    if scenario_comparison.empty:
        investment_options = pd.DataFrame(columns=columns)
        investment_options.to_csv(output_dir / "investment_options.csv", index=False)
        return investment_options

    usable = scenario_comparison[
        scenario_comparison["scenario"] != "Reference"
    ].copy()

    usable = usable[
        usable["absolute_reduction_vs_reference_2050"].notna()
    ].copy()

    usable = usable[
        usable["absolute_reduction_vs_reference_2050"] > 0
    ].copy()

    if usable.empty:
        investment_options = pd.DataFrame(columns=columns)
        investment_options.to_csv(output_dir / "investment_options.csv", index=False)
        return investment_options

    usable = usable.sort_values(
        by="absolute_reduction_vs_reference_2050",
        ascending=False,
    ).reset_index(drop=True)

    rows = []

    for i, (_, row) in enumerate(usable.iterrows(), start=1):
        percent_reduction = row["percent_reduction_vs_reference_2050"]

        if pd.isna(percent_reduction):
            priority = "Evidence unclear"
        elif percent_reduction >= 10:
            priority = "High priority"
        elif percent_reduction >= 1:
            priority = "Medium priority"
        else:
            priority = "Low priority"

        rows.append(
            {
                "country": country,
                "condition": condition,
                "priority_rank": i,
                "scenario": row["scenario"],
                "lever": row["lever"],
                "investment_option": row["investment_option"],
                "estimated_reduction_vs_reference_2050": row[
                    "absolute_reduction_vs_reference_2050"
                ],
                "estimated_percent_reduction_vs_reference_2050": row[
                    "percent_reduction_vs_reference_2050"
                ],
                "investment_rationale": row["investment_rationale"],
                "investment_priority": priority,
            }
        )

    investment_options = pd.DataFrame(rows)

    investment_options.to_csv(output_dir / "investment_options.csv", index=False)

    return investment_options