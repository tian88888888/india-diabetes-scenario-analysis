import argparse

from src.build_panel import build_panel
from src.visualise import plot_trend
from src.scenario import generate_scenario_card
from pathlib import Path

from src.analysis import build_indicator_summary, build_domain_summary
from src.foresight_scenarios import (
    build_forecast_scenario_summary,
    build_scenario_comparison,
    build_improvement_levers,
)

def parse_args():
    parser = argparse.ArgumentParser(
        description="Run country-condition health scenario pipeline."
    )

    parser.add_argument(
        "--country",
        required=True,
        help="Country ISO3 code, e.g. IND",
    )

    parser.add_argument(
        "--condition",
        required=True,
        help="Condition name, e.g. Diabetes",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    country = args.country
    condition = args.condition

    panel, foresight = build_panel(country, condition)

    output_base = Path(f"outputs/{country}/{condition}")

    indicator_summary = build_indicator_summary(panel)
    indicator_summary.to_csv(output_base / "indicator_summary.csv", index=False)

    domain_summary = build_domain_summary(indicator_summary)
    domain_summary.to_csv(output_base / "domain_summary.csv", index=False)
    
    forecast_summary = build_forecast_scenario_summary(
        foresight=foresight,
        country=country,
        condition=condition,
    )

    scenario_comparison = build_scenario_comparison(
        forecast_summary=forecast_summary,
        country=country,
        condition=condition,
    )

    improvement_levers = build_improvement_levers(
        scenario_comparison=scenario_comparison,
        country=country,
        condition=condition,
    )

    output_dir = f"outputs/{country}/{condition}/figures"

    plot_trend(
        panel,
        indicator_id="DALYS_RATE",
        title=f"{country} {condition} DALYs rate",
        ylabel="Age-standardised DALYs rate",
        output_path=f"{output_dir}/dalys_rate_trend.png",
    )

    plot_trend(
        panel,
        indicator_id="DEATHS_RATE",
        title=f"{country} {condition} deaths rate",
        ylabel="Age-standardised deaths rate",
        output_path=f"{output_dir}/deaths_rate_trend.png",
    )

    plot_trend(
        panel,
        indicator_id="PREVALENCE_RATE",
        title=f"{country} {condition} prevalence rate",
        ylabel="Age-standardised prevalence rate",
        output_path=f"{output_dir}/prevalence_rate_trend.png",
    )

    plot_trend(
        panel,
        indicator_id="POP_65PLUS",
        title=f"{country} population aged 65+",
        ylabel="Population aged 65+ (%)",
        output_path=f"{output_dir}/population_65plus_trend.png",
    )

    plot_trend(
        panel,
        indicator_id="URBAN_POP",
        title=f"{country} urban population",
        ylabel="Urban population (%)",
        output_path=f"{output_dir}/urban_population_trend.png",
    )

    plot_trend(
        panel,
        indicator_id="OOP_HEALTH_EXP",
        title=f"{country} out-of-pocket health expenditure",
        ylabel="Out-of-pocket expenditure (% current health expenditure)",
        output_path=f"{output_dir}/oop_health_exp_trend.png",
    )
    plot_trend(
        panel,
        indicator_id="LIBDEM",
        title=f"{country} liberal democracy index",
        ylabel="Liberal democracy index",
        output_path=f"{output_dir}/liberal_democracy_trend.png",
    )
    plot_trend(
        panel,
        indicator_id="POVERTY_HEADCOUNT",
        title=f"{country} poverty headcount",
        ylabel="Poverty headcount ratio",
        output_path=f"{output_dir}/poverty_headcount_trend.png",
    )

    scenario_path = generate_scenario_card(
        panel=panel,
        indicator_summary=indicator_summary,
        domain_summary=domain_summary,
        forecast_summary=forecast_summary,
        scenario_comparison=scenario_comparison,
        improvement_levers=improvement_levers,
        country=country,
        condition=condition,
    )

    print("Pipeline completed successfully.")
    print(f"Scenario card saved to: {scenario_path}")


if __name__ == "__main__":
    main()