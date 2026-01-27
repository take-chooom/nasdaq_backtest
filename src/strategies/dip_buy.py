import pandas as pd
from matplotlib import pyplot as plt
from src.metrics import max_drawdown

def dip_buy(df:pd.DataFrame, dip:float, amount=1000):
    df = df.copy().sort_values("date").reset_index(drop=True)
    
    df["buy_signal"] = df["ret"] <= -dip
    
    df["units_bought"] = 0.0
    df.loc[df["buy_signal"], "units_bought"] = amount / df.loc[df["buy_signal"], "adj_close"]
    
    df["units_total"] = df["units_bought"].cumsum()
    df["value"] = df["units_total"] * df["adj_close"]
    
    #累積投資額
    df["total_invested"] = df["buy_signal"].cumsum() * amount 

    #その時点のリターン%
    df["return_pct_series"] = ((df["value"] / df["total_invested"]) - 1) * 100
    df.loc[df["total_invested"] == 0, "return_pct_series"] = float("nan")
    
    maxdd = max_drawdown(df["value"]) * 100
    
    #グラフ用
    df["value_10k_usd"] = df["value"] / 10000
    df["invested_10k_usd"] = df["total_invested"] / 10000
    
    final_value = float(df["value_10k_usd"].iloc[-1])
    total_invested = float(df["invested_10k_usd"].iloc[-1])
    return_pct = (final_value / total_invested - 1) * 100 if total_invested != 0 else float("nan")
    
    return {
        "final_value": final_value,
        "total_invested": total_invested,
        "return_pct": return_pct,
        "max_drawdown_pct": maxdd,
        "history_df": df
    }

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
    