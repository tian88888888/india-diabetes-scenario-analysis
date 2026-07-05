from pathlib import Path
import matplotlib.pyplot as plt


def plot_trend(panel, indicator_id, title, ylabel, output_path):
    """
    Plot one indicator over time.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(8, 5))
    plt.plot(panel["year"], panel[indicator_id], marker="o")
    plt.title(title)
    plt.xlabel("Year")
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()