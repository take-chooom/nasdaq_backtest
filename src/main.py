import pandas as pd
import os
from matplotlib import pyplot as plt
from src.load_prices import load_prices
from src.strategies.dip_buy import dip_buy
from src.strategies.lumpsum import simulate_yearly_lumpsum
from src.utils import calculate_final_metrics
from src.metrics import max_drawdown

def main():
    os.makedirs("output", exist_ok=True)
    df = load_prices("data/prices.sqlite")
    
    rows = []
    # --- lumpsum ---
    res = simulate_yearly_lumpsum(df, yearly_amount=10000)
    # `simulate_yearly_lumpsum` now returns a SimResult dataclass
    hist_ls = res.history_df
    # metrics are already computed in res, but we can recalc if needed
    metrics = calculate_final_metrics(hist_ls)
    maxdd = res.max_drawdown_pct

    rows.append({
        "strategy": "lumpsum_yearly",
        "dip": None,
        "amount_usd": 10000,    # yearly_amount
        "buy_cnt": len(hist_ls),
        "final_value": res.final_value,
        "total_invested": res.total_invested,
        "return_pct": res.return_pct,
        "max_drawdown_pct": maxdd,
    })

    #-----描画------
    plt.figure(figsize=(10,5))
    plt.plot(
        hist_ls["date"],
        hist_ls["return_pct_series"],
        label="lumpsum",
        linewidth=2,
    )
    
    # --- dip_buy grid search ---
    for dip in [0.01*i for i in range(2,10)]:
        res = dip_buy(df, dip=dip, amount=1000)

        history_df = res.history_df
        buy_cnt = int(history_df["buy_signal"].sum())
        metrics = calculate_final_metrics(history_df)
        maxdd = res.max_drawdown_pct

        rows.append({
            "strategy": f"dip_buy_weekly_{int(dip*100)}pct",
            "dip": dip,
            "amount_usd": 1000,
            "buy_cnt": buy_cnt,
            "final_value": res.final_value,
            "total_invested": res.total_invested,
            "return_pct": res.return_pct,
            "max_drawdown_pct": maxdd,
        })
        
        #----描画----
        dip_pct = int(dip * 100)
        plt.plot(history_df["date"],
                 history_df["return_pct_series"],
                 label=f"dip {dip_pct}%")
        
    
    result_df = pd.DataFrame(rows).sort_values(
        ["return_pct", "max_drawdown_pct"], ascending=[False,False]
    )
    result_df.to_csv("output/results1.csv", index=False)
    result_df.to_excel("output/results1.xlsx", index=False)#見やすいように
    
    #----グラフを保存----
    plt.title("Strategy Comparison (QQQ)")
    plt.xlabel("Date")
    plt.ylabel("Return (%)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    plt.savefig("output/strategy_comparison.png", dpi=150)
    plt.close()

    
    
if __name__ == "__main__":
    main()