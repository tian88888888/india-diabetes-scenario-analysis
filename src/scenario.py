from pathlib import Path


def calculate_change(panel, indicator_id):
    clean = panel[["year", indicator_id]].dropna().sort_values("year")

    if len(clean) < 2:
        return None

    start_year = int(clean.iloc[0]["year"])
    end_year = int(clean.iloc[-1]["year"])
    start_value = clean.iloc[0][indicator_id]
    end_value = clean.iloc[-1][indicator_id]

    absolute_change = end_value - start_value
    percent_change = (absolute_change / start_value) * 100 if start_value != 0 else None

    return {
        "start_year": start_year,
        "end_year": end_year,
        "start_value": start_value,
        "end_value": end_value,
        "absolute_change": absolute_change,
        "percent_change": percent_change,
    }


def format_change(change):
    if change is None:
        return "Not enough data available."

    pct = change["percent_change"]

    if pct is None:
        pct_text = "percentage change unavailable"
    else:
        pct_text = f"{pct:.1f}%"

    return (
        f"{change['start_year']} to {change['end_year']}: "
        f"{change['start_value']:.2f} → {change['end_value']:.2f} "
        f"({pct_text})"
    )


def generate_scenario_card(panel, country, condition):
    dalys_change = calculate_change(panel, "DALYS_RATE")
    ageing_change = calculate_change(panel, "POP_65PLUS")
    urban_change = calculate_change(panel, "URBAN_POP")
    oop_change = calculate_change(panel, "OOP_HEALTH_EXP")
    health_exp_change = calculate_change(panel, "HEALTH_EXP_GDP")
    internet_change = calculate_change(panel, "INTERNET_USERS")

    text = f"""# {country} — {condition} Scenario Card

## 1. Disease burden signal

**Diabetes DALYs rate**

{format_change(dalys_change)}

This shows the long-term burden signal for diabetes. DALYs are used as the main burden measure because they combine premature mortality and non-fatal health loss.

## 2. Risk drivers

### Population ageing

{format_change(ageing_change)}

Ageing is a key risk driver because diabetes and its complications become more common as populations get older.

### Urbanisation

{format_change(urban_change)}

Urbanisation is treated as a lifestyle-transition signal. It may reflect changes in diet, physical activity, work patterns, and service access.

## 3. Health system and financial protection

### Out-of-pocket health expenditure

{format_change(oop_change)}

Out-of-pocket expenditure is interpreted as a financial barrier to care. A lower value generally suggests improved financial protection.

### Health expenditure as % of GDP

{format_change(health_exp_change)}

Health expenditure is interpreted as a system-capacity signal. Higher investment may improve prevention, screening, treatment, and long-term management.

## 4. Individual capability

### Internet access

{format_change(internet_change)}

Internet access is used as a proxy for information access and digital capability, which may support health literacy, telehealth, and prevention outreach.

## 5. Brief-facing interpretation

This scenario card does not claim that freedom-pattern indicators directly cause diabetes burden. Instead, it uses them as contextual determinants for scenario thinking.

For {country}, the core scenario question is:

> Is prevention and health-system capacity improving quickly enough to offset demographic and lifestyle-transition pressures?

## 6. Early scenario hypothesis

If diabetes burden continues to rise while ageing and urbanisation also increase, {country} may face a chronic-disease transition scenario where prevention, early screening, affordability, and primary-care access become increasingly important.

## 7. Suggested prevention investment angles

- Earlier diabetes screening and risk identification
- Primary-care based chronic disease management
- Health literacy and digital outreach
- Financial protection for long-term treatment
- Urban lifestyle and prevention interventions
"""

    output_dir = Path(f"outputs/{country}/{condition}")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "scenario_card.md"
    output_path.write_text(text, encoding="utf-8")

    return output_path