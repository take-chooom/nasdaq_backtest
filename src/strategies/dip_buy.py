import pandas as pd
from matplotlib import pyplot as plt
from src.metrics import max_drawdown
from src.utils import normalize_backtest_results, calculate_final_metrics

# shared dataclasses for strategy results and params
from src.strategies.types import DipBuyParams, SimResult
    
def simulate(df:pd.DataFrame, params:DipBuyParams) -> SimResult:
    df = df.copy().sort_values("date").reset_index(drop=True)
    
    dip = params.dip_threshold
    amount = params.buy_amount
    initial = params.initial_amount if params.initial_amount is not None else amount
    
    
    df["buy_signal"] = (df["ret"] <= -dip).fillna(False)
    
    df["units_bought"] = 0.0
    
    #初期投資(最初に必ず買う)
    df.loc[0, "units_bought"] = initial / df.loc[0, "adj_close"]
    df["initial_invested"] = 0.0
    df.loc[0, "initial_invested"] = initial
    
    #追加投資(dipが発生したときに買う)
    df.loc[df["buy_signal"], "units_bought"] += amount / df.loc[df["buy_signal"], "adj_close"]
    
    
    df["units_total"] = df["units_bought"].cumsum()
    df["value"] = df["units_total"] * df["adj_close"]
    
    #累積投資額
    df["total_invested"] = df["initial_invested"].cumsum() + df["buy_signal"].cumsum() * amount
    
    df = normalize_backtest_results(df)#正規化
    
    maxdd = max_drawdown(df["value"]) * 100
    
    metrics = calculate_final_metrics(df)  # dict
    final_value = metrics["final_value"]
    total_invested = metrics["total_invested"]
    return_pct = metrics["return_pct"]
    
    return SimResult(
        final_value = float(final_value), #型ぶれを防ぐために明示的にfloatにキャスト
        total_invested = float(total_invested),
        return_pct = float(return_pct),
        max_drawdown_pct = float(maxdd),
        history_df = df,
        n_trades = int(df["buy_signal"].sum()) + 1,  #初期投資の回数もカウント
    )
    


def dip_buy(df:pd.DataFrame, dip:float, amount:float = 1000) -> SimResult:
    params = DipBuyParams(dip_threshold=dip, buy_amount=amount, initial_amount=amount)
    return simulate(df, params)
    


if __name__ == "__main__":
    import os
    from src.load_prices import load_prices
    
    os.makedirs("output", exist_ok=True)
    
    db_path = "data/prices.sqlite"
    df = load_prices(db_path)
    
    res = dip_buy(df,0.03)
    final_value, total_invested, return_pct, max_drawdown_pct, history_df = (
        res["final_value"], res["total_invested"], res["return_pct"], res["max_drawdown_pct"],res["history_df"])
    
    buy_cnt = int(history_df["buy_signal"].sum())
    
    print(f"final_value:{final_value:.2f}万ドル,最終リターン(%):{return_pct:.2f}%")
    print(f"購入回数:{buy_cnt}回,最大DD;{max_drawdown_pct: 2f}%")
    #グラフ表示
    x = history_df["date"]
    y1 = history_df["value_10k_usd"]
    y2 = history_df["invested_10k_usd"]
    
    plt.figure(figsize=(10,5))
    plt.plot(x, y1, label="Portfolio Value (10k USD)")
    plt.plot(x, y2, label="Total Invested (10k USD)", linestyle="--")
    
    plt.title("dip_buy_3pct Value (QQQ)")
    plt.xlabel("Date")
    plt.ylabel("Value (10k USD)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("output/dip_buy_3pct_value.png", dpi=150)
    