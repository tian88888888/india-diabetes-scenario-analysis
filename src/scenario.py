from pathlib import Path
import pandas as pd


def format_value(value):
    if pd.isna(value):
        return "NA"
    return f"{value:.2f}"


def format_percent(value):
    if pd.isna(value):
        return "NA"
    return f"{value:.1f}%"


def format_indicator_row(row):
    if pd.isna(row["start_year"]) or pd.isna(row["end_year"]):
        return f"- **{row['label']}**: insufficient data."

    return (
        f"- **{row['label']}**: "
        f"{format_value(row['start_value'])} in {int(row['start_year'])} → "
        f"{format_value(row['end_value'])} in {int(row['end_year'])} "
        f"({format_percent(row['percent_change'])}); "
        f"interpretation: `{row['interpretation']}`"
    )


def get_domain_text(indicator_summary, domain):
    domain_df = indicator_summary[
        (indicator_summary["domain"] == domain)
        & (indicator_summary["interpretation"] != "insufficient_data")
    ]

    if domain_df.empty:
        return "- Not enough data available."

    return "\n".join(
        format_indicator_row(row)
        for _, row in domain_df.iterrows()
    )


def format_forecast_summary(forecast_summary):
    if forecast_summary is None or forecast_summary.empty:
        return "- No IHME Foresight scenario summary available."

    lines = []

    for _, row in forecast_summary.iterrows():
        lines.append(
            f"- **{row['scenario']}**: "
            f"2025 DALYs rate = {format_value(row['dalys_rate_2025'])}; "
            f"2050 DALYs rate = {format_value(row['dalys_rate_2050'])}; "
            f"2025–2050 change = {format_percent(row['dalys_percent_change_2025_2050'])}"
        )

    return "\n".join(lines)


def format_scenario_comparison(scenario_comparison):
    if scenario_comparison is None or scenario_comparison.empty:
        return "- No scenario comparison available."

    lines = []

    for _, row in scenario_comparison.iterrows():
        scenario = row["scenario"]

        lines.append(
            f"- **{scenario}**: "
            f"2050 DALYs rate = {format_value(row['dalys_rate_2050'])}; "
            f"reduction vs Reference = "
            f"{format_value(row['absolute_reduction_vs_reference_2050'])} "
            f"({format_percent(row['percent_reduction_vs_reference_2050'])}); "
            f"lever: **{row['lever']}**"
        )

    return "\n".join(lines)


def format_investment_options(investment_options):
    if investment_options is None or investment_options.empty:
        return "- No investment options could be ranked from the available Foresight scenario data."

    lines = []

    for _, row in investment_options.iterrows():
        lines.append(
            f"{int(row['priority_rank'])}. **{row['investment_option']}** "
            f"({row['investment_priority']})\n"
            f"   - Scenario evidence: **{row['scenario']}**\n"
            f"   - Main lever: {row['lever']}\n"
            f"   - Estimated 2050 DALYs-rate reduction vs Reference: "
            f"{format_value(row['estimated_reduction_vs_reference_2050'])} "
            f"({format_percent(row['estimated_percent_reduction_vs_reference_2050'])})\n"
            f"   - Rationale: {row['investment_rationale']}"
        )

    return "\n".join(lines)


def get_top_investment_sentence(investment_options):
    if investment_options is None or investment_options.empty:
        return (
            "No investment option could be prioritised from the available "
            "Foresight scenario data."
        )

    top = investment_options.iloc[0]

    return (
        f"The leading investment option is **{top['investment_option']}**, supported by the "
        f"**{top['scenario']}** Foresight scenario. This scenario shows an estimated "
        f"2050 DALYs-rate reduction of "
        f"{format_value(top['estimated_reduction_vs_reference_2050'])} "
        f"({format_percent(top['estimated_percent_reduction_vs_reference_2050'])}) "
        f"compared with the Reference trajectory."
    )


def generate_scenario_card(
    panel,
    indicator_summary,
    domain_summary,
    forecast_summary,
    scenario_comparison,
    investment_options,
    country,
    condition,
):
    disease_burden = get_domain_text(indicator_summary, "Disease burden")
    risk_pressure = get_domain_text(indicator_summary, "Risk pressure")
    economic_capability = get_domain_text(indicator_summary, "Economic capability")
    economic_constraint = get_domain_text(indicator_summary, "Economic constraint")
    health_capacity = get_domain_text(indicator_summary, "Health system capacity")
    health_barrier = get_domain_text(indicator_summary, "Health system barrier")
    individual_capability = get_domain_text(indicator_summary, "Individual capability")
    governance_context = get_domain_text(indicator_summary, "Governance context")

    forecast_text = format_forecast_summary(forecast_summary)
    comparison_text = format_scenario_comparison(scenario_comparison)
    investment_text = format_investment_options(investment_options)
    top_investment_sentence = get_top_investment_sentence(investment_options)

    text = f"""# {country} — {condition} Scenario Card

## 1. Purpose

This scenario card summarises historical disease burden, IHME Foresight scenario projections, and country-level determinants for **{country} + {condition}**.

The goal is not to prove causality. The goal is to support forecasting scenario thinking for prevention, health-system readiness, and investment prioritisation.

---

## 2. Historical disease burden signal

{disease_burden}

---

## 3. IHME Foresight scenario summary

{forecast_text}

---

## 4. Scenario comparison against Reference

{comparison_text}

---

## 5. Priority improvement levers

{investment_text}

---

## 6. Main scenario implication

{top_investment_sentence}

This means the scenario analysis should focus less on whether burden is rising in general, and more on which improvement pathway produces the largest projected reduction compared with the Reference trajectory.

---

## 7. Country determinant context

### Risk pressure

{risk_pressure}

### Economic capability

{economic_capability}

### Economic constraint

{economic_constraint}

### Health system capacity

{health_capacity}

### Health system barriers

{health_barrier}

### Individual capability

{individual_capability}

### Governance and civic context

{governance_context}

---

## 8. Brief-facing interpretation

This scenario card combines three types of evidence:

1. **Historical GBD burden**  
   Shows how the condition has changed over time.

2. **IHME Foresight scenarios**  
   Compares future disease burden under Reference and improvement scenarios.

3. **Country determinants**  
   Provides context for whether improvement pathways may be feasible or where investment might be needed.

The key brief-facing question is:

> Which improvement pathway appears most promising under IHME Foresight, and what country-level determinants may support or constrain that pathway?

---

## 9. Suggested use in team scenario work

- Treat **Reference** as the baseline future trajectory.
- Compare improvement scenarios against Reference.
- Use the largest projected reduction to identify priority intervention levers.
- Use country determinants to explain feasibility, constraints, and investment needs.
- Avoid claiming direct causality between determinants and disease burden.
"""

    output_dir = Path(f"outputs/{country}/{condition}")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "scenario_card.md"
    output_path.write_text(text, encoding="utf-8")

    return output_path