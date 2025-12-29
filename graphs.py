import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.ticker import FuncFormatter, MaxNLocator
from matplotlib.lines import Line2D

scale = 100_000


def plot_median_balances(balances: dict, title: str, filename: str):
    """
    balances format:
    {
        'Market': {1: [...], 2: [...], ...},
        'Box 2':  {1: [...], 2: [...], ...},
    }
    """
    logy = True

    plt.figure(figsize=(8, 5))
    plt.title("Median balances")
    ax = plt.gca()

    for system, yearly_data in balances.items():
        years = sorted(yearly_data.keys())
        medians = [
            np.median(yearly_data[y]) / scale
            for y in years
        ]
        ax.plot(years, medians, label=system)

    ax.set_xlabel("Years")

    unit = f"x{scale:,}"
    ax.set_ylabel(f"Balance {unit}{' (LOG)' if logy else ''}")

    if logy:
        ax.set_yscale("log")
        ax.yaxis.set_major_formatter(
            FuncFormatter(lambda y, _: f"{y:,.0f}".replace(",", "."))
        )
        # ax.yaxis.set_minor_formatter(
        #     FuncFormatter(lambda y, _: f"{y:,.0f}".replace(",", "."))
        # )

    else:
        ax.ticklabel_format(style='plain', axis='y')  # geen scientific notation
        ax.yaxis.set_major_locator(MaxNLocator(nbins=8))
        ax.yaxis.set_major_formatter(
            FuncFormatter(lambda y, _: f"{y:,.0f}".replace(",", "."))
        )

    ax.grid(True, which="both", alpha=0.3)
    ax.legend()

    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

def plot_median_with_min_max(
    balances: dict,
    title: str,
    filename: str,
):
    """
    Plot median with min and max lines.
    Y-axis always starts at zero.
    """

    logy = True

    plt.figure(figsize=(8, 5))
    plt.title("Median balances, with 10%-90% intervals")
    ax = plt.gca()

    for system, yearly_data in balances.items():
        years = sorted(yearly_data.keys())
        medians = [
            np.median(yearly_data[y]) / scale
            for y in years
        ]
        q_vals = [
            np.percentile(yearly_data[y], 10) / scale
            for y in years
        ]
        q2_vals = [
            np.percentile(yearly_data[y], 90) / scale
            for y in years
        ]

        line = ax.plot(years, medians, label=system)[0]

        # Min & Max lines with same color, no label
        ax.plot(years, q_vals, color=line.get_color(), linestyle=":", alpha=0.15)
        ax.plot(years, q2_vals, color=line.get_color(), linestyle="--", alpha=0.15)

    ax.set_xlabel("Jaar")
    unit = f"x{scale:,}"
    ax.set_ylabel(f"Balance {unit}{' (LOG)' if logy else ''}")

    if logy:
        ax.set_yscale("log")
        ax.yaxis.set_major_formatter(
            FuncFormatter(lambda y, _: f"{y:,.0f}".replace(",", "."))
        )
        # ax.yaxis.set_minor_formatter(
        #     FuncFormatter(lambda y, _: f"{y:,.0f}".replace(",", "."))
        # )

    else:
        ax.ticklabel_format(style='plain', axis='y')  # geen scientific notation
        ax.yaxis.set_major_locator(MaxNLocator(nbins=8))
        ax.yaxis.set_major_formatter(
            FuncFormatter(lambda y, _: f"{y:,.0f}".replace(",", "."))
        )

    ax.grid(True, which="both", alpha=0.3)

    custom_handles = [
        Line2D([0], [0], color='gray', linestyle=":", alpha=0.6, label="10%"),
        Line2D([0], [0], color='gray', linestyle="--", alpha=0.6, label="90%")
    ]

    ax.legend(handles=ax.get_legend_handles_labels()[0] + custom_handles)
    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
