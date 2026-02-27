import pandas as pd
from matplotlib import pyplot as plt


def normalize_backtest_results(
    df: pd.DataFrame,
    total_invested_col: str = "total_invested",
    value_col: str = "value",
) -> pd.DataFrame:
    """
    バックテスト結果DFに、比較・可視化で使う派生列を追加する。

    追加列:
      - return_pct_series: (value / total_invested - 1) * 100
      - value_10k_usd: value / 10000
      - invested_10k_usd: total_invested / 10000
    """
    df = df.copy()

    # 10k USD単位に変換（先に作っておくと後続が楽）
    df["value_10k_usd"] = df[value_col] / 10000
    df["invested_10k_usd"] = df[total_invested_col] / 10000

    # リターン率の計算（投資ゼロの行はNaN）
    df["return_pct_series"] = (df[value_col] / df[total_invested_col] - 1) * 100
    df.loc[df[total_invested_col] == 0, "return_pct_series"] = float("nan")

    return df


def calculate_final_metrics(
    df: pd.DataFrame,
    value_10k_col: str = "value_10k_usd",
    invested_10k_col: str = "invested_10k_usd",
) -> dict:
    """
    最終時点のメトリクスを返す（グリッドサーチで扱いやすい dict 形式）。

    Returns:
        {
          "final_value": float,
          "total_invested": float,
          "return_pct": float | None
        }
    """
    # 最終行がNaNの可能性を考えて、最後の有効値を拾う
    invested_series = df[invested_10k_col].dropna()
    value_series = df[value_10k_col].dropna()

    if invested_series.empty or value_series.empty:
        return {"final_value": float("nan"), "total_invested": 0.0, "return_pct": None}

    total_invested = float(invested_series.iloc[-1])
    final_value = float(value_series.iloc[-1])

    if total_invested <= 0:
        return {"final_value": final_value, "total_invested": total_invested, "return_pct": None}

    return_pct = (final_value / total_invested - 1) * 100
    return {"final_value": final_value, "total_invested": total_invested, "return_pct": float(return_pct)}


def plot_portfolio_comparison(
    x,
    y1,
    y2,
    title: str,
    xlabel: str,
    ylabel: str,
    label1: str = "Portfolio Value (10k USD)",
    label2: str = "Total Invested (10k USD)",
    output_path: str | None = None,
    show: bool = True,
) -> None:
    """
    ポートフォリオ価値と投資額の比較グラフを描画。
    グリッドサーチ時は show=False 推奨。
    """
    plt.figure(figsize=(10, 5))
    plt.plot(x, y1, label=label1, linewidth=2)
    plt.plot(x, y2, label=label2, linestyle="--", linewidth=2)

    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150)

    if show:
        plt.show()
    else:
        plt.close()