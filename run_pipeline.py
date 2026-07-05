import argparse

from src.build_panel import build_panel
from src.visualise import plot_trend
from src.scenario import generate_scenario_card


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

    panel = build_panel(country, condition)

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

    scenario_path = generate_scenario_card(
        panel=panel,
        country=country,
        condition=condition,
    )

    print("Pipeline completed successfully.")
    print(f"Scenario card saved to: {scenario_path}")


if __name__ == "__main__":
    main()