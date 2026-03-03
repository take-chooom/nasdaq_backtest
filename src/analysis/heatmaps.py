import os
import pandas as pd
import matplotlib.pyplot as plt


def save_heatmap(df: pd.DataFrame, value_col: str, title: str, out_path: str):
    pivot = (
        df.pivot_table(
            index="buy_amount",
            columns="dip_threshold",
            values=value_col,
            aggfunc="max",
        )
        .sort_index()
    )

    plt.figure(figsize=(10, 6))
    plt.imshow(pivot.values, aspect="auto")
    plt.colorbar(label=value_col)

    plt.xticks(range(len(pivot.columns)), pivot.columns, rotation=45)
    plt.yticks(range(len(pivot.index)), pivot.index)

    plt.xlabel("dip_threshold")
    plt.ylabel("buy_amount")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def main():
    os.makedirs("output", exist_ok=True)

    df = pd.read_csv("output/results2.csv")

    save_heatmap(df, "score", "Heatmap: Score", "output/heatmap_score.png")
    save_heatmap(df, "CAGR", "Heatmap: CAGR", "output/heatmap_cagr.png")
    save_heatmap(df, "MDD_pct", "Heatmap: Max Drawdown (%)", "output/heatmap_mdd.png")
    save_heatmap(df, "rate_per_year", "Heatmap: Buys per Year", "output/heatmap_rate.png")

    print("Saved heatmaps to output/ directory.")


if __name__ == "__main__":
    main()